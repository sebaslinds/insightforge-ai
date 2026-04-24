import json
import logging
from typing import Any

from google import genai

try:
    from config import get_settings
    from errors import AIServiceError, ConfigurationError
except ModuleNotFoundError:
    from backend.config import get_settings
    from backend.errors import AIServiceError, ConfigurationError


logger = logging.getLogger(__name__)
MAX_INSIGHT_ROWS = 50


def _build_sql_prompt(question: str) -> str:
    return f"""
You are a BI Copilot that converts business questions into SQL.
Return only SQL, with no markdown fences or explanation.
Generate read-only SQL only. Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, or TRUNCATE statements.
Use a simple sales analytics schema unless the user provides more context:
- sales(id, product, category, price, quantity, date, customer_id)

Revenue is calculated as price * quantity.
When answering revenue questions, alias the calculated metric as revenue.
Rows ingested by the ethical demo scraper use category = 'Scraped Demo'.
When users ask for scraped demo products, filter with category = 'Scraped Demo', not product LIKE '%scraped demo%'.

Question: {question}
""".strip()


def _build_insight_prompt(data: list[dict[str, Any]]) -> str:
    data_sample = data[:MAX_INSIGHT_ROWS]
    return f"""
You are a senior BI analyst.
Analyze the dataset and return concise, professional business insights.
Focus on trends, anomalies, and useful next actions.
Use 2-4 short sentences.
Return plain text only.
Do not use markdown, bullets, asterisks, headings, or numbered lists.
Do not mention technical implementation details.

Dataset sample:
{json.dumps(data_sample, default=str)}
""".strip()


def _clean_sql(response_text: str) -> str:
    sql = response_text.strip()

    if sql.startswith("```"):
        lines = sql.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        sql = "\n".join(lines).strip()

    sql = sql.rstrip(";").strip()
    if not sql:
        return ""

    return f"{sql};"


def _validate_sql(sql: str) -> None:
    if not sql:
        raise AIServiceError("Gemini returned an empty SQL response.")

    first_token = sql.split(maxsplit=1)[0].lower()
    if first_token not in {"select", "with"}:
        raise AIServiceError("Gemini returned a non-read-only SQL statement.")


def _get_gemini_client() -> genai.Client:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ConfigurationError("GEMINI_API_KEY environment variable is not set.")

    return genai.Client(api_key=settings.gemini_api_key)


def generate_sql(question: str) -> str:
    settings = get_settings()

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=_build_sql_prompt(question),
        )
    except Exception as exc:
        logger.exception("Gemini request failed")
        raise AIServiceError("Gemini request failed.") from exc

    if not response.text:
        raise AIServiceError("Gemini returned an empty response.")

    sql = _clean_sql(response.text)
    _validate_sql(sql)
    return sql


def generate_insight(data: list[dict[str, Any]]) -> str:
    if not data:
        return "No records were returned, so there are no business insights to summarize."

    settings = get_settings()

    try:
        client = _get_gemini_client()
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=_build_insight_prompt(data),
        )
    except Exception as exc:
        logger.exception("Gemini insight request failed")
        raise AIServiceError("Gemini failed to generate insights.") from exc

    if not response.text:
        raise AIServiceError("Gemini returned an empty insight response.")

    return response.text.strip()
