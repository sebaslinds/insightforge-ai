import logging
from dataclasses import dataclass
from datetime import date

import requests
from bs4 import BeautifulSoup

try:
    from database import SessionLocal, init_db
    from models import Sale
except ModuleNotFoundError:
    from backend.database import SessionLocal, init_db
    from backend.models import Sale


logger = logging.getLogger(__name__)
DEMO_ECOMMERCE_URL = "https://webscraper.io/test-sites/e-commerce/allinone"
SCRAPED_CUSTOMER_ID = "SCRAPER-DEMO"
REQUEST_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class ScrapedProduct:
    name: str
    category: str
    price: float


@dataclass(frozen=True)
class ScrapeResult:
    source: str
    inserted: int
    skipped: int
    total_found: int


def _parse_price(value: str) -> float:
    cleaned = value.replace("$", "").replace(",", "").strip()
    return float(cleaned)


def fetch_demo_products(url: str = DEMO_ECOMMERCE_URL) -> list[ScrapedProduct]:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": "BI-Copilot-Portfolio-Demo/1.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    products: list[ScrapedProduct] = []

    for card in soup.select(".thumbnail, .card"):
        title = card.select_one(".title, .card-title a, a.title")
        price = card.select_one(".price, .card-price")
        if not title or not price:
            continue

        name = title.get_text(strip=True)
        if not name:
            continue

        try:
            parsed_price = _parse_price(price.get_text(strip=True))
        except ValueError:
            logger.warning("Skipping product with invalid price: %s", name)
            continue

        products.append(
            ScrapedProduct(
                name=name[:120],
                category="Scraped Demo",
                price=parsed_price,
            )
        )

    return products


def ingest_demo_products() -> ScrapeResult:
    products = fetch_demo_products()
    init_db()

    inserted = 0
    skipped = 0
    today = date.today()

    with SessionLocal() as session:
        max_id = session.query(Sale.id).order_by(Sale.id.desc()).limit(1).scalar() or 0
        existing_products = {
            product
            for (product,) in session.query(Sale.product)
            .filter(Sale.customer_id == SCRAPED_CUSTOMER_ID)
            .all()
        }

        for product in products:
            if product.name in existing_products:
                skipped += 1
                continue

            max_id += 1
            session.add(
                Sale(
                    id=max_id,
                    product=product.name,
                    category=product.category,
                    price=product.price,
                    quantity=1,
                    date=today,
                    customer_id=SCRAPED_CUSTOMER_ID,
                )
            )
            existing_products.add(product.name)
            inserted += 1

        session.commit()

    return ScrapeResult(
        source=DEMO_ECOMMERCE_URL,
        inserted=inserted,
        skipped=skipped,
        total_found=len(products),
    )
