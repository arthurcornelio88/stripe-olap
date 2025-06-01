import os
import sys
import json
import tempfile

def configure_gcp_credentials():
    """
    Configure les credentials GCP à partir de la variable d'environnement GCP_CREDS_FILE.
    Si elle contient du JSON brut, crée un fichier temporaire. Sinon, utilise le chemin existant.
    Définit GOOGLE_APPLICATION_CREDENTIALS pour les SDK GCP.
    """
    gcp_creds = os.environ.get("GCP_CREDS_FILE")

    if not gcp_creds:
        print("❌ GCP_CREDS_FILE is not set in the environment.")
        sys.exit(1)

    # Cas 1 : contenu JSON brut (commence par '{')
    if gcp_creds.strip().startswith("{"):
        print("📄 GCP_CREDS_FILE is raw JSON content. Writing to temp file...")
        try:
            # Vérifie que c'est bien un JSON valide
            json.loads(gcp_creds)
        except json.JSONDecodeError:
            print("❌ GCP_CREDS_FILE looks like JSON but is invalid.")
            sys.exit(1)

        # Écrit le JSON dans un fichier temporaire
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            tmp.write(gcp_creds)
            gcp_creds_path = tmp.name
    else:
        # Cas 2 : chemin vers fichier existant
        gcp_creds_path = gcp_creds
        if not os.path.exists(gcp_creds_path):
            print(f"❌ GCP_CREDS_FILE path does not exist: {gcp_creds_path}")
            sys.exit(1)

    # Configuration de l’auth Google
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_creds_path
    print(f"✅ GCP credentials configured from {gcp_creds_path}")
