# Building Data Pipeline with Python and PySpark - Pacmann Mentoring Workspace

<div align="center">

![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQL](https://img.shields.io/badge/SQL-000000?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-0db7ed?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge)
![uv](https://img.shields.io/badge/uv-5C5CFF?style=for-the-badge)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)

</div>

My project workspace and learning log for the **Pacmann Academy Bootcamp** program **Building Data Pipeline with Python and Spark**.

The repository is organized by mentoring folders. The current implemented work is in `mentoring_1`, while the remaining folders are reserved for the next exercises.

## Intent

- **Build reproducible data engineering exercises**
- **Keep setup and outputs easy to review**
- **Grow each mentoring folder into a documented project artifact**

**Focus:** data profiling, data quality validation, reproducible local setup, and clear documentation.

---

## Project Status & Navigation

| Area (Shortcut) | Output / Features | Status |
| :--- | :--- | :--- |
| [**Mentoring 1**](./mentoring_1/) | Data profiling notebook, JSON quality reports, PostgreSQL source setup | ✅ Active / Completed |
| [**Mentoring 2**](./mentoring_2/) | Not Yet | 🚧 Planned |
| [**Mentoring 3**](./mentoring_3/) | Not Yet | 🚧 Planned |
| [**Mentoring 4**](./mentoring_4/) | Not Yet | 🚧 Planned |

---

## Progress Log

- [x] **Mentoring 1**: Data profiling and data quality checks on the Paccafe PostgreSQL dataset.
- [ ] **Mentoring 2**: Next mentoring task not started yet.
- [ ] **Mentoring 3**: Next mentoring task not started yet.
- [ ] **Mentoring 4**: Next mentoring task not started yet.

---

## Current Workspace Snapshot

- `mentoring_1` is the active project folder and already includes its own [README](./mentoring_1/README.md), notebook, reports, and summary.
- The current exercise uses Python, pandas, SQLAlchemy, Jupyter, Docker Compose, and PostgreSQL.
- Although the repository name includes Spark, the implemented work so far is centered on Python and SQL-based profiling rather than PySpark processing.

---

## Mentoring 1 Highlights

- Source dataset loaded from PostgreSQL via Docker Compose
- Data profiling for 6 tables: `customers`, `employees`, `inventory_tracking`, `order_details`, `orders`, `products`
- Output artifacts:
  - `mentoring_1/notebooks/data_profiling_quality_check.ipynb`
  - `mentoring_1/outputs/data_profiling_report.json`
  - `mentoring_1/outputs/data_quality_report.json`
  - `mentoring_1/summary.md`
- Main issues identified:
  - invalid categorical values in employee roles, payment methods, and inventory reasons
  - missing values in `orders.customer_id` and `customers.phone`
  - product prices stored as strings with currency symbols
  - negative values in `customers.loyalty_points` and parsed product price fields

---

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
