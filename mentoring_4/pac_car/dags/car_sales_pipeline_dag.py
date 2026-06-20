from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

PIPELINE_ENVIRONMENT = {
    "DATASET_ROOT": "/app/dataset",
    "BRAND_REFERENCE_PATH": "/app/dataset/car_brand.csv",
    "STATE_REFERENCE_PATH": "/app/dataset/api_data.json",
    "SRC_POSTGRES_HOST": "source_db",
    "SRC_POSTGRES_PORT": "5432",
    "SRC_POSTGRES_DB": "source_db",
    "SRC_POSTGRES_USER": "admin",
    "SRC_POSTGRES_PASSWORD": "admin",
    "STG_POSTGRES_HOST": "staging_db",
    "STG_POSTGRES_PORT": "5432",
    "STG_POSTGRES_DB": "staging_db",
    "STG_POSTGRES_USER": "admin",
    "STG_POSTGRES_PASSWORD": "admin",
    "WH_POSTGRES_HOST": "warehouse_db",
    "WH_POSTGRES_PORT": "5432",
    "WH_POSTGRES_DB": "warehouse_db",
    "WH_POSTGRES_USER": "admin",
    "WH_POSTGRES_PASSWORD": "admin",
    "LOG_POSTGRES_HOST": "log_db",
    "LOG_POSTGRES_PORT": "5432",
    "LOG_POSTGRES_DB": "log_db",
    "LOG_POSTGRES_USER": "admin",
    "LOG_POSTGRES_PASSWORD": "admin",
    "MINIO_ENDPOINT_URL": "http://minio:9000",
    "MINIO_ACCESS_KEY": "admin",
    "MINIO_SECRET_KEY": "admin1234",
    "MINIO_BUCKET_NAME": "pac-car-models",
    "MLFLOW_TRACKING_URI": "http://mlflow:5000",
    "MLFLOW_S3_ENDPOINT_URL": "http://minio:9000",
    "AWS_ACCESS_KEY_ID": "admin",
    "AWS_SECRET_ACCESS_KEY": "admin1234",
    "SPARK_MASTER_URL": "spark://spark-master:7077",
    "ARTIFACT_DIR": "/tmp/pac_car_artifacts",
    "LOG_DIR": "/tmp/pac_car_logs",
    "MODEL_TEST_SIZE": "0.2",
    "MODEL_RANDOM_SEED": "42",
    "PYSPARK_PYTHON": "python",
    "PYSPARK_DRIVER_PYTHON": "python",
    "GIT_PYTHON_REFRESH": "quiet",
}


with DAG(
    dag_id="pac_car_sales_pipeline",
    description="End-to-end car sales ETL and machine learning pipeline.",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["pac_car", "etl", "ml"],
) as dag:
    run_pipeline = DockerOperator(
        task_id="run_car_sales_pipeline",
        image="pac_car-pipeline:latest",
        command="pac-car-pipeline",
        docker_url="unix://var/run/docker.sock",
        network_mode="pac_car_network",
        mount_tmp_dir=False,
        auto_remove="success",
        environment=PIPELINE_ENVIRONMENT,
    )
