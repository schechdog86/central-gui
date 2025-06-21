"""
Main Qt6 Application for Schechter Customs LLC AI Platform
==========================================================

This module provides the main application class that initializes and manages
the entire Qt6 GUI system with modern architecture patterns.
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QStyleFactory
from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtGui import QIcon

from .views.main_window import MainWindow
from .themes.theme_manager import ThemeManager
from .utils.logger import setup_logging
from .utils.config_manager import ConfigManager


class SchechterAIApplication(QApplication):
    """
    Main application class for the Schechter Customs LLC AI Platform.
    
    Features:
    - Modern Qt6 interface with theming support
    - Plugin architecture for AI components
    - Asynchronous operation management
    - Comprehensive error handling
    - Settings persistence
    """
    
    # Signals for application-wide events
    themeChanged = pyqtSignal(str)  # Emitted when theme changes
    statusChanged = pyqtSignal(str, str)  # component, status
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Setup basic application properties
        self.setApplicationName("Schechter AI Platform")
        self.setApplicationDisplayName("Schechter Customs LLC - AI Platform")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Schechter Customs LLC")
        self.setOrganizationDomain("schechter-customs.com")
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.theme_manager = ThemeManager(self)
        self.main_window = None
        self.logger = None
        
        # Setup application
        self._setup_logging()
        self._setup_application()
        self._setup_error_handling()
        
    def _setup_logging(self):
        """Setup application-wide logging."""
        self.logger = setup_logging(
            level=self.config_manager.get('logging.level', 'INFO'),
            log_file=self.config_manager.get_log_file_path()
        )
        self.logger.info("Schechter AI Platform starting...")
        
    def _setup_application(self):
        """Setup basic application configuration."""
        # Set application icon
        icon_path = (
            Path(__file__).parent / "resources" / "icons" / "app_icon.png"
        )
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Apply initial theme
        theme_name = self.config_manager.get('appearance.theme', 'dark')
        self.theme_manager.apply_theme(theme_name)
        
        # Setup style
        self.setStyle(QStyleFactory.create('Fusion'))
        
        # Connect signals
        self.themeChanged.connect(self.theme_manager.apply_theme)
        
    def _setup_error_handling(self):
        """Setup global error handling."""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            if self.logger:
                self.logger.error(
                    "Uncaught exception",
                    exc_info=(exc_type, exc_value, exc_traceback)
                )
            
        sys.excepthook = handle_exception
        
    def initialize_main_window(self) -> MainWindow:
        """Initialize and show the main window."""
        if self.main_window is None:
            self.main_window = MainWindow(
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                parent=None
            )
            
            # Connect window signals
            self.main_window.closed.connect(self.quit)
            
            # Restore window state
            self._restore_window_state()
            
        return self.main_window
        
    def show_main_window(self):
        """Show the main application window."""
        if self.main_window is None:
            self.initialize_main_window()
            
        if self.main_window is not None:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        
    def _restore_window_state(self):
        """Restore window geometry and state from settings."""
        settings = QSettings()
        
        if self.main_window is not None:
            # Restore geometry
            geometry = settings.value("window/geometry")
            if geometry:
                self.main_window.restoreGeometry(geometry)
            
            # Restore window state
            state = settings.value("window/state")
            if state:
                self.main_window.restoreState(state)
            
    def _save_window_state(self):
        """Save window geometry and state to settings."""
        if self.main_window:
            settings = QSettings()
            settings.setValue(
                "window/geometry", self.main_window.saveGeometry()
            )
            settings.setValue(
                "window/state", self.main_window.saveState()
            )
            
    def quit(self):
        """Clean shutdown of the application."""
        if self.logger:
            self.logger.info("Schechter AI Platform shutting down...")
        
        # Save window state
        self._save_window_state()
        
        # Save configuration
        self.config_manager.save()
        
        # Cleanup main window
        if self.main_window:
            self.main_window.cleanup()
            
        # Quit application
        super().quit()


def create_application(argv=None) -> SchechterAIApplication:
    """
    Factory function to create the main application.
    
    Args:
        argv: Command line arguments (optional)
        
    Returns:
        Configured SchechterAIApplication instance
    """
    if argv is None:
        argv = sys.argv
        
    # Enable high DPI scaling
    # QApplication.setAttribute(QApplication.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = SchechterAIApplication(argv)
    return app


def main(argv=None):
    """
    Main entry point for the Qt6 GUI application.
    
    Args:
        argv: Command line arguments (optional)
        
    Returns:
        Application exit code
    """
    app = create_application(argv)
    
    try:
        # Initialize and show main window
        app.show_main_window()
        
        # Start event loop
        return app.exec()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    finally:
        app.quit()


if __name__ == "__main__":
    sys.exit(main())
