import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

try:
    from database import SessionLocal, init_db
    from errors import QueryExecutionError
    import models
except ModuleNotFoundError:
    from backend.database import SessionLocal, init_db
    from backend.errors import QueryExecutionError
    from backend import models


logger = logging.getLogger(__name__)
MAX_RESULT_ROWS = 500
ALLOWED_QUERY_STARTS = {"select", "with"}
BLOCKED_SQL_TOKENS = {
    "alter",
    "attach",
    "create",
    "delete",
    "detach",
    "drop",
    "insert",
    "pragma",
    "replace",
    "truncate",
    "update",
}
BLOCKED_SQL_PATTERN = re.compile(
    rf"\b({'|'.join(sorted(BLOCKED_SQL_TOKENS))})\b",
    flags=re.IGNORECASE,
)
SQL_COMMENT_PATTERN = re.compile(r"(--|/\*)")


def _validate_read_only_sql(sql: str) -> None:
    normalized = sql.strip().rstrip(";")
    if not normalized:
        raise QueryExecutionError("SQL query must not be empty.")

    if ";" in normalized:
        raise QueryExecutionError("Multiple SQL statements are not allowed.")

    if SQL_COMMENT_PATTERN.search(normalized):
        raise QueryExecutionError("SQL comments are not allowed.")

    first_token = normalized.split(maxsplit=1)[0].lower()
    if first_token not in ALLOWED_QUERY_STARTS:
        raise QueryExecutionError("Only read-only SELECT queries are allowed.")

    if BLOCKED_SQL_PATTERN.search(normalized):
        raise QueryExecutionError("Query contains blocked SQL operations.")


def _strip_trailing_semicolon(sql: str) -> str:
    return sql.strip().rstrip(";").strip()


def _limit_query(sql: str) -> str:
    query = _strip_trailing_semicolon(sql)
    return f"SELECT * FROM ({query}) AS limited_query LIMIT {MAX_RESULT_ROWS}"


def _normalize_known_ai_sql(sql: str) -> str:
    query = sql.strip()
    scraped_product_filter = re.compile(
        r"product\s+LIKE\s+'%scraped demo%'",
        flags=re.IGNORECASE,
    )
    return scraped_product_filter.sub("category = 'Scraped Demo'", query)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _rows_to_records(rows: list[Any]) -> list[dict[str, Any]]:
    return [
        {key: _serialize_value(value) for key, value in row._mapping.items()}
        for row in rows
    ]


def run_query(sql: str) -> list[dict[str, Any]]:
    """Execute read-only SQL against the configured database."""
    sql = _normalize_known_ai_sql(sql)
    _validate_read_only_sql(sql)
    init_db()

    try:
        with SessionLocal() as session:
            rows = session.execute(text(_limit_query(sql))).all()
            session.rollback()
    except SQLAlchemyError as exc:
        logger.exception("Failed to execute SQL query")
        raise QueryExecutionError("Failed to execute SQL query.") from exc

    return _rows_to_records(rows)
