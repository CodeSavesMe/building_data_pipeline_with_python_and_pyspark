# PAC Car Run Report Summary

Report ini merangkum hasil run terakhir setelah project dijalankan dari kondisi Docker storage kosong.

## Run Context

| Item | Value |
|---|---|
| Reset command | `docker compose -f pac_car/docker-compose.yml down -v` |
| Start command | `docker compose -f pac_car/docker-compose.yml up -d` |
| Airflow DAG | `pac_car_sales_pipeline` |
| Airflow run id | `clean_start_20260617_0001` |
| Task id | `run_car_sales_pipeline` |
| Run state | `success` |
| Execution date | `2026-06-16T20:11:11+00:00` |
| Start date | `2026-06-16T20:11:15.742663+00:00` |
| End date | `2026-06-16T20:14:46.094368+00:00` |
| Pipeline start | `2026-06-16 20:11:57` |
| Pipeline duration | `160.06` seconds |
| Final status | `SUCCESS` |

## Storage Reset Result

The `down -v` reset removed and recreated these project volumes:

| Volume |
|---|
| `pac_car_source_volume` |
| `pac_car_staging_volume` |
| `pac_car_warehouse_volume` |
| `pac_car_log_volume` |
| `pac_car_minio_volume` |
| `pac_car_mlflow_volume` |
| `pac_car_airflow_db_volume` |

After reset, the clean run generated only one model artifact and one prediction artifact in MinIO.

## Docker Images Used

| Service/container | Image | Tag | Size |
|---|---|---|---|
| `pac_car_airflow_db` | `postgres` | `16` | `159MB` |
| `pac_car_airflow_init` | `pac_car-airflow` | `latest` | `429MB` |
| `pac_car_airflow_scheduler` | `pac_car-airflow` | `latest` | `429MB` |
| `pac_car_airflow_webserver` | `pac_car-airflow` | `latest` | `429MB` |
| `pac_car_log_db` | `postgres` | `16` | `159MB` |
| `pac_car_minio` | `minio/minio` | `latest` | `57.5MB` |
| `pac_car_minio_init` | `minio/mc` | `latest` | `27.4MB` |
| `pac_car_mlflow` | `pac_car-pipeline` | `latest` | `2.21GB` |
| `pac_car_notebook` | `pac_car-notebook` | `latest` | `2.26GB` |
| `pac_car_pipeline` | `pac_car-pipeline` | `latest` | `2.21GB` |
| `pac_car_source_db` | `postgres` | `16` | `159MB` |
| `pac_car_spark_master` | `pac_car-spark` | `latest` | `465MB` |
| `pac_car_spark_worker` | `pac_car-spark` | `latest` | `465MB` |
| `pac_car_staging_db` | `postgres` | `16` | `159MB` |
| `pac_car_warehouse_db` | `postgres` | `16` | `159MB` |

## Service Status

All required services were running after the clean start.

| Service | Status |
|---|---|
| `source_db` | healthy |
| `staging_db` | healthy |
| `warehouse_db` | healthy |
| `log_db` | healthy |
| `airflow_db` | healthy |
| `minio` | healthy |
| `airflow-webserver` | healthy |
| `airflow-scheduler` | running |
| `pipeline` | running |
| `mlflow` | running |
| `notebook` | running |
| `spark-master` | running |
| `spark-worker` | running |

## Pipeline Results

### Extraction

| Source | Rows |
|---|---:|
| Source database sales | 30000 |
| Brand reference | 51 |
| State reference | 68 |

### Staging

| Table | Rows |
|---|---:|
| `public.car_sales` | 30000 |
| `public.car_brand` | 51 |
| `public.us_state` | 68 |

### Transformation

| Metric | Rows |
|---|---:|
| Processed rows | 30000 |
| Loaded rows | 28818 |
| Rejected rows | 1182 |
| Warehouse rows | 28818 |

### Database Row Counts

| Database | Table | Rows |
|---|---|---:|
| `source_db` | `public.car_sales` | 30000 |
| `staging_db` | `public.car_sales` | 30000 |
| `warehouse_db` | `public.car_sales` | 28818 |
| `log_db` | `public.etl_log` | 5 |

## Machine Learning Results

| Item | Value |
|---|---|
| Feature columns | `year`, `brand_car_id`, `id_state`, `condition`, `odometer`, `mmr`, `transmission`, `color`, `interior` |
| Train/test split | `80%/20%` |
| Algorithm | `DecisionTreeRegressor` |
| R2 score | `0.9708` |
| RMSE | `1661.8552` |
| MAE | `1018.6319` |
| MLflow experiment | `pac_car_sales_price_prediction` |
| MLflow run | `car_sales_decision_tree_20260616_201432` |

## MinIO Artifacts

| Type | Object | Size |
|---|---|---:|
| Model | `s3://pac-car-models/models/car_sales_decision_tree_20260616_201432.pkl` | `33571` bytes |
| Prediction output | `s3://pac-car-models/predictions/car_sales_predictions_20260616_201432.csv` | `446326` bytes |

## Verification Commands

```bash
docker compose -f pac_car/docker-compose.yml down -v
docker compose -f pac_car/docker-compose.yml up -d
docker compose -f pac_car/docker-compose.yml images
docker compose -f pac_car/docker-compose.yml ps
docker compose -f pac_car/docker-compose.yml exec -T airflow-scheduler airflow dags trigger pac_car_sales_pipeline --run-id clean_start_20260617_0001
docker compose -f pac_car/docker-compose.yml exec -T airflow-scheduler airflow dags list-runs -d pac_car_sales_pipeline --no-backfill
```

## Conclusion

The project can start from empty Docker volumes and complete the full Airflow-triggered pipeline successfully. The clean run repopulated the PostgreSQL databases, transformed the warehouse dataset, trained the model, logged metrics to MLflow, and saved both model and prediction artifacts to MinIO.
