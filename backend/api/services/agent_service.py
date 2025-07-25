import logging
from uuid import uuid4
import os
import json
from json.decoder import JSONDecodeError
from typing import Dict, Any
from backend.api.models.agent import AgentAskRequest, AgentWorkflowRequest, AgentChatRequest
from backend.agent.intent_orchestrator import IntentOrchestrator
from langchain_core.messages import HumanMessage, AIMessage

# In-memory session store (for demo/testing; use Redis/db for production)
SESSION_MEMORY: Dict[str, IntentOrchestrator] = {}
CHATS_DIR = os.path.join(os.getcwd(), 'chats')
os.makedirs(CHATS_DIR, exist_ok=True)

def save_chat_history(chat_id: str, history: Any):
    # Convert LangChain messages to dicts
    serializable = []
    for m in history:
        if hasattr(m, 'type') and hasattr(m, 'content'):
            serializable.append({'type': m.type, 'content': m.content})
        else:
            serializable.append(m)
    with open(os.path.join(CHATS_DIR, f'{chat_id}.json'), 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

def load_chat_history(chat_id: str):
    path = os.path.join(CHATS_DIR, f'{chat_id}.json')
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert dicts back to LangChain messages
                messages = []
                for m in data:
                    if isinstance(m, dict) and 'type' in m and 'content' in m:
                        if m['type'] == 'human':
                            messages.append(HumanMessage(content=m['content']))
                        elif m['type'] == 'ai':
                            messages.append(AIMessage(content=m['content']))
                        else:
                            messages.append(m)
                    else:
                        messages.append(m)
                return messages
        except JSONDecodeError:
            logging.warning(f"Corrupted chat file skipped: {path}")
            return None
    return None

def list_chats():
    return [f[:-5] for f in os.listdir(CHATS_DIR) if f.endswith('.json')]

def load_all_chats():
    for chat_id in list_chats():
        history = load_chat_history(chat_id)
        if history:
            orchestrator = IntentOrchestrator()
            orchestrator.memory.chat_memory.messages = history
            SESSION_MEMORY[chat_id] = orchestrator

# Load all chats on server start
load_all_chats()

class AgentService:
    @staticmethod
    def ask(request: AgentAskRequest) -> Dict[str, Any]:
        orchestrator = IntentOrchestrator()
        result = orchestrator.handle_request(request.question)
        return {
            "response": result.get("response"),
            "memory": result.get("memory"),
            "tools_used": result.get("tools_used"),
            "detected_intent": result.get("detected_intent"),
        }

    @staticmethod
    def workflow(request: AgentWorkflowRequest) -> Dict[str, Any]:
        # TODO: Connect to orchestrator workflow
        return {"result": f"[Stub] Workflow executed with steps: {request.steps}"}

    @staticmethod
    def create_session(chat_id: str):
        if chat_id not in SESSION_MEMORY:
            SESSION_MEMORY[chat_id] = IntentOrchestrator()
            logging.info(f"[AgentService.create_session] Created new session: {chat_id}")

    @staticmethod
    def chat_with_id(chat_id: str, request: AgentChatRequest) -> Dict[str, Any]:
        logging.info(f"[AgentService.chat_with_id] chat_id: {chat_id}")
        orchestrator = SESSION_MEMORY.get(chat_id)
        if orchestrator is None:
            orchestrator = IntentOrchestrator()
            SESSION_MEMORY[chat_id] = orchestrator
        # Build input with context if provided
        if request.context:
            context_str = "\n".join(f"{k}: {v}" for k, v in request.context.items())
            agent_input = f"{request.message}\n{context_str}"
        else:
            agent_input = request.message
        result = orchestrator.handle_request(agent_input)
        # Persist chat history (use chat_memory.messages)
        save_chat_history(chat_id, orchestrator.memory.chat_memory.messages)
        return {
            "chat_id": chat_id,
            "response": result.get("response"),
            "memory": result.get("memory"),
            "tools_used": result.get("tools_used"),
            "detected_intent": result.get("detected_intent"),
        }

    @staticmethod
    def list_chats() -> Dict[str, Any]:
        return {"chats": list_chats()}

    @staticmethod
    def get_chat_history(chat_id: str) -> Dict[str, Any]:
        history = load_chat_history(chat_id)
        if history is None:
            return {"error": "Chat not found"}
        return {"chat_id": chat_id, "history": history}