import os
from datetime import datetime, timezone
from dotenv import load_dotenv

from gcp import configure_gcp_credentials
from scripts.csv_builders import (
    build_fact_invoices,
    build_dim_customers,
    build_dim_products,
    build_dim_prices,
    build_dim_payment_methods,
    build_dim_subscriptions
)
from scripts.olap_io import (
    load_latest_oltp_json_from_gcs,
    save_fact,
    save_dim,
)

# 🔁 Charge les variables d'environnement (.env)
load_dotenv()
ENV = os.getenv("ENV", "DEV").upper()

def main():
    print(f"🚀 Starting ETL for ENV={ENV}")

    # 🛡 Configure les credentials ADC
    configure_gcp_credentials()

    # ⏱ Fige un seul timestamp pour tout le run
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    print(f"📁 Using timestamp: {timestamp}")

    # 📥 Charge les données brutes
    raw = load_latest_oltp_json_from_gcs()
    print(f"✅ Loaded raw tables: {list(raw.keys())}")

    # 🏗 Build et sauvegarde
    fact_df = build_fact_invoices(raw)
    save_fact(fact_df, timestamp=timestamp)

    dims = {
        "dim_customers": build_dim_customers,
        "dim_products": build_dim_products,
        "dim_prices": build_dim_prices,
        "dim_payment_methods": build_dim_payment_methods,
        "dim_subscriptions": build_dim_subscriptions,
    }

    for dim_name, builder in dims.items():
        dim_df = builder(raw)
        save_dim(dim_df, dim_name, timestamp=timestamp)

    print("🎉 ETL completed successfully")

if __name__ == "__main__":
    main()
