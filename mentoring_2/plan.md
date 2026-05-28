# Week 4 Execution Plan

## Goal

Build an enterprise-style data integration pipeline for PacCafe using the required layer model:

```text
Source -> Staging -> Warehouse
```

The project must document the data sources, target sink, proposed stack, requirements, solution design, and pipeline design. The implementation must include logging, error handling, and failed-data dumping to object storage.

## Requirements From Task Brief

- Identify all source systems from `data_pipeline_paccafe`:
  - Source repository: `data_pipeline_paccafe`
  - Source PostgreSQL database: `paccafe`
  - Cafe sales data: `orders` and `order_details`
  - Employee data: `employees`
  - Member customer data: `customers`
  - Product data: `products`
  - Inventory tracking history: `inventory_tracking`
- Store branch data from copied spreadsheet data: `store_branch_paccofee.csv`
- Define the sink for integrated data.
- Define the tech stack used to build the pipeline.
- Create requirement gathering and solution documentation.
- Design a pipeline using `Source -> Staging -> Warehouse`.
- Build Python scripts for:
  - Helper functions
  - Staging extract/load
  - Warehouse extract/transform/load
  - Main orchestration
- Store process logs.
- Handle failures consistently.
- Dump failed data to object storage, preferably MinIO.

Scope decision: Google Sheets API extraction is intentionally skipped because the store branch spreadsheet data has already been copied into `data/source/store_branch_paccofee.csv`. The pipeline uses that local copied CSV as the spreadsheet source.

The MinIO/object-storage requirement remains in scope because the task brief notes that failed process data should be saved or dumped into object storage, and MinIO is allowed for that purpose.

## Proposed Architecture

### Source Layer

Sources are read from the `data_pipeline_paccafe` repository on the `week-4` branch and from the copied spreadsheet CSV for store branch data.

- Docker Compose source service: `source_db`.
- Source database name: `paccafe`.
- Staging database name: `staging`.
- Warehouse database name: `warehouse`.
- Log database name: `pipeline_log`.
- Operational database tables:
  - `customers`
  - `employees`
  - `orders`
  - `order_details`
  - `products`
  - `inventory_tracking`
- Copied spreadsheet CSV for `store_branch_paccofee`.

### Staging Layer

The staging layer stores source-aligned raw tables with minimal transformation:

- Preserve source column names as much as possible.
- Add ingestion metadata columns such as `ingested_at`, `source_name`, and `batch_id`.
- Use source-aligned staging tables from `data_pipeline_paccafe/staging_data/init.sql`:
  - `customers`
  - `employees`
  - `orders`
  - `order_details`
  - `products`
  - `inventory_tracking`
  - `store_branch`

### Warehouse Layer

The warehouse layer stores analytics-ready tables. Proposed model:

- Dimensions:
  - `dim_customers`
  - `dim_employees`
  - `dim_products`
  - `dim_store_branch`
  - `dim_date`
- Facts:
  - `fct_order`
  - `fct_inventory`

The provided `data_pipeline_paccafe/warehouse_data/init.sql` already defines the base warehouse table names above. The transformation implementation should follow that target schema unless documentation later changes the model.

### Failed Data Handling

When extract, transform, or load fails:

- Log the failure with job name, batch ID, source name, exception type, and traceback.
- Dump failed rows or failed payloads to MinIO.
- Use a path convention like:

```text
failed-data/{layer}/{job_name}/{batch_id}/{timestamp}.json
```

## Proposed Tech Stack

- Python for pipeline orchestration.
- uv for Python environment and dependency management.
- SQL transformations executed in PostgreSQL.
- PostgreSQL services from `data_pipeline_paccafe/docker-compose.yaml`:
  - `source_db` for source data on host port `5433`.
  - `staging_db` for staging sink on host port `5434`.
  - `warehouse_db` for warehouse sink on host port `5435`.
  - `log_db` for ETL logs on host port `5436`.
- Local `psql` command-line client for PostgreSQL access.
- Local CSV copy for spreadsheet extraction.
- MinIO for failed-data object storage.
- Docker Compose for local services.
- pytest for unit and integration tests.
- Standard Python logging for pipeline logs.
- Jupyter notebook for database inspection.

## OOP Design Standard

The implementation should separate responsibilities:

- `config`: environment and runtime settings.
- `core`: reusable contracts, exceptions, and logging.
- `domain`: business entities and warehouse concepts.
- `infrastructure`: concrete adapters for database, SQL files, and object storage.
- `staging`: source-to-staging jobs.
- `warehouse`: staging-to-warehouse jobs.
- `orchestration`: pipeline runner and main entrypoint.
- `tests`: unit and integration checks.

The job flow should use dependency injection, so each job receives the clients it needs instead of creating infrastructure directly inside the job logic.

## Execution Steps

1. Prepare environment
   - Confirm `data_pipeline_paccafe` is on the `week-4` branch.
   - Start required services from `data_pipeline_paccafe/docker-compose.yaml`.
   - Use the copied Google Spreadsheet data at `data/source/store_branch_paccofee.csv`.
   - Configure `.env` values for source, staging, warehouse, log, spreadsheet, and MinIO.

2. Inspect source data
   - List available source tables from `data_pipeline_paccafe/source_data/init.sql`.
   - Inspect row counts, primary keys, nullable fields, and date fields.
   - Inspect the copied spreadsheet CSV columns.
   - Document source-to-target mapping.

3. Write documentation
   - Add requirement gathering.
   - Add source, sink, and tech stack.
   - Add pipeline design.
   - Add error handling and rerun strategy.

4. Implement helpers
   - Database connection client.
   - SQL file reader.
   - Spreadsheet copy reader.
   - MinIO failed-data client.
   - Logging configuration.

5. Implement staging jobs
   - Extract each source table from `data_pipeline_paccafe.source_db`.
   - Load raw data to staging tables.
   - Add ingestion metadata.
   - Log row counts and job status.

6. Implement warehouse jobs
   - Read from staging tables.
   - Apply transformations and data model rules.
   - Load dimension and fact tables.
   - Log row counts and job status.

7. Implement orchestration
   - Build a single main command that runs staging then warehouse.
   - Stop on fatal failures.
   - Dump failed data to MinIO.
   - Return non-zero status for failed runs.

8. Validate
   - Run unit tests with `uv run python -m pytest`.
   - Run integration tests against local Docker services.
   - Validate staging row counts against source row counts.
   - Validate warehouse referential integrity and duplicate keys.
   - Use `notebooks/db_data_check.ipynb` to inspect source, staging, warehouse, and log data.

## Initial Folder Skeleton

```text
.
├── config/
├── data/
│   └── failed/
├── docs/
│   ├── design/
│   └── requirements/
├── logs/
├── scripts/
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

## Definition Of Done

- `README.md` documents requirements, solution, stack, source/sink, and pipeline design.
- Pipeline can run from one main command.
- Staging tables are populated from all source systems.
- Warehouse tables are populated from staging.
- Logs are generated for every job.
- Failed data is dumped to object storage.
- Tests cover helpers and transformation logic.
- Run instructions are clear and reproducible.
