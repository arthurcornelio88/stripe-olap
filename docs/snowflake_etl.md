Voici la **version complète prête à l’emploi** de ton fichier `docs/snowflake_etl.md`, à inclure dans ton dépôt.

---

````markdown
# 📘 Snowflake Integration for the OLAP Pipeline

## 🧭 Goal

This document outlines how Snowflake is integrated into the OLAP ETL process. It explains:

- What Snowflake is and how we use it
- How we connect and authenticate
- How data is dynamically loaded from GCS
- How infrastructure, tables, and views are versioned and deployed
- The available Makefile targets to automate everything

---

## ❄️ What is Snowflake?

[Snowflake](https://www.snowflake.com/) is a cloud-native data warehouse designed for scalability and flexible data access.

For this OLAP project, Snowflake acts as the **destination layer**. Transformed data is loaded there in the form of:

- `fact_` tables (e.g., `fact_invoices`)
- `dim_` tables (e.g., `dim_customers`)
- `vw_` views for analysis

---

## 🔐 Configuration

We authenticate to Snowflake via environment variables stored in `.env.snowflake`:

```ini
SNOWFLAKE_USER=<your-username>
SNOWFLAKE_PASSWORD=<your-password>
SNOWFLAKE_ACCOUNT=<your-account>
SNOWFLAKE_DATABASE=STRIPE_OLAP # Already set
SNOWFLAKE_SCHEMA=RAW # Already set
SNOWFLAKE_WAREHOUSE=WH_STRIPE_OLAP # Already set
````

These credentials are loaded automatically by the ETL scripts.

> You can pick them in your Snowflake UI at `Account Details`.

---

## ⚙️ Connecting from Python

We use the official `snowflake-connector-python` library to execute all SQL commands.

Connection is handled centrally in `load_to_snowflake.py`:

```python
conn = snowflake.connector.connect(
    user=...,
    password=...,
    account=...,
    warehouse=...,
    database=...,
    schema=...
)
```

---

## 🗂 File Structure

All Snowflake logic is versioned and stored in:

```
scripts/sql/
├── setup_snowflake_infra.sql     # Create database, schema, warehouse
├── create_tables.sql             # Define fact_ and dim_ tables
├── view_for_analytics.sql        # Create business views for BI
├── copy_into_tables.sql          # COPY INTO commands (templated)
```

These files are automatically run by the `load_to_snowflake.py` script.

---

## ☁️ Loading Data from GCS

The OLAP pipeline outputs CSV files to GCS, under timestamped folders like:

```
gs://stripe-bucket-prod_v3/olap_outputs/2025-05-30_16-33-17/
```

The Python utility `get_latest_olap_gcs_path` detects the latest one automatically.

---

## 🧩 COPY INTO Automation

Instead of generating SQL inline, we use `scripts/sql/copy_into_tables.sql` with placeholders:

```sql
CREATE OR REPLACE STAGE gcs_stage_prod
  URL = 'gcs://{{BUCKET}}/{{OLAP_PATH}}'
  STORAGE_INTEGRATION = my_gcs_integration;

COPY INTO fact_invoices FROM @gcs_stage_prod/fact_invoices.csv FILE_FORMAT=(TYPE=CSV FIELD_DELIMITER=',' SKIP_HEADER=1);
...
```

These placeholders are replaced dynamically via Python before execution.

---

## 🧱 Table Structure

All core tables are defined in `create_tables.sql`. They follow a standard star schema model:

* `fact_invoices`: billing events
* `dim_customers`: customer info
* `dim_products`, `dim_prices`, etc.

---

## 👓 Analytical Views

Views are created for business analysis and dashboards. These are defined in `view_for_analytics.sql`.

| View name                 | Description                              |
| ------------------------- | ---------------------------------------- |
| `vw_monthly_revenue`      | Monthly revenue aggregated from invoices |
| `vw_customer_ltv`         | Customer lifetime value (LTV)            |
| `vw_active_subscriptions` | Subscriptions that are currently active  |

They are auto-deployed along with the pipeline.

---

## 🛠 Makefile Targets

| Command                 | Description                                        |
| ----------------------- | -------------------------------------------------- |
| `make load_snowflake`   | Full pipeline: infra + tables + views + data load  |
| `make dryrun_snowflake` | Preview all SQL steps without executing anything   |
| `make setup_snowflake`  | Run only the infrastructure setup (DB, schema, WH) |

---

## ✅ Summary

* Snowflake is the final layer of the OLAP pipeline
* All SQL logic is centralized in versioned `.sql` files
* Python orchestrates execution, with dynamic GCS path detection
* The pipeline is fully automatable via `make`
