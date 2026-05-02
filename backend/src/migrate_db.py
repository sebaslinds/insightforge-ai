import os
import asyncio
from google.cloud.sql.connector import Connector
import sqlalchemy
from sqlalchemy import text
from core.database import Base, engine
import core.models          # Important pour enregistrer les modèles
import core.tenant_models   # Important pour enregistrer les modèles

async def init_db():
    print("--- Initialisation de la base de données Cloud SQL ---")
    
    # On force la création des tables via l'engine configuré
    try:
        # Note: En local, assurez-vous d'avoir GOOGLE_APPLICATION_CREDENTIALS pointant vers votre gcp-key.json
        print("Connexion à Cloud SQL et création des tables...")
        Base.metadata.create_all(bind=engine)
        print("Succès : Les tables ont été créées.")
        
        # Vérification
        with engine.connect() as conn:
            result = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result]
            print(f"Tables trouvées : {', '.join(tables)}")
            
    except Exception as e:
        print(f"Erreur lors de la création des tables : {e}")

if __name__ == "__main__":
    # On utilise l'engine synchrone car metadata.create_all est synchrone
    Base.metadata.create_all(bind=engine)
    print("Opération terminée.")
