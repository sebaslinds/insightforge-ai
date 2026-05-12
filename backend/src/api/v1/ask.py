from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.ask import AskRequest
from core.security import get_current_user
from core.tenant_models import AdminUser, Tenant
from services.ai.ai_service import generate_sql, generate_insight
from services.query.query_service import run_query
from services.decision.engine import make_decisions
from services.automation.action_executor import execute_decisions
from services.ml.predictor import get_ml_metrics
import pandas as pd

router = APIRouter()

@router.post("/")
async def ask(req: AskRequest, current_user: AdminUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. SQL generation via GPT-4o (Text-to-SQL)
    sql = await generate_sql(req.question)

    # 2. Data query depuis PostgreSQL avec filtrage tenant
    data = run_query(sql, {"tenant_id": current_user.tenant_id})

    # 3. Anomaly detection simple
    anomalies = [1000] if any(d.get("revenue_usd", 0) > 500 for d in data) else []

    # 4. Decision Engine
    decisions = make_decisions(data, anomalies)

    # 5. Data Summary
    df = pd.DataFrame(data)
    data_summary = ""
    if not df.empty:
        df = df.fillna("non_catégorisé")
        if len(df) > 50:
            data_summary = f"Total records: {len(df)}\n"
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    data_summary += f"- {col}: mean={df[col].mean():.2f}, min={df[col].min()}, max={df[col].max()}\n"
                else:
                    data_summary += f"- {col}: unique_values={df[col].nunique()}\n"
        else:
            data_summary = df.to_string()

    # 6. AI Explanation
    payload = {
        "question": req.question,
        "decisions": decisions,
        "data_summary": data_summary,
        "ml_metrics": get_ml_metrics(),
        "sql": sql,
    }
    explanation = await generate_insight(payload, req.language)

    # 7. Auto Execution
    execution_results = execute_decisions(decisions)

    # 8. Follow-ups
    if req.language == "fr":
        follow_ups = ["Détails par segment ?", "Facteurs d'attrition ?", "Anomalies récentes ?", "Risque churn élevé ?"]
    else:
        follow_ups = ["Segment details?", "Churn drivers?", "Recent anomalies?", "High churn risk?"]

    # 9. Calcul Empreinte Carbone
    row_count = len(data)
    current_carbon = 0.2 + (row_count / 1000 * 0.05)
    
    # Mise à jour de l'accumulé pour le Tenant
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if tenant:
        current_total = float(tenant.total_carbon_footprint or 0.0)
        tenant.total_carbon_footprint = current_total + current_carbon
        db.commit()
        total_carbon = tenant.total_carbon_footprint
    else:
        total_carbon = current_carbon

    return {
        "sql": sql,
        "data": data,
        "decisions": decisions,
        "explanation": explanation,
        "execution_results": execution_results,
        "follow_ups": follow_ups,
        "carbon_footprint": current_carbon,
        "total_carbon_footprint": total_carbon
    }
