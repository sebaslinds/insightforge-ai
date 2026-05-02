"""
AI Service : génère SQL (mock) et insights via OpenAI GPT-4o (réel).
"""
from core.config import get_settings

# ── SQL Generation (mock, sera remplacé par Text-to-SQL GPT) ──────────────────
def generate_sql(question: str) -> str:
    """Génère une requête SQL simplifiée à partir d'une question NL."""
    q = question.lower()
    if "churn" in q or "churned" in q:
        return "SELECT user_id, engagement_score, days_since_last_use FROM users WHERE churned = true LIMIT 20"
    if "segment" in q or "profil" in q:
        return "SELECT plan, COUNT(*) as count, AVG(engagement_score) as avg_score FROM users GROUP BY plan"
    if "event" in q or "événement" in q or "evenement" in q:
        return "SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type ORDER BY count DESC LIMIT 10"
    if "revenue" in q or "revenu" in q:
        return "SELECT plan, COUNT(*) as users, SUM(engagement_score) as total_score FROM users GROUP BY plan"
    return "SELECT user_id, plan, engagement_score, days_since_last_use FROM users ORDER BY engagement_score DESC LIMIT 20"


# ── GPT-4o Insight Generation ─────────────────────────────────────────────────
async def generate_insight(payload: dict, language: str = "en") -> str:
    """Génère une analyse IA via GPT-4o. Fallback mock si pas de clé API."""
    settings = get_settings()

    if not settings.OPENAI_API_KEY:
        # Fallback sans clé
        return (
            "Anomalie de revenu détectée. Les utilisateurs avec un score d'engagement < 30 "
            "présentent un risque de churn élevé."
            if language == "fr"
            else "Revenue anomaly detected. Users with engagement score < 30 show high churn risk."
        )

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        system_prompt = (
            "Tu es un analyste SaaS expert en rétention client et en ML. "
            "Analyse les données fournies et donne une réponse concise, chiffrée et actionnable en français. "
            "Formate ta réponse en 2-3 phrases maximum."
            if language == "fr"
            else
            "You are a SaaS analyst expert in customer retention and ML. "
            "Analyze the provided data and give a concise, quantified, and actionable response in English. "
            "Keep your response to 2-3 sentences maximum."
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": str(payload)},
            ],
            max_tokens=300,
            temperature=0.4,
        )
        return response.choices[0].message.content

    except Exception as e:
        return (
            f"Erreur IA : {str(e)[:80]}. Vérifiez votre clé OPENAI_API_KEY."
            if language == "fr"
            else f"AI Error: {str(e)[:80]}. Check your OPENAI_API_KEY."
        )
