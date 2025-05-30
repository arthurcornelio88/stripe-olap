import os
from pathlib import Path
from dotenv import load_dotenv
from scripts.olap_io import load_latest_olap_outputs
from gcp import configure_gcp_credentials

load_dotenv()

GCS_BUCKET = os.getenv("GCS_BUCKET")
OUTPUT_FILE = Path("scripts/sql/copy_into_tables.sql")

def generate_copy_into_sql(df_dict: dict) -> str:
    lines = []
    for table_name, df in df_dict.items():
        lines.append(f"COPY INTO {table_name} (")
        for col in df.columns:
            lines.append(f"    {col},")
        lines[-1] = lines[-1].rstrip(',')  # remove trailing comma
        lines.append(")")
        lines.append(f"FROM @STRIPE_OLAP.RAW.GCS_STAGE_PROD/{table_name}.csv")
        lines.append("FILE_FORMAT = (")
        lines.append("    TYPE = CSV,")
        lines.append("    FIELD_DELIMITER = ',',")
        lines.append("    SKIP_HEADER = 1")
        lines.append(");")
    return "\n".join(lines)

def main():
    print("🔐 Configuring GCP credentials...")
    configure_gcp_credentials()

    print("📥 Downloading OLAP outputs from GCS...")
    dfs = load_latest_olap_outputs(GCS_BUCKET)

    print("🛠 Generating COPY INTO SQL script...")
    sql_script = generate_copy_into_sql(dfs)

    print(f"💾 Writing to {OUTPUT_FILE}...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(sql_script)
    print("✅ copy_into_tables.sql generated successfully.")

if __name__ == "__main__":
    main()
