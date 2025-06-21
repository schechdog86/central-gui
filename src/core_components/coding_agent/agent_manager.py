"""
Coding Agent Manager - Bridge between Coding Agent and Main GUI
Provides comprehensive access to all coding agent features
"""

import sys
import os
import json
import threading
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add coding-agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'coding-agent'))

try:
    from src.core.agent import CodingAgent
    from src.core.config import Config
    from src.core.skills import SkillManager, create_default_skill_manager
    from src.core.agent_memory import AgentMemory
    from src.core.memory.memory_manager import MemoryManager
    from src.core.knowledge.knowledge_manager import KnowledgeManager
    from src.core.tools.tool_manager import ToolManager
    from src.ui.mcp_manager import MCPManager
except ImportError as e:
    print(f"Warning: Could not import coding agent modules: {e}")
    CodingAgent = None
    Config = None

logger = logging.getLogger(__name__)


class CodingAgentManager:
    """Manages the coding agent and provides interface for GUI integration."""
    
    def __init__(self):
        """Initialize the coding agent manager."""
        self.agent = None
        self.config = None
        self.skill_manager = None
        self.mcp_manager = None
        self.is_initialized = False
        self._init_lock = threading.Lock()
        
        # Feature states
        self.features = {
            'memory': {'enabled': True, 'status': 'Ready'},
            'skills': {'enabled': True, 'status': 'Ready'},
            'rag': {'enabled': False, 'status': 'Not Configured'},
            'mcp': {'enabled': False, 'status': 'Not Started'},
            'knowledge': {'enabled': True, 'status': 'Ready'},
            'tools': {'enabled': True, 'status': 'Ready'}
        }
        
        # Stats and metrics
        self.stats = {
            'queries_processed': 0,
            'tokens_used': 0,
            'skills_used': {},
            'memory_items': 0,
            'knowledge_items': 0
        }
    
    def initialize(self, config_path: str = None) -> Dict[str, Any]:
        """Initialize the coding agent with configuration."""
        with self._init_lock:
            if self.is_initialized:
                return {'status': 'already_initialized'}
            
            try:
                # Load or create config
                if config_path and os.path.exists(config_path):
                    self.config = Config(config_path)
                else:
                    # Create default config
                    self.config = self._create_default_config()
                
                # Initialize the agent
                self.agent = CodingAgent(self.config)
                
                # Initialize skill manager
                self.skill_manager = create_default_skill_manager()
                
                # Initialize MCP manager if available
                try:
                    self.mcp_manager = MCPManager()
                    self.features['mcp']['status'] = 'Ready'
                except:
                    logger.warning("MCP Manager not available")
                
                self.is_initialized = True
                self._update_stats()
                
                return {
                    'status': 'success',
                    'features': self.features,
                    'stats': self.stats
                }
                
            except Exception as e:
                logger.error(f"Failed to initialize coding agent: {e}")
                return {
                    'status': 'error',
                    'error': str(e)
                }
    
    def _create_default_config(self) -> 'Config':
        """Create default configuration."""
        config = Config()
        
        # AI settings
        config.set('ai', 'provider', 'ollama')
        config.set('ai', 'model', 'deepseek-coder:latest')
        config.set('ai', 'temperature', 0.7)
        
        # Memory settings
        config.set('memory', 'enabled', True)
        config.set('memory', 'max_items', 1000)
        config.set('memory', 'backup_interval_minutes', 15)
        
        # System settings
        config.set('system', 'memory_dir', './storage/memory')
        config.set('system', 'knowledge_dir', './storage/knowledge')
        
        return config
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query through the coding agent."""
        if not self.is_initialized:
            return {'error': 'Agent not initialized'}
        
        try:
            # Update stats
            self.stats['queries_processed'] += 1
            
            # Prepare context
            full_context = {
                'skill_manager': self.skill_manager,
                'features': self.features
            }
            if context:
                full_context.update(context)
            
            # Process query
            response = self.agent.process_query(query)
            
            # Track skill usage
            self._track_skill_usage(query)
            
            # Update stats
            self._update_stats()
            
            return {
                'response': response,
                'stats': self.stats,
                'features': self.features
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {'error': str(e)}
    
    def get_skills(self) -> Dict[str, Any]:
        """Get all skills and their status."""
        if not self.skill_manager:
            return {}
        
        return self.skill_manager.get_skills()
    
    def add_skill_xp(self, skill_name: str, xp: int) -> Dict[str, Any]:
        """Add XP to a skill."""
        if not self.skill_manager:
            return {'error': 'Skill manager not initialized'}
        
        try:
            leveled_up = self.skill_manager.gain_xp(skill_name, xp)
            return {
                'skill': skill_name,
                'xp_added': xp,
                'leveled_up': leveled_up,
                'new_level': self.skill_manager.skills[skill_name].level
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_memory_items(self, memory_type: str = 'all', limit: int = 100) -> List[Dict[str, Any]]:
        """Get memory items from the agent."""
        if not self.agent:
            return []
        
        try:
            if hasattr(self.agent, 'memory_manager'):
                # Get memories based on type
                memories = []
                
                if memory_type in ['all', 'short']:
                    memories.extend(self._get_short_term_memories(limit))
                
                if memory_type in ['all', 'long']:
                    memories.extend(self._get_long_term_memories(limit))
                
                if memory_type in ['all', 'critical']:
                    memories.extend(self._get_critical_memories(limit))
                
                return memories[:limit]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting memory items: {e}")
            return []
    
    def add_memory(self, content: str, memory_type: str = 'short', 
                   metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a memory item to the agent."""
        if not self.agent:
            return {'error': 'Agent not initialized'}
        
        try:
            if hasattr(self.agent, 'memory_manager'):
                # Add memory based on type
                result = self.agent.memory_manager.add_memory(
                    content, memory_type, metadata or {}
                )
                
                self._update_stats()
                return {'status': 'success', 'memory_id': result}
            
            return {'error': 'Memory manager not available'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories using semantic search."""
        if not self.agent:
            return []
        
        try:
            if hasattr(self.agent, 'memory_manager'):
                results = self.agent.memory_manager.search(query, limit)
                return results
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []
    
    def get_knowledge_items(self, category: str = 'all') -> List[Dict[str, Any]]:
        """Get knowledge items from the agent."""
        if not self.agent or not hasattr(self.agent, 'knowledge_manager'):
            return []
        
        try:
            items = self.agent.knowledge_manager.get_items(category)
            return items
        except Exception as e:
            logger.error(f"Error getting knowledge items: {e}")
            return []
    
    def add_knowledge(self, title: str, content: str, category: str, 
                     tags: List[str] = None) -> Dict[str, Any]:
        """Add a knowledge item."""
        if not self.agent or not hasattr(self.agent, 'knowledge_manager'):
            return {'error': 'Knowledge manager not available'}
        
        try:
            result = self.agent.knowledge_manager.add_item(
                title, content, category, tags or []
            )
            self._update_stats()
            return {'status': 'success', 'item_id': result}
        except Exception as e:
            return {'error': str(e)}
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools."""
        if not self.agent or not hasattr(self.agent, 'tool_manager'):
            return []
        
        try:
            tools = self.agent.tool_manager.get_available_tools()
            return tools
        except Exception as e:
            logger.error(f"Error getting tools: {e}")
            return []
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool."""
        if not self.agent or not hasattr(self.agent, 'tool_manager'):
            return {'error': 'Tool manager not available'}
        
        try:
            result = self.agent.tool_manager.execute(tool_name, args)
            return {'status': 'success', 'result': result}
        except Exception as e:
            return {'error': str(e)}
    
    def start_mcp(self) -> Dict[str, Any]:
        """Start MCP services."""
        if not self.mcp_manager:
            return {'error': 'MCP manager not available'}
        
        try:
            self.mcp_manager.start_all()
            self.features['mcp']['status'] = 'Running'
            self.features['mcp']['enabled'] = True
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}
    
    def stop_mcp(self) -> Dict[str, Any]:
        """Stop MCP services."""
        if not self.mcp_manager:
            return {'error': 'MCP manager not available'}
        
        try:
            self.mcp_manager.stop_all()
            self.features['mcp']['status'] = 'Stopped'
            self.features['mcp']['enabled'] = False
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP service status."""
        if not self.mcp_manager:
            return {'status': 'not_available'}
        
        try:
            return self.mcp_manager.get_status()
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Analyze a code file."""
        if not self.agent:
            return {'error': 'Agent not initialized'}
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Analyze using agent
            analysis = self.agent.analyze_code(code, file_path)
            
            # Track skill usage
            self.add_skill_xp('Code Analysis', 10)
            
            return {
                'status': 'success',
                'analysis': analysis
            }
        except Exception as e:
            return {'error': str(e)}
    
    def generate_code(self, prompt: str, language: str = 'python') -> Dict[str, Any]:
        """Generate code based on prompt."""
        if not self.agent:
            return {'error': 'Agent not initialized'}
        
        try:
            # Generate code
            code = self.agent.generate_code(prompt, language)
            
            # Track skill usage
            self.add_skill_xp(language.title(), 15)
            
            return {
                'status': 'success',
                'code': code,
                'language': language
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_short_term_memories(self, limit: int) -> List[Dict[str, Any]]:
        """Get short-term memories."""
        # Implementation depends on actual memory structure
        return []
    
    def _get_long_term_memories(self, limit: int) -> List[Dict[str, Any]]:
        """Get long-term memories."""
        return []
    
    def _get_critical_memories(self, limit: int) -> List[Dict[str, Any]]:
        """Get critical memories."""
        return []
    
    def _track_skill_usage(self, query: str):
        """Track skill usage based on query."""
        # Simple keyword-based tracking
        query_lower = query.lower()
        
        if 'python' in query_lower:
            self.add_skill_xp('Python', 5)
        if 'debug' in query_lower:
            self.add_skill_xp('Debugging', 5)
        if 'test' in query_lower:
            self.add_skill_xp('Testing', 5)
        if 'refactor' in query_lower:
            self.add_skill_xp('Refactoring', 5)
        if 'document' in query_lower or 'docs' in query_lower:
            self.add_skill_xp('Documentation', 5)
        if 'git' in query_lower or 'commit' in query_lower:
            self.add_skill_xp('Git', 5)
    
    def _update_stats(self):
        """Update internal statistics."""
        if self.agent:
            if hasattr(self.agent, 'memory_manager'):
                self.stats['memory_items'] = self.agent.memory_manager.get_count()
            if hasattr(self.agent, 'knowledge_manager'):
                self.stats['knowledge_items'] = self.agent.knowledge_manager.get_count()
            if hasattr(self.agent, 'execution_stats'):
                self.stats['tokens_used'] = self.agent.execution_stats.get('tokens_used', 0)
    
    def get_achievements(self) -> List[str]:
        """Get achievements earned."""
        if not self.skill_manager:
            return []
        
        return self.skill_manager.get_achievements()
    
    def export_data(self, export_path: str) -> Dict[str, Any]:
        """Export all agent data."""
        try:
            data = {
                'skills': self.get_skills(),
                'achievements': self.get_achievements(),
                'stats': self.stats,
                'features': self.features,
                'memories': self.get_memory_items(limit=1000),
                'knowledge': self.get_knowledge_items()
            }
            
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return {'status': 'success', 'path': export_path}
        except Exception as e:
            return {'error': str(e)}
    
    def import_data(self, import_path: str) -> Dict[str, Any]:
        """Import agent data."""
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            # Import skills
            if 'skills' in data and self.skill_manager:
                for skill_name, skill_data in data['skills'].items():
                    self.skill_manager.add_skill(skill_name, skill_data['description'])
                    # Set level and XP
                    skill = self.skill_manager.skills[skill_name]
                    skill.level = skill_data['level']
                    skill.xp = skill_data['xp']
            
            return {'status': 'success'}
        except Exception as e:
            return {'error': str(e)}
