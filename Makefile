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

all: oltp-olap test  ## Run both ETL and tests

.PHONY: help oltp-olap test test-offline all
