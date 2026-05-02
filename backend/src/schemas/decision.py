from pydantic import BaseModel
from typing import List, Dict, Any

class DecisionRequest(BaseModel):
    data: List[Dict[str, Any]]
    anomalies: List[float]
