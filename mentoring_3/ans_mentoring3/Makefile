COMPOSE ?= docker compose
UV ?= uv

.DEFAULT_GOAL := help

.PHONY: help config build up run rerun status counts audit profiles changes summary \
	report warehouse-shell logs eda eda-execute lock-check test lint check down reset

help: ## Show all reusable commands
	@awk 'BEGIN {FS = ":.*##"; printf "Available commands:\n"} \
		/^[a-zA-Z0-9_-]+:.*##/ {printf "  make %-18s %s\n", $$1, $$2}' \
		$(MAKEFILE_LIST)

config: ## Validate and render Docker Compose configuration
	$(COMPOSE) config --quiet

build: ## Build the Spark ETL runtime image
	$(COMPOSE) build spark_etl

up: ## Start source and warehouse databases only
	$(COMPOSE) up -d --wait source_db data_warehouse

run: ## Build and run the complete ETL stack
	$(COMPOSE) up --build --abort-on-container-exit --exit-code-from spark_etl

rerun: up ## Run another ETL batch against existing database volumes
	$(COMPOSE) run --rm --service-ports spark_etl

status: ## Show Docker Compose service status
	$(COMPOSE) ps

counts: ## Show row counts for all warehouse business tables
	$(COMPOSE) exec -T data_warehouse sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -P pager=off -c "SELECT '\''education_status'\'' AS table_name, COUNT(*) AS row_count FROM education_status UNION ALL SELECT '\''marital_status'\'', COUNT(*) FROM marital_status UNION ALL SELECT '\''marketing_campaign_deposit'\'', COUNT(*) FROM marketing_campaign_deposit UNION ALL SELECT '\''customers'\'', COUNT(*) FROM customers UNION ALL SELECT '\''transactions'\'', COUNT(*) FROM transactions;"'

audit: ## Show the latest ETL audit run
	$(COMPOSE) exec -T data_warehouse sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -P pager=off -c "SELECT run_id, status, ROUND(duration_seconds::numeric, 2) AS seconds, started_at, finished_at, error_message FROM etl_pipeline_runs ORDER BY started_at DESC LIMIT 1;"'

profiles: ## Show source and target profiles from the latest run
	$(COMPOSE) exec -T data_warehouse sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -P pager=off -c "SELECT stage, dataset_name, row_count, previous_row_count, row_count_delta, null_count, duplicate_key_count FROM etl_data_profiles WHERE run_id = (SELECT run_id FROM etl_pipeline_runs ORDER BY started_at DESC LIMIT 1) ORDER BY stage, dataset_name;"'

changes: ## Show semi-CDC results from the latest run
	$(COMPOSE) exec -T data_warehouse sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -P pager=off -c "SELECT dataset_name, inserted_count, updated_count, deleted_count, unchanged_count FROM etl_change_summary WHERE run_id = (SELECT run_id FROM etl_pipeline_runs ORDER BY started_at DESC LIMIT 1) ORDER BY dataset_name;"'

summary: audit counts profiles changes ## Show all latest ETL validation results

report: ## Print the latest JSON profiling report
	@if command -v jq >/dev/null 2>&1; then \
		jq . logs/latest_profile_summary.json; \
	else \
		cat logs/latest_profile_summary.json; \
	fi

warehouse-shell: ## Open an interactive psql shell in the warehouse
	$(COMPOSE) exec data_warehouse sh -c 'exec psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

logs: ## Follow the persistent ETL application log
	tail -f logs/etl_pipeline.log

eda: ## Build and start the optional Jupyter EDA service
	$(COMPOSE) --profile eda up --build notebook

eda-execute: up ## Execute the EDA notebook headlessly and save its outputs
	$(COMPOSE) --profile eda build notebook
	$(COMPOSE) --profile eda run --rm --no-deps notebook \
		/app/.venv/bin/jupyter nbconvert --to notebook --execute --inplace \
		--ExecutePreprocessor.timeout=600 /app/script/eda.ipynb

lock-check: ## Verify that uv.lock is synchronized with pyproject.toml
	$(UV) lock --check

test: ## Run the complete pytest suite
	$(UV) run pytest

lint: ## Run Ruff checks
	$(UV) run ruff check src tests

check: lock-check lint test ## Run dependency, lint, and test checks

down: ## Stop containers without deleting database volumes
	$(COMPOSE) down

reset: ## Stop containers and delete database volumes
	$(COMPOSE) down -v
