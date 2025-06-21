"""
Mock configuration manager for testing
======================================

Provides a simple config manager that doesn't require file I/O.
"""

class MockConfigManager:
    """Mock configuration manager for testing."""
    
    def __init__(self):
        self.config = {
            'appearance': {
                'theme': 'dark',
                'font_size': 12,
                'font_family': 'Arial'
            },
            'general': {
                'auto_save': True,
                'check_updates': True,
                'language': 'en'
            },
            'paths': {
                'workspace': '/home/user/workspace',
                'projects': '/home/user/projects'
            },
            'components': {
                'coding_agent': {'enabled': True},
                'web_scraper': {'enabled': True},
                'ray_cluster': {'enabled': True},
                'llm_chat': {'enabled': True}
            }
        }
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        parts = key.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """Set a configuration value."""
        parts = key.split('.')
        config = self.config
        
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
    
    def save(self):
        """Mock save method."""
        pass
    
    def load(self):
        """Mock load method."""
        pass
    
    def get_all(self):
        """Get all configuration."""
        return self.config.copy()