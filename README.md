# Building Data Pipeline with Python and PySpark - Pacmann Mentoring Workspace

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL-316192?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Source%20%7C%20Staging%20%7C%20Warehouse-4169E1?logo=postgresql)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter)
![pandas](https://img.shields.io/badge/pandas-Data%20Profiling-150458?logo=pandas)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM%20%2F%20Connection-D71F00)
![uv](https://img.shields.io/badge/uv-Python%20Environment-6E46FF)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-PySpark%20ETL-E25A1C?logo=apachespark)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-Orchestration-017CEE?logo=apacheairflow)
![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-0194E2?logo=mlflow)
![MinIO](https://img.shields.io/badge/MinIO-Object%20Storage-C72E49?logo=minio)

This repository serves as a practice workspace for the **Building Data Pipeline with Python and PySpark** mentoring program by Pacmann. Each `mentoring_*` folder contains the tasks, source code, notebooks, documentation, and output artifacts for its respective mentoring session.

Currently, `mentoring_1` through `mentoring_4` contain complete implementations:

* **`mentoring_1`**: Focuses on data profiling and quality checks using PostgreSQL.
* **`mentoring_2`**: Builds a local ETL pipeline from the source database to the staging area and data warehouse.
* **`mentoring_3`**: Implements a multi-source ETL pipeline utilizing PySpark and a PostgreSQL Data Warehouse.
* **`mentoring_4`**: Adds an Airflow-orchestrated car sales ETL and machine learning pipeline with MLflow and MinIO.

The Mentoring 4 database dataset comes from an external repository and is intentionally
not tracked as a nested Git repository. Clone it before starting the stack:

```bash
git clone https://github.com/Kurikulum-Sekolah-Pacmann/data_pipeline_exercise_4.git \
  mentoring_4/dataset/data_pipeline_exercise_4
```

## Project Status & Navigation

| Mentoring | Focus | Status |
| --- | --- | --- |
| [`mentoring_1`](./mentoring_1/) | Data profiling notebook, JSON quality reports, PostgreSQL source setup | ✅ Completed |
| [`mentoring_2`](./mentoring_2/) | Source -> Staging -> Warehouse ETL, PostgreSQL warehouse, MinIO job-failure payload dump, DB check notebook/PDF | ✅ Completed |
| [`mentoring_3`](./mentoring_3/ans_mentoring3/) | PySpark ETL from PostgreSQL and CSV to PostgreSQL warehouse, profiling, audit history, and semi-CDC | ✅ Completed |
| [`mentoring_4`](./mentoring_4/) | Car sales ETL and ML pipeline with PySpark, Airflow, MLflow, and MinIO | ✅ Completed |

## Progress Log

- [x] **Mentoring 1** - Data profiling and quality validation on Pacmann source datasets.
- [x] **Mentoring 2** - Data integration and ETL pipeline with PostgreSQL source, staging, warehouse, logging, MinIO, uv, and database checking notebook/PDF.
- [x] **Mentoring 3** - Multi-source PySpark ETL with PostgreSQL, CSV, data profiling, audit tables, semi-CDC, centralized logging, and Docker Compose.
- [x] **Mentoring 4** - Car sales ETL and supervised regression pipeline with PostgreSQL, PySpark, Airflow, MLflow, and MinIO.

## Current Workspace Snapshot

- `mentoring_1` through `mentoring_4` are completed project folders.
- The implementations use Python, pandas, PySpark, scikit-learn, SQLAlchemy, PostgreSQL, Docker Compose, uv, Airflow, MLflow, MinIO, pytest, and Jupyter Notebook.
- `mentoring_1` validates source data quality and generates profiling artifacts.
- `mentoring_2` builds an OOP-style ETL pipeline from source to staging and warehouse, with operational logging and job-failure payload handling.
- `mentoring_3` integrates PostgreSQL and CSV sources into a PostgreSQL warehouse using PySpark, with profiling, audit history, and batch semi-CDC comparison.
- `mentoring_4` integrates car sales and reference data into a model-ready warehouse, trains a selling-price regression model, and publishes tracked artifacts.

## Mentoring 1 Highlights

Folder: [`mentoring_1`](./mentoring_1/)

### What It Contains

- Dockerized PostgreSQL source database seeded from CSV files.
- Jupyter notebook for profiling and quality checks.
- Scripted data loading utilities.
- JSON quality reports.
- Local environment configuration using `uv`.

### Main Artifacts

- [`mentoring_1/README.md`](./mentoring_1/README.md) - Main documentation for mentoring 1.
- [`mentoring_1/READ.md`](./mentoring_1/READ.md) - Detailed execution notes.
- `mentoring_1/notebooks/data_profiling_quality_check.ipynb` - Profiling notebook.
- `mentoring_1/output/data_quality_report.json` - Generated quality report.
- `mentoring_1/docs/data_profiling_quality_check.pdf` - Exported notebook report.

### Typical Commands

Run these from inside `mentoring_1`:

```bash
uv sync
uv run python scripts/load_all_data.py
uv run jupyter lab
```

## Mentoring 2 Highlights

Folder: [`mentoring_2`](./mentoring_2/)

### What It Contains

- OOP-style ETL skeleton and implementation under `src/paccafe_pipeline`.
- Docker Compose services for `source_db`, `staging_db`, `warehouse_db`, `log_db`, and MinIO.
- Source extraction from PostgreSQL `paccafe` and local spreadsheet copy for store branch data.
- Staging load for source tables and copied spreadsheet data.
- Warehouse load for dimension and fact tables.
- ETL execution logging into `pipeline_log.public.etl_log`.
- Job-failure payload dump support to MinIO with local fallback.
- Database validation notebook and exported PDF.

### Main Artifacts

- [`mentoring_2/README.md`](./mentoring_2/README.md) - Main documentation for mentoring 2.
- [`mentoring_2/READ.md`](./mentoring_2/READ.md) - Task-based execution documentation.
- [`mentoring_2/plan.md`](./mentoring_2/plan.md) - Execution plan based on week 4 task.
- [`mentoring_2/notebooks/db_data_check.ipynb`](./mentoring_2/notebooks/db_data_check.ipynb) - Notebook to inspect data in each database.
- [`mentoring_2/docs/db_data_check.pdf`](./mentoring_2/docs/db_data_check.pdf) - Exported database check report.
- [`mentoring_2/data/source/store_branch_paccofee.csv`](./mentoring_2/data/source/store_branch_paccofee.csv) - Local copy of store branch spreadsheet data.

### Warehouse Output Snapshot

| Table | Rows |
| --- | ---: |
| `dim_customers` | 204 |
| `dim_employees` | 103 |
| `dim_products` | 54 |
| `dim_store_branch` | 3 |
| `fct_order` | 1010 |
| `fct_inventory` | 162 |

### Typical Commands

Run these from inside `mentoring_2`:

```bash
uv sync
docker compose up -d
uv run python scripts/run_pipeline.py
uv run python -m pytest
uv run jupyter lab notebooks/db_data_check.ipynb
```

## Mentoring 3 Highlights

Folder: [`mentoring_3/ans_mentoring3`](./mentoring_3/ans_mentoring3/)

### What It Contains

- PySpark extraction from PostgreSQL through JDBC and from a partitioned CSV dataset.
- Source and target profiling for row counts, null values, and duplicate primary keys.
- Source-to-target transformations for dates, times, gender, balances, campaign fields, and warehouse schemas.
- PostgreSQL warehouse loading using the required truncate-and-append strategy.
- Batch semi-CDC comparison for inserted, updated, deleted, and unchanged rows.
- Persistent audit history in `etl_pipeline_runs`, `etl_data_profiles`, and `etl_change_summary`.
- Hexagonal application structure with domain, ports, adapters, application, and infrastructure modules.
- Centralized Loguru logging, retry handling, Docker Compose runtime, pytest, Ruff, and an optional EDA notebook.

### Main Artifacts

- [`mentoring_3/ans_mentoring3/README.md`](./mentoring_3/ans_mentoring3/README.md) - Main documentation for mentoring 3.
- [`mentoring_3/task_mentoring_3.md`](./mentoring_3/task_mentoring_3.md) - Original mentoring task.
- [`mentoring_3/ans_mentoring3/docs/source-to-target-map.md`](./mentoring_3/ans_mentoring3/docs/source-to-target-map.md) - Field-level source-to-target mapping.
- [`mentoring_3/ans_mentoring3/docs/latest-etl-run-summary.md`](./mentoring_3/ans_mentoring3/docs/latest-etl-run-summary.md) - Latest validated ETL run summary.
- [`mentoring_3/ans_mentoring3/script/eda.ipynb`](./mentoring_3/ans_mentoring3/script/eda.ipynb) - Source data exploration notebook.
- [`mentoring_3/ans_mentoring3/logs/latest_profile_summary.json`](./mentoring_3/ans_mentoring3/logs/latest_profile_summary.json) - Latest machine-readable profile and semi-CDC report.

### Latest Warehouse Snapshot

The latest full ETL run started from empty databases on **June 14, 2026 WIB** and completed with the `SUCCEEDED` status in 59.49 seconds.

| Table | Rows | Initial Inserted |
| --- | ---: | ---: |
| `education_status` | 4 | 4 |
| `marital_status` | 3 | 3 |
| `marketing_campaign_deposit` | 45,211 | 45,211 |
| `customers` | 1,048,567 | 1,048,567 |
| `transactions` | 1,048,567 | 1,048,567 |

All target tables have zero duplicate primary keys. Every row was classified as `inserted` because the source and warehouse databases were reinitialized before the pipeline ran.

### Typical Commands

Run these from inside `mentoring_3/ans_mentoring3`:

```bash
cp .env.example .env
make run
make summary
make check
make eda
```

## Mentoring 4 Highlights

Folder: [`mentoring_4`](./mentoring_4/)

### What It Contains

- End-to-end car sales pipeline from PostgreSQL source to staging and warehouse.
- Brand mapping from a copied spreadsheet fixture and state mapping from an API-style fixture.
- PySpark transformation using a locally built Spark master and worker image.
- Data cleaning, reference joins, validation, deduplication, and rejected-row accounting.
- Supervised regression with scikit-learn `DecisionTreeRegressor`.
- Airflow orchestration through `DockerOperator`.
- MLflow experiment tracking and MinIO model/prediction artifact storage.
- PostgreSQL ETL audit logs and centralized application logging.
- Docker-based JupyterLab exploration notebook.

### Main Artifacts

- [`mentoring_4/README.md`](./mentoring_4/README.md) - Mentoring entry point and external dataset setup.
- [`mentoring_4/pac_car/README.md`](./mentoring_4/pac_car/README.md) - Main documentation and operational runbook.
- [`mentoring_4/task_mentoring_4.md`](./mentoring_4/task_mentoring_4.md) - Original mentoring task.
- [`mentoring_4/pac_car/project_explanation.md`](./mentoring_4/pac_car/project_explanation.md) - Beginner-oriented explanation of the architecture and prediction logic.
- [`mentoring_4/pac_car/report_summary.md`](./mentoring_4/pac_car/report_summary.md) - Latest clean-start validation report.
- [`mentoring_4/pac_car/notebooks/data_exploration.ipynb`](./mentoring_4/pac_car/notebooks/data_exploration.ipynb) - Executed source and reference data exploration notebook.
- [`mentoring_4/pac_car/docker-compose.yml`](./mentoring_4/pac_car/docker-compose.yml) - Complete PostgreSQL, Spark, Airflow, MLflow, MinIO, pipeline, and notebook stack.

### Latest Validated Run

The latest full run started from empty Docker volumes on **June 17, 2026 WIB** and completed through Airflow with the `success` state.

| Item | Result |
| --- | ---: |
| Source sales rows | 30,000 |
| Staging sales rows | 30,000 |
| Warehouse sales rows | 28,818 |
| Rejected rows | 1,182 |
| R2 score | 0.9708 |
| RMSE | 1661.8552 |
| MAE | 1018.6319 |

The run stored a timestamped model under `s3://pac-car-models/models/` and its test prediction CSV under `s3://pac-car-models/predictions/`.

### Typical Commands

Run these from the repository root:

```bash
docker compose -f mentoring_4/pac_car/docker-compose.yml up -d --build
docker compose -f mentoring_4/pac_car/docker-compose.yml exec -T airflow-scheduler \
  airflow dags trigger pac_car_sales_pipeline
docker compose -f mentoring_4/pac_car/docker-compose.yml ps
```

## Repository Structure

```text
data_pipeline_with_python_and_spark/
├── README.md
├── mentoring_1/
│   ├── README.md
│   ├── READ.md
│   ├── notebooks/
│   ├── scripts/
│   ├── src/
│   ├── output/
│   └── docs/
├── mentoring_2/
│   ├── README.md
│   ├── READ.md
│   ├── plan.md
│   ├── notebooks/
│   ├── scripts/
│   ├── src/
│   ├── tests/
│   ├── data/
│   └── docs/
├── mentoring_3/
│   ├── task_mentoring_3.md
│   └── ans_mentoring3/
│       ├── README.md
│       ├── Dockerfile
│       ├── Makefile
│       ├── docker-compose.yml
│       ├── data/
│       ├── docker/
│       ├── docs/
│       ├── logs/
│       ├── script/
│       ├── src/
│       └── tests/
└── mentoring_4/
    ├── README.md
    ├── task_mentoring_4.md
    ├── dataset/
    │   ├── api_data.json
    │   └── car_brand.csv
    └── pac_car/
        ├── README.md
        ├── docker-compose.yml
        ├── dags/
        ├── docker/
        ├── notebooks/
        ├── project_explanation.md
        ├── report_summary.md
        └── src/
```

## Notes

- Each mentoring folder is intended to be runnable and documented independently.
- Prefer running commands from inside the relevant `mentoring_*` directory.
- Environment values, database ports, and service names can differ between mentoring folders, so check each folder's README before running commands.

## Credits

Built as part of the **Pacmann Academy Bootcamp** learning journey.

<div align="center">

### Building Data Pipeline with Python and PySpark

Dokumen ini dibuat sebagai bagian dari pembelajaran di <strong>Pacmann Academy Bootcamp</strong>.

<a href="https://pacmann.io">
  <img src="https://img.shields.io/badge/BOOTCAMP%20%7C%20PACMANN%20ACADEMY-0D3B66?style=for-the-badge&logoColor=white" alt="Pacmann Academy">
</a>

<a href="https://pacmann.io">pacmann.io</a>

</div>
