"""
Wakili Quick1 Backend Package

A comprehensive legal automation system for Kenyan legal professionals.
"""

__version__ = "1.0.0"
__author__ = "Wakili Team"
__description__ = "AI-powered legal automation platform for Kenyan legal professionals"

# Package-level imports for convenience
from .agent.drafting_agent import DraftingAgent
from .agent.research_agent.research_agent import ResearchAgent

__all__ = [
    'DraftingAgent',
    'ResearchAgent',
]