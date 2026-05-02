import os
from google.cloud import storage
from core.config import get_settings
from pathlib import Path

settings = get_settings()

def get_storage_client():
    """Initialise le client GCS. Utilise les identifiants par défaut en prod (Service Account)."""
    if settings.ENVIRONMENT == "development" and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        # En dev local, on peut simuler ou utiliser un client sans auth si on n'a pas encore de compte de service
        return None
    return storage.Client(project=settings.GOOGLE_CLOUD_PROJECT)

def upload_model_to_gcs(local_path: str, gcs_blob_name: str):
    """Télécharge un fichier local (ex: modèle .pkl) vers GCS."""
    client = get_storage_client()
    if not client:
        print(f"Skipping upload: No GCS client (Dev mode). File: {local_path}")
        return

    bucket = client.bucket(settings.GCS_BUCKET)
    blob = bucket.blob(gcs_blob_name)
    blob.upload_from_filename(local_path)
    print(f"File {local_path} uploaded to {gcs_blob_name}.")

def download_model_from_gcs(gcs_blob_name: str, local_path: str):
    """Télécharge un modèle depuis GCS vers le disque local pour l'inférence."""
    client = get_storage_client()
    if not client:
        print(f"Skipping download: No GCS client (Dev mode). Blob: {gcs_blob_name}")
        return

    # S'assurer que le dossier parent existe
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)

    bucket = client.bucket(settings.GCS_BUCKET)
    blob = bucket.blob(gcs_blob_name)
    blob.download_to_filename(local_path)
    print(f"Blob {gcs_blob_name} downloaded to {local_path}.")
