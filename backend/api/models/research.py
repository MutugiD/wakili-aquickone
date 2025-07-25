from pydantic import BaseModel, Field
from typing import Optional, List

class ResearchQueryRequest(BaseModel):
    question: str
    context: Optional[str] = None

class ResearchResponse(BaseModel):
    answer: str
    sources: Optional[List[str]] = None
    query_id: Optional[str] = None