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
    if "cohort" in q or "cohorte" in q or "semaine" in q or "week" in q:
        return "SELECT plan, segment, COUNT(*) as user_count FROM users GROUP BY plan, segment"
    if "user" in q or "utilisateur" in q or "combien" in q:
        return "SELECT plan, segment, COUNT(*) as user_count, AVG(engagement_score) as avg_engagement FROM users GROUP BY plan, segment"
    if "churn" in q or "churned" in q:
        return "SELECT plan, segment, COUNT(*) as churned_users, AVG(engagement_score) as avg_score_at_churn FROM users WHERE churned = true GROUP BY plan, segment"
    if "segment" in q or "profil" in q:
        return "SELECT segment, COUNT(*) as count, AVG(engagement_score) as avg_score, AVG(days_since_last_use) as avg_recency FROM users GROUP BY segment"
    if "event" in q or "événement" in q or "evenement" in q:
        return "SELECT event_type, COUNT(*) as total_events, COUNT(DISTINCT user_id) as unique_users FROM events GROUP BY event_type ORDER BY total_events DESC LIMIT 10"
    if "revenue" in q or "revenu" in q:
        return "SELECT plan, COUNT(*) as users, SUM(CASE WHEN plan = 'Enterprise' THEN 499 WHEN plan = 'Pro' THEN 49 ELSE 0 END) as revenue_usd FROM users GROUP BY plan"
    return "SELECT user_id, plan, segment, engagement_score, days_since_last_use FROM users ORDER BY engagement_score DESC LIMIT 50"


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
            "Tu es un analyste SaaS expert en stratégie de revenus et rétention. "
            "Analyse les données fournies et donne une réponse concise, chiffrée et ultra-visuelle en français. "
            "IMPORTANT: \n"
            "1. Utilise TOUJOURS les chiffres du 'data_summary' (6000+ users). Sois précis.\n"
            "2. Inclus SYSTEMATIQUEMENT un graphique Recharts via un bloc JSON si les données s'y prêtent.\n"
            "   - 'pie' pour la répartition par plan ou segment.\n"
            "   - 'bar' pour comparer des moyennes ou des comptes.\n"
            "   - 'area' pour les séries temporelles ou distributions.\n"
            "3. Assure la COHERENCE : si on te pose une question sur une cohorte spécifique (ex: W18), utilise les chiffres du 'data_summary' pour estimer la répartition proportionnellement à la taille de la cohorte indiquée dans la question.\n"
            "4. Ne confonds jamais les POURCENTAGES et les COMPTES ABSOLUS (ex: 19% de 100 users = 19 users, pas 19% users).\n"
            "5. CONCISION & FINITION : Sois bref (max 150 mots). Termine TOUJOURS tes phrases. Ne laisse jamais un point suspendu.\n"
            "6. Explique l'impact business court (ex: pourquoi le churn est élevé).\n\n"
            f"Définitions des variables ML :\n{FEATURE_DEFS}\n\n"
            "Format JSON obligatoire pour les graphiques :\n"
            "```json\n"
            "{\"type\": \"area\" | \"pie\" | \"bar\", \"items\": [{\"name\": \"label\", \"value\": 123}, ...]}\n"
            "```"
            if language == "fr"
            else
            "You are a SaaS analyst expert in revenue strategy and retention. "
            "Analyze the provided data and give a concise, quantified, and ultra-visual response in English. "
            "IMPORTANT: \n"
            "1. ALWAYS use the figures from 'data_summary' (6000+ users). Be precise.\n"
            "2. SYSTEMATICALLY include a Recharts graph via a JSON block if the data allows.\n"
            "3. Ensure CONSISTENCY: if asked about a specific cohort (e.g., W18), use the 'data_summary' figures to estimate the breakdown proportionally to the cohort size mentioned in the question.\n"
            "4. Never confuse PERCENTAGES and ABSOLUTE COUNTS (e.g., 19% of 100 users = 19 users, not 19% users).\n"
            "5. CONCISENESS & COMPLETION: Be brief (max 150 words). ALWAYS complete your sentences. Never leave a point hanging.\n"
            "6. Explain short business impact (e.g., why churn is high).\n\n"
            f"ML Feature Definitions:\n{FEATURE_DEFS}\n\n"
            "Mandatory JSON format for charts:\n"
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
            max_tokens=800,
            temperature=0.4,
        )
        return response.choices[0].message.content

    except Exception as e:
        return (
            f"Erreur IA : {str(e)[:80]}. Vérifiez votre clé OPENAI_API_KEY."
            if language == "fr"
            else f"AI Error: {str(e)[:80]}. Check your OPENAI_API_KEY."
        )
