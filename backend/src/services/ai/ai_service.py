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

        FEATURE_DEFS = {
            "session_count_7d": "Nombre de sessions sur les 7 derniers jours. Indique la fréquence d'usage.",
            "feature_breadth": "Nombre de fonctionnalités uniques utilisées. Indique la profondeur de l'adoption produit.",
            "avg_session_duration": "Durée moyenne des sessions en minutes.",
            "days_since_last_use": "Nombre de jours depuis la dernière activité. Indique la récence.",
            "engagement_score": "Score composite (0-100) calculé par notre moteur à partir de l'activité globale."
        }

        system_prompt = (
            "Tu es un analyste SaaS expert en rétention client et en ML. "
            "Analyse les données fournies et donne une réponse concise, chiffrée et actionnable en français. "
            "IMPORTANT: Utilise les chiffres du 'data_summary' (qui contient les totaux et distributions réels de la BD) pour tes calculs et tes tableaux. "
            "Ne te base pas sur un échantillon partiel. Si le résumé dit 'Total records: 6272', utilise ce chiffre.\n\n"
            f"Définitions des variables ML :\n{FEATURE_DEFS}\n\n"
            "L'importance des variables (feature_importance) est calculée par le modèle XGBoost via le gain d'information : "
            "plus une variable aide à réduire l'incertitude sur la prédiction du churn, plus son importance est élevée.\n\n"
            "Utilise le Markdown : tableaux pour les chiffres, listes à puces pour les points clés. "
            "Inclus impérativement un bloc JSON à la fin pour un graphique Recharts si pertinent :\n"
            "```json\n"
            "{\"type\": \"area\" | \"pie\" | \"bar\", \"items\": [{\"name\": \"label\", \"value\": 123}, ...]}\n"
            "```"
            if language == "fr"
            else
            "You are a SaaS analyst expert in customer retention and ML. "
            "Analyze the provided data and give a concise, quantified, and actionable response in English. "
            "IMPORTANT: Use the numbers from 'data_summary' (real DB totals and distributions) for your calculations. "
            "Do not use a partial sample. If the summary says 'Total records: 6272', use that figure.\n\n"
            f"ML Feature Definitions:\n{FEATURE_DEFS}\n\n"
            "Feature importance is calculated by the XGBoost model via information gain: "
            "the more a variable helps reduce uncertainty in churn prediction, the higher its importance.\n\n"
            "Use Markdown: tables for numbers, bullet points for key takeaways. "
            "Always include a JSON block at the end for a Recharts graph if relevant:\n"
            "```json\n"
            "{\"type\": \"area\" | \"pie\" | \"bar\", \"items\": [{\"name\": \"label\", \"value\": 123}, ...]}\n"
            "```"
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
