import os
import re
import json
from io import BytesIO
from pathlib import Path
from datetime import timezone

import pandas as pd
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

GCS_BUCKET = os.getenv("GCS_BUCKET")
ENV = os.getenv("ENV", "DEV").upper()


def configure_storage_client():
    return storage.Client()


def load_latest_oltp_json_from_gcs(bucket_name=None, prefix="dump/") -> dict:
    if bucket_name is None:
        bucket_name = GCS_BUCKET

    client = configure_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    dump_blobs = [b for b in blobs if re.search(r"db_dump_prod_.*\.json$", b.name)]

    if not dump_blobs:
        raise FileNotFoundError(f"No valid dump files found in bucket '{bucket_name}/{prefix}'")

    latest_blob = max(dump_blobs, key=lambda b: b.updated)
    print(f"📦 Latest dump found: {latest_blob.name} (Last modified: {latest_blob.updated})")

    raw_bytes = latest_blob.download_as_bytes()
    return json.load(BytesIO(raw_bytes))


def load_latest_olap_outputs(bucket_name: str, prefix="olap_outputs/") -> dict:
    client = configure_storage_client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    # Trouve les noms de dossiers horodatés
    time_folders = sorted(
        {b.name.split("/")[1] for b in blobs if b.name.count("/") > 1},
        reverse=True
    )

    if not time_folders:
        raise FileNotFoundError("No OLAP output folders found.")

    latest_folder = time_folders[0]
    print(f"📁 Latest OLAP output folder: {latest_folder}")

    expected_files = [
        "fact_invoices.csv",
        "dim_customers.csv",
        "dim_products.csv",
        "dim_prices.csv",
        "dim_payment_methods.csv",
        "dim_subscriptions.csv",
    ]

    result = {}
    for fname in expected_files:
        blob_path = f"{prefix}{latest_folder}/{fname}"
        blob = bucket.blob(blob_path)
        content = blob.download_as_bytes()
        df = pd.read_csv(BytesIO(content))
        result[fname.replace(".csv", "")] = df

    return result


def upload_csv_to_gcs(df: pd.DataFrame, bucket_name: str, destination_blob_path: str):
    client = configure_storage_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_path)

    with BytesIO() as buffer:
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        blob.upload_from_file(buffer, content_type="text/csv")

    print(f"☁️ Uploaded to: gs://{bucket_name}/{destination_blob_path}")


def save_fact(df: pd.DataFrame, timestamp: str):
    filename = "fact_invoices.csv"

    if ENV == "PROD":
        output_path = f"olap_outputs/{timestamp}/{filename}"
        upload_csv_to_gcs(df, GCS_BUCKET, output_path)
    else:
        local_path = Path(f"olap_outputs/{filename}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(local_path, index=False)
        print(f"💾 Saved locally to: {local_path}")


def save_dim(df: pd.DataFrame, name: str, timestamp: str):
    filename = f"{name}.csv"

    if ENV == "PROD":
        output_path = f"olap_outputs/{timestamp}/{filename}"
        upload_csv_to_gcs(df, GCS_BUCKET, output_path)
        print(f"☁️ Uploaded {name} to GCS at: gs://{GCS_BUCKET}/{output_path}")
    else:
        local_path = Path(f"olap_outputs/{filename}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(local_path, index=False)
        print(f"💾 Saved {name} locally to: {local_path}")
