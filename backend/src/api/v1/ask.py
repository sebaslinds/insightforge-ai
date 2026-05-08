from fastapi import APIRouter
from schemas.ask import AskRequest
from services.ai.ai_service import generate_sql, generate_insight
from services.query.query_service import run_query
from services.decision.engine import make_decisions
from services.automation.action_executor import execute_decisions
from services.ml.predictor import get_ml_metrics
import pandas as pd

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

    # 5. Data Summary pour l'IA (éviter de tronquer arbitrairement)
    df = pd.DataFrame(data)
    data_summary = ""
    if not df.empty:
        if len(df) > 50:
            # Si trop de données, on donne un résumé statistique par colonne
            data_summary = f"Total records: {len(df)}\n"
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    data_summary += f"- {col}: mean={df[col].mean():.2f}, min={df[col].min()}, max={df[col].max()}\n"
                    # Ajout d'une distribution par tranches de 10 pour les scores
                    if "score" in col.lower():
                        bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                        dist = pd.cut(df[col], bins=bins).value_counts().sort_index()
                        data_summary += f"  Distribution {col}: {dist.to_dict()}\n"
                else:
                    data_summary += f"- {col}: unique_values={df[col].nunique()}, top_values={df[col].value_counts().head(3).to_dict()}\n"
        else:
            data_summary = df.to_string()

    # 6. AI Explanation via GPT-4o (async)
    payload = {
        "question": req.question,
        "decisions": decisions,
        "data_summary": data_summary,
        "ml_metrics": get_ml_metrics(), # Importance des features
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
