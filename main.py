#!/usr/bin/env python3
"""
Central GUI - Main Entry Point
==============================

PyQt6-based AI platform interface with modern architecture.
"""
import sys
import logging
from pathlib import Path

# Add the qt_gui directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 10):
        logger.warning(
            f"Python version {sys.version_info.major}."
            f"{sys.version_info.minor} detected. "
            "Version 3.10+ is recommended."
        )
    
    # Check required packages
    required_packages = [
        'PyQt6',
        'requests',
        'beautifulsoup4',
        'jsonschema',
        'aiohttp',
        'coloredlogs'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing


def main():
    """Main entry point for the Central GUI application."""
    try:
        logger.info("Starting Central GUI Application...")
        
        # Check dependencies
        missing_deps = check_dependencies()
        if missing_deps:
            logger.error(
                f"Missing dependencies: {', '.join(missing_deps)}. "
                "Please run 'pip install -r requirements.txt'"
            )
            return 1
        
        # Import PyQt6 components
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QCoreApplication
            from qt_gui.main_application import MainApplication
        except ImportError as e:
            logger.error(f"Failed to import PyQt6 components: {e}")
            logger.error(
                "Please ensure PyQt6 is installed: "
                "pip install PyQt6>=6.6.0"
            )
            return 1
        
        # Set application properties
        QCoreApplication.setApplicationName("Central GUI")
        QCoreApplication.setApplicationVersion("1.0.0")
        QCoreApplication.setOrganizationName("Schechter Customs LLC")
        
        # Create and run application
        app = MainApplication(sys.argv)
        
        logger.info("Central GUI Application started successfully")
        return app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
