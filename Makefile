# Makefile - Gestion des commandes ETL et tests

ENV ?= DEV
PYTHON := .venv/bin/python

# Default target
.DEFAULT_GOAL := help

# Help: print all available commands
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

oltp-olap:  ## Run the ETL process
	@echo "🚀 Running ETL (ENV=$(ENV))..."
	ENV=$(ENV) .venv/bin/python scripts/etl_to_snowflake.py

test:  ## Run the tests
	@echo "🧪 Running tests..."
	ENV=$(ENV) pytest -v tests/

test-offline:  ## Run tests with GCS mocked (offline mode)
	@echo "🧪 Running tests (OFFLINE mode)..."
	OFFLINE=1 ENV=$(ENV) pytest -v tests/

# Makefile for OLAP + Snowflake pipeline

generate_sql_queries:  ## Generate CREATE TABLE SQL and COPY INTO from GCS CSVs
	ENV=PROD python scripts/generate_create_tables.py
	ENV=PROD python scripts/generate_copy_into_sql.py

load_snowflake: ## Load everything (infra + tables + views + load data)
	ENV=PROD python scripts/load_to_snowflake.py

dryrun_snowflake: ## Print all SQL steps without executing anything
	ENV=PROD python scripts/load_to_snowflake.py --dry-run


setup_snowflake: ## Only set up infra (database, schema, warehouse)
	ENV=PROD python -c "import sys; sys.path.insert(0, 'scripts'); \
from load_to_snowflake import connect_to_snowflake, run_sql_file; \
conn = connect_to_snowflake(); run_sql_file('scripts/sql/setup_snowflake_infra.sql', conn)"


all: oltp-olap test generate_sql_queries load_snowflake ## Run both ETL and tests

.PHONY: help oltp-olap test test-offline generate_sql_queries load_snowflake dryrun_snowflake setup_snowflake all
