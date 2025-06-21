"""
AI Agent Enhancer - Integrates MCP coding tools with AI agents
Provides coding capabilities to AI agents through MCP connections
"""
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import asyncio

from .mcp_manager import MCPManager

logger = logging.getLogger(__name__)


class AIAgentEnhancer:
    """Enhances AI agents with MCP coding capabilities"""
    
    def __init__(self, mcp_manager: MCPManager, ollama_manager=None):
        """
        Initialize AI Agent Enhancer
        
        Args:
            mcp_manager: MCP Manager instance
            ollama_manager: Ollama manager for LLM interactions
        """
        self.mcp_manager = mcp_manager
        self.ollama_manager = ollama_manager
        self.agent_tools = {}
        self.coding_prompts = self._load_coding_prompts()
        self.tool_execution_history = []
        
    def _load_coding_prompts(self) -> Dict[str, str]:
        """Load coding-specific prompts for AI agents"""
        return {
            "code_generation": """You are a coding assistant for Schechter Customs LLC. 
            Generate high-quality, production-ready code following best practices.
            Focus on business automation, web development, and data processing.
            
            Available MCP tools: {available_tools}
            
            Requirements:
            - Write clean, documented code
            - Include error handling
            - Follow Python/JavaScript best practices
            - Consider business logic requirements
            
            Task: {task}
            Language: {language}
            """,
            
            "code_analysis": """You are a code review assistant for Schechter Customs LLC.
            Analyze code for quality, security, and business logic correctness.
            
            Available MCP tools: {available_tools}
            
            Analysis focus:
            - Code quality and maintainability
            - Security vulnerabilities
            - Performance optimizations
            - Business logic accuracy
            - Best practices compliance
            
            Code to analyze: {code}
            """,
            
            "debugging": """You are a debugging assistant for Schechter Customs LLC.
            Help identify and fix bugs in business automation code.
            
            Available MCP tools: {available_tools}
            
            Debugging approach:
            - Analyze error messages and stack traces
            - Identify root causes
            - Suggest specific fixes
            - Provide testing recommendations
            
            Error/Issue: {error}
            Code context: {code}
            """,
            
            "refactoring": """You are a code refactoring assistant for Schechter Customs LLC.
            Improve code structure, readability, and maintainability.
            
            Available MCP tools: {available_tools}
            
            Refactoring goals:
            - Improve code organization
            - Enhance readability
            - Optimize performance
            - Reduce technical debt
            - Maintain business logic integrity
            
            Code to refactor: {code}
            Refactoring goal: {goal}
            """,
            
            "business_automation": """You are a business automation specialist for Schechter Customs LLC.
            Create code solutions for business processes and workflows.
            
            Available MCP tools: {available_tools}
            
            Business focus areas:
            - Customer service automation
            - Inventory management
            - Accounting/financial processes
            - Marketing automation
            - Sales pipeline management
            
            Business requirement: {requirement}
            System integration: {integration}
            """
        }
    
    def enhance_agent_with_coding_tools(self, agent_name: str, 
                                      coding_categories: List[str] = None) -> bool:
        """
        Enhance an AI agent with coding capabilities
        
        Args:
            agent_name: Name of the AI agent to enhance
            coding_categories: List of coding categories to enable
            
        Returns:
            True if enhancement successful
        """
        try:
            if coding_categories is None:
                coding_categories = [
                    "code_generation", "code_analysis", "debugging",
                    "refactoring", "testing", "documentation"
                ]
            
            # Get available coding tools
            available_tools = {}
            for category in coding_categories:
                category_tools = self._get_tools_for_category(category)
                if category_tools:
                    available_tools[category] = category_tools
            
            # Store agent tool configuration
            self.agent_tools[agent_name] = {
                "categories": coding_categories,
                "available_tools": available_tools,
                "enabled": True,
                "preferences": {
                    "language": "python",
                    "framework": "fastapi",
                    "style": "business_focused"
                }
            }
            
            logger.info(f"Enhanced agent {agent_name} with {len(available_tools)} coding tool categories")
            return True
            
        except Exception as e:
            logger.error(f"Error enhancing agent {agent_name}: {e}")
            return False
    
    def _get_tools_for_category(self, category: str) -> List[Dict[str, Any]]:
        """Get MCP tools for a specific category"""
        tools = []
        for server_name, tool_categories in self.mcp_manager.coding_tools.items():
            if category in tool_categories:
                tools.extend(tool_categories[category])
        return tools
    
    async def execute_coding_task(self, agent_name: str, task_type: str, 
                                 task_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a coding task using enhanced AI agent
        
        Args:
            agent_name: Name of the enhanced agent
            task_type: Type of coding task
            task_params: Task parameters
            
        Returns:
            Task execution result
        """
        if agent_name not in self.agent_tools:
            raise ValueError(f"Agent {agent_name} is not enhanced with coding tools")
        
        try:
            # Get agent configuration
            agent_config = self.agent_tools[agent_name]
            available_tools = agent_config["available_tools"]
            
            # Prepare prompt based on task type
            if task_type not in self.coding_prompts:
                raise ValueError(f"Unknown task type: {task_type}")
            
            prompt_template = self.coding_prompts[task_type]
            
            # Format prompt with available tools and task parameters
            formatted_prompt = prompt_template.format(
                available_tools=json.dumps(available_tools, indent=2),
                **task_params
            )
            
            # Execute with LLM if available
            result = {"success": False, "result": None, "tools_used": []}
            
            if self.ollama_manager:
                # Use enhanced prompt with tool awareness
                llm_response = await self._execute_with_llm(
                    agent_name, formatted_prompt, task_type, task_params
                )
                result.update(llm_response)
            
            # Log execution
            self.tool_execution_history.append({
                "agent": agent_name,
                "task_type": task_type,
                "parameters": task_params,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing coding task for {agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_with_llm(self, agent_name: str, prompt: str, 
                              task_type: str, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding task with LLM integration"""
        try:
            # Get agent preferences
            agent_config = self.agent_tools[agent_name]
            preferences = agent_config.get("preferences", {})
            
            # Prepare messages for LLM
            messages = [
                {
                    "role": "system",
                    "content": f"You are an AI coding assistant for Schechter Customs LLC. "
                              f"You have access to MCP coding tools and should use them when appropriate. "
                              f"Preferred language: {preferences.get('language', 'python')}, "
                              f"Framework: {preferences.get('framework', 'fastapi')}, "
                              f"Style: {preferences.get('style', 'business_focused')}"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # Get LLM response
            model_name = "llama3.2:3b"  # Default model
            response = self.ollama_manager.generate(model_name, messages)
            
            if response and "response" in response:
                llm_output = response["response"]
                
                # Parse LLM response for tool usage
                tools_used = self._parse_tool_usage(llm_output)
                
                # Execute any MCP tools mentioned in the response
                tool_results = await self._execute_mentioned_tools(tools_used, task_params)
                
                return {
                    "success": True,
                    "result": llm_output,
                    "tools_used": tools_used,
                    "tool_results": tool_results
                }
            else:
                return {"success": False, "error": "No response from LLM"}
                
        except Exception as e:
            logger.error(f"Error in LLM execution: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_tool_usage(self, llm_output: str) -> List[str]:
        """Parse LLM output for tool usage indicators"""
        tools_used = []
        
        # Look for tool usage patterns in LLM output
        tool_patterns = [
            "using code analysis tool",
            "running tests with", 
            "formatting code with",
            "checking syntax with",
            "generating documentation with",
            "refactoring with"
        ]
        
        for pattern in tool_patterns:
            if pattern in llm_output.lower():
                tools_used.append(pattern)
        
        return tools_used
    
    async def _execute_mentioned_tools(self, tools_used: List[str], 
                                     task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tools mentioned in LLM response"""
        tool_results = {}
        
        for tool_pattern in tools_used:
            try:
                # Map tool patterns to actual MCP tools
                if "code analysis" in tool_pattern:
                    # Execute code analysis tool
                    result = await self._execute_code_analysis_tool(task_params)
                    tool_results["code_analysis"] = result
                elif "test" in tool_pattern:
                    # Execute testing tool
                    result = await self._execute_testing_tool(task_params)
                    tool_results["testing"] = result
                # Add more tool mappings as needed
                
            except Exception as e:
                logger.error(f"Error executing tool {tool_pattern}: {e}")
                tool_results[tool_pattern] = {"error": str(e)}
        
        return tool_results
    
    async def _execute_code_analysis_tool(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code analysis via MCP"""
        try:
            # Find a connected server with code analysis tools
            for server_name, tool_categories in self.mcp_manager.coding_tools.items():
                if "code_analysis" in tool_categories and tool_categories["code_analysis"]:
                    analysis_tool = tool_categories["code_analysis"][0]
                    
                    result = self.mcp_manager.execute_coding_tool(
                        server_name,
                        analysis_tool["name"],
                        {
                            "code": task_params.get("code", ""),
                            "language": task_params.get("language", "python")
                        }
                    )
                    
                    return result
            
            return {"error": "No code analysis tool available"}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute_testing_tool(self, task_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute testing tool via MCP"""
        try:
            # Find a connected server with testing tools
            for server_name, tool_categories in self.mcp_manager.coding_tools.items():
                if "testing" in tool_categories and tool_categories["testing"]:
                    testing_tool = tool_categories["testing"][0]
                    
                    result = self.mcp_manager.execute_coding_tool(
                        server_name,
                        testing_tool["name"],
                        {
                            "code": task_params.get("code", ""),
                            "test_type": task_params.get("test_type", "unit"),
                            "language": task_params.get("language", "python")
                        }
                    )
                    
                    return result
            
            return {"error": "No testing tool available"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_agent_capabilities(self, agent_name: str) -> Dict[str, Any]:
        """Get coding capabilities of an enhanced agent"""
        if agent_name not in self.agent_tools:
            return {"enhanced": False}
        
        agent_config = self.agent_tools[agent_name]
        return {
            "enhanced": True,
            "categories": agent_config["categories"],
            "available_tools": len(agent_config["available_tools"]),
            "preferences": agent_config["preferences"],
            "total_tools": sum(len(tools) for tools in agent_config["available_tools"].values())
        }
    
    def get_coding_task_history(self, agent_name: str = None) -> List[Dict[str, Any]]:
        """Get coding task execution history"""
        if agent_name:
            return [
                task for task in self.tool_execution_history 
                if task["agent"] == agent_name
            ]
        return self.tool_execution_history
    
    def create_business_coding_agent(self, agent_name: str) -> bool:
        """Create a business-focused coding agent"""
        business_categories = [
            "code_generation", "automation", "web_development", 
            "database", "testing", "documentation"
        ]
        
        success = self.enhance_agent_with_coding_tools(agent_name, business_categories)
        
        if success:
            # Set business-specific preferences
            self.agent_tools[agent_name]["preferences"].update({
                "language": "python",
                "framework": "fastapi", 
                "database": "sqlite",
                "focus": "business_automation",
                "style": "enterprise_ready"
            })
            
            logger.info(f"Created business coding agent: {agent_name}")
        
        return success
