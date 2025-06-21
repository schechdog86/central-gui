"""
MCP Integration for Schechter Customs LLC AI Agent System
Integrates Model Context Protocol to enhance LLM and AI agents with external tool access
"""

__version__ = "1.0.0"
__author__ = "Schechter Customs LLC"

from .mcp_manager import MCPManager
from .agent_enhancer import AIAgentEnhancer
from .business_tools import BusinessToolsManager

__all__ = [
    "MCPManager",
    "AIAgentEnhancer", 
    "BusinessToolsManager"
]
