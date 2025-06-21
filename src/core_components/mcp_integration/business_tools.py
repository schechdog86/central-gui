"""
Business Tools Manager - Schechter Customs LLC specific MCP integrations
Manages business-specific coding tools and automations
"""
import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio

from .mcp_manager import MCPManager
from .agent_enhancer import AIAgentEnhancer

logger = logging.getLogger(__name__)


class BusinessToolsManager:
    """Manages business-specific coding tools for Schechter Customs LLC"""
    
    def __init__(self, mcp_manager: MCPManager, agent_enhancer: AIAgentEnhancer):
        """
        Initialize Business Tools Manager
        
        Args:
            mcp_manager: MCP Manager instance
            agent_enhancer: AI Agent Enhancer instance
        """
        self.mcp_manager = mcp_manager
        self.agent_enhancer = agent_enhancer
        self.business_agents = {}
        self.automation_templates = self._load_automation_templates()
        self.project_templates = self._load_project_templates()
        
    def _load_automation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load business automation templates"""
        return {
            "customer_service_bot": {
                "description": "AI-powered customer service automation",
                "tools_needed": ["web_development", "database", "testing"],
                "languages": ["python", "javascript"],
                "frameworks": ["fastapi", "react"],
                "template": {
                    "backend": "fastapi_customer_service.py",
                    "frontend": "react_chat_interface.js", 
                    "database": "customer_service_schema.sql",
                    "config": "customer_service_config.json"
                }
            },
            
            "inventory_manager": {
                "description": "Automated inventory tracking and management",
                "tools_needed": ["database", "automation", "testing"],
                "languages": ["python", "sql"],
                "frameworks": ["fastapi", "sqlite"],
                "template": {
                    "main": "inventory_manager.py",
                    "database": "inventory_schema.sql",
                    "api": "inventory_api.py",
                    "scheduler": "inventory_scheduler.py"
                }
            },
            
            "accounting_automation": {
                "description": "Automated accounting and financial reporting",
                "tools_needed": ["database", "automation", "documentation"],
                "languages": ["python", "sql"],
                "frameworks": ["fastapi", "sqlite"],
                "template": {
                    "main": "accounting_automation.py",
                    "reports": "financial_reports.py",
                    "database": "accounting_schema.sql",
                    "integrations": "quickbooks_integration.py"
                }
            },
            
            "marketing_automation": {
                "description": "Marketing campaign and social media automation",
                "tools_needed": ["web_development", "automation", "testing"],
                "languages": ["python", "javascript"],
                "frameworks": ["fastapi", "react"],
                "template": {
                    "backend": "marketing_automation.py",
                    "frontend": "marketing_dashboard.js",
                    "email": "email_campaign_manager.py",
                    "social": "social_media_scheduler.py"
                }
            },
            
            "sales_pipeline": {
                "description": "CRM and sales pipeline management",
                "tools_needed": ["web_development", "database", "automation"],
                "languages": ["python", "javascript", "sql"],
                "frameworks": ["fastapi", "react", "sqlite"],
                "template": {
                    "backend": "sales_pipeline.py",
                    "frontend": "sales_dashboard.js",
                    "database": "crm_schema.sql",
                    "reports": "sales_reports.py"
                }
            },
            
            "data_processor": {
                "description": "Business data processing and analysis",
                "tools_needed": ["code_generation", "database", "testing"],
                "languages": ["python", "sql"],
                "frameworks": ["pandas", "sqlite"],
                "template": {
                    "main": "data_processor.py",
                    "analyzers": "business_analyzers.py",
                    "exporters": "report_exporters.py",
                    "database": "data_warehouse_schema.sql"
                }
            }
        }
    
    def _load_project_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load project structure templates"""
        return {
            "web_application": {
                "structure": {
                    "backend/": {
                        "main.py": "FastAPI main application",
                        "models/": "Database models",
                        "api/": "API endpoints", 
                        "services/": "Business logic",
                        "utils/": "Utility functions"
                    },
                    "frontend/": {
                        "src/": "React source code",
                        "components/": "React components",
                        "pages/": "Application pages",
                        "styles/": "CSS styling"
                    },
                    "database/": {
                        "schema.sql": "Database schema",
                        "migrations/": "Database migrations",
                        "seeds/": "Sample data"
                    },
                    "tests/": {
                        "test_api.py": "API tests",
                        "test_models.py": "Model tests",
                        "test_services.py": "Service tests"
                    },
                    "docs/": {
                        "README.md": "Project documentation",
                        "API.md": "API documentation"
                    }
                }
            },
            
            "automation_script": {
                "structure": {
                    "main.py": "Main automation script",
                    "config/": "Configuration files",
                    "modules/": "Automation modules",
                    "logs/": "Log files",
                    "tests/": "Test files",
                    "requirements.txt": "Dependencies",
                    "README.md": "Documentation"
                }
            },
            
            "desktop_application": {
                "structure": {
                    "main.py": "Main GUI application",
                    "gui/": "GUI components",
                    "logic/": "Business logic",
                    "data/": "Data handling",
                    "resources/": "Images and assets",
                    "tests/": "Test files",
                    "requirements.txt": "Dependencies",
                    "README.md": "Documentation"
                }
            }
        }
    
    async def create_business_agent(self, agent_name: str, 
                                  business_function: str) -> Dict[str, Any]:
        """
        Create a business-specific AI agent
        
        Args:
            agent_name: Name for the new agent
            business_function: Type of business function (customer_service, inventory, etc.)
            
        Returns:
            Agent creation result
        """
        try:
            if business_function not in self.automation_templates:
                return {
                    "success": False,
                    "error": f"Unknown business function: {business_function}",
                    "available_functions": list(self.automation_templates.keys())
                }
            
            # Get template for this business function
            template = self.automation_templates[business_function]
            
            # Create enhanced agent
            success = self.agent_enhancer.create_business_coding_agent(agent_name)
            
            if not success:
                return {"success": False, "error": "Failed to create base agent"}
            
            # Configure agent for specific business function
            agent_config = {
                "name": agent_name,
                "business_function": business_function,
                "description": template["description"],
                "tools_needed": template["tools_needed"],
                "languages": template["languages"],
                "frameworks": template["frameworks"],
                "template": template["template"],
                "created_at": asyncio.get_event_loop().time(),
                "status": "active"
            }
            
            self.business_agents[agent_name] = agent_config
            
            # Set up specific MCP tools for this business function
            await self._setup_business_tools(agent_name, business_function)
            
            logger.info(f"Created business agent {agent_name} for {business_function}")
            
            return {
                "success": True,
                "agent_name": agent_name,
                "business_function": business_function,
                "capabilities": self.agent_enhancer.get_agent_capabilities(agent_name),
                "configuration": agent_config
            }
            
        except Exception as e:
            logger.error(f"Error creating business agent {agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _setup_business_tools(self, agent_name: str, business_function: str) -> None:
        """Setup MCP tools specific to business function"""
        try:
            template = self.automation_templates[business_function]
            tools_needed = template["tools_needed"]
            
            # Search for relevant MCP servers
            for tool_category in tools_needed:
                relevant_servers = self.mcp_manager.search_coding_tools(
                    category=tool_category
                )
                
                # Connect to top relevant servers
                for server in relevant_servers[:2]:  # Connect to top 2 servers per category
                    qualified_name = server.get("qualifiedName", "")
                    if qualified_name:
                        await asyncio.sleep(0.1)  # Small delay
                        self.mcp_manager.connect_to_coding_server(qualified_name)
            
            logger.info(f"Set up business tools for {agent_name}")
            
        except Exception as e:
            logger.error(f"Error setting up business tools for {agent_name}: {e}")
    
    async def generate_business_code(self, agent_name: str, 
                                   project_type: str,
                                   specifications: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate business-specific code using AI agent
        
        Args:
            agent_name: Name of the business agent
            project_type: Type of project to generate
            specifications: Project specifications
            
        Returns:
            Code generation result
        """
        if agent_name not in self.business_agents:
            return {"success": False, "error": f"Business agent {agent_name} not found"}
        
        try:
            agent_config = self.business_agents[agent_name]
            business_function = agent_config["business_function"]
            
            # Prepare task parameters
            task_params = {
                "task": f"Generate {project_type} for {business_function}",
                "language": specifications.get("language", "python"),
                "framework": specifications.get("framework", "fastapi"),
                "business_function": business_function,
                "specifications": specifications,
                "project_structure": self.project_templates.get(project_type, {})
            }
            
            # Execute code generation task
            result = await self.agent_enhancer.execute_coding_task(
                agent_name, 
                "code_generation",
                task_params
            )
            
            if result.get("success"):
                # Post-process the generated code
                processed_result = await self._process_generated_code(
                    result, business_function, project_type
                )
                result.update(processed_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating business code: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_generated_code(self, generation_result: Dict[str, Any],
                                    business_function: str,
                                    project_type: str) -> Dict[str, Any]:
        """Post-process generated code with business-specific enhancements"""
        try:
            # Add business-specific imports and configurations
            business_enhancements = {
                "customer_service": {
                    "imports": ["from fastapi import FastAPI, WebSocket", "import sqlite3"],
                    "config": {"database": "customer_service.db", "port": 8001}
                },
                "inventory": {
                    "imports": ["import pandas as pd", "import sqlite3", "from datetime import datetime"],
                    "config": {"database": "inventory.db", "port": 8002}
                },
                "accounting": {
                    "imports": ["import pandas as pd", "from decimal import Decimal", "import sqlite3"],
                    "config": {"database": "accounting.db", "port": 8003}
                },
                "marketing": {
                    "imports": ["import requests", "from datetime import datetime", "import json"],
                    "config": {"database": "marketing.db", "port": 8004}
                },
                "sales": {
                    "imports": ["import pandas as pd", "from datetime import datetime", "import sqlite3"],
                    "config": {"database": "sales.db", "port": 8005}
                }
            }
            
            enhancements = business_enhancements.get(business_function, {})
            
            return {
                "business_enhancements": enhancements,
                "suggested_structure": self.project_templates.get(project_type, {}),
                "next_steps": [
                    "Review generated code",
                    "Set up database schema", 
                    "Configure environment variables",
                    "Run tests",
                    "Deploy to production"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error processing generated code: {e}")
            return {"processing_error": str(e)}
    
    async def automate_business_process(self, agent_name: str,
                                      process_name: str,
                                      process_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automate a specific business process
        
        Args:
            agent_name: Name of the business agent
            process_name: Name of the process to automate
            process_details: Details about the process
            
        Returns:
            Automation result
        """
        if agent_name not in self.business_agents:
            return {"success": False, "error": f"Business agent {agent_name} not found"}
        
        try:
            # Prepare automation task
            task_params = {
                "task": f"Create automation for {process_name}",
                "process_name": process_name,
                "process_details": process_details,
                "language": "python",
                "automation_type": "business_process"
            }
            
            # Execute automation task
            result = await self.agent_enhancer.execute_coding_task(
                agent_name,
                "business_automation", 
                task_params
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error automating business process: {e}")
            return {"success": False, "error": str(e)}
    
    def get_available_business_functions(self) -> List[str]:
        """Get list of available business functions"""
        return list(self.automation_templates.keys())
    
    def get_business_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get status of a business agent"""
        if agent_name not in self.business_agents:
            return {"exists": False}
        
        agent_config = self.business_agents[agent_name]
        capabilities = self.agent_enhancer.get_agent_capabilities(agent_name)
        
        return {
            "exists": True,
            "configuration": agent_config,
            "capabilities": capabilities,
            "connected_tools": len(self.mcp_manager.connected_servers),
            "coding_categories": len(self.mcp_manager.get_available_coding_categories())
        }
    
    def get_all_business_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all business agents and their configurations"""
        return self.business_agents
    
    async def test_business_agent(self, agent_name: str) -> Dict[str, Any]:
        """Test a business agent's capabilities"""
        if agent_name not in self.business_agents:
            return {"success": False, "error": f"Business agent {agent_name} not found"}
        
        try:
            # Simple test task
            test_params = {
                "task": "Generate a simple hello world function",
                "language": "python",
                "code": "def hello_world():\n    return 'Hello, Schechter Customs LLC!'"
            }
            
            result = await self.agent_enhancer.execute_coding_task(
                agent_name,
                "code_generation",
                test_params
            )
            
            return {
                "success": True,
                "agent_name": agent_name,
                "test_result": result,
                "status": "Agent is working correctly" if result.get("success") else "Agent needs attention"
            }
            
        except Exception as e:
            logger.error(f"Error testing business agent {agent_name}: {e}")
            return {"success": False, "error": str(e)}
