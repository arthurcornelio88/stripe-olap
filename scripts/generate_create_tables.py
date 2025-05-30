import os
import re
from io import BytesIO
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from scripts.olap_io import load_latest_olap_outputs
from gcp import configure_gcp_credentials

load_dotenv()

GCS_BUCKET = os.getenv("GCS_BUCKET")
OUTPUT_FILE = Path("scripts/sql/create_tables.sql")

# 🔧 Forcer certains types si inférés à tort
TYPE_OVERRIDES = {
    # IDs toujours forcés en STRING
    "invoice_id": "STRING",
    "customer_id": "STRING",
    "subscription_id": "STRING",
    "product_id": "STRING",
    "price_id": "STRING",
    "payment_method_id": "STRING",
    "payment_intent_id": "STRING",
    "charge_id": "STRING",

    # Cas spécifiques corrigés
    "receipt_number": "STRING",         # ex: '2072-1714' -> STRING
    "card_brand": "STRING",             # parfois inféré à tort en float
    "payment_method_type": "STRING",    # vide donc mal typé parfois
    "invoice_id": "STRING",             # vide dans payment_intents

    # Champs avec valeurs nulles interprétées comme float
    "cancel_at": "TIMESTAMP",
    "ended_at": "TIMESTAMP",
}


# 🧠 Pattern ISO8601
def is_iso_datetime(val: str) -> bool:
    iso_dt_pattern = r"^\d{4}-\d{2}-\d{2}[ T](\d{2}:\d{2}:\d{2})"
    return isinstance(val, str) and re.match(iso_dt_pattern, val) is not None

def infer_snowflake_type(col_name: str, series: pd.Series) -> str:
    # Force via override
    if col_name in TYPE_OVERRIDES:
        return TYPE_OVERRIDES[col_name]

    sample = series.dropna().astype(str).head(5)
    if sample.apply(is_iso_datetime).all():
        return "TIMESTAMP"

    mapping = {
        'object': 'STRING',
        'float64': 'FLOAT',
        'int64': 'NUMBER',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP'
    }
    return mapping.get(str(series.dtype), 'STRING')

def generate_create_table_sql(df_dict: dict) -> str:
    lines = []
    for table_name, df in df_dict.items():
        lines.append(f"CREATE OR REPLACE TABLE {table_name} (")
        for col in df.columns:
            col_type = infer_snowflake_type(col, df[col])
            lines.append(f"    {col} {col_type},")
        lines[-1] = lines[-1].rstrip(',')
        lines.append(");\n")
    return "\n".join(lines)

def main():
    print("🔐 Configuring GCP credentials...")
    configure_gcp_credentials()

    print("📥 Downloading OLAP outputs from GCS...")
    dfs = load_latest_olap_outputs(GCS_BUCKET)

    print("🛠 Inferring schema and generating SQL...")
    sql_script = generate_create_table_sql(dfs)

    print(f"💾 Writing to {OUTPUT_FILE}...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(sql_script)
    print("✅ create_tables.sql generated successfully.")

if __name__ == "__main__":
    main()
