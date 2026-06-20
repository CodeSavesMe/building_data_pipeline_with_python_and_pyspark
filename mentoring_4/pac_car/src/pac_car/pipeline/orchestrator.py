from __future__ import annotations

import traceback

from pac_car.clients.database_client import PostgresClient
from pac_car.clients.object_storage_client import MinioClient
from pac_car.clients.reference_api_client import StateReferenceClient
from pac_car.clients.spreadsheet_client import BrandReferenceClient
from pac_car.config.settings import PipelineSettings
from pac_car.pipeline.car_sales_extractor import CarSalesExtractor
from pac_car.pipeline.car_sales_loader import CarSalesLoader
from pac_car.pipeline.car_sales_ml_pipeline import CarSalesMlPipeline
from pac_car.pipeline.car_sales_transformer import CarSalesTransformer
from pac_car.utils.etl_log_repository import EtlLogRepository
from pac_car.utils.logging import configure_logging
from pac_car.utils.summary import ExecutionSummary


def run_pipeline(settings: PipelineSettings) -> ExecutionSummary:
    logger = configure_logging(settings.log_dir)
    summary = ExecutionSummary()
    transformer: CarSalesTransformer | None = None
    database_clients: list[PostgresClient] = []

    try:
        source_db = PostgresClient(settings.source_db, logger)
        staging_db = PostgresClient(settings.staging_db, logger)
        warehouse_db = PostgresClient(settings.warehouse_db, logger)
        log_db = PostgresClient(settings.log_db, logger)
        database_clients.extend([source_db, staging_db, warehouse_db, log_db])

        etl_log = EtlLogRepository(log_db, logger)
        extractor = CarSalesExtractor(
            source_db=source_db,
            staging_db=staging_db,
            warehouse_db=warehouse_db,
            brand_reference_client=BrandReferenceClient(settings.brand_reference_path, logger),
            state_reference_client=StateReferenceClient(settings.state_reference_path, logger),
            logger=logger,
        )
        loader = CarSalesLoader(staging_db=staging_db, warehouse_db=warehouse_db, logger=logger)

        source_sales = extractor.extract_source_sales()
        brand_reference = extractor.extract_brand_reference()
        state_reference = extractor.extract_state_reference()
        summary.extraction_rows.update(
            {
                "source_sales": len(source_sales),
                "brand_reference": len(brand_reference),
                "state_reference": len(state_reference),
            }
        )
        etl_log.write(step="extract", component="CarSalesExtractor", status="SUCCESS")

        summary.staging_rows["car_sales"] = loader.load_staging_sales(source_sales)
        summary.staging_rows["car_brand"] = loader.load_staging_brands(brand_reference)
        summary.staging_rows["us_state"] = loader.load_staging_states(state_reference)
        etl_log.write(
            step="load_staging",
            component="CarSalesLoader",
            status="SUCCESS",
            table_name="public.car_sales, public.car_brand, public.us_state",
        )

        staging_sales = extractor.extract_staging_sales()
        staging_brands = extractor.extract_staging_brands()
        staging_states = extractor.extract_staging_states()
        transformer = CarSalesTransformer(logger, spark_master_url=settings.spark_master_url)
        transform_result = transformer.transform(staging_sales, staging_brands, staging_states)
        summary.transformed_rows = len(transform_result.dataframe)
        summary.rejected_rows = transform_result.rejected_rows
        etl_log.write(step="transform", component="CarSalesTransformer", status="SUCCESS")

        loader.load_warehouse_sales(transform_result.dataframe)
        summary.warehouse_rows = warehouse_db.count_rows("car_sales")
        etl_log.write(
            step="load_warehouse",
            component="CarSalesLoader",
            status="SUCCESS",
            table_name="public.car_sales",
        )

        warehouse_sales = extractor.extract_warehouse_sales()
        model_pipeline = CarSalesMlPipeline(
            minio_client=MinioClient(settings.minio, logger),
            artifact_dir=settings.artifact_dir,
            logger=logger,
            test_size=settings.model_test_size,
            random_seed=settings.model_random_seed,
            mlflow_tracking_uri=settings.mlflow_tracking_uri,
        )
        model_result = model_pipeline.train_and_publish(warehouse_sales)
        summary.feature_columns = model_result.feature_columns
        summary.train_test_split = model_result.train_test_split
        summary.algorithm = model_result.algorithm
        summary.model_metrics = model_result.metrics
        summary.artifact_file = model_result.artifact_file
        summary.artifact_uri = model_result.artifact_uri
        summary.prediction_file = model_result.prediction_file
        summary.prediction_uri = model_result.prediction_uri
        etl_log.write(step="modeling", component="CarSalesMlPipeline", status="SUCCESS")

        summary.mark_success()
        logger.info(summary.render())
        return summary
    except Exception as exc:
        summary.mark_failed(f"{exc}\n{traceback.format_exc()}")
        logger.exception("Pipeline failed")
        try:
            if database_clients:
                EtlLogRepository(database_clients[-1], logger).write(
                    step="pipeline",
                    component="orchestrator",
                    status="FAILED",
                    error_message=str(exc),
                )
        finally:
            logger.info(summary.render())
        return summary
    finally:
        if transformer is not None:
            transformer.stop()
        for client in database_clients:
            client.dispose()
