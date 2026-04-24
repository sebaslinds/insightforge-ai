from fastapi import APIRouter

try:
    from schemas import IngestionResponse
    from services.scraper_service import ingest_demo_products
except ModuleNotFoundError:
    from backend.schemas import IngestionResponse
    from backend.services.scraper_service import ingest_demo_products


router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/scrape-demo", response_model=IngestionResponse)
def scrape_demo() -> IngestionResponse:
    result = ingest_demo_products()
    return IngestionResponse(
        source=result.source,
        inserted=result.inserted,
        skipped=result.skipped,
        total_found=result.total_found,
    )
