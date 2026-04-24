import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from ai import generate_insight, generate_sql
    from config import get_settings
    from errors import AppError
    from routes.ingestion import router as ingestion_router
    from schemas import AskRequest, AskResponse, HealthResponse
    from services.chart_service import suggest_chart
    from services.query_service import run_query
    from services.seed_service import seed_database
except ModuleNotFoundError:
    from backend.ai import generate_insight, generate_sql
    from backend.config import get_settings
    from backend.errors import AppError
    from backend.routes.ingestion import router as ingestion_router
    from backend.schemas import AskRequest, AskResponse, HealthResponse
    from backend.services.chart_service import suggest_chart
    from backend.services.query_service import run_query
    from backend.services.seed_service import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database(reset=False)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(ingestion_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("%s %s failed: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.public_message},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )


def answer_question(question: str) -> AskResponse:
    """Generate SQL for the question and execute it against sample data."""
    sql = generate_sql(question)
    data = run_query(sql)
    insight = generate_insight(data)
    chart = suggest_chart(data)
    return AskResponse(
        sql=sql,
        data=data,
        insight=insight,
        chart=chart,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return answer_question(request.question)
