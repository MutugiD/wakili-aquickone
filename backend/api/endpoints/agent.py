from fastapi import APIRouter, Request, Path
from backend.api.models.agent import AgentAskRequest, AgentWorkflowRequest, AgentChatRequest
from backend.api.services.agent_service import AgentService
from typing import Optional, Dict
import uuid

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/ask")
def agent_ask(request: AgentAskRequest):
    return AgentService.ask(request)

@router.post("/workflow")
def agent_workflow(request: AgentWorkflowRequest):
    return AgentService.workflow(request)

@router.post("/chat")
def create_chat():
    chat_id = str(uuid.uuid4())
    AgentService.create_session(chat_id)
    return {"chat_id": chat_id}

@router.post("/chat/{chat_id}")
def agent_chat(chat_id: str, request: AgentChatRequest):
    return AgentService.chat_with_id(chat_id, request)

@router.get("/chats")
def list_chats():
    return AgentService.list_chats()

@router.get("/chat/{chat_id}/history")
def get_chat_history(chat_id: str):
    return AgentService.get_chat_history(chat_id)