Absolutely — here is a clean, **English-language documentation** tailored to your project. It includes a short explanation of how Snowflake works, what needs to be configured, dynamic GCS folder logic, and meaningful descriptions of each analytical view.

---

# 📘 Snowflake Integration for the OLAP Pipeline

## 🧭 Goal

This document outlines how to integrate **Snowflake** into the OLAP ETL process. It covers:

* Required setup for Snowflake access
* How to connect and load data from Google Cloud Storage (GCS)
* Best practices for table and view definitions
* How to expose clean, analyst-friendly data models

---

## ❄️ What is Snowflake?

[Snowflake](https://www.snowflake.com/) is a cloud-native data warehouse designed for high scalability, elastic compute, and seamless storage. It can:

* Load and query large volumes of structured/semi-structured data
* Ingest files directly from cloud storage (GCS, S3, etc.)
* Provide fine-grained access control and share datasets with external users

For this OLAP project, it acts as the **final destination** for transformed `fact_` and `dim_` tables, allowing analysts and BI tools to query data cleanly.

---

## 🔐 What needs to be configured?

### 1. Snowflake Account

You’ll need credentials from your Snowflake admin:

* **User name**
* **Password**
* **Account ID** (usually like `abcd-efg123.region.gcp`)
* **Warehouse name** (compute unit, e.g., `ANALYTICS_WH`)
* **Database name**
* **Schema** (e.g., `PUBLIC`)

### 2. GCS Storage Integration

To let Snowflake read files from GCS, a **Storage Integration** must be configured in Snowflake. This integration:

* Links to a specific GCS bucket
* Is named (e.g., `my_gcs_integration`)
* Is tied to a service account and IAM roles in GCP

> This is a **one-time setup**, usually done by a platform admin.

---

## ⚙️ Connecting from Python

Create a file named `.env.snowflake` with your credentials:

```ini
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=your_warehouse
```

Use Python + `snowflake-connector-python`:

```python
import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv(".env.snowflake")

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)
```

---

## ☁️ Loading Data from GCS to Snowflake

### 🔍 Step 1: Detect latest OLAP folder on GCS

The OLAP pipeline outputs CSV files to folders like:

```
gs://stripe-bucket-prod_v3/olap_outputs/2025-05-30_16-33-17/
```

A utility (`get_latest_olap_gcs_path`) scans the `olap_outputs/` folder and selects the latest timestamped directory automatically.

### 🧩 Step 2: Create a GCS stage in Snowflake

```sql
CREATE OR REPLACE STAGE gcs_stage_prod
  URL = 'gcs://stripe-bucket-prod_v3/olap_outputs/2025-05-30_16-33-17/'
  STORAGE_INTEGRATION = my_gcs_integration;
```

> This allows Snowflake to read directly from the bucket.

### 📥 Step 3: Load each table with `COPY INTO`

```sql
COPY INTO fact_invoices
FROM @gcs_stage_prod/fact_invoices.csv
FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1);
```

Repeat for all files: `dim_customers.csv`, `dim_products.csv`, etc.

This logic is automated in `load_to_snowflake.py`.

---

## 🧱 Table Structure

Your data is organized into:

* **fact\_**\* tables — transactional data like invoices
* **dim\_**\* tables — reference data like customers, products, prices, etc.

All tables are stored in Snowflake and kept up-to-date via the ETL pipeline.

---

## 👓 Analytical Views

Views are created on top of raw tables to provide clean, business-friendly models for exploration and dashboarding.

### Example views:

| View name                 | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `vw_monthly_revenue`      | Total revenue grouped by month                 |
| `vw_customer_ltv`         | Lifetime value (LTV) per customer              |
| `vw_active_subscriptions` | Currently active subscriptions based on status |

#### Example:

```sql
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
  DATE_TRUNC('month', created_at) AS month,
  SUM(amount) AS total_revenue
FROM fact_invoices
GROUP BY 1
ORDER BY 1;
```

These views are versioned in `sql/views_for_analytics.sql` and deployed alongside the rest of the pipeline.

---

## ✅ Summary

* Snowflake is the final destination of OLAP-transformed data
* GCS is used to transfer files between the pipeline and Snowflake
* Python automates credential handling and `COPY INTO` logic
* Views are maintained to support analysts and BI tools