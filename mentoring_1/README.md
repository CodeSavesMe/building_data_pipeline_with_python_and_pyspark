# Mentoring 1 - Data Profiling and Data Quality

This folder contains the implementation for a Pacmann Academy data engineering exercise focused on profiling and validating a PostgreSQL cafe sales dataset. The work is delivered in a Jupyter Notebook, supported by configuration files, a Docker Compose setup for the source database, and JSON output reports.

## Objective

The exercise covers three main areas:

- data profiling for all tables in the source database
- data quality checks for missing values, dates, numeric columns, and negative values
- recommendations for dataset cleaning and improvement

## Dataset Scope

The source database contains these tables:

- `customers`
- `employees`
- `inventory_tracking`
- `order_details`
- `orders`
- `products`

## Folder Structure

```text
mentoring_1/
├── config.toml
├── pyproject.toml
├── summary.md
├── task_mentoring_week1.md
├── uv.lock
├── notebooks/
│   └── data_profiling_quality_check.ipynb
├── outputs/
│   ├── data_profiling_report.json
│   └── data_quality_report.json
└── data_pipeline_paccafe/
    ├── README.md
    ├── docker-compose.yaml
    └── source_data/
        └── init.sql
```

## Tech Stack

- Python 3.11+
- pandas
- SQLAlchemy
- psycopg2-binary
- JupyterLab
- PostgreSQL 16
- Docker Compose
- `uv`

## Setup

### 1. Install dependencies

From this `mentoring_1` directory:

```bash
uv sync
```

### 2. Create environment variables for PostgreSQL

Create a `.env` file inside `data_pipeline_paccafe/`:

```bash
SRC_POSTGRES_DB=paccafe
SRC_POSTGRES_HOST=localhost
SRC_POSTGRES_USER=postgres
SRC_POSTGRES_PASSWORD=postgres
SRC_POSTGRES_PORT=5433
```

These values match the current database configuration in `config.toml`.

### 3. Start the source database

```bash
cd data_pipeline_paccafe
docker compose up -d
```

The database will be initialized from `source_data/init.sql`.

### 4. Run the notebook

Return to `mentoring_1` and start Jupyter:

```bash
uv run jupyter lab
```

Open:

- `notebooks/data_profiling_quality_check.ipynb`

## What the Notebook Produces

The notebook implements:

- table discovery from PostgreSQL
- extraction of each table into pandas DataFrames
- row and column shape checks
- column data type checks
- unique value checks for selected categorical columns
- profiling report generation in JSON format
- missing value checks
- date format validation
- numeric validation
- negative value validation
- data quality report generation in JSON format
- recommendations for data cleaning

## Outputs

This folder already contains the generated outputs:

- `notebooks/data_profiling_quality_check.ipynb`
- `outputs/data_profiling_report.json`
- `outputs/data_quality_report.json`
- `summary.md`

## Findings Summary

Based on the current reports and summary:

- `employees.role` contains invalid category values such as `me`, `third`, and `today`
- `orders.payment_method` contains `ERROR`
- `inventory_tracking.reason` contains `ERROR`
- `orders.customer_id` has missing values, which likely represent guest orders
- `customers.phone` has missing values
- `products.unit_price` and `products.cost_price` are stored as strings instead of numeric types
- `customers.loyalty_points` includes negative values

## Notes

- `config.toml` centralizes the database connection, output paths, and validation rules used in the exercise.
- The source database service is defined in `data_pipeline_paccafe/docker-compose.yaml`.
- The exercise is implemented with Python and pandas, even though the parent repository name mentions Spark.

---

<div align="center">

### Mentoring - 1 - Data Profiling and Data Quality
Dokumen ini dibuat sebagai bagian dari pembelajaran di <strong>Pacmann Academy Bootcamp</strong>.

<a href="https://pacmann.io">
  <img src="https://img.shields.io/badge/BOOTCAMP%20%7C%20PACMANN%20ACADEMY-0D3B66?style=for-the-badge&logoColor=white" alt="Pacmann Academy">
</a>

<a href="https://pacmann.io">pacmann.io</a>

</div>