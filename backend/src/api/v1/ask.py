from fastapi import APIRouter
from schemas.ask import AskRequest
from services.ai.ai_service import generate_sql, generate_insight
from services.query.query_service import run_query
from services.decision.engine import make_decisions
from services.automation.action_executor import execute_decisions

router = APIRouter()

@router.post("/")
async def ask(req: AskRequest):
    # 1. SQL generation (keyword-based)
    sql = generate_sql(req.question)

    # 2. Data query depuis PostgreSQL
    data = run_query(sql)

    # 3. Anomaly detection simple
    anomalies = [1000] if any(d.get("revenue", 0) > 500 for d in data) else []

    # 4. Decision Engine
    decisions = make_decisions(data, anomalies)

    # 5. AI Explanation via GPT-4o (async)
    payload = {
        "question": req.question,
        "decisions": decisions,
        "data": data[:20],
        "sql": sql,
    }
    explanation = await generate_insight(payload, req.language)

    # 6. Auto Execution
    execution_results = execute_decisions(decisions)

    # 7. Follow-ups contextuels
    if req.language == "fr":
        follow_ups = [
            "Pouvez-vous détailler les revenus par segment ?",
            "Quels sont les principaux facteurs d'attrition ?",
            "Montrez-moi les anomalies récentes en détail.",
            "Quels utilisateurs sont à risque élevé de churn ?",
        ]
    else:
        follow_ups = [
            "Can you break down revenue by segment?",
            "What are the main drivers of churn?",
            "Show me recent anomalies in detail.",
            "Which users are at high churn risk?",
        ]

    return {
        "sql": sql,
        "data": data,
        "decisions": decisions,
        "explanation": explanation,
        "execution_results": execution_results,
        "follow_ups": follow_ups,
    }
