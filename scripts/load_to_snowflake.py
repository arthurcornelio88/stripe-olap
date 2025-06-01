import os
import argparse
from dotenv import load_dotenv
import snowflake.connector
from olap_io import get_latest_olap_gcs_path
from gcp import configure_gcp_credentials

load_dotenv()

def connect_to_snowflake():
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )


def run_sql_file(path: str, conn):
    with open(path, 'r') as file:
        content = file.read()

    # Split by semicolon
    commands = content.split(';')
    cur = conn.cursor()

    for cmd in commands:
        cleaned = cmd.strip()
        # Skip empty or pure comment blocks
        if not cleaned or cleaned.startswith('--'):
            continue
        print(f"▶ Executing: {cleaned}")
        cur.execute(cleaned)

    cur.close()

def run_sql_file_with_substitution(path: str, conn, substitutions: dict):
    with open(path, 'r') as file:
        content = file.read()
    for key, val in substitutions.items():
        content = content.replace(f"{{{{{key}}}}}", val)

    commands = content.split(';')
    cur = conn.cursor()

    for cmd in commands:
        cleaned = cmd.strip()
        if not cleaned or cleaned.startswith('--'):
            continue
        print(f"▶ Executing: {cleaned}")
        cur.execute(cleaned)

    cur.close()



def print_sql_file(path: str, substitutions: dict = None):
    with open(path, 'r') as file:
        content = file.read()
    if substitutions:
        for key, val in substitutions.items():
            content = content.replace(f"{{{{{key}}}}}", val)
    print(content)


def main(dry_run=False):
    print("🔐 Configuring GCP credentials...")
    configure_gcp_credentials()

    bucket = os.getenv("GCS_BUCKET")
    if not bucket:
        raise EnvironmentError("❌ GCS_BUCKET is not set in environment")

    print("📁 Locating latest OLAP folder...")
    olap_path = get_latest_olap_gcs_path(bucket)

    substitutions = {
        "BUCKET": bucket,
        "OLAP_PATH": olap_path
    }

    if dry_run:
        print("\n--- DRY RUN ---")

        for label, path in [
            ("SETUP INFRASTRUCTURE", "scripts/sql/setup_snowflake_infra.sql"),
            ("CREATE TABLES", "scripts/sql/create_tables.sql"),
            ("CREATE VIEWS", "scripts/sql/view_for_analytics.sql"),
            ("COPY INTO", "scripts/sql/copy_into_tables.sql")
        ]:
            print(f"\n-- {label} ({path}) --")
            print_sql_file(path, substitutions if "COPY" in label else None)

        print("\n✅ No SQL was executed.")
        return

    print("❄️ Connecting to Snowflake...")
    conn = connect_to_snowflake()

    print("🏗️ Running infrastructure setup...")
    run_sql_file("scripts/sql/setup_snowflake_infra.sql", conn)

    # 🧭 Reset session context explicitly
    cur = conn.cursor()
    cur.execute("USE DATABASE STRIPE_OLAP;")
    cur.execute("USE SCHEMA RAW;")
    cur.execute(f"USE WAREHOUSE {os.getenv('SNOWFLAKE_WAREHOUSE')};")
    cur.close()

    print("🧱 Creating tables...")
    run_sql_file("scripts/sql/create_tables.sql", conn)

    print("📊 Creating views...")
    run_sql_file("scripts/sql/view_for_analytics.sql", conn)

    print("☁️ Creating GCS stage...")
    run_sql_file_with_substitution("scripts/sql/create_stage.sql", conn, substitutions)

    print("📤 Loading data from GCS to Snowflake via COPY INTO...")
    run_sql_file_with_substitution("scripts/sql/copy_into_tables.sql", conn, substitutions)


    print("🎉 All done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load latest OLAP data into Snowflake from GCS.")
    parser.add_argument("--dry-run", action="store_true", help="Print SQL commands without executing.")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
