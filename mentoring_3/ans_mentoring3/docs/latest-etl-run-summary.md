# Latest ETL Run Summary

## Execution

- Execution date: June 14, 2026 WIB (June 13, 2026 UTC)
- Completion time: 01:37:23 WIB (18:37:23 UTC)
- Run ID: `c0a2e914-b5ac-44db-92a3-6658ed1d2daf`
- Mode: clean initialization followed by a full refresh
- Spark version: 3.5.5
- Spark master: `local[4]`
- Result: successful
- ETL duration: 59.49 seconds
- Persistent log: `logs/etl_pipeline.log`
- Machine-readable report: `logs/latest_profile_summary.json`

Before execution, Docker Compose removed both PostgreSQL data volumes. The source
and warehouse databases were then recreated from their initialization SQL files,
so this run had no previous audit or warehouse snapshot.

## Profile Results

| Stage | Dataset | Rows | Previous | Delta | Nulls | Duplicate Keys |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Source | `education_status` | 4 | none | none | 0 | 0 |
| Source | `marital_status` | 3 | none | none | 0 | 0 |
| Source | `marketing_campaign_deposit` | 45,211 | none | none | 0 | 0 |
| Source | `new_bank_transactions.csv` | 1,048,567 | none | none | 3,620 | 0 |
| Target | `education_status` | 4 | none | none | 0 | 0 |
| Target | `marital_status` | 3 | none | none | 0 | 0 |
| Target | `marketing_campaign_deposit` | 45,211 | none | none | 0 | 0 |
| Target | `customers` | 1,048,567 | none | none | 5,917 | 0 |
| Target | `transactions` | 1,048,567 | none | none | 0 | 0 |

Previous row counts and deltas are empty because this was the first audited run
after deleting and recreating the database volumes.

## Transformation Findings

| Field | Source Profile | Target Profile | Transformation Effect |
| --- | ---: | ---: | --- |
| Gender | 1,100 null | 0 null | Missing and unknown values map to `Other` |
| Location | 151 null | 151 null | Null values are preserved |
| Account balance | 2,369 null | 2,369 null | Null values are preserved after numeric parsing |
| Date of birth | 0 Spark null | 3,397 null | Empty or invalid strings become null after date parsing |

## Semi-CDC Result

| Dataset | Inserted | Updated | Deleted | Unchanged |
| --- | ---: | ---: | ---: | ---: |
| `education_status` | 4 | 0 | 0 | 0 |
| `marital_status` | 3 | 0 | 0 | 0 |
| `marketing_campaign_deposit` | 45,211 | 0 | 0 | 0 |
| `customers` | 1,048,567 | 0 | 0 | 0 |
| `transactions` | 1,048,567 | 0 | 0 | 0 |

All rows were correctly classified as inserted because the warehouse was empty.
The comparison uses each table's primary key and a SHA-256 hash of the remaining
payload. This is a batch snapshot comparison for observability, not log-based CDC.

## Warehouse Validation

The writer verified every target row count after loading:

| Warehouse Table | Rows |
| --- | ---: |
| `education_status` | 4 |
| `marital_status` | 3 |
| `marketing_campaign_deposit` | 45,211 |
| `customers` | 1,048,567 |
| `transactions` | 1,048,567 |

The run and its nine profiles and five change summaries were persisted in:

- `etl_pipeline_runs`
- `etl_data_profiles`
- `etl_change_summary`

## Historical Parallelism Benchmark

| Configuration | Duration | Difference |
| --- | ---: | ---: |
| `local[2]`, 4 shuffle partitions | 41.83 seconds | Baseline |
| `local[4]`, 8 shuffle partitions | 37.62 seconds | 10.1% faster |

Those measurements predate source and target profiling and semi-CDC. The current
59.49-second duration includes database initialization state checks, aggregate
profiling scans, warehouse snapshot comparison, loading, and row-count validation.
