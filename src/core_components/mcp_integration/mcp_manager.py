"""
MCP Manager for AI Agent System Integration - Coding Focused
Manages MCP connections and provides coding tools to AI agents
"""
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
import httpx

from .server_manager import MCPServerManager

logger = logging.getLogger(__name__)


class MCPManager:
    """Manager for MCP connections and coding tool access for AI agents"""
    
    def __init__(self, config_path: str = "config/mcp_config.json"):
        """
        Initialize MCP Manager with coding focus
        
        Args:
            config_path: Path to MCP configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.api_key = self.config.get("smithery_api_key", "")
        self.base_url = "https://registry.smithery.ai/"
        self.connected_servers = {}
        self.available_tools = {}
        self.coding_tools = {}
        
        # Initialize server manager for easy JSON configuration
        self.server_manager = MCPServerManager()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading MCP config: {e}")
                return self._default_config()
        else:
            config = self._default_config()
            self.save_config(config)
            return config
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default MCP configuration with coding focus"""
        return {
            "smithery_api_key": "f8126f95-8a57-4059-9666-ff6f0a9ff10e",
            "enabled_servers": [
                # Core coding tools
                "github/repository-tools",
                "vscode/extensions-api", 
                "python/code-analysis",
                "javascript/node-tools",
                "web/development-stack",
                
                # AI coding assistants
                "anthropic/claude-dev",
                "openai/codex-integration",
                "github/copilot-api",
                
                # Development environments
                "docker/container-tools",
                "git/version-control",
                "npm/package-manager",
                "pip/python-packages",
                
                # Testing and quality
                "pytest/testing-framework",
                "eslint/code-quality",
                "black/code-formatter",
                "mypy/type-checker",
                
                # Databases and APIs
                "postgresql/database-tools",
                "sqlite/local-database",
                "rest/api-tools",
                "graphql/query-tools",
                
                # Business coding tools
                "schechter-customs/business-logic",
                "schechter-customs/automation-scripts",
                "schechter-customs/data-processing"
            ],
            "coding_categories": {
                "development": {
                    "enabled": True,
                    "priority": "high",
                    "tools": [
                        "code_generation", "refactoring", "debugging", 
                        "testing", "documentation", "code_review"
                    ]
                },
                "web_development": {
                    "enabled": True,
                    "priority": "high", 
                    "tools": [
                        "html_css_tools", "javascript_frameworks", "backend_apis",
                        "database_integration", "responsive_design"
                    ]
                },
                "python_development": {
                    "enabled": True,
                    "priority": "high",
                    "tools": [
                        "fastapi_tools", "django_tools", "flask_tools",
                        "data_science", "automation_scripts", "gui_development"
                    ]
                },
                "database_management": {
                    "enabled": True,
                    "priority": "medium",
                    "tools": [
                        "sql_generation", "schema_design", "query_optimization",
                        "migration_tools", "backup_automation"
                    ]
                },
                "devops_automation": {
                    "enabled": True,
                    "priority": "medium",
                    "tools": [
                        "deployment_scripts", "server_management", "monitoring",
                        "container_orchestration", "ci_cd_pipelines"
                    ]
                },
                "business_automation": {
                    "enabled": True,
                    "priority": "high",
                    "tools": [
                        "report_generation", "data_processing", "workflow_automation",
                        "integration_scripts", "custom_business_logic"
                    ]
                }
            },
            "supported_languages": [
                "python", "javascript", "typescript", "html", "css", 
                "sql", "bash", "powershell", "json", "yaml", "xml"
            ],
            "project_types": [
                "web_application", "desktop_gui", "api_service", 
                "automation_script", "data_processing", "business_logic"
            ],
            "auto_connect": True,
            "max_concurrent_tools": 10,
            "code_analysis_enabled": True,
            "auto_test_generation": True,
            "documentation_generation": True
        }
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save MCP configuration"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.config = config
        except Exception as e:
            logger.error(f"Error saving MCP config: {e}")
    
    def set_api_key(self, api_key: str) -> None:
        """Set Smithery API key"""
        self.api_key = api_key
        self.config["smithery_api_key"] = api_key
        self.save_config(self.config)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def search_coding_tools(self, language: str = "", category: str = "") -> List[Dict[str, Any]]:
        """
        Search for coding-specific MCP servers
        
        Args:
            language: Programming language (python, javascript, etc.)
            category: Tool category (development, testing, etc.)
            
        Returns:
            List of relevant coding MCP servers
        """
        if not self.api_key:
            logger.warning("Smithery API key not set")
            return []
            
        try:
            query_parts = ["coding", "development", "programming"]
            if language:
                query_parts.append(language)
            if category:
                query_parts.append(category)
                
            query = " ".join(query_parts)
            url = f"{self.base_url}servers"
            params = {"q": query, "pageSize": 50}
            
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            servers = data.get("servers", [])
            
            # Filter for coding-relevant servers
            coding_servers = []
            coding_keywords = [
                "code", "programming", "development", "git", "github", 
                "python", "javascript", "web", "api", "database", 
                "testing", "debugging", "refactor", "lint"
            ]
            
            for server in servers:
                description = server.get("description", "").lower()
                name = server.get("name", "").lower()
                
                if any(keyword in description or keyword in name for keyword in coding_keywords):
                    coding_servers.append(server)
            
            return coding_servers
            
        except Exception as e:
            logger.error(f"Error searching coding tools: {e}")
            return []
    
    def connect_to_coding_server(self, qualified_name: str) -> bool:
        """
        Connect to a coding-focused MCP server
        
        Args:
            qualified_name: Server qualified name
            
        Returns:
            True if connection successful
        """
        if not self.api_key:
            logger.warning("Smithery API key not set")
            return False
            
        try:
            # Get server details
            url = f"{self.base_url}servers/{qualified_name}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            server_info = response.json()
            deployment_url = server_info.get("deploymentUrl")
            
            if not deployment_url:
                logger.warning(f"Server {qualified_name} is not deployed")
                return False
            
            # Test connection
            test_response = requests.get(deployment_url, headers=self._get_headers())
            test_response.raise_for_status()
            
            # Store connection info
            self.connected_servers[qualified_name] = {
                "server_info": server_info,
                "deployment_url": deployment_url,
                "connected_at": str(asyncio.get_event_loop().time()),
                "server_type": "coding"
            }
            
            # Load coding tools from this server
            self._load_coding_tools(qualified_name)
            
            logger.info(f"Connected to coding MCP server: {qualified_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to coding server {qualified_name}: {e}")
            return False
    
    def _load_coding_tools(self, qualified_name: str) -> None:
        """Load coding tools available from a connected server"""
        try:
            server_info = self.connected_servers[qualified_name]
            deployment_url = server_info["deployment_url"]
            
            # Get tools list
            tools_url = f"{deployment_url}/tools"
            response = requests.get(tools_url, headers=self._get_headers())
            
            if response.status_code == 200:
                tools_data = response.json()
                tools = tools_data.get("tools", [])
                
                # Categorize coding tools
                coding_tool_categories = {
                    "code_generation": [],
                    "code_analysis": [],
                    "testing": [],
                    "debugging": [],
                    "refactoring": [],
                    "documentation": [],
                    "version_control": [],
                    "package_management": [],
                    "database": [],
                    "web_development": [],
                    "automation": []
                }
                
                for tool in tools:
                    tool_name = tool.get("name", "").lower()
                    tool_desc = tool.get("description", "").lower()
                    
                    # Categorize based on keywords
                    if any(keyword in tool_name or keyword in tool_desc 
                           for keyword in ["generate", "create", "build"]):
                        coding_tool_categories["code_generation"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["analyze", "lint", "check"]):
                        coding_tool_categories["code_analysis"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["test", "pytest", "unittest"]):
                        coding_tool_categories["testing"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["debug", "trace", "breakpoint"]):
                        coding_tool_categories["debugging"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["refactor", "optimize", "clean"]):
                        coding_tool_categories["refactoring"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["doc", "comment", "readme"]):
                        coding_tool_categories["documentation"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["git", "commit", "branch"]):
                        coding_tool_categories["version_control"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["npm", "pip", "package"]):
                        coding_tool_categories["package_management"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["sql", "database", "db"]):
                        coding_tool_categories["database"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["web", "html", "css", "js"]):
                        coding_tool_categories["web_development"].append(tool)
                    elif any(keyword in tool_name or keyword in tool_desc 
                             for keyword in ["automate", "script", "workflow"]):
                        coding_tool_categories["automation"].append(tool)
                
                self.coding_tools[qualified_name] = coding_tool_categories
                self.available_tools[qualified_name] = tools
                
                total_tools = sum(len(category_tools) for category_tools in coding_tool_categories.values())
                logger.info(f"Loaded {total_tools} coding tools from {qualified_name}")
            
        except Exception as e:
            logger.error(f"Error loading coding tools from {qualified_name}: {e}")
    
    def get_coding_tools_for_language(self, language: str) -> Dict[str, List[Dict]]:
        """
        Get coding tools filtered by programming language
        
        Args:
            language: Programming language (python, javascript, etc.)
            
        Returns:
            Dictionary of categorized tools for the language
        """
        language_tools = {}
        
        for server_name, tool_categories in self.coding_tools.items():
            for category, tools in tool_categories.items():
                language_specific_tools = []
                
                for tool in tools:
                    tool_name = tool.get("name", "").lower()
                    tool_desc = tool.get("description", "").lower()
                    
                    if language.lower() in tool_name or language.lower() in tool_desc:
                        language_specific_tools.append(tool)
                
                if language_specific_tools:
                    if category not in language_tools:
                        language_tools[category] = []
                    language_tools[category].extend(language_specific_tools)
        
        return language_tools
    
    def execute_coding_tool(self, server_name: str, tool_name: str, 
                           parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a coding tool via MCP
        
        Args:
            server_name: Name of the connected server
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            
        Returns:
            Tool execution result
        """
        if server_name not in self.connected_servers:
            raise ValueError(f"Server {server_name} is not connected")
        
        try:
            deployment_url = self.connected_servers[server_name]["deployment_url"]
            tool_url = f"{deployment_url}/tools/{tool_name}/execute"
            
            payload = {
                "parameters": parameters,
                "context": {
                    "user": "schechter-customs-ai-agent",
                    "project_type": "business_automation",
                    "language_preference": "python"
                }
            }
            
            response = requests.post(
                tool_url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Executed coding tool {tool_name} on {server_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing coding tool {tool_name}: {e}")
            return {"error": str(e), "success": False}
    
    def get_available_coding_categories(self) -> List[str]:
        """Get list of available coding tool categories"""
        categories = set()
        for tool_categories in self.coding_tools.values():
            categories.update(tool_categories.keys())
        return sorted(list(categories))
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        return self.config.get("supported_languages", [])
    
    def is_coding_focused(self) -> bool:
        """Check if MCP manager is configured for coding"""
        return len(self.coding_tools) > 0 or len(self.config.get("coding_categories", {})) > 0
    
    async def auto_connect_coding_servers(self) -> Dict[str, bool]:
        """
        Automatically connect to essential coding servers
        
        Returns:
            Dictionary of connection results
        """
        if not self.config.get("auto_connect", False):
            return {}
        
        essential_servers = [
            "github/repository-tools",
            "python/code-analysis", 
            "vscode/extensions-api",
            "git/version-control"
        ]
        
        connection_results = {}
        
        for server in essential_servers:
            try:
                success = self.connect_to_coding_server(server)
                connection_results[server] = success
                if success:
                    logger.info(f"Auto-connected to {server}")
                else:
                    logger.warning(f"Failed to auto-connect to {server}")
                    
                # Small delay between connections
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error auto-connecting to {server}: {e}")
                connection_results[server] = False
        
        return connection_results
