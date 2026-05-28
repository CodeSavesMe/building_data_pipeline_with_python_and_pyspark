# Building Data Pipeline with Python and PySpark - Pacmann Mentoring Workspace

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL-316192?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Source%20%7C%20Staging%20%7C%20Warehouse-4169E1?logo=postgresql)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter)
![pandas](https://img.shields.io/badge/pandas-Data%20Profiling-150458?logo=pandas)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM%20%2F%20Connection-D71F00)
![uv](https://img.shields.io/badge/uv-Python%20Environment-6E46FF)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-Planned-E25A1C?logo=apachespark)

Repository ini dipakai sebagai workspace latihan mentoring **Building Data Pipeline with Python and PySpark** dari Pacmann. Setiap folder `mentoring_*` menyimpan tugas, kode, notebook, dokumentasi, dan artefak output untuk sesi mentoring terkait.

Saat ini `mentoring_1` dan `mentoring_2` sudah berisi implementasi lengkap. `mentoring_1` fokus pada data profiling dan quality check PostgreSQL, sementara `mentoring_2` fokus pada pipeline ETL lokal dari source database ke staging, warehouse, logging database, dan MinIO.

## Project Status & Navigation

| Mentoring | Focus | Status |
| --- | --- | --- |
| [`mentoring_1`](./mentoring_1/) | Data profiling notebook, JSON quality reports, PostgreSQL source setup | ✅ Completed |
| [`mentoring_2`](./mentoring_2/) | Source -> Staging -> Warehouse ETL, PostgreSQL warehouse, MinIO job-failure payload dump, DB check notebook/PDF | ✅ Completed |
| `mentoring_3` | Reserved for the next mentoring task | Planned |
| `mentoring_4` | Reserved for the next mentoring task | Planned |

## Progress Log

- [x] **Mentoring 1** - Data profiling and quality validation on Pacmann source datasets.
- [x] **Mentoring 2** - Data integration and ETL pipeline with PostgreSQL source, staging, warehouse, logging, MinIO, uv, and database checking notebook/PDF.
- [ ] **Mentoring 3** - Not started.
- [ ] **Mentoring 4** - Not started.

## Current Workspace Snapshot

- `mentoring_1` and `mentoring_2` are completed project folders.
- The active implementation uses Python, pandas, SQLAlchemy, PostgreSQL, Docker Compose, uv, MinIO, and Jupyter Notebook.
- `mentoring_1` validates source data quality and generates profiling artifacts.
- `mentoring_2` builds an OOP-style ETL pipeline from source to staging and warehouse, with operational logging and job-failure payload handling.
- Spark is included in the overall course scope but has not been used yet in the completed mentoring folders.

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
└── mentoring_4/
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
