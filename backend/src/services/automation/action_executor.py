from services.automation.slack_alerts import send_slack_alert
from typing import List, Dict

async def execute_decisions(decisions: List[Dict]):
    """Execute automated actions based on decisions"""
    results = []
    
    for decision in decisions:
        action_type = decision.get("type")
        priority = decision.get("priority", "medium")
        message = decision.get("message", "No message provided")
        
        if action_type == "alert":
            # Action: Send Slack Alert
            success_data = await send_slack_alert(message, priority)
            status = "sent" if success_data.get("status") == "sent" else "failed"
            results.append({"action": "slack_alert", "status": status})
            
        elif action_type == "recommendation":
            # Action: Log recommendation for review
            print(f"[ACTION] Recommendation logged for review: {message}")
            results.append({"action": "log_recommendation", "status": "logged"})
            
    return results
