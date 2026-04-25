import logging
import time
from uuid import uuid4
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
    from services.cache_service import LRUCache
    from services.chart_service import suggest_chart
    from services.query_service import run_query
    from services.seed_service import seed_database
except ModuleNotFoundError:
    from backend.ai import generate_insight, generate_sql
    from backend.config import get_settings
    from backend.errors import AppError
    from backend.routes.ingestion import router as ingestion_router
    from backend.schemas import AskRequest, AskResponse, HealthResponse
    from backend.services.cache_service import LRUCache
    from backend.services.chart_service import suggest_chart
    from backend.services.query_service import run_query
    from backend.services.seed_service import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()
answer_cache: LRUCache[AskResponse] = LRUCache(max_size=64)


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
    request_id = getattr(request.state, "request_id", "-")
    logger.warning(
        "request_failed request_id=%s method=%s path=%s status_code=%s error=%s",
        request_id,
        request.method,
        request.url.path,
        exc.status_code,
        exc,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.public_message, "request_id": request_id},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "-")
    logger.exception(
        "unhandled_error request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error.", "request_id": request_id},
    )


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    logger.info(
        "request_started request_id=%s method=%s path=%s client=%s",
        request_id,
        request.method,
        request.url.path,
        request.client.host if request.client else "-",
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.exception(
            "request_error request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request_finished request_id=%s method=%s path=%s status_code=%s duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


def answer_question(question: str) -> AskResponse:
    """Generate SQL for the question and execute it against sample data."""
    cache_key = " ".join(question.lower().split())

    def build_answer() -> AskResponse:
        logger.info("answer_cache_miss question=%s", cache_key)
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

    return answer_cache.get_or_set(cache_key, build_answer)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    return answer_question(request.question)
