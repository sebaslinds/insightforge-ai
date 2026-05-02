from typing import List, Dict

def make_decisions(data: List[Dict], anomalies: List[float]) -> List[Dict]:
    decisions = []
    total_revenue = sum(d.get("revenue", 0) for d in data)
    
    # 🔴 Rule 1: anomalies
    if anomalies:
        decisions.append({
            "type": "alert",
            "priority": "high",
            "message": f"{len(anomalies)} anomalies detected",
            "confidence": 0.9
        })
        
    # 🟡 Rule 2: low revenue
    if total_revenue < 1000:
        decisions.append({
            "type": "recommendation",
            "priority": "medium",
            "message": "Revenue is low — investigate pricing",
            "confidence": 0.7
        })
        
    return decisions
