"""
Component Manager for Qt6 GUI
=============================

Manages all AI platform components and their lifecycle.
"""

import logging
from typing import Dict, Optional, Any

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer

from ...utils.config_manager import ConfigManager


class ComponentManager(QObject):
    """
    Manages the lifecycle and communication between AI platform components.

    Features:
    - Component discovery and loading
    - Lifecycle management (start/stop/restart)
    - Health monitoring
    - Inter-component communication
    - Error handling and recovery
    """

    # Signals
    componentRegistered = pyqtSignal(str, dict)  # component_id, metadata
    componentStarted = pyqtSignal(str)  # component_id
    componentStopped = pyqtSignal(str)  # component_id
    componentStatusChanged = pyqtSignal(str, str)  # component_id, status
    componentError = pyqtSignal(str, str)  # component_id, error_msg
    healthStatusChanged = pyqtSignal(str, bool)  # component_id, is_healthy

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.logger = logging.getLogger("SchechterAI.ComponentManager")

        # Component registry
        self.components: Dict[str, Dict[str, Any]] = {}
        self.component_instances: Dict[str, Any] = {}
        self.component_threads: Dict[str, QThread] = {}

        # Health monitoring
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self._check_component_health)

        # Initialize default components
        self._register_default_components()

        # Component configuration loaded dynamically
        self.component_views: Dict[str, QWidget] = {}
        self.component_widgets: Dict[str, QWidget] = {}

        self.logger.info("ComponentManager initialized")

    def _register_default_components(self):
        """Register the default AI platform components."""

        default_components = [
            {
                'id': 'coding_agent',
                'name': 'Coding Agent',
                'description': 'AI coding assistant with memory and skills',
                'icon': '🤖',
                'category': 'AI Agents',
                'path': '/home/ed/codebase/centralized-ai-ui/coding-agent',
                'main_module': 'main.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'anonymous_browser',
                'name': 'Anonymous Browser',
                'description': 'Docker-based anonymous browsing system',
                'icon': '🌐',
                'category': 'Web Tools',
                'path': (
                    '/home/ed/codebase/centralized-ai-ui/anonymous_browser'
                ),
                'main_module': 'launcher.py',
                'requires_docker': True,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'web_scraper',
                'name': 'Web Scraper',
                'description': 'Advanced web scraping and data extraction',
                'icon': '🕷️',
                'category': 'Web Tools',
                'path': '/home/ed/codebase/centralized-ai-ui/src/web_scraper',
                'main_module': 'scraper_manager.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'workspace_tracker',
                'name': 'Workspace Tracker',
                'description': 'Project management and workspace tracking',
                'icon': '📁',
                'category': 'Productivity',
                'path': (
                    '/home/ed/codebase/centralized-ai-ui/workspace-tracker'
                ),
                'main_module': 'main.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'mcp_integration',
                'name': 'MCP Integration',
                'description': 'Model Context Protocol integration',
                'icon': '🔌',
                'category': 'AI Infrastructure',
                'path': '/home/ed/codebase/centralized-ai-ui/mcp',
                'main_module': 'mcp_service.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'ollama',
                'name': 'Ollama LLM',
                'description': 'Local large language model server',
                'icon': '🦙',
                'category': 'AI Infrastructure',
                'path': '/home/ed/codebase/centralized-ai-ui/ollama',
                'main_module': 'ollama_service.py',
                'requires_docker': True,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'settings',
                'name': 'Platform Settings',
                'description': 'Global platform configuration',
                'icon': '⚙️',
                'category': 'System',
                'path': '/home/ed/codebase/centralized-ai-ui/settings',
                'main_module': 'settings_manager.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': False
            },
            {
                'id': 'agent_orchestrator',
                'name': 'Agent Orchestrator',
                'description': 'Multi-agent coordination and management',
                'icon': '🎭',
                'category': 'AI Agents',
                'path': (
                    '/home/ed/codebase/centralized-ai-ui/agent-orchestrator'
                ),
                'main_module': 'orchestrator.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'ray_cluster',
                'name': 'Ray Cluster',
                'description': 'Distributed computing and scaling',
                'icon': '🌟',
                'category': 'Infrastructure',
                'path': '/home/ed/codebase/centralized-ai-ui/ray-cluster',
                'main_module': 'cluster_manager.py',
                'requires_docker': True,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'llm_builder',
                'name': 'LLM Builder',
                'description': (
                    'Custom language model training and fine-tuning'
                ),
                'icon': '🧠',
                'category': 'AI Development',
                'path': '/home/ed/codebase/centralized-ai-ui/llm-builder',
                'main_module': 'builder.py',
                'requires_docker': True,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'n8n_integration',
                'name': 'n8n Workflow Automation',
                'description': 'Visual workflow automation and integration',
                'icon': '🔄',
                'category': 'Automation',
                'path': '/home/ed/codebase/centralized-ai-ui/n8n',
                'main_module': 'n8n_service.py',
                'requires_docker': True,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'mcp_server',
                'name': 'MCP Server',
                'description': 'Model Context Protocol server implementation',
                'icon': '🖥️',
                'category': 'AI Infrastructure',
                'path': '/home/ed/codebase/centralized-ai-ui/mcp-server',
                'main_module': 'server.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            },
            {
                'id': 'llm_chat',
                'name': 'LLM Chat Interface',
                'description': (
                    'Interactive chat interface for language models'
                ),
                'icon': '💬',
                'category': 'AI Interfaces',
                'path': '/home/ed/codebase/centralized-ai-ui/llm-chat',
                'main_module': 'chat_interface.py',
                'requires_docker': False,
                'auto_start': False,
                'health_check': True
            }
        ]

        for component in default_components:
            self.register_component(
                component['id'],
                component['name'],
                component['description'],
                component.get('path', ''),
                component.get('main_module', ''),
                component.get('icon', '📦'),
                component.get('category', 'General'),
                component.get('requires_docker', False),
                component.get('auto_start', False),
                component.get('health_check', True)
            )

    def register_component(
        self,
        component_id: str,
        name: str,
        description: str,
        path: str = '',
        main_module: str = '',
        icon: str = '📦',
        category: str = 'General',
        requires_docker: bool = False,
        auto_start: bool = False,
        health_check: bool = True
    ):
        """Register a new component with the manager."""
        try:
            metadata = {
                'name': name,
                'description': description,
                'path': path,
                'main_module': main_module,
                'icon': icon,
                'category': category,
                'requires_docker': requires_docker,
                'auto_start': auto_start,
                'health_check': health_check,
                'status': 'registered',
                'last_health_check': None,
                'error_count': 0
            }

            self.components[component_id] = metadata
            self.componentRegistered.emit(component_id, metadata)
            self.logger.info(f"Registered component: {name}")

        except Exception as e:
            self.logger.error(f"Failed to register component {name}: {e}")
            self.componentError.emit(component_id, str(e))

    def get_component_view(self, component_id: str) -> Optional[QWidget]:
        """Get or create a view for the specified component."""
        try:
            if component_id in self.component_views:
                return self.component_views[component_id]

            # Create view based on component type
            view = self._create_component_view(component_id)
            if view:
                self.component_views[component_id] = view
                return view

            return None

        except Exception as e:
            self.logger.error(f"Failed to get view for {component_id}: {e}")
            self.componentError.emit(component_id, str(e))
            return None

    def _create_component_view(self, component_id: str) -> Optional[QWidget]:
        """Create a view for the specified component."""
        try:
            if component_id == 'web_scraper':
                from ..web_scraper_view import WebScraperView
                return WebScraperView()

            elif component_id == 'coding_agent':
                from ..coding_agent_view import CodingAgentView
                return CodingAgentView()

            elif component_id == 'anonymous_browser':
                from ..anonymous_browser_view import AnonymousBrowserView
                return AnonymousBrowserView()

            elif component_id == 'ollama':
                from ..ollama_view import OllamaView
                return OllamaView()

            elif component_id == 'settings':
                from ..settings_view import SettingsView
                return SettingsView()

            elif component_id == 'agent_orchestrator':
                from ..agent_orchestrator_view import AgentOrchestratorView
                return AgentOrchestratorView()

            elif component_id == 'ray_cluster':
                from ..ray_cluster_view import RayClusterView
                return RayClusterView()

            elif component_id == 'workspace_tracker':
                from ..workspace_tracker_view import WorkspaceTrackerView
                return WorkspaceTrackerView()

            elif component_id == 'llm_builder':
                from ..llm_builder_view import LLMBuilderView
                return LLMBuilderView()

            elif component_id == 'n8n_integration':
                from ..n8n_integration_view import N8NIntegrationView
                return N8NIntegrationView()

            elif component_id == 'mcp_server':
                from ..mcp_server_view import MCPServerView
                return MCPServerView()

            elif component_id == 'llm_chat':
                from ..llm_chat_view import LLMChatView
                return LLMChatView()

            else:
                # Create a generic placeholder view
                placeholder = QWidget()
                placeholder.setObjectName(f"{component_id}_placeholder")
                return placeholder

        except ImportError as e:
            self.logger.warning(
                f"Could not import view for {component_id}: {e}"
            )
            # Create a placeholder widget
            placeholder = QWidget()
            placeholder.setObjectName(f"{component_id}_placeholder")
            return placeholder

        except Exception as e:
            self.logger.error(f"Error creating view for {component_id}: {e}")
            return None

    def start_component(self, component_id: str) -> bool:
        """Start a component."""
        try:
            if component_id not in self.components:
                self.logger.error(f"Component {component_id} not registered")
                return False

            component = self.components[component_id]
            self.logger.info(f"Starting component: {component['name']}")

            # Update status
            component['status'] = 'starting'
            self.componentStatusChanged.emit(component_id, 'starting')

            # Simulate component startup
            # In real implementation, this would start the actual component
            component['status'] = 'running'
            self.componentStatusChanged.emit(component_id, 'running')
            self.componentStarted.emit(component_id)

            return True

        except Exception as e:
            self.logger.error(f"Failed to start {component_id}: {e}")
            self.componentError.emit(component_id, str(e))
            return False

    def stop_component(self, component_id: str) -> bool:
        """Stop a component."""
        try:
            if component_id not in self.components:
                self.logger.error(f"Component {component_id} not registered")
                return False

            component = self.components[component_id]
            self.logger.info(f"Stopping component: {component['name']}")

            # Update status
            component['status'] = 'stopping'
            self.componentStatusChanged.emit(component_id, 'stopping')

            # Simulate component shutdown
            component['status'] = 'stopped'
            self.componentStatusChanged.emit(component_id, 'stopped')
            self.componentStopped.emit(component_id)

            return True

        except Exception as e:
            self.logger.error(f"Failed to stop {component_id}: {e}")
            self.componentError.emit(component_id, str(e))
            return False

    def restart_component(self, component_id: str) -> bool:
        """Restart a component."""
        try:
            if self.stop_component(component_id):
                return self.start_component(component_id)
            return False

        except Exception as e:
            self.logger.error(f"Failed to restart {component_id}: {e}")
            self.componentError.emit(component_id, str(e))
            return False

    def get_component_status(self, component_id: str) -> str:
        """Get the current status of a component."""
        if component_id in self.components:
            return self.components[component_id].get('status', 'unknown')
        return 'not_registered'

    def get_all_components(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered components."""
        return self.components.copy()

    def start_health_monitoring(self, interval: int = 30000):
        """Start health monitoring for all components."""
        self.health_timer.start(interval)
        self.logger.info("Health monitoring started")

    def stop_health_monitoring(self):
        """Stop health monitoring."""
        self.health_timer.stop()
        self.logger.info("Health monitoring stopped")

    def _check_component_health(self):
        """Check the health of all components."""
        for component_id, component in self.components.items():
            if component.get('health_check', False):
                try:
                    # Simulate health check
                    is_healthy = self._perform_health_check(component_id)
                    self.healthStatusChanged.emit(component_id, is_healthy)

                    if not is_healthy:
                        component['error_count'] = (
                            component.get('error_count', 0) + 1
                        )
                        if component['error_count'] > 3:
                            self.logger.warning(
                                f"Component {component_id} unhealthy, "
                                f"attempting restart"
                            )
                            self.restart_component(component_id)

                except Exception as e:
                    self.logger.error(
                        f"Health check failed for {component_id}: {e}"
                    )

    def _perform_health_check(self, component_id: str) -> bool:
        """Perform a health check for a specific component."""
        # This is a placeholder implementation
        # In reality, this would check if the component is responsive
        component = self.components.get(component_id)
        if not component:
            return False

        status = component.get('status', 'unknown')
        return status == 'running'
