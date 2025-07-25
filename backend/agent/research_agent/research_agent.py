from typing import Any, Dict, List, Optional
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_tavily import TavilySearch, TavilyExtract, TavilyCrawl
from backend.prompts.agent_prompts import research_system_prompt, research_user_prompt
from backend.agent.memory import AgentMemory
from backend.agent.tooling import ToolRegistry

class ResearchAgent:
    """
    Modular Research Agent for legal research tasks (case law, statutes, etc.).
    Integrates with Tavily/LangChain for search, extract, and crawl.
    Designed for orchestrator compatibility.
    """
    def __init__(self, memory: AgentMemory, tool_registry: ToolRegistry, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        load_dotenv()
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        # LangChain Tavily tools
        self.search_tool = TavilySearch(max_results=5, include_domains=["kenyalaw.org"], topic="general")
        self.extract_tool = TavilyExtract(extract_depth="advanced")
        self.crawl_tool = TavilyCrawl()
        self.system_prompt = research_system_prompt
        self.user_prompt = research_user_prompt
        self.memory = memory
        self.tools = tool_registry
        # Register tools
        self.tools.register("search", self._search)
        self.tools.register("extract", self._extract)
        self.tools.register("crawl", self._crawl)

    def build_prompt(self, user_query: str) -> str:
        """
        Build a complete prompt using the organized prompt structure.
        """
        return f"{self.system_prompt}\n\n{self.user_prompt.format(user_query=user_query)}"

    def _search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute legal research search using Tavily.
        """
        try:
            return self.search_tool.invoke({"query": query, **kwargs})
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}", "url": "", "title": "Error", "content": ""}]

    def _extract(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from specific legal web pages.
        """
        try:
            return self.extract_tool.invoke({"urls": [url], **kwargs})
        except Exception as e:
            return {"error": f"Extraction failed: {str(e)}", "content": ""}

    def _crawl(self, base_url: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Crawl legal websites for comprehensive content gathering.
        """
        try:
            return self.crawl_tool.invoke({"base_url": base_url, **kwargs})
        except Exception as e:
            return [{"error": f"Crawl failed: {str(e)}", "url": base_url, "content": ""}]

    def handle_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle research requests with improved error handling and context management.
        """
        req_type = request.get('type')
        user_query = request.get('query', '')

        if req_type in self.tools.tools:
            try:
                result = self.tools.call(req_type, **request)
                # Add to memory: user query as input, result as output
                self.memory.add_message(user_query, str(result))
                return {"result": result, "memory": self.memory.get_history()}
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                self.memory.add_message(user_query, error_msg)
                return {"error": error_msg, "memory": self.memory.get_history()}

        # Handle unknown request type
        error_msg = f"Unknown request type: {req_type}"
        self.memory.add_message(user_query, error_msg)
        return {"error": error_msg, "memory": self.memory.get_history()}

    def get_research_summary(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a verbose, step-by-step research summary with contextual citations and links for legal professionals.
        """
        if not results:
            return "No research results found."

        summary = "# Legal Research Process\n\n"
        for i, result in enumerate(results[:5], 1):  # Limit to top 5 results
            if "error" in result:
                continue
            title = result.get('title', 'Untitled')
            url = result.get('url', 'No URL')
            content = result.get('content', 'No content')
            summary += f"**Step {i}:** {title}\n\n"
            summary += f"- **Source:** [{url}]({url})\n"
            summary += f"- **Context:** {content[:600]}...\n\n"  # Show a large chunk of content for legal review
        summary += "\n---\n"
        summary += "**All sources are cited inline above. For full details, visit the provided links.**\n"
        return summary