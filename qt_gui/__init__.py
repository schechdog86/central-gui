"""
Modern Qt6 GUI for Schechter Customs LLC Centralized AI Platform
===============================================================

A professional, modular Qt6 interface for managing multiple AI tools:
- Coding Agent with memory and skills system
- Anonymous Browser for business intelligence
- Web Scraper for data collection
- Workspace Tracker for project management
- Ollama LLM integration
- MCP (Model Context Protocol) servers
- Code Analysis tools
- Ray Cluster management

Architecture:
- MVVM pattern with Qt's ModelView system
- Plugin-based design for extensibility
- Modern UI with dark/light theming
- Asynchronous operations for responsiveness
- Comprehensive error handling and logging
"""

__version__ = "1.0.0"
__author__ = "Schechter Customs LLC"

# Import main components
from .main_application import SchechterAIApplication
from .views.main_window import MainWindow

__all__ = [
    'SchechterAIApplication',
    'MainWindow'
]
