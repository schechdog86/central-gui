"""
MCP Server Manager - Easy JSON-based server configuration
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages MCP servers with easy JSON configuration"""
    
    def __init__(self, config_path: str = "config/mcp_servers.json"):
        """Initialize server manager with JSON config"""
        self.config_path = Path(config_path)
        self.servers_config = self._load_servers_config()
    
    def _load_servers_config(self) -> Dict[str, Any]:
        """Load servers configuration from JSON"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading servers config: {e}")
                return self._default_servers_config()
        else:
            config = self._default_servers_config()
            self.save_servers_config(config)
            return config
    
    def _default_servers_config(self) -> Dict[str, Any]:
        """Get default servers configuration"""
        return {
            "server_categories": {
                "coding_essentials": {
                    "name": "Essential Coding Tools",
                    "description": "Core coding and development tools",
                    "servers": [
                        {
                            "qualified_name": "github/repository-tools",
                            "display_name": "GitHub Tools",
                            "description": "Repository management and Git operations",
                            "category": "version_control",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["git_operations", "repo_management", "pull_requests"]
                        },
                        {
                            "qualified_name": "python/code-analysis",
                            "display_name": "Python Code Analyzer", 
                            "description": "Python code quality and analysis tools",
                            "category": "code_analysis",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["syntax_check", "linting", "security_scan"]
                        },
                        {
                            "qualified_name": "vscode/extensions-api",
                            "display_name": "VS Code Extensions",
                            "description": "VS Code extension integration",
                            "category": "development_environment",
                            "enabled": True,
                            "auto_connect": False,
                            "tools_provided": ["editor_integration", "debugging", "extensions"]
                        }
                    ]
                },
                "web_development": {
                    "name": "Web Development",
                    "description": "Tools for web application development",
                    "servers": [
                        {
                            "qualified_name": "javascript/node-tools",
                            "display_name": "Node.js Tools",
                            "description": "JavaScript and Node.js development tools",
                            "category": "web_development",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["npm_management", "bundling", "testing"]
                        },
                        {
                            "qualified_name": "web/development-stack",
                            "display_name": "Web Dev Stack",
                            "description": "Full-stack web development tools",
                            "category": "web_development", 
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["html_css", "frontend_frameworks", "responsive_design"]
                        },
                        {
                            "qualified_name": "rest/api-tools",
                            "display_name": "REST API Tools",
                            "description": "API development and testing tools",
                            "category": "api_development",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["api_testing", "documentation", "schema_validation"]
                        }
                    ]
                },
                "business_automation": {
                    "name": "Business Automation",
                    "description": "Schechter Customs LLC specific business tools",
                    "servers": [
                        {
                            "qualified_name": "schechter-customs/customer-service",
                            "display_name": "Customer Service Tools",
                            "description": "Customer support automation tools",
                            "category": "business_logic",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["chat_bot", "ticket_system", "knowledge_base"]
                        },
                        {
                            "qualified_name": "schechter-customs/inventory-manager", 
                            "display_name": "Inventory Management",
                            "description": "Inventory tracking and management",
                            "category": "business_logic",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["stock_tracking", "reorder_automation", "reporting"]
                        },
                        {
                            "qualified_name": "schechter-customs/accounting-tools",
                            "display_name": "Accounting Automation",
                            "description": "Financial and accounting automation",
                            "category": "business_logic",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["invoice_generation", "expense_tracking", "financial_reports"]
                        }
                    ]
                },
                "database_tools": {
                    "name": "Database Tools",
                    "description": "Database development and management",
                    "servers": [
                        {
                            "qualified_name": "sqlite/local-database",
                            "display_name": "SQLite Tools",
                            "description": "Local database management",
                            "category": "database",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["schema_design", "query_builder", "migrations"]
                        },
                        {
                            "qualified_name": "postgresql/database-tools",
                            "display_name": "PostgreSQL Tools", 
                            "description": "PostgreSQL database tools",
                            "category": "database",
                            "enabled": False,
                            "auto_connect": False,
                            "tools_provided": ["advanced_queries", "performance_tuning", "replication"]
                        }
                    ]
                },
                "testing_quality": {
                    "name": "Testing & Quality",
                    "description": "Code testing and quality assurance",
                    "servers": [
                        {
                            "qualified_name": "pytest/testing-framework",
                            "display_name": "PyTest Framework",
                            "description": "Python testing framework integration",
                            "category": "testing",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["unit_tests", "integration_tests", "coverage_reports"]
                        },
                        {
                            "qualified_name": "eslint/code-quality",
                            "display_name": "ESLint Quality",
                            "description": "JavaScript code quality tools",
                            "category": "code_quality",
                            "enabled": True,
                            "auto_connect": True,
                            "tools_provided": ["linting", "formatting", "best_practices"]
                        }
                    ]
                }
            },
            "custom_servers": [],
            "connection_settings": {
                "auto_connect_on_startup": True,
                "retry_failed_connections": True,
                "connection_timeout": 30,
                "max_concurrent_connections": 10
            }
        }
    
    def save_servers_config(self, config: Dict[str, Any]) -> None:
        """Save servers configuration to JSON"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.servers_config = config
            logger.info("Servers configuration saved")
        except Exception as e:
            logger.error(f"Error saving servers config: {e}")
    
    def add_custom_server(self, server_config: Dict[str, Any]) -> bool:
        """Add a custom MCP server"""
        try:
            # Validate required fields
            required_fields = ["qualified_name", "display_name", "description"]
            for field in required_fields:
                if field not in server_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Set defaults
            server_config.setdefault("category", "custom")
            server_config.setdefault("enabled", True)
            server_config.setdefault("auto_connect", False)
            server_config.setdefault("tools_provided", [])
            
            # Add to custom servers
            self.servers_config["custom_servers"].append(server_config)
            self.save_servers_config(self.servers_config)
            
            logger.info(f"Added custom server: {server_config['qualified_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom server: {e}")
            return False
    
    def remove_custom_server(self, qualified_name: str) -> bool:
        """Remove a custom MCP server"""
        try:
            custom_servers = self.servers_config["custom_servers"]
            original_count = len(custom_servers)
            
            self.servers_config["custom_servers"] = [
                server for server in custom_servers 
                if server["qualified_name"] != qualified_name
            ]
            
            if len(self.servers_config["custom_servers"]) < original_count:
                self.save_servers_config(self.servers_config)
                logger.info(f"Removed custom server: {qualified_name}")
                return True
            else:
                logger.warning(f"Custom server not found: {qualified_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing custom server: {e}")
            return False
    
    def get_all_servers(self) -> List[Dict[str, Any]]:
        """Get all configured servers"""
        all_servers = []
        
        # Add servers from categories
        for category_name, category_data in self.servers_config["server_categories"].items():
            for server in category_data["servers"]:
                server_copy = server.copy()
                server_copy["source_category"] = category_name
                all_servers.append(server_copy)
        
        # Add custom servers
        for server in self.servers_config["custom_servers"]:
            server_copy = server.copy()
            server_copy["source_category"] = "custom"
            all_servers.append(server_copy)
        
        return all_servers
    
    def get_enabled_servers(self) -> List[Dict[str, Any]]:
        """Get only enabled servers"""
        return [server for server in self.get_all_servers() if server.get("enabled", False)]
    
    def get_auto_connect_servers(self) -> List[Dict[str, Any]]:
        """Get servers marked for auto-connection"""
        return [server for server in self.get_enabled_servers() if server.get("auto_connect", False)]
    
    def update_server_status(self, qualified_name: str, enabled: bool) -> bool:
        """Enable/disable a server"""
        try:
            # Check in categories
            for category_data in self.servers_config["server_categories"].values():
                for server in category_data["servers"]:
                    if server["qualified_name"] == qualified_name:
                        server["enabled"] = enabled
                        self.save_servers_config(self.servers_config)
                        return True
            
            # Check in custom servers
            for server in self.servers_config["custom_servers"]:
                if server["qualified_name"] == qualified_name:
                    server["enabled"] = enabled
                    self.save_servers_config(self.servers_config)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating server status: {e}")
            return False
    
    def export_servers_config(self, export_path: str) -> bool:
        """Export servers configuration to a file"""
        try:
            with open(export_path, 'w') as f:
                json.dump(self.servers_config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False
    
    def import_servers_config(self, import_path: str, merge: bool = True) -> bool:
        """Import servers configuration from a file"""
        try:
            with open(import_path, 'r') as f:
                imported_config = json.load(f)
            
            if merge:
                # Merge with existing configuration
                # Add custom servers
                existing_custom = {s["qualified_name"] for s in self.servers_config["custom_servers"]}
                for server in imported_config.get("custom_servers", []):
                    if server["qualified_name"] not in existing_custom:
                        self.servers_config["custom_servers"].append(server)
                
                # Update connection settings
                self.servers_config["connection_settings"].update(
                    imported_config.get("connection_settings", {})
                )
            else:
                # Replace entire configuration
                self.servers_config = imported_config
            
            self.save_servers_config(self.servers_config)
            return True
            
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return False
    
    def get_servers_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get servers filtered by category"""
        return [server for server in self.get_all_servers() 
                if server.get("category") == category or server.get("source_category") == category]
    
    def get_connection_settings(self) -> Dict[str, Any]:
        """Get connection settings"""
        return self.servers_config.get("connection_settings", {})
    
    def update_connection_settings(self, settings: Dict[str, Any]) -> None:
        """Update connection settings"""
        self.servers_config["connection_settings"].update(settings)
        self.save_servers_config(self.servers_config)
