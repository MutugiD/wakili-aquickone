from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder, PromptTemplate
from backend.agent.legal_tools import get_legal_tools
from backend.agent.memory import AgentMemory
from backend.prompts.workflow_prompts import intent_detection_prompt_template
from backend.agent.drafting_agent import DraftingAgent
from typing import Dict, Any, List
import os
import json
import traceback

class IntentOrchestrator:
    """
    Intent-based orchestrator using LangChain's tool-calling for dynamic routing.
    Supports multi-agent hops and human-in-the-loop intervention.
    """
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4.1",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
            max_tokens=4000
        )

        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Get all legal tools including human intervention
        self.tools = get_legal_tools()

        # Initialize DraftingAgent
        self.drafting_agent = DraftingAgent()

        # Create custom prompt for better intent detection
        custom_prompt = """You are a Kenyan legal assistant that helps lawyers with document drafting, research, extraction, and case management.

IMPORTANT: First analyze the user's intent, then choose the appropriate tool.

INTENT ANALYSIS RULES:
- If the query asks for legal information, case law, statutes, or research → use research_kenyan_law
- If the query asks to extract, summarize, or analyze a document (PDF, DOCX, etc.) or mentions a file path → use extract_document
- If the query asks to draft/create a document → use appropriate drafting tool
- If the query asks to review/check a document → use review_legal_document
- If the query is complex or unclear → use escalate_to_human

Available tools:
- research_kenyan_law: For legal research, case law, statutes, precedents
- extract_document: For extracting structured data or summaries from a document. Usage: extract_document(file_path) or "extract from file: <path>"
- draft_demand_letter: For formal requests to other parties
- draft_plaint: For preparing lawsuits
- review_legal_document: For document compliance review
- escalate_to_human: For complex cases requiring human judgment

Example: To extract all parties from a PDF, say "extract from file: /path/to/file.pdf" or "summarize document: /path/to/file.pdf"

{chat_history}
Human: {input}
{agent_scratchpad}"""

        # Initialize the agent with custom prompt
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            agent_kwargs={"prefix": custom_prompt}
        )

    def _detect_intent(self, user_query: str) -> Dict[str, str]:
        """
        Detect the intent of the user query before tool selection.
        """
        intent_prompt = intent_detection_prompt_template.format(
            intents="research, draft, review, extract, escalate",
            user_query=user_query
        )

        try:
            response = self.llm.invoke(intent_prompt)
            query_lower = user_query.lower()
            # Improved intent detection logic
            if any(word in query_lower for word in ["extract", "summarize", "analyze", "parse", "read"]) and any(word in query_lower for word in ["document", "pdf", "docx", "file"]):
                return {"next_action": "extract_document", "tool_to_use": "extract_document", "reasoning": "Extraction request detected"}
            if any(word in query_lower for word in ["draft", "create", "write", "prepare", "generate"]) and any(word in query_lower for word in ["letter", "document", "plaint", "brief", "affidavit"]):
                # Determine document type
                for doc_type in ["demand_letter", "plaint", "brief", "affidavit"]:
                    if doc_type.replace('_', ' ') in query_lower or doc_type in query_lower:
                        return {"next_action": "draft_document", "tool_to_use": doc_type, "reasoning": f"Drafting request detected for {doc_type}"}
                return {"next_action": "draft_document", "tool_to_use": "demand_letter", "reasoning": "Drafting request detected (default to demand_letter)"}
            elif any(word in query_lower for word in ["research", "find", "search", "case law", "statute", "precedent", "legal information"]):
                return {"next_action": "research_kenyan_law", "tool_to_use": "research_kenyan_law", "reasoning": "Research query detected"}
            elif any(word in query_lower for word in ["review", "check", "examine", "verify", "compliance"]):
                return {"next_action": "review_legal_document", "tool_to_use": "review_legal_document", "reasoning": "Review request detected"}
            elif any(word in query_lower for word in ["complex", "unclear", "multiple parties", "fraud", "complicated"]):
                return {"next_action": "escalate_to_human", "tool_to_use": "escalate_to_human", "reasoning": "Complex or unclear request"}
            else:
                return {"next_action": "escalate_to_human", "tool_to_use": "escalate_to_human", "reasoning": "Unclear intent - escalating to human"}
        except Exception as e:
            return {"next_action": "escalate_to_human", "tool_to_use": "escalate_to_human", "reasoning": f"Intent detection error: {str(e)}"}

    def _execute_tool_directly(self, tool_name: str, query: str, context: Dict[str, Any] = None) -> str:
        """
        Execute a tool directly based on intent detection, including DraftingAgent for drafting tasks.
        """
        # Drafting agent integration
        if tool_name in ["demand_letter", "plaint", "brief", "affidavit"]:
            # Use context if provided, else just pass query as facts
            doc_context = context or {"facts": query}
            return self.drafting_agent.draft_document(tool_name, doc_context)
        # Fallback to legacy tools
        tool_map = {tool.name: tool for tool in self.tools}
        if tool_name in tool_map:
            try:
                result = tool_map[tool_name].invoke(query)
                return str(result)
            except Exception as e:
                return f"Error executing {tool_name}: {str(e)}"
        else:
            return f"Tool {tool_name} not found"

    def handle_request(self, user_query: str, context: Dict = None) -> Dict[str, Any]:
        """
        Handle user request using dynamic tool-calling based on intent.

        Args:
            user_query: The user's request
            context: Additional context (optional, e.g., facts, research, user input)

        Returns:
            Dict containing the response and any additional information
        """
        try:
            if context:
                context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
                agent_input = f"{user_query}\n{context_str}"
            else:
                agent_input = user_query
            # Use the agent to process the input, ensuring memory is updated
            response = self.agent.run({"input": agent_input})
            return {
                "success": True,
                "response": response,
                "memory": self.memory.load_memory_variables({}),
                "tools_used": [],
                "detected_intent": "[see agent output]"
            }
        except Exception as e:
            print("[AGENT ERROR]", str(e))
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "memory": self.memory.load_memory_variables({})
            }

    def _extract_tools_used(self, response: str) -> List[str]:
        tools_used = []
        tool_names = ["draft_demand_letter", "draft_plaint", "review_legal_document",
                     "research_kenyan_law", "escalate_to_human", "human_tool"]
        for tool_name in tool_names:
            if tool_name in response.lower():
                tools_used.append(tool_name)
        return tools_used

    def get_memory(self) -> Dict[str, Any]:
        return self.memory.load_memory_variables({})

    def clear_memory(self):
        self.memory.clear()