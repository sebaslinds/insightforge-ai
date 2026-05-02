from typing import List, Dict
from services.ai.ai_service import generate_insight
import asyncio

async def explain_decisions_async(decisions: List[Dict], data: List[Dict], language: str = "en") -> str:
    payload = {
        "decisions": decisions,
        "data": data[:20]
    }
    return await generate_insight(payload, language)

def explain_decisions(decisions: List[Dict], data: List[Dict], language: str = "en") -> str:
    """Wrapper synchrone pour compatibilité avec les endpoints non-async."""
    return asyncio.run(explain_decisions_async(decisions, data, language))
