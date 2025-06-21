"""
Web Scraper Manager for Schechter Customs LLC Platform
Manages web scraping functionality and integrates with the main GUI
"""
import logging
import threading
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class WebScraperManager:
    """Manages web scraping operations for the platform."""
    
    def __init__(self):
        """Initialize the Web Scraper Manager."""
        self.active_jobs = {}
        self.job_results = {}
        self.job_counter = 0
        self.is_running = False
        
    def initialize(self) -> bool:
        """
        Initialize the web scraper.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.is_running = True
            logger.info("Web Scraper Manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Web Scraper Manager: {e}")
            return False
    
    def create_scrape_job(self, url: str, options: Dict[str, Any] = None) -> str:
        """
        Create a new web scraping job.
        
        Args:
            url: URL to scrape
            options: Scraping options (selectors, depth, etc.)
            
        Returns:
            Job ID
        """
        self.job_counter += 1
        job_id = f"scrape_{self.job_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        job = {
            'id': job_id,
            'url': url,
            'options': options or {},
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        
        self.active_jobs[job_id] = job
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self._execute_scrape, args=(job_id,))
        thread.daemon = True
        thread.start()
        
        return job_id
    
    def _execute_scrape(self, job_id: str):
        """Execute the scraping job."""
        job = self.active_jobs.get(job_id)
        if not job:
            return
            
        try:
            job['status'] = 'running'
            job['started_at'] = datetime.now().isoformat()
            
            # Perform the scraping
            response = requests.get(job['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract based on options
            options = job['options']
            result = {
                'url': job['url'],
                'title': soup.title.string if soup.title else None,
                'text': soup.get_text(strip=True)[:5000],  # First 5000 chars
                'links': [a.get('href') for a in soup.find_all('a', href=True)][:50],
                'images': [img.get('src') for img in soup.find_all('img', src=True)][:50]
            }
            
            # Custom selectors if provided
            if 'selectors' in options:
                result['custom_data'] = {}
                for name, selector in options['selectors'].items():
                    elements = soup.select(selector)
                    result['custom_data'][name] = [elem.get_text(strip=True) for elem in elements]
            
            job['result'] = result
            job['status'] = 'completed'
            job['completed_at'] = datetime.now().isoformat()
            
            # Move to results
            self.job_results[job_id] = job
            
        except Exception as e:
            job['status'] = 'failed'
            job['error'] = str(e)
            job['completed_at'] = datetime.now().isoformat()
            logger.error(f"Scraping job {job_id} failed: {e}")
    
    def get_status(self, job_id: str = None) -> Dict[str, Any]:
        """Get status of scraping jobs."""
        if job_id:
            job = self.active_jobs.get(job_id) or self.job_results.get(job_id)
            return job if job else {'error': 'Job not found'}
        else:
            return {
                'active_jobs': len(self.active_jobs),
                'completed_jobs': len(self.job_results),
                'is_running': self.is_running
            }
    
    def get_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get results of a completed job."""
        return self.job_results.get(job_id)
    
    def shutdown(self):
        """Shutdown the scraper manager."""
        self.is_running = False
        logger.info("Web Scraper Manager shut down")
