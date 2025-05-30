import os
import sys

def configure_gcp_credentials():
    """
    Configure les credentials GCP à partir de la variable d'environnement GCP_CREDS_FILE.
    Définit GOOGLE_APPLICATION_CREDENTIALS si nécessaire.
    """
    gcp_creds_file = os.environ.get("GCP_CREDS_FILE")

    if not gcp_creds_file:
        print("❌ GCP_CREDS_FILE is not set in the environment.")
        sys.exit(1)

    if not os.path.exists(gcp_creds_file):
        print(f"❌ GCP_CREDS_FILE path does not exist: {gcp_creds_file}")
        sys.exit(1)

    # Important: this is what Google Auth reads
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds_file
    print(f"✅ GCP credentials configured from {gcp_creds_file}")
