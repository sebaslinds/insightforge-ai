from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

try:
    from config import get_settings
except ModuleNotFoundError:
    from backend.config import get_settings


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return database_url


settings = get_settings()
engine = create_engine(
    _normalize_database_url(settings.database_url),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
