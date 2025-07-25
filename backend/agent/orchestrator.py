from typing import Dict, Any, List
import os
import openai
import json
from backend.agent.research_agent.research_agent import ResearchAgent
from backend.agent.memory import AgentMemory
from backend.agent.tooling import ToolRegistry
from langchain_openai import ChatOpenAI
from backend.prompts.workflow_prompts import intent_detection_prompt_template

class TaskInterpreter:
    """
    Task Interpreter for forward-looking action determination using LLM prompt/classifier.
    Determines what tool/action to take next based on user query and context.
    """
    def __init__(self, actions: List[str] = None):
        self.actions = actions or [
            "search_kenyan_law",
            "extract_case_details",
            "crawl_legal_site",
            "draft_demand_letter",
            "draft_plaint",
            "draft_brief",
            "review_evidence",
            "escalate_case",
            "other"
        ]
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def render_intent_detection_prompt(self, user_query: str) -> str:
        actions_str = "\n- ".join(["" if not self.actions else ""] + self.actions)
        return intent_detection_prompt_template.format(
            intents=actions_str,
            user_query=user_query
        )

    def detect_intent(self, user_query: str) -> Dict[str, Any]:
        prompt = self.render_intent_detection_prompt(user_query)
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "system", "content": prompt}],
                temperature=0,
                max_tokens=4000
            )
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            json_str = content[start:end]
            result = json.loads(json_str)
            return result
        except Exception as e:
            return {"next_action": "other", "tool_to_use": None, "reasoning": f"LLM error: {e}"}

class Orchestrator:
    """
    Orchestrator for routing requests to the correct agent based on detected next action.
    Supports multi-stage workflows (e.g., search then extract). Passes memory/context between agents.
    """
    def __init__(self):
        # Shared memory and tool registry for all agents
        self.llm = ChatOpenAI(model="gpt-4.1", api_key=os.getenv("OPENAI_API_KEY"), temperature=0, max_tokens=4000)
        self.memory = AgentMemory(memory_type="buffer")
        self.tools = ToolRegistry()
        self.task_interpreter = TaskInterpreter()
        self.research_agent = ResearchAgent(memory=self.memory, tool_registry=self.tools)
        # TODO: Add other agents as they are implemented

    def handle(self, user_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        action_result = self.task_interpreter.detect_intent(user_query)
        next_action = action_result.get("next_action")
        tool_to_use = action_result.get("tool_to_use")

        # Route based on next action and tool
        if next_action == "search_kenyan_law" and tool_to_use == "search":
            research_result = self.research_agent.handle_request({"type": "search", "query": user_query}, context=context)
            return {"action": next_action, "tool_used": tool_to_use, "result": research_result}

        elif next_action == "extract_case_details" and tool_to_use == "extract":
            # Extract from specific URLs found in previous search
            # TODO: Implement URL extraction from memory
            research_result = self.research_agent.handle_request({"type": "extract", "url": "placeholder_url"}, context=context)
            return {"action": next_action, "tool_used": tool_to_use, "result": research_result}

        elif next_action == "crawl_legal_site" and tool_to_use == "crawl":
            research_result = self.research_agent.handle_request({"type": "crawl", "base_url": "kenyalaw.org"}, context=context)
            return {"action": next_action, "tool_used": tool_to_use, "result": research_result}

        # TODO: Add routing for 'draft_demand_letter', 'draft_plaint', etc.
        return {"error": f"No action available for: {next_action}", "reasoning": action_result.get("reasoning")}