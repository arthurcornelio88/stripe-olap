import os
import pytest
from scripts.olap_io import load_latest_oltp_json_from_gcs, load_latest_olap_outputs
from scripts.gcp import configure_gcp_credentials

@pytest.fixture(scope="session", autouse=True)
def gcp_setup():
    """
    Configure les credentials GCP une seule fois pour toute la session de test.
    """
    configure_gcp_credentials()

@pytest.fixture(scope="session")
def raw_json_dump(gcp_setup):
    """
    Charge le dernier dump JSON depuis GCS.
    """
    return load_latest_oltp_json_from_gcs()

@pytest.fixture(scope="session")
def olap_outputs(gcp_setup):
    """
    Charge les derniers outputs OLAP depuis GCS.
    """
    bucket = os.getenv("GCS_BUCKET")
    if not bucket:
        pytest.exit("❌ GCS_BUCKET not set in environment")
    return load_latest_olap_outputs(bucket)#
