"""
Configuration management for the Qt6 GUI application.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt6.QtCore import QSettings


class ConfigManager:
    """
    Manages application configuration with both JSON files and Qt settings.

    Features:
    - Hierarchical configuration with dot notation
    - Automatic persistence
    - Default value support
    - Type validation
    """

    def __init__(self, config_dir: Optional[Path] = None):
        self.logger = logging.getLogger("SchechterAI.Config")

        # Setup directories
        if config_dir is None:
            config_dir = Path.home() / ".schechter_ai"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "config.json"
        self.settings = QSettings()
        
        # Default configuration
        self.defaults = {
            'appearance': {
                'theme': 'dark',
                'font_size': 11,
                'font_family': 'Segoe UI'
            },
            'logging': {
                'level': 'INFO',
                'file_enabled': True
            },
            'components': {
                'coding_agent': {
                    'enabled': True,
                    'auto_start': False
                },
                'web_scraper': {
                    'enabled': True,
                    'timeout': 30
                },
                'anonymous_browser': {
                    'enabled': True,
                    'docker_enabled': True
                },
                'workspace_tracker': {
                    'enabled': True,
                    'auto_scan': True
                }
            },
            'ai': {
                'ollama': {
                    'host': 'localhost',
                    'port': 11434,
                    'default_model': 'codellama'
                }
            }
        }
        
        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.logger.info(
                    f"Loaded configuration from {self.config_file}"
                )
                return self._merge_with_defaults(config)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

        # Return defaults if file doesn't exist or loading failed
        self.logger.info("Using default configuration")
        return self.defaults.copy()
        
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults to ensure all keys exist."""
        def merge_dicts(default: Dict, loaded: Dict) -> Dict:
            result = default.copy()
            for key, value in loaded.items():
                if (key in result and isinstance(result[key], dict) and
                        isinstance(value, dict)):
                    result[key] = merge_dicts(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_dicts(self.defaults, config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key in dot notation (e.g., 'appearance.theme')
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

        # Save to Qt settings as well
        self.settings.setValue(key, value)

    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def get_log_file_path(self) -> Path:
        """Get the path for the log file."""
        return self.config_dir / "application.log"

    def get_data_dir(self) -> Path:
        """Get the application data directory."""
        data_dir = self.config_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
