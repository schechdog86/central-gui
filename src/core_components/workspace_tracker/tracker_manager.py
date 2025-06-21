"""
Workspace Tracker Manager for Schechter Customs LLC Platform
Manages workspace tracking functionality and integrates with the main GUI
This is being replaced by enhanced_tracker_manager.py for full functionality
"""
import logging
import subprocess
import requests
import json
import threading
import os
import sys
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

# Import the enhanced manager that has ALL features
from .enhanced_tracker_manager import EnhancedWorkspaceTrackerManager as WorkspaceTrackerManager

# For backward compatibility, keep the original name
__all__ = ['WorkspaceTrackerManager']
    """Manages workspace tracking operations for the platform."""
    
    def __init__(self):
        """Initialize the Workspace Tracker Manager."""
        self.api_base_url = "http://127.0.0.1:8912"
        self.api_running = False
        self.current_workspace = None
        self.tasks = {}
        self.api_process = None
        self.crawler = None
        self.crawl_result = None
        self.crawl_thread = None
        
    def initialize(self) -> bool:
        """
        Initialize the workspace tracker manager.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if API server is running
            self.api_running = self._check_api_status()
            
            if not self.api_running:
                # Try to start the API server
                self._start_api_server()
            
            # Initialize workspace crawler
            self._init_crawler()
                
            logger.info("Workspace Tracker Manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Workspace Tracker Manager: {e}")
            return False
    
    def _init_crawler(self):
        """Initialize the workspace crawler."""
        try:
            # Get the path to workspacetracker
            workspace_tracker_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "workspacetracker"
            )
            
            # Add to path
            if workspace_tracker_path not in sys.path:
                sys.path.insert(0, workspace_tracker_path)
            
            # Import workspace crawler
            from workspacetracker.core.workspace_crawler import WorkspaceCrawler
            self.crawler = WorkspaceCrawler()
            logger.info("Workspace crawler initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace crawler: {e}")
            self.crawler = None
    
    def _check_api_status(self) -> bool:
        """Check if the API server is running."""
        try:
            response = requests.get(f"{self.api_base_url}/tasks", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _start_api_server(self):
        """Start the workspace tracker API server."""
        try:
            # Get the path to workspacetracker
            workspace_tracker_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "workspacetracker"
            )
            
            # Import and start the API server
            import sys
            sys.path.insert(0, workspace_tracker_path)
            
            from workspacetracker.api_server import start_api_server_in_thread
            start_api_server_in_thread()
            
            # Wait a moment for server to start
            import time
            time.sleep(2)
            
            self.api_running = self._check_api_status()
            logger.info("Workspace Tracker API server started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            self.api_running = False
    
    def create_task(self, title: str, description: str = "", priority: str = "medium") -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high)
            
        Returns:
            Created task data
        """
        if not self.api_running:
            return {"error": "API server not running"}
            
        try:
            task_data = {
                "title": title,
                "description": description,
                "priority": priority,
                "file_ids": []
            }
            
            response = requests.post(f"{self.api_base_url}/tasks", json=task_data)
            if response.status_code == 200:
                task = response.json()
                self.tasks[task['id']] = task
                return task
            else:
                return {"error": f"Failed to create task: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {"error": str(e)}
    
    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        if not self.api_running:
            return []
            
        try:
            response = requests.get(f"{self.api_base_url}/tasks")
            if response.status_code == 200:
                tasks = response.json()
                # Update local cache
                for task in tasks:
                    self.tasks[task['id']] = task
                return tasks
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as complete."""
        if not self.api_running:
            return False
            
        try:
            response = requests.post(f"{self.api_base_url}/tasks/{task_id}/complete")
            if response.status_code == 200:
                if task_id in self.tasks:
                    self.tasks[task_id]['status'] = 'completed'
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    def add_comment(self, task_id: str, author: str, comment: str) -> bool:
        """Add a comment to a task."""
        if not self.api_running:
            return False
            
        try:
            comment_data = {
                "author": author,
                "comment": comment
            }
            
            response = requests.post(f"{self.api_base_url}/tasks/{task_id}/comment", json=comment_data)
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return False
    
    def get_comments(self, task_id: str) -> List[Dict[str, Any]]:
        """Get comments for a task."""
        if not self.api_running:
            return []
            
        try:
            response = requests.get(f"{self.api_base_url}/tasks/{task_id}/comments")
            if response.status_code == 200:
                return response.json()
            return []
                
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            return []
    
    def add_summary(self, task_id: str, author: str, summary: str) -> bool:
        """Add a summary to a task."""
        if not self.api_running:
            return False
            
        try:
            summary_data = {
                "author": author,
                "summary": summary
            }
            
            response = requests.post(f"{self.api_base_url}/tasks/{task_id}/summary", json=summary_data)
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error adding summary: {e}")
            return False
    
    def set_workspace(self, workspace_path: str) -> bool:
        """Set the current workspace path."""
        if os.path.exists(workspace_path):
            self.current_workspace = workspace_path
            logger.info(f"Workspace set to: {workspace_path}")
            return True
        else:
            logger.error(f"Workspace path does not exist: {workspace_path}")
            return False
    
    def crawl_workspace(self, progress_callback: Optional[Callable[[str, float], None]] = None,
                       max_files: int = 1000) -> Dict[str, Any]:
        """
        Crawl the current workspace to analyze files and structure.
        
        Args:
            progress_callback: Optional callback for progress updates
            max_files: Maximum number of files to analyze
            
        Returns:
            Crawl results dictionary
        """
        if not self.current_workspace:
            return {"error": "No workspace set"}
        
        if not self.crawler:
            return {"error": "Crawler not initialized"}
        
        if self.crawl_thread and self.crawl_thread.is_alive():
            return {"error": "Crawl already in progress"}
        
        # Start crawl in background thread
        self.crawl_thread = threading.Thread(
            target=self._perform_crawl,
            args=(progress_callback, max_files)
        )
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
        
        return {"status": "Crawl started"}
    
    def _perform_crawl(self, progress_callback, max_files):
        """Perform the workspace crawl in a background thread."""
        try:
            self.crawl_result = self.crawler.crawl_workspace(
                self.current_workspace,
                progress_callback=progress_callback,
                max_files=max_files
            )
            logger.info(f"Workspace crawl completed: {self.crawl_result.file_count} files")
        except Exception as e:
            logger.error(f"Error during workspace crawl: {e}")
            self.crawl_result = None
    
    def get_crawl_status(self) -> Dict[str, Any]:
        """Get the status of the current or last crawl."""
        if self.crawl_thread and self.crawl_thread.is_alive():
            return {"status": "in_progress"}
        
        if self.crawl_result:
            return {
                "status": "completed",
                "file_count": self.crawl_result.file_count,
                "code_files": len(self.crawl_result.code_files),
                "doc_files": len(self.crawl_result.doc_files),
                "functions": sum(len(funcs) for funcs in self.crawl_result.functions.values()),
                "classes": sum(len(classes) for classes in self.crawl_result.classes.values()),
                "duration": self.crawl_result.duration_seconds
            }
        
        return {"status": "not_started"}
    
    def get_crawl_results(self) -> Optional[Dict[str, Any]]:
        """Get the full crawl results."""
        if self.crawl_result:
            return self.crawl_result.to_dict()
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get workspace tracker status."""
        return {
            'api_running': self.api_running,
            'api_url': self.api_base_url,
            'current_workspace': self.current_workspace,
            'task_count': len(self.tasks),
            'tasks': list(self.tasks.values())
        }
    
    def shutdown(self):
        """Shutdown the workspace tracker manager."""
        # Note: API server runs in daemon thread, will stop with main process
        logger.info("Workspace Tracker Manager shut down")
