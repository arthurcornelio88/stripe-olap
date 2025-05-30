# ❄️ Snowflake ↔️ GCS Integration

This folder contains manual provisioning scripts for Snowflake's integration with GCS.

## 📌 Purpose

Allow Snowflake to securely access files stored in GCS using a `STORAGE INTEGRATION`.

## 🔧 Setup Steps

### 1. In Snowflake (ACCOUNTADMIN only)

Edit and run [`scripts/sql/storage_integration_template.sql`](./scripts/sql/storage_integration_template.sql).

After execution:

```sql
DESC INTEGRATION GCS_INT;
````

Note down:

* `STORAGE_GCP_SERVICE_ACCOUNT`
* `STORAGE_GCP_EXTERNAL_ID`

### 2. In GCP Console

1. Go to **IAM → Grant Access**
2. Add the **Snowflake-provided service account**
3. Grant it `Storage Object Viewer` (or `Storage Admin`)
4. Use the `EXTERNAL_ID` if required for trust conditions

---

## ✅ Once Done

Your integration can be used like this:

```sql
CREATE OR REPLACE STAGE STRIPE_OLAP.RAW.GCS_STAGE_PROD
  URL = 'gcs://stripe-bucket-prod_v3/olap_outputs/...'
  STORAGE_INTEGRATION = GCS_INT;
```
