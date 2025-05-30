# 🧠 Stripe OLAP Pipeline

Transform raw Stripe dumps (OLTP) into clean OLAP data models with a fully automated ETL pipeline powered by Python, GCS, and Snowflake.

---

## 🔄 Pipeline Overview

This project converts JSON dumps into analytics-ready Snowflake tables.

```

Raw JSON Dump
↓
ETL Python (scripts/etl\_to\_snowflake.py)
↓
fact\_ / dim\_ CSVs
↓
Uploaded to GCS
↓
Loaded into Snowflake (COPY INTO)
↓
Views for BI (vw\_monthly\_revenue, vw\_customer\_ltv...)

````

📄 For more context on the data modeling and transformations, see [`docs/fact_table.md`](docs/fact_table.md)

---

## 🧬 Environment Setup

Create the following environment files:

### `.env`

```ini
ENV=PROD
GCS_BUCKET=stripe-bucket-prod_v3             # anonymize if needed
GCP_CREDS_FILE=gcp_service_account.json      # anonymize if needed
````

### `.env.snowflake`

```ini
SNOWFLAKE_USER=STRIPEB2
SNOWFLAKE_PASSWORD=your_strong_password
SNOWFLAKE_ACCOUNT=UZPYBJI-XA86551
SNOWFLAKE_DATABASE=STRIPE_OLAP
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_WAREHOUSE=WH_STRIPE_OLAP
```

> 🔐 These should never be committed.

---

## 🛠 Usage via `make`

All commands are available via `make`. You can run any step independently or combine them.

### 🧩 Available commands

| Command                 | Description                                    |
| ----------------------- | ---------------------------------------------- |
| `make help`             | Show all available make targets                |
| `make oltp-olap`        | Run the JSON → CSV transformation pipeline     |
| `make test`             | Run all tests                                  |
| `make test-offline`     | Run tests in GCS-offline/mock mode             |
| `make generate_create_tables`     | Creates sql create tables commands from OLTP .csv             |
| `make setup_snowflake`  | Create Snowflake infra (DB, schema, warehouse) |
| `make load_snowflake`   | Load data: create tables, views, COPY INTO     |
| `make dryrun_snowflake` | Preview all SQL commands without executing     |
| `make all`              | Run everything: transform + test + load        |

---

## 🗂 File Structure

```
.
├── .env / .env.snowflake     # Secrets and config
├── Makefile                  # Commands for the full pipeline
├── scripts/
│   ├── olap_io.py            # GCS CSV upload/download
│   ├── etl_to_snowflake.py   # JSON → CSV pipeline
│   ├── load_to_snowflake.py  # Full Snowflake loader
│   ├── gcp.py                # GCS credential config
│   └── sql/                  # All versioned SQL scripts
│       ├── setup_snowflake_infra.sql
│       ├── create_tables.sql
│       ├── view_for_analytics.sql
│       ├── copy_into_tables.sql
│       └── create_stage.sql
├── docs/
│   ├── fact_table.md         # Explanation of OLTP vs OLAP tables
│   ├── snowflake_etl.md      # Deep dive into Snowflake integration
│   └── snowflake_gcs.md      # How to configure GCS ↔ Snowflake integration
├── tests/                    # Pytest-based validation of tables
└── olap_outputs/             # Local or GCS output location
```

---

## 🔁 Full Pipeline Execution

```bash
make all ENV=PROD
```

This will:

1. Run the ETL
2. Upload the CSVs to GCS
3. Run validation tests
4. Load the latest OLAP dump into Snowflake

---

## ❄️ GCS ↔ Snowflake Integration

To set up Snowflake external access to GCS via `STORAGE INTEGRATION`, see:

👉 [`docs/snowflake_gcs.md`](docs/snowflake_gcs.md)

## 🚀 To Go Further

This project is fully operational — you can run it locally, validate it with tests, and inspect the result visually (see screenshots above).

To explore how the Snowflake schema was modeled:

👉 [`docs/fact_dim.md`](docs/fact_dim.md)

To understand the full logic behind the GCS-to-Snowflake data loading process:

👉 [`docs/snowflake_etl.md`](docs/snowflake_etl.md)

---