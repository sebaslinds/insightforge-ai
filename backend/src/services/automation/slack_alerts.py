"""
Alertes automatiques — Étape 6.
Slack via webhook HTTP réel + Email via Resend API.
Seuil : churn_score > 0.7 → alerte HIGH
"""
import os
import httpx
from typing import Optional

# ── Config depuis env ─────────────────────────────────────────────────────────
SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
RESEND_API_KEY:    Optional[str] = os.getenv("RESEND_API_KEY")
ALERT_EMAIL_FROM:  str = os.getenv("ALERT_EMAIL_FROM", "alerts@insightforge.ai")
ALERT_EMAIL_TO:    str = os.getenv("ALERT_EMAIL_TO", "admin@insightforge.ai")

CHURN_ALERT_THRESHOLD: float = float(os.getenv("CHURN_ALERT_THRESHOLD", "0.7"))


# ── Slack ─────────────────────────────────────────────────────────────────────

async def send_slack_alert(message: str, priority: str = "medium") -> dict:
    """
    Envoie un message au webhook Slack configuré.
    Fallback console si SLACK_WEBHOOK_URL non défini.
    """
    emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(priority, "⚠️")
    block_text = f"{emoji} *InsightForge Alert* [{priority.upper()}]\n{message}"

    if not SLACK_WEBHOOK_URL:
        print(f"\n[SLACK MOCK] {block_text}\n")
        return {"status": "mock", "message": block_text}

    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": block_text},
            }
        ]
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(SLACK_WEBHOOK_URL, json=payload)
        resp.raise_for_status()

    return {"status": "sent", "slack_status": resp.status_code}


# ── Email (Resend) ────────────────────────────────────────────────────────────

async def send_email_alert(subject: str, body_html: str) -> dict:
    """
    Envoie un email via l'API Resend.
    Fallback console si RESEND_API_KEY non défini.
    """
    if not RESEND_API_KEY:
        print(f"\n[EMAIL MOCK]\nSubject: {subject}\n{body_html}\n")
        return {"status": "mock"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": ALERT_EMAIL_FROM,
                "to":   [ALERT_EMAIL_TO],
                "subject": subject,
                "html": body_html,
            },
        )
        resp.raise_for_status()

    return {"status": "sent", "resend_id": resp.json().get("id")}


# ── Alerte churn ──────────────────────────────────────────────────────────────

async def trigger_churn_alert(user_id: str, churn_score: float, segment: str) -> dict:
    """
    Déclenche une alerte Slack + Email si churn_score > seuil.
    Retourne un dict avec les résultats d'envoi.
    """
    if churn_score < CHURN_ALERT_THRESHOLD:
        return {"triggered": False}

    priority = "high" if churn_score >= 0.85 else "medium"
    slack_msg = (
        f"Utilisateur `{user_id}` — segment *{segment}*\n"
        f"Score de churn : *{churn_score:.0%}* (seuil : {CHURN_ALERT_THRESHOLD:.0%})\n"
        f"Action recommandée : déclencher une campagne de rétention immédiate."
    )
    email_html = f"""
    <h2>🚨 Alerte Churn — InsightForge</h2>
    <p><strong>User ID :</strong> {user_id}</p>
    <p><strong>Segment :</strong> {segment}</p>
    <p><strong>Churn Score :</strong> {churn_score:.0%}</p>
    <p><strong>Recommandation :</strong> Déclencher une campagne de rétention immédiate.</p>
    """

    slack_result = await send_slack_alert(slack_msg, priority=priority)
    email_result = await send_email_alert(
        subject=f"[InsightForge] Churn Alert — {user_id} ({churn_score:.0%})",
        body_html=email_html,
    )

    return {
        "triggered": True,
        "user_id": user_id,
        "churn_score": churn_score,
        "priority": priority,
        "slack": slack_result,
        "email": email_result,
    }
