# BI Copilot

Full-stack BI Copilot demo with FastAPI, Gemini, SQLAlchemy, PostgreSQL-ready data access, and a Vite/React dashboard with Recharts.

## Local Backend

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe scripts\seed_db.py
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

Set `GEMINI_API_KEY` before calling `POST /ask`.

## Local Frontend

```powershell
cd frontend
npm install
npm run dev
```

## API

`POST /ask`

```json
{
  "question": "Top products by revenue"
}
```

Response:

```json
{
  "sql": "SELECT product, price * quantity AS revenue FROM sales LIMIT 10;",
  "data": [],
  "insight": "Concise business insight.",
  "chart": {
    "type": "bar",
    "x": "product",
    "y": "revenue"
  }
}
```

`POST /ingestion/scrape-demo`

Scrapes an ethical demo e-commerce site, cleans product data, and inserts new rows into the `sales` table.

```json
{
  "source": "https://webscraper.io/test-sites/e-commerce/allinone",
  "inserted": 3,
  "skipped": 0,
  "total_found": 3
}
```

## Tests

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests -q
```
