from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import get_settings
from google.cloud.sql.connector import Connector, IPTypes
import os

settings = get_settings()

def get_connection():
    """Gère la connexion à Cloud SQL ou PostgreSQL standard."""
    os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
    if settings.CLOUD_SQL_CONNECTION_NAME:
        # Initialise le connecteur Cloud SQL
        connector = Connector()
        conn = connector.connect(
            settings.CLOUD_SQL_CONNECTION_NAME,
            "pg8000",
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", ""),
            db=os.getenv("DB_NAME", "insightforge"),
            ip_type=IPTypes.PUBLIC  # Ou PRIVATE si VPC configuré
        )
        return conn
    return None

# Moteur SQLAlchemy
if settings.CLOUD_SQL_CONNECTION_NAME:
    engine = create_engine(
        "postgresql+pg8000://",
        creator=get_connection,
        pool_pre_ping=True,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"options": "-c timezone=utc"} if settings.DATABASE_URL.startswith("postgresql") else {}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
