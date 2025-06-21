"""
Anonymous Browser Manager for Schechter Customs LLC Platform
Manages Docker-based anonymous browser instances
"""
import logging
import subprocess
import json
import os
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages anonymous browser instances using Docker."""
    
    def __init__(self, docker_compose_path: str = None):
        """
        Initialize the Browser Manager.
        
        Args:
            docker_compose_path: Path to docker-compose.yml file
        """
        self.docker_compose_path = docker_compose_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "anonymous_browser",
            "docker-compose.yml"
        )
        self.active_sessions = {}
        self.container_status = 'stopped'
        self.is_docker_available = self._check_docker()
        
    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            logger.warning("Docker not found. Browser functionality limited.")
            return False
    
    def initialize(self) -> bool:
        """
        Initialize the browser manager.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.is_docker_available:
                logger.error("Docker is not available")
                return False
                
            logger.info("Browser Manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Browser Manager: {e}")
            return False
    
    def start_browser_container(self) -> bool:
        """Start the browser Docker container."""
        if not self.is_docker_available:
            return False
            
        try:
            # Check if container is already running
            check_cmd = ['docker', 'ps', '--filter', 'name=anonymous-browser', '--format', '{{.Names}}']
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if 'anonymous-browser' in result.stdout:
                self.container_status = 'running'
                logger.info("Browser container is already running")
                return True
            
            # Start container using docker-compose
            cmd = ['docker-compose', '-f', self.docker_compose_path, 'up', '-d']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.container_status = 'running'
                logger.info("Browser container started successfully")
                return True
            else:
                logger.error(f"Failed to start container: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting browser container: {e}")
            return False
    
    def stop_browser_container(self) -> bool:
        """Stop the browser Docker container."""
        if not self.is_docker_available:
            return False
            
        try:
            cmd = ['docker-compose', '-f', self.docker_compose_path, 'down']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.container_status = 'stopped'
                logger.info("Browser container stopped successfully")
                return True
            else:
                logger.error(f"Failed to stop container: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping browser container: {e}")
            return False
    
    def create_browser_session(self, profile_name: str = None) -> Dict[str, Any]:
        """Create a new browser session."""
        if self.container_status != 'running':
            if not self.start_browser_container():
                return {'error': 'Failed to start browser container'}
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            'id': session_id,
            'profile': profile_name or 'default',
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'url': 'http://localhost:3000'  # Default browser URL
        }
        
        self.active_sessions[session_id] = session
        return session
    
    def get_browser_status(self) -> Dict[str, Any]:
        """Get browser system status."""
        return {
            'docker_available': self.is_docker_available,
            'container_status': self.container_status,
            'active_sessions': len(self.active_sessions),
            'sessions': list(self.active_sessions.keys())
        }
    
    def shutdown(self):
        """Shutdown the browser manager."""
        if self.container_status == 'running':
            self.stop_browser_container()
        logger.info("Browser Manager shut down")
