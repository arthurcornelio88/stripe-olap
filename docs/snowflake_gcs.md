# ❄️ Snowflake ↔️ GCS Integration

This document explains the **automated** GCS-Snowflake integration setup included in the OLAP pipeline.

## 🚀 **Automated Setup (Recommended)**

The integration is **fully automated** via the pipeline:

```bash
cd /home/arthurcornelio88/jedha/stripe_b2/olap
ENV=PROD make all
```

This automatically:
1. ✅ Creates the `GCS_INT` storage integration in Snowflake
2. ✅ Retrieves Snowflake's service account credentials
3. ✅ Grants GCP permissions via `gcloud` CLI
4. ✅ Tests the integration and loads data

## 🔧 **What Happens Behind the Scenes**

### Step 1: Storage Integration Creation

The system creates this integration in Snowflake (requires `ACCOUNTADMIN` role):

```sql
CREATE STORAGE INTEGRATION GCS_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://stripe-bucket-prod_v3')
  COMMENT = 'Integration between Snowflake and GCS bucket for OLAP pipeline';
```

### Step 2: Credential Retrieval

Snowflake provides a unique service account:

```sql
DESC INTEGRATION GCS_INT;
```

Returns:
- **Service Account**: `kn0q00000@gcpeuropewest3-1-d3ca.iam.gserviceaccount.com`
- **External ID**: (if required for additional security)

### Step 3: GCP Permissions Grant

The system automatically grants storage permissions:

```bash
gcloud projects add-iam-policy-binding stripe-b2-gcp \
  --member="serviceAccount:kn0q00000@gcpeuropewest3-1-d3ca.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

**Why `storage.admin`?**
- `storage.objects.get` - Read files from GCS
- `storage.objects.list` - List bucket contents (required by Snowflake)
- `storage.buckets.get` - Access bucket metadata

### Step 4: Stage Creation & Data Loading

Creates the external stage:

```sql
CREATE STAGE GCS_STAGE_PROD
  URL = 'gcs://stripe-bucket-prod_v3/olap_outputs/2025-09-08_20-01-32/'
  STORAGE_INTEGRATION = GCS_INT;
```

Then loads data via `COPY INTO`:

```sql
COPY INTO fact_invoices
FROM @GCS_STAGE_PROD/fact_invoices.csv
FILE_FORMAT = (TYPE = CSV, SKIP_HEADER = 1);
```

## 🛠️ **Manual Setup (If Needed)**

If you need to set up the integration manually:

### Option 1: Via Script

```bash
ENV=PROD make setup_gcs_integration
```

### Option 2: Via Snowflake UI

1. **Login as ACCOUNTADMIN** in Snowflake UI
2. **Execute the integration SQL**:
   ```sql
   CREATE STORAGE INTEGRATION GCS_INT
     TYPE = EXTERNAL_STAGE
     STORAGE_PROVIDER = GCS
     ENABLED = TRUE
     STORAGE_ALLOWED_LOCATIONS = ('gcs://stripe-bucket-prod_v3')
     COMMENT = 'Integration between Snowflake and GCS bucket for OLAP pipeline';
   ```

3. **Get the service account**:
   ```sql
   DESC INTEGRATION GCS_INT;
   ```

4. **Grant GCP access**:
   - Go to [GCP Console IAM](https://console.cloud.google.com/iam-admin/iam)
   - Click "Grant Access"
   - Add the Snowflake service account as principal
   - Grant `Storage Admin` role

### Option 3: Via GCloud CLI

```bash
# Get the service account from Snowflake first, then:
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="serviceAccount:SNOWFLAKE_SERVICE_ACCOUNT_HERE" \
  --role="roles/storage.admin"
```

## 🔍 **Troubleshooting**

### Common Issues

**Error: "Permission denied on GCS bucket"**
- Solution: Ensure service account has `storage.admin` role
- Check: `gcloud projects get-iam-policy $(gcloud config get-value project)`

**Error: "Integration already exists"**
- Solution: The integration is idempotent, this is not a problem
- Alternative: `DROP INTEGRATION GCS_INT;` then recreate

**Error: "ACCOUNTADMIN role required"**
- Solution: Switch to ACCOUNTADMIN role in Snowflake UI
- Check: `SELECT CURRENT_ROLE();`

### Verification Commands

```sql
-- Check integration exists
SHOW INTEGRATIONS;

-- Test stage access
LIST @GCS_STAGE_PROD;

-- Verify table data
SELECT COUNT(*) FROM fact_invoices;
```

## 📊 **Integration Benefits**

- ✅ **Security**: No permanent credentials stored
- ✅ **Performance**: Direct GCS → Snowflake transfer
- ✅ **Scalability**: Handles large datasets efficiently  
- ✅ **Automation**: Zero manual intervention required
- ✅ **Cost-effective**: Pay only for data transfer

## 🎯 **Production Usage**

Once integrated, your pipeline automatically:

1. **Generates dimensional CSVs** → GCS
2. **Creates Snowflake tables** with proper schema
3. **Loads data efficiently** via `COPY INTO`
4. **Creates analytical views** for business queries
5. **Validates data integrity** through tests

**Result**: Production-ready OLAP system with automated GCS integration! 🚀
