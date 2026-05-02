from fastapi import APIRouter
from schemas.decision import DecisionRequest
from services.decision.engine import make_decisions
from services.decision.explainer import explain_decisions
from services.automation.action_executor import execute_decisions

router = APIRouter()

@router.post("/")
def decision(req: DecisionRequest):
    decisions = make_decisions(req.data, req.anomalies)
    explanation = explain_decisions(decisions, req.data)
    
    # 🔥 AUTO-EXECUTION (Event-driven)
    execution_results = execute_decisions(decisions)
    
    return {
        "decisions": decisions,
        "explanation": explanation,
        "execution_results": execution_results
    }
