# Makefile - Gestion des commandes ETL et tests

ENV ?= DEV
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest

export PYTHONPATH := $(shell pwd)

.DEFAULT_GOAL := help

# ========= SETUP =========

uv: ## Installe uv + dépendances et affiche version Python
	wget -qO- https://astral.sh/uv/install.sh | sh
	uv sync
	$(PYTHON) --version

# ========= HELP =========

help: ## Affiche toutes les commandes disponibles
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile \
	| sort \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ========= ETL PIPELINE =========

oltp-olap:  ## Run the ETL process
	@echo "🚀 Running ETL (ENV=$(ENV))..."
	ENV=$(ENV) $(PYTHON) scripts/etl_to_snowflake.py

# ========= TESTS =========

test:  ## Run the tests
	@echo "🧪 Running tests..."
	ENV=$(ENV) $(PYTEST) -v tests/

test-offline:  ## Run tests with GCS mocked (offline mode)
	@echo "🧪 Running tests (OFFLINE mode)..."
	OFFLINE=1 ENV=$(ENV) $(PYTEST) -v tests/

# ========= SNOWFLAKE LOGIC =========

setup_gcs_integration: ## Setup automatic GCS-Snowflake integration
	ENV=PROD $(PYTHON) scripts/setup_gcs_integration.py

generate_sql_queries:  ## Generate CREATE TABLE SQL and COPY INTO from GCS CSVs
	ENV=PROD $(PYTHON) scripts/generate_create_tables.py
	ENV=PROD $(PYTHON) scripts/generate_copy_into_sql.py

load_snowflake: setup_gcs_integration ## Load everything (GCS integration + infra + tables + views + load data)
	ENV=PROD $(PYTHON) scripts/load_to_snowflake.py

dryrun_snowflake: ## Print all SQL steps without executing anything
	ENV=PROD $(PYTHON) scripts/load_to_snowflake.py --dry-run

setup_snowflake: ## Only set up infra (database, schema, warehouse)
	ENV=PROD $(PYTHON) -c "import sys; sys.path.insert(0, 'scripts'); \
from load_to_snowflake import connect_to_snowflake, run_sql_file; \
conn = connect_to_snowflake(); run_sql_file('scripts/sql/setup_snowflake_infra.sql', conn)"

# ========= FULL PIPELINE =========

conclusion: ## Display pipeline completion summary
	@echo ""
	@echo "🎉 =============================================="
	@echo "🎉 OLAP PIPELINE COMPLETED SUCCESSFULLY!"
	@echo "🎉 =============================================="
	@echo ""
	@echo "✅ ETL Transformation: OLTP → Dimensional Model"
	@echo "✅ Snowflake Integration: GCS → Data Warehouse"
	@echo "✅ Tables Created: 1 Fact + 7 Dimensions"
	@echo "✅ Views Created: 3 Business Analytics Views"
	@echo "✅ Tests Passed: All validations successful"
	@echo ""
	@echo "🔗 Next Steps:"
	@echo "   • Open Snowflake UI: Query your dimensional data"
	@echo "   • Run analytics: SELECT * FROM vw_monthly_revenue;"
	@echo "   • Demo ready: Your OLAP pipeline is production-ready!"
	@echo ""

all: uv oltp-olap generate_sql_queries load_snowflake test conclusion ## Run complete OLAP pipeline: ETL + Snowflake + tests + summary

.PHONY: help uv oltp-olap test test-offline generate_sql_queries load_snowflake dryrun_snowflake setup_snowflake conclusion all
