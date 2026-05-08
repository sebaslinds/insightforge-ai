"""
AI Service : génère SQL (mock) et insights via OpenAI GPT-4o (réel).
"""
from core.config import get_settings

# ── SQL Generation (mock, sera remplacé par Text-to-SQL GPT) ──────────────────
def generate_sql(question: str) -> str:
    """Génère une requête SQL simplifiée à partir d'une question NL."""
    q = question.lower()
    if "plan" in q or "répartition" in q or "distribution" in q or "conversion" in q or "taux" in q:
        return "SELECT plan, COUNT(*) as users FROM users GROUP BY plan ORDER BY users DESC"
    if "user" in q or "utilisateur" in q or "combien" in q:
        return "SELECT plan, segment, COUNT(*) as count FROM users GROUP BY plan, segment"
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
            "Utilise le Markdown pour rendre tes réponses plus graphiques : utilise des tableaux pour les chiffres, "
            "des listes à puces pour les points clés et des émojis pour illustrer tes propos. "
            "Si les données s'y prêtent (ex: répartition par segment, tendance de revenus), inclus impérativement un bloc JSON à la fin de ta réponse pour générer un graphique Recharts avec ce format exact : "
            "```json\n"
            "{\"type\": \"area\" | \"pie\" | \"bar\", \"items\": [{\"name\": \"label\", \"value\": 123}, ...]}\n"
            "```\n"
            "Sois visuel, moderne et précis."
            if language == "fr"
            else
            "You are a SaaS analyst expert in customer retention and ML. "
            "Analyze the provided data and give a concise, quantified, and actionable response in English. "
            "Use Markdown to make your responses more graphical: use tables for numbers, "
            "bullet points for key takeaways, and emojis to illustrate your points. "
            "If the data allows (e.g. segment breakdown, revenue trend), always include a JSON block at the end of your response to generate a Recharts graph with this exact format: "
            "```json\n"
            "{\"type\": \"area\" | \"pie\" | \"bar\", \"items\": [{\"name\": \"label\", \"value\": 123}, ...]}\n"
            "```\n"
            "Be visual, modern and precise."
        )

        user_content = str(payload)
        if isinstance(payload, dict) and "prompt_override" in payload:
            user_content = payload["prompt_override"]

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
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
