"""
Wakili Quick1 Agent Package

AI agents for legal automation including research, drafting, and analysis.
"""

__version__ = "1.0.0"

# Package-level imports
from .drafting_agent import DraftingAgent
from .research_agent.research_agent import ResearchAgent
from .intent_orchestrator import IntentOrchestrator

__all__ = [
    'DraftingAgent',
    'ResearchAgent',
    'IntentOrchestrator',
]