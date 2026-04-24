import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    database_url: str
    cors_origins: list[str]
    cors_origin_regex: str | None
    app_name: str = "BI Copilot API"


@lru_cache
def get_settings() -> Settings:
    default_database_path = Path(__file__).resolve().parent / "bi_copilot.db"
    cors_origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{default_database_path.as_posix()}"),
        cors_origins=[
            origin.strip()
            for origin in cors_origins.split(",")
            if origin.strip()
        ],
        cors_origin_regex=os.getenv(
            "CORS_ORIGIN_REGEX",
            r"https://.*\.vercel\.app",
        ),
    )
