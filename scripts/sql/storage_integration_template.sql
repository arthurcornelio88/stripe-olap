-- ❄️ Run this manually with ACCOUNTADMIN role

CREATE STORAGE INTEGRATION GCS_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://{{GCS_BUCKET}}')
  COMMENT = 'Integration between Snowflake and GCS bucket for OLAP pipeline';

-- After running:
--   DESC INTEGRATION GCS_INT;
-- Then go to GCP and:
-- - Add the service account as IAM member
-- - Use the External ID for trust configuration
