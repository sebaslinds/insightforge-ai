import pytest
from fastapi.testclient import TestClient

import ai
import main
from errors import AIServiceError, QueryExecutionError
from scripts.seed_db import seed
from services.query_service import run_query
from services.scraper_service import ScrapedProduct


@pytest.fixture(scope="module", autouse=True)
def seeded_database() -> None:
    seed()


def test_health() -> None:
    client = TestClient(main.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_ask_with_mocked_gemini(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(main.app)
    main.answer_cache.clear()

    monkeypatch.setattr(
        main,
        "generate_sql",
        lambda question: (
            "SELECT product, price * quantity AS revenue "
            "FROM sales ORDER BY revenue DESC LIMIT 3;"
        ),
    )
    monkeypatch.setattr(
        main,
        "generate_insight",
        lambda data: "Top revenue is concentrated in premium computer products.",
    )

    response = client.post("/ask", json={"question": "Top products by revenue"})

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"sql", "data", "insight", "chart"}
    assert payload["data"]
    assert payload["chart"] == {"type": "bar", "x": "product", "y": "revenue"}


def test_run_query_accepts_select() -> None:
    rows = run_query("SELECT product, price * quantity AS revenue FROM sales LIMIT 2;")

    assert len(rows) == 2
    assert {"product", "revenue"} <= set(rows[0])


def test_run_query_normalizes_scraped_demo_product_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(main.app)
    monkeypatch.setattr(
        "services.scraper_service.fetch_demo_products",
        lambda: [
            ScrapedProduct(name="Portfolio Product C", category="Scraped Demo", price=39.99),
        ],
    )
    client.post("/ingestion/scrape-demo")

    rows = run_query(
        "SELECT product, price FROM sales "
        "WHERE product LIKE '%scraped demo%' "
        "ORDER BY price;"
    )

    assert rows
    assert {"product", "price"} <= set(rows[0])


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE sales;",
        "DELETE FROM sales;",
        "SELECT * FROM sales; DELETE FROM sales;",
        "SELECT * FROM sales -- comment",
    ],
)
def test_run_query_blocks_unsafe_sql(sql: str) -> None:
    with pytest.raises(QueryExecutionError):
        run_query(sql)


def test_ai_sql_validation_blocks_unsafe_generated_sql() -> None:
    with pytest.raises(AIServiceError):
        ai._validate_sql("SELECT * FROM sales; DROP TABLE sales;")


def test_sql_prompt_includes_schema_and_aggregation_rules() -> None:
    prompt = ai._build_sql_prompt("Revenue by category")

    assert "Use this exact SQLite schema" in prompt
    assert "sales" in prompt
    assert "product" in prompt
    assert "SUM(price * quantity)" in prompt
    assert "GROUP BY category" in prompt


def test_insight_prompt_requests_structured_bullets() -> None:
    prompt = ai._build_insight_prompt([{"product": "Laptop Pro 14", "revenue": 7495.0}])

    assert "- Trend:" in prompt
    assert "- Anomaly:" in prompt
    assert "- Recommendation:" in prompt


def test_answer_question_caches_repeated_questions(monkeypatch: pytest.MonkeyPatch) -> None:
    main.answer_cache.clear()
    calls = {"sql": 0, "insight": 0}

    def fake_generate_sql(question: str) -> str:
        calls["sql"] += 1
        return "SELECT product, price * quantity AS revenue FROM sales LIMIT 2;"

    def fake_generate_insight(data: list[dict]) -> str:
        calls["insight"] += 1
        return "- Trend: Revenue is product-led.\n- Anomaly: None is evident.\n- Recommendation: Monitor premium items."

    monkeypatch.setattr(main, "generate_sql", fake_generate_sql)
    monkeypatch.setattr(main, "generate_insight", fake_generate_insight)

    first = main.answer_question("Top products by revenue")
    second = main.answer_question("  top PRODUCTS   by revenue ")

    assert first == second
    assert calls == {"sql": 1, "insight": 1}


def test_app_errors_include_request_id(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(main.app)
    main.answer_cache.clear()

    monkeypatch.setattr(main, "generate_sql", lambda question: "DROP TABLE sales;")

    response = client.post("/ask", json={"question": "Delete everything"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["detail"] == "Unable to execute SQL query."
    assert payload["request_id"]
    assert response.headers["X-Request-ID"] == payload["request_id"]


def test_scrape_demo_ingests_products(monkeypatch: pytest.MonkeyPatch) -> None:
    client = TestClient(main.app)

    monkeypatch.setattr(
        "services.scraper_service.fetch_demo_products",
        lambda: [
            ScrapedProduct(name="Portfolio Product A", category="Scraped Demo", price=19.99),
            ScrapedProduct(name="Portfolio Product B", category="Scraped Demo", price=29.99),
        ],
    )

    response = client.post("/ingestion/scrape-demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] >= 0
    assert payload["total_found"] == 2
