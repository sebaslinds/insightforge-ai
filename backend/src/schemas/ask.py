from pydantic import BaseModel
from typing import Optional

class AskRequest(BaseModel):
    question: str
    language: Optional[str] = "en"
