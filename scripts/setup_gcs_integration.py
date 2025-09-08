#!/usr/bin/env python3
"""
🔧 GCS-Snowflake Integration Automation Script
Fully automates the configuration of Snowflake → GCS access
"""

import os
import subprocess
import sys
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

def get_gcp_project():
    """Get current GCP project"""
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Error getting GCP project: {e}")
        return None

def connect_snowflake():
    """Connect to Snowflake with ACCOUNTADMIN role"""
    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        role='ACCOUNTADMIN'  # Required to create integration
    )

def create_storage_integration(conn, gcs_bucket):
    """Create GCS integration in Snowflake"""
    print("🔧 Creating GCS integration...")
    
    cur = conn.cursor()
    
    # SQL pour créer l'intégration
    integration_sql = f"""
CREATE STORAGE INTEGRATION IF NOT EXISTS GCS_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://{gcs_bucket}')
  COMMENT = 'Integration between Snowflake and GCS bucket for OLAP pipeline';
"""
    
    try:
        cur.execute(integration_sql)
        print("✅ GCS integration created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating integration: {e}")
        return False
    finally:
        cur.close()

def get_snowflake_service_account(conn):
    """Get Snowflake service account for GCP"""
    print("🔍 Retrieving Snowflake credentials...")
    
    cur = conn.cursor()
    
    try:
        cur.execute("DESC INTEGRATION GCS_INT;")
        results = cur.fetchall()
        
        service_account = None
        external_id = None
        
        for row in results:
            if 'STORAGE_GCP_SERVICE_ACCOUNT' in str(row[0]):
                service_account = row[2]
            elif 'STORAGE_GCP_EXTERNAL_ID' in str(row[0]):
                external_id = row[2]
        
        return service_account, external_id
    
    except Exception as e:
        print(f"❌ Error retrieving credentials: {e}")
        return None, None
    finally:
        cur.close()

def grant_gcp_access(service_account, gcp_project):
    """Grant GCS access to Snowflake service account"""
    print(f"🔐 Granting GCP permissions to: {service_account}")
    
    try:
        # Commande gcloud pour donner accès
        cmd = [
            'gcloud', 'projects', 'add-iam-policy-binding', gcp_project,
            f'--member=serviceAccount:{service_account}',
            '--role=roles/storage.admin'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ GCP permissions granted successfully!")
            return True
        else:
            print(f"❌ gcloud error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error granting permissions: {e}")
        return False



def main():
    """Main function"""
    print("🚀 Automatic GCS-Snowflake Integration Setup")
    print("=" * 60)
    
    # 1. Check prerequisites
    gcs_bucket = os.getenv("GCS_BUCKET")
    if not gcs_bucket:
        print("❌ GCS_BUCKET variable not defined in .env")
        sys.exit(1)
    
    gcp_project = get_gcp_project()
    if not gcp_project:
        print("❌ Unable to retrieve GCP project")
        sys.exit(1)
    
    print(f"📦 GCS Bucket: {gcs_bucket}")
    print(f"🏗️ GCP Project: {gcp_project}")
    
    # 2. Snowflake connection
    try:
        print("❄️ Connecting to Snowflake...")
        conn = connect_snowflake()
        print("✅ Connected to Snowflake")
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        sys.exit(1)
    
    # 3. Create integration
    if not create_storage_integration(conn, gcs_bucket):
        conn.close()
        sys.exit(1)
    
    # 4. Get service account
    service_account, external_id = get_snowflake_service_account(conn)
    if not service_account:
        print("❌ Unable to retrieve Snowflake service account")
        conn.close()
        sys.exit(1)
    
    print(f"🔑 Snowflake Service Account: {service_account}")
    if external_id:
        print(f"🆔 External ID: {external_id}")
    
    # 5. Grant GCP access
    if not grant_gcp_access(service_account, gcp_project):
        conn.close()
        sys.exit(1)
    
    conn.close()
    print("\n🎉 GCS-SNOWFLAKE INTEGRATION CONFIGURED SUCCESSFULLY!")
    print("✅ You can now use: ENV=PROD make load_snowflake")

if __name__ == "__main__":
    main()
