# Mentoring 4 - Car Sales ETL and Machine Learning Pipeline

This folder contains the fourth Pacmann Academy data engineering mentoring exercise.
The submission builds an end-to-end car sales pipeline with PostgreSQL, PySpark,
Airflow, scikit-learn, MLflow, and MinIO.

The original task is available in [task_mentoring_4.md](task_mentoring_4.md).
The implementation and operational runbook are available in
[pac_car/README.md](pac_car/README.md).

## Objective

The project combines a source database and two reference datasets, cleans and maps
the data into a model-ready warehouse, trains a selling-price regression model, and
stores reproducible model and prediction artifacts.

```text
Source and references -> Staging -> PySpark transform -> Warehouse
Warehouse -> ML preprocessing -> Training -> Evaluation -> MinIO and MLflow
```

## Folder Structure

```text
mentoring_4/
|- README.md
|- task_mentoring_4.md
|- dataset/
|  |- api_data.json
|  |- car_brand.csv
|  `- data_pipeline_exercise_4/    # external repository, ignored by parent Git
|     |- source_data/init.sql
|     |- staging_data/init.sql
|     |- warehouse_data/init.sql
|     `- log_data/init.sql
`- pac_car/
   |- README.md
   |- docker-compose.yml
   |- dags/
   |- docker/
   |- notebooks/
   |- src/
   |- project_explanation.md
   `- report_summary.md
```

## Dataset Arrangement

Mentoring 4 uses two types of dataset files.

### Tracked Reference Files

These small files are tracked by the parent repository:

| File | Purpose | Validated rows |
| --- | --- | ---: |
| `dataset/car_brand.csv` | Maps `brand_car` names to `brand_car_id` | 51 |
| `dataset/api_data.json` | Maps state codes to `id_state` and state names | 68 |

The pipeline image copies these files into `/app/dataset` so Airflow one-off
containers can read them without host bind mounts.

### External Database Dataset

`dataset/data_pipeline_exercise_4` is an external Git repository:

```text
https://github.com/Kurikulum-Sekolah-Pacmann/data_pipeline_exercise_4.git
```

It is intentionally ignored by the parent repository and is not stored as a Git
submodule or nested gitlink. Clone it manually before starting the project:

```bash
git clone https://github.com/Kurikulum-Sekolah-Pacmann/data_pipeline_exercise_4.git \
  mentoring_4/dataset/data_pipeline_exercise_4
```

When running commands from inside `mentoring_4`, use:

```bash
git clone https://github.com/Kurikulum-Sekolah-Pacmann/data_pipeline_exercise_4.git \
  dataset/data_pipeline_exercise_4
```

The PAC Car Compose stack uses only the database initialization directories from
this repository. Its original `docker-compose.yml` and `.env` are not required by
the PAC Car runtime.

## Database Initialization Files

| External path | PAC Car service | Purpose |
| --- | --- | --- |
| `source_data/init.sql` | `source_db` | Creates and seeds raw car sales data |
| `staging_data/init.sql` | `staging_db` | Creates raw sales and reference staging tables |
| `warehouse_data/init.sql` | `warehouse_db` | Creates the clean model-ready sales table |
| `log_data/init.sql` | `log_db` | Creates the ETL audit table |

Docker Compose mounts these directories into `/docker-entrypoint-initdb.d` for the
corresponding PostgreSQL services. PostgreSQL runs these scripts only when its data
volume is empty.

## Project Components

| Component | Location | Responsibility |
| --- | --- | --- |
| Original task | `task_mentoring_4.md` | Exercise requirements |
| Main project | `pac_car/` | ETL, ML, orchestration, and infrastructure code |
| Data exploration | `pac_car/notebooks/data_exploration.ipynb` | Source and reference profiling |
| Airflow DAG | `pac_car/dags/car_sales_pipeline_dag.py` | Containerized workflow trigger |
| Concept guide | `pac_car/project_explanation.md` | Beginner explanation and prediction logic |
| Run report | `pac_car/report_summary.md` | Latest clean-start validation evidence |

## Prerequisites

- Docker Engine or Docker Desktop with Docker Compose v2
- Git for cloning the external dataset
- enough Docker memory for PostgreSQL, Spark, Airflow, MLflow, and MinIO

Host Python, Java, and `uv` are only required for local development outside Docker.

## Quickstart

Run all commands from the repository root.

### 1. Clone the External Dataset

Skip this command when the directory already exists.

```bash
git clone https://github.com/Kurikulum-Sekolah-Pacmann/data_pipeline_exercise_4.git \
  mentoring_4/dataset/data_pipeline_exercise_4
```

### 2. Build and Start the Stack

```bash
docker compose -f mentoring_4/pac_car/docker-compose.yml config --quiet
docker compose -f mentoring_4/pac_car/docker-compose.yml up -d --build
docker compose -f mentoring_4/pac_car/docker-compose.yml ps
```

### 3. Trigger the Airflow Pipeline

```bash
docker compose -f mentoring_4/pac_car/docker-compose.yml exec -T airflow-scheduler \
  airflow dags trigger pac_car_sales_pipeline
```

Inspect run status:

```bash
docker compose -f mentoring_4/pac_car/docker-compose.yml exec -T airflow-scheduler \
  airflow dags list-runs -d pac_car_sales_pipeline --no-backfill
```

### 4. Stop the Stack

```bash
docker compose -f mentoring_4/pac_car/docker-compose.yml down
```

Use volume deletion only when database initialization must run again from zero:

```bash
docker compose -f mentoring_4/pac_car/docker-compose.yml down -v
```

This removes PostgreSQL data, Airflow metadata, MLflow history, and MinIO artifacts.

## Service Access

| Service | URL |
| --- | --- |
| Airflow | http://localhost:18080 |
| JupyterLab | http://localhost:18888 |
| MLflow | http://localhost:15000 |
| MinIO Console | http://localhost:19095 |
| Spark Master | http://localhost:18081 |
| Spark Worker | http://localhost:18082 |

Default local credentials:

- Airflow: `admin` / `admin`
- MinIO: `admin` / `admin1234`

## Latest Validated Run

The latest run started from empty Docker volumes and completed through Airflow with
the `success` state.

| Item | Result |
| --- | ---: |
| Source sales rows | 30,000 |
| Staging sales rows | 30,000 |
| Warehouse sales rows | 28,818 |
| Rejected rows | 1,182 |
| R2 score | 0.9708 |
| RMSE | 1661.8552 |
| MAE | 1018.6319 |

See [pac_car/report_summary.md](pac_car/report_summary.md) for the complete result,
service status, Docker image list, and MinIO artifact locations.

## Notes

- Do not add `dataset/data_pipeline_exercise_4` to the parent Git index.
- Local changes inside the external dataset repository remain independent from this project.
- The PAC Car Compose file is the only Compose entrypoint required for this submission.
- Database initialization SQL runs only for empty PostgreSQL volumes.
- Reference fixture files remain tracked so model training is reproducible offline.

---

<div align="center">

### Mentoring 4 - Car Sales ETL and Machine Learning Pipeline

This project was created as part of the learning program at
<strong>Pacmann Academy Bootcamp</strong>.

<a href="https://pacmann.io">
  <img src="https://img.shields.io/badge/BOOTCAMP%20%7C%20PACMANN%20ACADEMY-0D3B66?style=for-the-badge&logoColor=white" alt="Pacmann Academy">
</a>

<a href="https://pacmann.io">pacmann.io</a>

</div>
