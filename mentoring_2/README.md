# Mentoring Week 4: PacCafe Data Integration Pipeline

dataclubs.talk cohort notes

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-enabled-6E46FF)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-source%20%7C%20staging%20%7C%20warehouse-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-error%20payload%20storage-C72E49)
![pytest](https://img.shields.io/badge/pytest-6%20passed-0A9EDC)

Program: Building Data Pipeline with Python and PySpark  
Cohort case: PacCafe analytics data integration  
Week: 4  
Pipeline model: `Source -> Staging -> Warehouse`  
Status: Completed for the local mentoring submission  

This project implements the week 4 PacCafe data integration task. The pipeline collects operational data from PostgreSQL, loads source-aligned data into staging, transforms it into an analytics warehouse, writes ETL logs, and stores job-failure payload metadata through MinIO with a local fallback.

This README is the single combined documentation for the previous `README.md` and `READ.md`. The original task brief is available in [task_mentoring_week_4.md](task_mentoring_week_4.md).

## Cohort Brief

### Project Background

PacCafe has several operational datasets that are stored in different places. The manager wants to build analysis and dashboard reporting, but the current data is scattered across operational database tables and spreadsheet data. This creates friction when combining sales, employee, member customer, inventory, product, and store branch information.

This project builds a data integration pipeline that centralizes the available data into a staging database and then transforms it into an analytics-ready warehouse.

### Business Problem

The business needs one reliable data source for analysis. The current condition has these issues:

- Sales, customers, employees, products, and inventory are stored in operational database tables.
- Store branch information is stored separately in Google Spreadsheet `store_branch_paccofee`.
- Data needs to be integrated before it can support dashboard use cases.
- Pipeline runs must be traceable through logs.
- Failed pipeline data must be retained for debugging and rerun.

### Learning Outcomes

This submission covers:

- Identify source, sink, and data stack for a data integration problem.
- Design a `Source -> Staging -> Warehouse` pipeline.
- Build a Python ETL project with OOP-style separation of concerns.
- Load operational PostgreSQL data into staging.
- Load copied spreadsheet data into staging.
- Transform staging data into dimension and fact tables.
- Persist ETL execution logs.
- Dump failure payloads to object storage.
- Validate output through tests, notebook, and exported PDF report.

## Requirement Completion

| Requirement | Status | Implementation |
| --- | --- | --- |
| Identify data source | Complete | PostgreSQL `paccafe` and copied spreadsheet data `store_branch_paccofee.csv`. |
| Identify data sink | Complete | PostgreSQL staging, PostgreSQL warehouse, PostgreSQL log database, MinIO object storage. |
| Identify tech stack | Complete | Python, uv, PostgreSQL, Docker Compose, MinIO, pytest, Jupyter. |
| Requirement gathering and solution design | Complete | Documented in this README and [plan.md](plan.md). |
| Pipeline design with Source -> Staging -> Warehouse | Complete | Implemented in `src/paccafe_pipeline`. |
| Helper functions | Complete | Database, logging, SQL reader, settings, and object storage helpers. |
| Staging script | Complete | `src/paccafe_pipeline/staging/jobs.py`. |
| Warehouse script | Complete | `src/paccafe_pipeline/warehouse/jobs.py` and `src/paccafe_pipeline/warehouse/sql.py`. |
| Main script | Complete | `src/paccafe_pipeline/orchestration/pipeline.py`, `scripts/run_pipeline.py`, and CLI `paccafe-pipeline`. |
| Logging process | Complete | ETL logs stored in `pipeline_log.public.etl_log`. |
| Error handling | Complete | Job-level exception handling and job-failure payload dump. |
| Object storage for job-failure payloads | Complete | MinIO bucket `failed-data`, with local fallback under `data/failed`. |
| Spreadsheet API fetch | Skipped by scope decision | Store branch spreadsheet data was manually copied into `data/source/store_branch_paccofee.csv` and loaded from that local source. |
| Database validation artifact | Complete | [notebooks/db_data_check.ipynb](notebooks/db_data_check.ipynb) and [docs/db_data_check.pdf](docs/db_data_check.pdf). |

### Functional Requirements

| ID | Requirement | Solution |
| --- | --- | --- |
| FR-01 | Identify project data sources | Use PostgreSQL source database `paccafe` and copied spreadsheet data `store_branch_paccofee.csv`. |
| FR-02 | Dump source data into a centralized layer | Load raw/source-aligned data into PostgreSQL staging database `staging`. |
| FR-03 | Build analytics-ready tables | Transform staging tables into warehouse dimensions and facts in PostgreSQL database `warehouse`. |
| FR-04 | Run all pipeline processes from one entrypoint | Provide a Python main runner under `src/paccafe_pipeline/orchestration`. |
| FR-05 | Add reusable helper functions | Provide reusable infrastructure modules for database, SQL reader, spreadsheet copy reader, logging, and object storage. |
| FR-06 | Store logs for each ETL process | Use standard Python logging and the `pipeline_log` PostgreSQL database for ETL log persistence. |
| FR-07 | Handle failed pipeline data | Dump job-failure payloads into MinIO object storage. |

### Non-Functional Requirements

| ID | Requirement | Solution |
| --- | --- | --- |
| NFR-01 | Maintainable project structure | Use OOP design with clear separation between config, core contracts, infrastructure, staging, warehouse, and orchestration. |
| NFR-02 | Reproducible local environment | Use Docker Compose from `data_pipeline_paccafe/docker-compose.yaml`. |
| NFR-03 | Testable implementation | Use pytest for unit tests and local end-to-end validation. |
| NFR-04 | Recoverable failure process | Keep logs and failed data dumps with job metadata. |
| NFR-05 | Clear operational documentation | Keep the task brief, plan, runbook, validation result, and artifact list in this repository. |

## Architecture

```mermaid
flowchart TD
    SRC_DB[(PostgreSQL Source<br/>paccafe)]
    SRC_CSV[[Spreadsheet Copy<br/>store_branch_paccofee.csv]]
    STG[(Staging Database<br/>staging<br/>source-aligned tables)]
    WH_STG[(Warehouse Transient Schema<br/>etl_staging)]
    WH[(Warehouse Database<br/>warehouse<br/>dimensions and facts)]
    LOG[(Log Database<br/>pipeline_log.public.etl_log)]
    MINIO[(MinIO Object Storage<br/>bucket name: failed-data)]
    LOCAL[[Local Fallback<br/>data/failed]]

    SRC_DB -->|extract and load source tables| STG
    SRC_CSV -->|load store branch data| STG
    STG -->|sync staging tables| WH_STG
    WH_STG -->|SQL transform and load| WH

    STG -. job status .-> LOG
    WH_STG -. job status .-> LOG
    WH -. warehouse summary .-> LOG

    STG -. job-failure payload .-> MINIO
    WH_STG -. job-failure payload .-> MINIO
    MINIO -. fallback when unavailable .-> LOCAL
```

### Implemented Pipeline Flow

1. Extract operational data from PostgreSQL source tables.
2. Extract store branch data from copied spreadsheet CSV.
3. Load raw/source-aligned data into the staging database.
4. Sync staging tables into the warehouse transient schema `etl_staging`.
5. Transform staging data into dimensional warehouse tables.
6. Load warehouse dimension and fact tables.
7. Write ETL logs for each process.
8. Store job-failure payloads in MinIO when a process fails.

## Data Sources

### PostgreSQL Source

Source repository and service:

```text
data_pipeline_paccafe/
source_db -> localhost:5433 -> database: paccafe
```

The source repository is expected to use the `week-4` branch, matching the mentoring task brief.

Source tables:

| Table | Description | Verified Rows |
| --- | --- | ---: |
| `customers` | Member customer data | 204 |
| `employees` | Employee data | 103 |
| `orders` | Sales order header data | 1010 |
| `order_details` | Sales order detail data | 3022 |
| `products` | Product and branch reference data | 54 |
| `inventory_tracking` | Inventory movement history | 162 |

### Spreadsheet Source

The task requires store branch data from spreadsheet. In this implementation, Google Sheets API extraction is intentionally skipped because the spreadsheet data has already been copied into the repository as CSV:

```text
data/source/store_branch_paccofee.csv
```

Copied data:

| store_id | store_name | created_at |
| ---: | --- | --- |
| 1 | Dapur Kenangan | 2025-01-31 20:43:18 |
| 2 | Laci Coffee | 2025-01-31 20:43:18 |
| 3 | Setara Coffee | 2025-01-31 20:43:18 |

## Data Sinks

| Sink | Service | Database or Bucket | Purpose |
| --- | --- | --- | --- |
| Staging database | `staging_db` | `staging` | Store raw/source-aligned data. |
| Warehouse database | `warehouse_db` | `warehouse` | Store analytics-ready dimensions and facts. |
| Log database | `log_db` | `pipeline_log` | Store ETL run history. |
| Object storage | `minio` | `failed-data` | Store job-failure payload metadata. |

## Warehouse Model

### Staging Layer

The staging layer stores source-aligned tables with minimal transformation. These tables are defined by `data_pipeline_paccafe/staging_data/init.sql`:

```text
customers
employees
orders
order_details
products
inventory_tracking
store_branch
```

Recommended ingestion metadata for future improvement:

```text
batch_id
source_name
ingested_at
```

### Warehouse Layer

The warehouse layer stores analytics-ready tables. These tables are defined by `data_pipeline_paccafe/warehouse_data/init.sql`.

Dimensions:

```text
dim_customers
dim_employees
dim_products
dim_store_branch
dim_date
```

Facts:

```text
fct_order
fct_inventory
```

### Source to Warehouse Mapping

| Source | Staging | Warehouse |
| --- | --- | --- |
| `customers` | `customers` | `dim_customers` |
| `employees` | `employees` | `dim_employees` |
| `products` | `products` | `dim_products` |
| `store_branch_paccofee.csv` | `store_branch` | `dim_store_branch` |
| `orders`, `order_details` | `orders`, `order_details` | `fct_order` |
| `inventory_tracking` | `inventory_tracking` | `fct_inventory` |
| warehouse init data | none | `dim_date` |

Expected warehouse output after a successful run:

| Warehouse Table | Rows |
| --- | ---: |
| `dim_customers` | 204 |
| `dim_employees` | 103 |
| `dim_products` | 54 |
| `dim_store_branch` | 3 |
| `fct_order` | 1010 |
| `fct_inventory` | 162 |

## Tech Stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.10+ |
| Environment manager | uv |
| Runtime orchestration | Python CLI and module entrypoint |
| Source database | PostgreSQL 16 |
| Staging database | PostgreSQL 16 |
| Warehouse database | PostgreSQL 16 |
| Log database | PostgreSQL 16 |
| Object storage | MinIO |
| Local services | Docker Compose |
| Testing | pytest |
| Data inspection | Jupyter Notebook, nbconvert PDF |
| Database client strategy | Local `psql` command wrapper |

## Project Structure

```text
.
├── README.md
├── READ.md
├── plan.md
├── task_mentoring_week_4.md
├── pyproject.toml
├── uv.lock
├── config/
│   └── .env.example
├── data/
│   ├── failed/
│   └── source/
│       └── store_branch_paccofee.csv
├── data_pipeline_paccafe/
│   ├── docker-compose.yaml
│   ├── source_data/
│   ├── staging_data/
│   ├── warehouse_data/
│   └── log_data/
├── docs/
│   ├── design/
│   ├── requirements/
│   └── db_data_check.pdf
├── notebooks/
│   ├── db_data_check.ipynb
│   └── db_data_check.html
├── scripts/
│   └── run_pipeline.py
├── sql/
│   ├── staging/
│   └── warehouse/
├── src/
│   └── paccafe_pipeline/
│       ├── config/
│       ├── core/
│       ├── domain/
│       ├── infrastructure/
│       ├── orchestration/
│       ├── staging/
│       └── warehouse/
└── tests/
    ├── integration/
    └── unit/
```

## OOP Package Design

| Package | Responsibility |
| --- | --- |
| `paccafe_pipeline.config` | Load runtime settings from environment variables. |
| `paccafe_pipeline.core` | Shared contracts, exceptions, and logging setup. |
| `paccafe_pipeline.domain` | Domain objects such as batch context. |
| `paccafe_pipeline.infrastructure` | Database, log repository, SQL reader, and object storage adapters. |
| `paccafe_pipeline.staging` | Source-to-staging extract/load jobs. |
| `paccafe_pipeline.warehouse` | Staging sync and warehouse transformation jobs. |
| `paccafe_pipeline.orchestration` | Pipeline assembly and main runner. |

Main pipeline classes:

| Class | Role |
| --- | --- |
| `PipelineRunner` | Runs staging then warehouse. |
| `SourceToStagingJob` | Copies one PostgreSQL source table into staging. |
| `SpreadsheetCopyToStagingJob` | Loads copied spreadsheet CSV into staging. |
| `WarehouseStagingSyncJob` | Syncs staging tables into warehouse transient schema `etl_staging`. |
| `WarehouseSqlJob` | Runs warehouse transformation SQL. |
| `PipelineLogRepository` | Persists ETL log events. |
| `MinioObjectStorageClient` | Dumps job-failure payload metadata to MinIO or local fallback. |

## Environment Configuration

The implementation uses defaults that match the provided `.env` values. You can override these variables if needed.

```env
SRC_POSTGRES_DB=paccafe
SRC_POSTGRES_USER=postgres
SRC_POSTGRES_PASSWORD=postgres
SRC_POSTGRES_PORT=5433

STG_POSTGRES_DB=staging
STG_POSTGRES_USER=postgres
STG_POSTGRES_PASSWORD=postgres
STG_POSTGRES_PORT=5434

WH_POSTGRES_DB=warehouse
WH_POSTGRES_USER=postgres
WH_POSTGRES_PASSWORD=postgres
WH_POSTGRES_PORT=5435

LOG_POSTGRES_DB=pipeline_log
LOG_POSTGRES_USER=postgres
LOG_POSTGRES_PASSWORD=postgres
LOG_POSTGRES_PORT=5436

MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

Additional supported variables:

```env
APP_ENV=local
LOG_LEVEL=INFO
STORE_BRANCH_CSV_PATH=data/source/store_branch_paccofee.csv
MINIO_ENDPOINT=localhost:9000
FAILED_DATA_BUCKET=failed-data
```

## Prerequisites

- Docker and Docker Compose
- PostgreSQL client CLI: `psql`
- Python 3.10 or newer
- uv

Check the important local tools:

```bash
docker --version
docker compose version
psql --version
uv --version
```

## Quickstart

Run from the `mentoring_2` directory.

### 1. Install Dependencies

```bash
uv sync
```

Install notebook dependencies too:

```bash
uv sync --group notebook
```

### 2. Start Local Services

```bash
cd data_pipeline_paccafe
docker compose up -d
cd ..
```

Expected service map:

| Service | Port | Database or UI |
| --- | ---: | --- |
| `source_db` | 5433 | `paccafe` |
| `staging_db` | 5434 | `staging` |
| `warehouse_db` | 5435 | `warehouse` |
| `log_db` | 5436 | `pipeline_log` |
| `minio` | 9000 | API |
| `minio` | 9090 | Console UI |

### 3. Run the Pipeline

Preferred command:

```bash
uv run paccafe-pipeline
```

Equivalent commands:

```bash
uv run python -m paccafe_pipeline
uv run python scripts/run_pipeline.py
```

### 4. Run Tests

```bash
uv run python -m pytest
```

Latest local result:

```text
6 passed
```

### 5. Inspect the Databases

Open the notebook:

```bash
uv run jupyter notebook notebooks/db_data_check.ipynb
```

Available validation artifacts:

- Notebook: [notebooks/db_data_check.ipynb](notebooks/db_data_check.ipynb)
- HTML export: [notebooks/db_data_check.html](notebooks/db_data_check.html)
- PDF export: [docs/db_data_check.pdf](docs/db_data_check.pdf)

## Manual Database Checks

Source database:

```bash
psql postgresql://postgres:postgres@localhost:5433/paccafe -c "\\dt"
```

Staging database:

```bash
psql postgresql://postgres:postgres@localhost:5434/staging -c "\\dt"
```

Warehouse database:

```bash
psql postgresql://postgres:postgres@localhost:5435/warehouse -c "\\dt"
```

ETL log database:

```bash
psql postgresql://postgres:postgres@localhost:5436/pipeline_log -c "select * from public.etl_log order by id desc limit 10;"
```

Warehouse row count check:

```bash
psql postgresql://postgres:postgres@localhost:5435/warehouse -c "
select 'dim_customers' as table_name, count(*) from public.dim_customers
union all select 'dim_employees', count(*) from public.dim_employees
union all select 'dim_products', count(*) from public.dim_products
union all select 'dim_store_branch', count(*) from public.dim_store_branch
union all select 'fct_order', count(*) from public.fct_order
union all select 'fct_inventory', count(*) from public.fct_inventory
order by table_name;
"
```

## Logging and Failure Handling

Note: `failed-data` is the MinIO bucket name for payloads produced by failed ETL jobs. It does not mean MinIO failed. In the latest validation, the MinIO service was running and the job-failure payload dump flow was verified.

This storage behavior comes from the week 4 task note: if a process fails, save or dump the failed data into object storage; MinIO is allowed for that object storage.

Every ETL job writes status information to:

```text
pipeline_log.public.etl_log
```

Log information includes:

- `log_id`
- `step`
- `component`
- `status`
- `table_name`
- `etl_date`
- `error_msg`

Successful jobs include row counts or warehouse summary data in `error_msg`. Failed jobs include the error message and job-failure payload path.

If a job fails:

1. The job catches the exception.
2. Failure metadata is written to `etl_log`.
3. A job-failure payload is dumped to MinIO bucket `failed-data`.
4. If MinIO is not reachable, the payload is written to local fallback storage under `data/failed`.
5. The pipeline raises the error and stops the run.

Recommended object path pattern for job-failure payloads:

```text
failed-data/{layer}/{job_name}/{batch_id}/{timestamp}.json
```

## Validation Summary

| Check | Result |
| --- | --- |
| Source PostgreSQL services | Verified |
| Staging PostgreSQL services | Verified |
| Warehouse PostgreSQL services | Verified |
| Log PostgreSQL service | Verified |
| MinIO service | Verified |
| Source table row counts | Verified |
| Staging table row counts | Verified |
| Warehouse table row counts | Verified |
| Store branch CSV load | Verified |
| ETL logging | Verified |
| Job-failure payload dump to MinIO | Verified |
| Unit tests | `6 passed` |
| Database check notebook | Executed |
| PDF report | Generated |

Verified source row counts:

```text
customers: 204
employees: 103
orders: 1010
order_details: 3022
products: 54
inventory_tracking: 162
```

Verified staging row counts after pipeline run:

```text
customers: 204
employees: 103
orders: 1010
order_details: 3022
products: 54
inventory_tracking: 162
store_branch: 3
```

Verified warehouse row counts after pipeline run:

```text
dim_customers: 204
dim_employees: 103
dim_products: 54
dim_store_branch: 3
fct_order: 1010
fct_inventory: 162
```

## Current Implementation Status

Completed:

- Requirement and execution plan in [plan.md](plan.md).
- `uv` project configuration in [pyproject.toml](pyproject.toml).
- `uv.lock` generated for reproducible dependency resolution.
- OOP folder skeleton.
- Runtime settings loader.
- Pipeline runner for staging and warehouse execution.
- PostgreSQL helper using `psql`.
- SQL file reader helper.
- Spreadsheet copy reader for `store_branch_paccofee.csv`.
- Logging helper.
- MinIO object-storage helper for job-failure payloads with local fallback.
- Unit tests for settings, helpers, spreadsheet copy, and pipeline construction.
- Docker Compose environment validated.
- PostgreSQL and MinIO services tested.
- Staging extract/load jobs for PostgreSQL source tables.
- Staging extract/load job for copied spreadsheet data.
- Warehouse staging sync.
- Warehouse dimension and fact loading.
- ETL log persistence into `pipeline_log.public.etl_log`.
- Error handling and job-failure payload dumping.
- Database check notebook in [notebooks/db_data_check.ipynb](notebooks/db_data_check.ipynb).
- Exported database check reports in [notebooks/db_data_check.html](notebooks/db_data_check.html) and [docs/db_data_check.pdf](docs/db_data_check.pdf).

Optional future improvement:

- Integration tests can be expanded, but the local end-to-end pipeline has already been validated.

## Main Artifacts

| Artifact | Description |
| --- | --- |
| [READ.md](READ.md) | Legacy alias that points back to this combined README. |
| [plan.md](plan.md) | Execution plan generated from the week 4 task brief. |
| [task_mentoring_week_4.md](task_mentoring_week_4.md) | Original mentoring task brief. |
| [pyproject.toml](pyproject.toml) | uv project configuration, package metadata, CLI entrypoint, and dependency groups. |
| [uv.lock](uv.lock) | Locked dependency resolution. |
| [src/paccafe_pipeline](src/paccafe_pipeline) | Main ETL package. |
| [scripts/run_pipeline.py](scripts/run_pipeline.py) | Script entrypoint for the pipeline. |
| [data/source/store_branch_paccofee.csv](data/source/store_branch_paccofee.csv) | Copied spreadsheet data. |
| [notebooks/db_data_check.ipynb](notebooks/db_data_check.ipynb) | Database inspection notebook. |
| [notebooks/db_data_check.html](notebooks/db_data_check.html) | HTML export of the database check notebook. |
| [docs/db_data_check.pdf](docs/db_data_check.pdf) | PDF report of database checks. |
| [tests/unit](tests/unit) | Unit tests for settings, helpers, and pipeline construction. |

## Troubleshooting

### `psql` command not found

Install PostgreSQL client tools and confirm `psql --version` works.

### Database connection refused

Check that Docker services are running:

```bash
cd data_pipeline_paccafe
docker compose ps
cd ..
```

### Port already in use

The project expects ports `5433`, `5434`, `5435`, `5436`, `9000`, and `9090`. Stop the conflicting service or update the compose and environment configuration together.

### If MinIO Upload Fails

The latest validation confirms MinIO works. If MinIO is unavailable in a future run, the pipeline falls back to local job-failure payload storage. Check:

```text
data/failed/
```

### Notebook cannot import package

Run the notebook through uv from the project root:

```bash
uv sync --group notebook
uv run jupyter notebook notebooks/db_data_check.ipynb
```

## Definition of Done

This mentoring task is considered complete because:

- Data source, sink, and stack are documented.
- Requirement gathering and solution design are documented.
- The pipeline implements `Source -> Staging -> Warehouse`.
- Source PostgreSQL tables are loaded into staging.
- Store branch spreadsheet copy is loaded into staging from `data/source/store_branch_paccofee.csv`.
- Warehouse dimensions and facts are populated.
- Logs are stored in a dedicated PostgreSQL log database.
- Job-failure payload handling is implemented through MinIO and local fallback.
- The pipeline can run from one CLI command.
- Tests pass locally.
- Local end-to-end pipeline execution has been validated.
- Database output is validated through notebook, HTML, and PDF artifacts.
