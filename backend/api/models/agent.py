from pydantic import BaseModel, Field
from typing import Optional, Dict

class AgentAskRequest(BaseModel):
    question: str
    context: Optional[Dict[str, str]] = None

class AgentWorkflowRequest(BaseModel):
    steps: list
    context: Optional[Dict[str, str]] = None

class AgentChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, str]] = None
    session_id: Optional[str] = None  # Only used for legacy endpoints