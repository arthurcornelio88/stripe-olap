from olap_io import get_latest_olap_gcs_path
from gcp import configure_gcp_credentials
import os

# Configure GCP credentials
configure_gcp_credentials()

bucket = os.getenv("GCS_BUCKET")
if not bucket:
    print("❌ GCS_BUCKET not set in environment")

# Trouver le dossier OLAP le plus récent
olap_path = get_latest_olap_gcs_path(bucket)

# Templates de COPY INTO
csv_files = [
    "fact_invoices.csv",
    "dim_customers.csv",
    "dim_products.csv",
    "dim_prices.csv",
    "dim_payment_methods.csv",
    "dim_subscriptions.csv",
    "dim_payment_intents.csv",
    "dim_charges.csv"
]

copy_commands = "\n".join([
    f"COPY INTO {f.replace('.csv','')} FROM @gcs_stage_prod/{olap_path}{f} FILE_FORMAT=(TYPE=CSV FIELD_DELIMITER=',' SKIP_HEADER=1);"
    for f in csv_files
])

# Exécuter création du stage (si pas déjà fait)
stage_command = f"""
create or replace stage gcs_stage_prod
  url='gcs://{GCS_BUCKET}/{olap_path}'
  storage_integration = my_gcs_integration;
"""

# Lancer SQL via Snowflake
cur = conn.cursor()
cur.execute(stage_command)
for cmd in copy_commands.split(";"):
    if cmd.strip():
        cur.execute(cmd)
cur.close()
