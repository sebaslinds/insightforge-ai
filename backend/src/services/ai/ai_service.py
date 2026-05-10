"""
AI Service : génère SQL (mock) et insights via OpenAI GPT-4o (réel).
"""
from core.config import get_settings

# ── SQL Generation (mock, sera remplacé par Text-to-SQL GPT) ──────────────────
async def generate_sql(question: str) -> str:
    """Génère une requête SQL précise via GPT-4o (Text-to-SQL)."""
    settings = get_settings()
    if not settings.OPENAI_API_KEY:
        return _generate_sql_mock(question)

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.strip())

        schema = """
        Table 'users': user_id, tenant_id, signup_date, plan ('free', 'pro', 'enterprise'), segment ('power_user', 'casual', 'at_risk', 'dormant'), session_count_30d, session_count_7d, avg_session_duration_min, feature_breadth, days_since_last_use, engagement_score, churn_score, churned (boolean).
        Table 'events': user_id, tenant_id, event_type ('page_view', 'feature_use', 'session_start'), feature, timestamp.
        """

        prompt = (
            f"Tu es un expert SQL pour PostgreSQL. Traduis la question SaaS suivante en SQL précis.\n"
            f"Schéma :\n{schema}\n\n"
            "RÈGLES CRITIQUES :\n"
            "1. Utilise TOUJOURS 'WHERE tenant_id = :tenant_id' pour isoler les données.\n"
            "2. Pour le REVENU : SUM(CASE WHEN LOWER(plan) = 'enterprise' THEN 499 WHEN LOWER(plan) = 'pro' THEN 49 ELSE 0 END) as revenue_usd.\n"
            "3. SEGMENTS : Si un segment est NULL, ignore-le dans les répartitions (`WHERE segment IS NOT NULL`) ou utilise `COALESCE(segment, 'non_catégorisé')`.\n"
            "4. Privilégie les AGRÉGATIONS (COUNT, AVG, SUM) pour répondre à des questions globales.\n"
            "5. Retourne UNIQUEMENT le code SQL brut. Pas de markdown, pas d'explications.\n"
            "6. Si la question est vague, fais un résumé : plan, segment, COUNT(*) as user_count, AVG(engagement_score) as avg_score.\n"
            "7. Ne dépasse pas 100 lignes de résultat (LIMIT 100).\n"
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question},
            ],
            temperature=0,
        )
        sql = response.choices[0].message.content.strip()
        # Nettoyage si Markdown présent
        if "```sql" in sql:
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql:
            sql = sql.split("```")[1].strip()
        return sql

    except Exception as e:
        print(f"[AI Service] SQL Gen Error: {e}")
        return _generate_sql_mock(question)


def _generate_sql_mock(question: str) -> str:
    """Fallback si GPT échoue ou pas de clé API."""
    q = question.lower()
    t_filter = "WHERE tenant_id = :tenant_id"
    if "revenue" in q or "revenu" in q:
        return f"SELECT plan, COUNT(*) as users, SUM(CASE WHEN LOWER(plan) = 'enterprise' THEN 499 WHEN LOWER(plan) = 'pro' THEN 49 ELSE 0 END) as revenue_usd FROM users {t_filter} GROUP BY plan"
    if "plan" in q or "distribution" in q:
        return f"SELECT plan, COUNT(*) as count FROM users {t_filter} GROUP BY plan"
    return f"SELECT plan, segment, COUNT(*) as user_count, AVG(engagement_score) as avg_score FROM users {t_filter} GROUP BY plan, segment"


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
        api_key = settings.OPENAI_API_KEY.strip()
        client = AsyncOpenAI(api_key=api_key)

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
            "   - 'pie' pour la répartition (ex: par plan ou segment). AGREGÈ TOUJOURS les données par catégorie.\n"
            "   - 'bar' pour comparer des moyennes ou des comptes.\n"
            "   - 'area' pour les séries temporelles ou distributions.\n"
            "   - IMPORTANT : Ne dépasse JAMAIS 6 segments dans un 'pie'. Si plus de 6 catégories existent, garde les 5 plus importantes et regroupe le reste sous 'Autres'.\n"
            "3. Assure la COHERENCE : si on te pose une question sur une cohorte spécifique (ex: W18), utilise les chiffres du 'data_summary' pour estimer la répartition proportionnellement à la taille de la cohorte indiquée dans la question.\n"
            "4. Ne confonds jamais les POURCENTAGES et les COMPTES ABSOLUS (ex: 19% de 100 users = 19 users, pas 19% users).\n"
            "5. CONCISION & FINITION : Sois bref (max 150 mots). Termine TOUJOURS tes phrases. Ne laisse jamais un point suspendu.\n"
            "6. Explique l'impact business court (ex: pourquoi le churn est élevé).\n\n"
            f"Définitions des variables ML :\n{FEATURE_DEFS}\n\n"
            "Format JSON obligatoire pour les graphiques (les valeurs doivent être agrégées/sommées) :\n"
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

        if not api_key:
            return "Erreur : La clé OPENAI_API_KEY est vide ou non configurée." if language == "fr" else "Error: OPENAI_API_KEY is empty or not configured."

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
