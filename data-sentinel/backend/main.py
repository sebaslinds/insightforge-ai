import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sklearn.ensemble import IsolationForest

app = FastAPI()

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DataPoint(BaseModel):
    value: float
    timestamp: str | None = None


class DetectRequest(BaseModel):
    data: list[float | DataPoint] = Field(min_length=2)

    @field_validator("data")
    @classmethod
    def validate_numeric_series(cls, data: list[float | DataPoint]) -> list[float | DataPoint]:
        if len(data) < 2:
            raise ValueError("At least two data points are required.")
        return data


class ScoredPoint(BaseModel):
    index: int
    value: float
    timestamp: str | None
    anomaly_score: float
    is_anomaly: bool


class Anomaly(BaseModel):
    index: int
    value: float
    timestamp: str | None
    anomaly_score: float


class DetectResponse(BaseModel):
    anomalies: list[Anomaly]
    series: list[ScoredPoint]
    threshold: float
    explanation: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect", response_model=DetectResponse)
def detect(req: DetectRequest) -> DetectResponse:
    points = _normalize_points(req.data)
    model = IsolationForest(contamination=0.1, random_state=42)
    X = [[point.value] for point in points]
    model.fit(X)
    preds = model.predict(X)  # -1 = anomaly
    decision_scores = model.decision_function(X)

    series = [
        ScoredPoint(
            index=index + 1,
            value=point.value,
            timestamp=point.timestamp,
            anomaly_score=round(float(-decision_scores[index]), 6),
            is_anomaly=preds[index] == -1,
        )
        for index, point in enumerate(points)
    ]
    anomalies = [
        Anomaly(
            index=point.index,
            value=point.value,
            timestamp=point.timestamp,
            anomaly_score=point.anomaly_score,
        )
        for point in series
        if point.is_anomaly
    ]

    return DetectResponse(
        anomalies=anomalies,
        series=series,
        threshold=0.0,
        explanation=_explain_anomalies(series, anomalies),
    )


def _normalize_points(data: list[float | DataPoint]) -> list[DataPoint]:
    return [
        item if isinstance(item, DataPoint) else DataPoint(value=float(item))
        for item in data
    ]


def _explain_anomalies(series: list[ScoredPoint], anomalies: list[Anomaly]) -> str:
    if not anomalies:
        return "No anomalies were detected. The values are close enough to the learned baseline for this short series."

    fallback = _build_fallback_explanation(series, anomalies)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=_build_explanation_prompt(series, anomalies),
        )
        return response.text.strip() if response.text else fallback
    except Exception:
        return fallback


def _build_fallback_explanation(series: list[ScoredPoint], anomalies: list[Anomaly]) -> str:
    values = [point.value for point in series]
    average = sum(values) / len(values)
    anomaly_text = ", ".join(
        f"{item.value:g}" if not item.timestamp else f"{item.value:g} at {item.timestamp}"
        for item in anomalies
    )
    return (
        f"Detected {len(anomalies)} anomalous point(s): {anomaly_text}. "
        f"These values deviate from the series average of {average:.2f} and received the highest anomaly scores."
    )


def _build_explanation_prompt(series: list[ScoredPoint], anomalies: list[Anomaly]) -> str:
    payload: dict[str, Any] = {
        "series": [point.model_dump() for point in series],
        "anomalies": [anomaly.model_dump() for anomaly in anomalies],
    }
    return f"""
You are Data Sentinel, an AI monitoring assistant.
Explain the detected anomalies in 2 concise sentences.
Mention the anomalous values, timing if present, and why they may need review.
Avoid technical model internals.

Detection payload:
{payload}
""".strip()
