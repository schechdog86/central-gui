"""
Enhanced Workspace Tracker Manager with FULL functionality
Integrates ALL features from the workspace tracker
"""
import logging
import subprocess
import requests
import json
import threading
import os
import sys
import sqlite3
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedWorkspaceTrackerManager(WorkspaceTrackerManager):
    """Enhanced manager with complete workspace tracker functionality."""
    
    def __init__(self):
        """Initialize the Workspace Tracker Manager with all features."""
        self.api_base_url = "http://127.0.0.1:8912"
        self.api_running = False
        self.current_workspace = None
        self.current_project = None
        
        # Data stores
        self.tasks = {}
        self.projects = {}
        self.modules = {}
        self.research_items = {}
        self.notes = {}
        self.files = {}
        
        # Components
        self.api_process = None
        self.crawler = None
        self.db_manager = None
        self.crawl_result = None
        self.crawl_thread = None
        
    def initialize(self) -> bool:
        """Initialize all workspace tracker components."""
        try:
            # Check if API server is running
            self.api_running = self._check_api_status()
            
            if not self.api_running:
                # Try to start the API server
                self._start_api_server()
            
            # Initialize workspace crawler
            self._init_crawler()
            
            # Initialize database
            self._init_database()
            
            # Initialize models
            self._init_models()
                
            logger.info("Workspace Tracker Manager fully initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Workspace Tracker Manager: {e}")
            return False
    
    def _init_database(self):
        """Initialize the database manager."""
        try:
            workspace_tracker_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "workspacetracker"
            )
            
            if workspace_tracker_path not in sys.path:
                sys.path.insert(0, workspace_tracker_path)
            
            from workspacetracker.database.db_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            self.db_manager.initialize()
            logger.info("Database manager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            self.db_manager = None
    
    def _init_models(self):
        """Initialize model classes."""
        try:
            from workspacetracker.models.project import Project
            from workspacetracker.models.module import Module
            from workspacetracker.models.task import Task
            from workspacetracker.models.research import ResearchItem
            from workspacetracker.models.note import Note
            from workspacetracker.models.file import ProjectFile
            
            self.Project = Project
            self.Module = Module
            self.Task = Task
            self.ResearchItem = ResearchItem
            self.Note = Note
            self.ProjectFile = ProjectFile
            
            logger.info("Models initialized")
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    # Project Management
    def create_project(self, name: str, path: str, description: str = "") -> Dict[str, Any]:
        """Create a new project."""
        try:
            project = self.Project(name, path, description)
            
            # Save to database if available
            if self.db_manager:
                self.db_manager.create_project(project)
            
            self.projects[project.id] = project
            self.current_project = project
            
            return {
                "id": project.id,
                "name": project.name,
                "path": project.path,
                "description": project.description,
                "created": project.created
            }
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {"error": str(e)}
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        try:
            if self.db_manager:
                projects = self.db_manager.get_all_projects()
                return [p.to_dict() for p in projects]
            else:
                return [p.to_dict() for p in self.projects.values()]
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    def set_current_project(self, project_id: str) -> bool:
        """Set the current active project."""
        try:
            if self.db_manager:
                project = self.db_manager.get_project(project_id)
                if project:
                    self.current_project = project
                    self.current_workspace = project.path
                    return True
            elif project_id in self.projects:
                self.current_project = self.projects[project_id]
                self.current_workspace = self.current_project.path
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting current project: {e}")
            return False
    
    # Module Management
    def create_module(self, name: str, description: str = "", parent_id: str = None) -> Dict[str, Any]:
        """Create a new module."""
        try:
            if not self.current_project:
                return {"error": "No project selected"}
            
            module = self.Module(name, description, parent_id)
            
            # Add to project
            self.current_project.add_module(module)
            
            # Save to database
            if self.db_manager:
                self.db_manager.update_project(self.current_project)
            
            self.modules[module.id] = module
            
            return module.to_dict()
        except Exception as e:
            logger.error(f"Error creating module: {e}")
            return {"error": str(e)}
    
    def get_modules(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Get modules for a project."""
        try:
            if project_id and self.db_manager:
                project = self.db_manager.get_project(project_id)
                if project:
                    return [m.to_dict() for m in project.modules]
            elif self.current_project:
                return [m.to_dict() for m in self.current_project.modules]
            return []
        except Exception as e:
            logger.error(f"Error getting modules: {e}")
            return []
    
    # Research Management
    def create_research_item(self, title: str, content: str, item_type: str = "document",
                           tags: List[str] = None, relevance: str = "medium", 
                           source: str = "") -> Dict[str, Any]:
        """Create a new research item."""
        try:
            if not self.current_project:
                return {"error": "No project selected"}
            
            research = self.ResearchItem(title, content, tags, relevance, item_type, source)
            
            # Add to project
            self.current_project.add_research_item(research)
            
            # Save to database
            if self.db_manager:
                self.db_manager.update_project(self.current_project)
            
            self.research_items[research.id] = research
            
            return research.to_dict()
        except Exception as e:
            logger.error(f"Error creating research item: {e}")
            return {"error": str(e)}
    
    def get_research_items(self, project_id: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Get research items, optionally filtered by tags."""
        try:
            items = []
            
            if project_id and self.db_manager:
                project = self.db_manager.get_project(project_id)
                if project:
                    items = project.research_items
            elif self.current_project:
                items = self.current_project.research_items
            
            # Filter by tags if provided
            if tags:
                items = [item for item in items if any(tag in item.tags for tag in tags)]
            
            return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"Error getting research items: {e}")
            return []
    
    # Note Management
    def create_note(self, content: str, target_type: str, target_id: str, 
                   author: str = "User") -> Dict[str, Any]:
        """Create a new note for any entity."""
        try:
            note = self.Note(content, target_type, target_id, author)
            
            # Save to database
            if self.db_manager:
                self.db_manager.create_note(note)
            
            self.notes[note.id] = note
            
            return note.to_dict()
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            return {"error": str(e)}
    
    def get_notes(self, target_type: str = None, target_id: str = None) -> List[Dict[str, Any]]:
        """Get notes filtered by target."""
        try:
            if self.db_manager:
                notes = self.db_manager.get_notes(target_type, target_id)
                return [n.to_dict() for n in notes]
            else:
                notes = self.notes.values()
                if target_type:
                    notes = [n for n in notes if n.target_type == target_type]
                if target_id:
                    notes = [n for n in notes if n.target_id == target_id]
                return [n.to_dict() for n in notes]
        except Exception as e:
            logger.error(f"Error getting notes: {e}")
            return []
    
    # File Management
    def add_file_annotation(self, file_path: str, line_number: int, 
                          annotation: str, annotation_type: str = "comment") -> Dict[str, Any]:
        """Add an annotation to a file."""
        try:
            from workspacetracker.models.file import CodeAnnotation
            
            annot = CodeAnnotation(line_number, annotation, annotation_type)
            
            # Get or create project file
            project_file = None
            for f in self.files.values():
                if f.file_path == file_path:
                    project_file = f
                    break
            
            if not project_file:
                project_file = self.ProjectFile(
                    file_path=file_path,
                    module_id=None,
                    file_type="code"
                )
                self.files[project_file.id] = project_file
            
            project_file.add_annotation(annot)
            
            # Save to database
            if self.db_manager:
                self.db_manager.create_or_update_file(project_file)
            
            return {
                "file_id": project_file.id,
                "annotation": annot.to_dict()
            }
        except Exception as e:
            logger.error(f"Error adding annotation: {e}")
            return {"error": str(e)}
    
    # Analytics and Metrics
    def get_project_metrics(self, project_id: str = None) -> Dict[str, Any]:
        """Get comprehensive metrics for a project."""
        try:
            project = None
            if project_id and self.db_manager:
                project = self.db_manager.get_project(project_id)
            elif self.current_project:
                project = self.current_project
            
            if not project:
                return {"error": "No project found"}
            
            # Calculate metrics
            total_tasks = len(project.tasks)
            completed_tasks = len([t for t in project.tasks if t.status == "completed"])
            
            metrics = {
                "project_name": project.name,
                "total_modules": len(project.modules),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "total_research_items": len(project.research_items),
                "total_notes": len(project.notes),
                "created_date": project.created,
                "last_modified": project.last_modified
            }
            
            # Add workspace analysis metrics if available
            if self.crawl_result:
                metrics.update({
                    "total_files": self.crawl_result.file_count,
                    "code_files": len(self.crawl_result.code_files),
                    "functions": sum(len(f) for f in self.crawl_result.functions.values()),
                    "classes": sum(len(c) for c in self.crawl_result.classes.values())
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {"error": str(e)}
