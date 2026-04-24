from typing import Any

from pydantic import BaseModel, Field, field_validator


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("Question must not be blank.")
        return question


class AskResponse(BaseModel):
    sql: str
    data: list[dict[str, Any]]
    insight: str
    chart: dict[str, str]


class HealthResponse(BaseModel):
    status: str


class IngestionResponse(BaseModel):
    source: str
    inserted: int
    skipped: int
    total_found: int
