"""
Main Window for Schechter Customs LLC AI Platform
=================================================

Modern Qt6 main window with sidebar navigation and component management.
"""

import logging
from typing import Dict, Optional, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QListWidget, QListWidgetItem, QStackedWidget, QStatusBar,
    QMenuBar, QMenu, QToolBar, QLabel, QPushButton, QMessageBox,
    QProgressBar, QTabWidget, QTabBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from PyQt6.QtGui import QAction, QIcon, QFont

from ..themes.theme_manager import ThemeManager
from ..utils.config_manager import ConfigManager
from .components.component_manager import ComponentManager
from .components import WelcomeView


class MainWindow(QMainWindow):
    """
    Main application window with modern UI and component management.
    
    Features:
    - Tabbed interface for each program/component
    - Dynamic tab creation and management
    - Status monitoring
    - Theme switching
    - Component lifecycle management
    """
    
    # Signals
    closed = pyqtSignal()
    componentActivated = pyqtSignal(str)
    
    def __init__(self, config_manager: ConfigManager, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.theme_manager = theme_manager
        self.logger = logging.getLogger("SchechterAI.MainWindow")
        
        # Component management
        self.component_manager = ComponentManager(self.config_manager, self)
        self.active_component = None
        
        # UI components
        self.tab_widget = None
        self.status_bar = None
        self.component_tabs = {}  # Maps component_id to tab index
        
        # Setup UI
        self._setup_window()
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_status_bar()
        self._setup_components()
        self._setup_connections()
        
        # Load initial state
        self._load_window_state()
        
        self.logger.info("Main window initialized")
        
    def _setup_window(self):
        """Setup basic window properties."""
        self.setWindowTitle("Schechter Customs LLC - AI Platform")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Center window on screen
        self._center_window()
        
    def _center_window(self):
        """Center the window on the screen."""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
        
    def _setup_ui(self):
        """Setup the main UI layout."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup tab widget
        self._setup_tab_widget()
        main_layout.addWidget(self.tab_widget)
        
    def _setup_tab_widget(self):
        """Setup the tab widget for program/component management."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Add welcome tab as default
        welcome_view = WelcomeView(self.config_manager)
        self.tab_widget.addTab(welcome_view, "🏠 Welcome")
        
        # Initialize all component tabs
        self._populate_component_tabs()
        
    def _populate_component_tabs(self):
        """Populate tabs with all available components."""
        # Define component tabs
        component_tabs = [
            ("🤖", "Coding Agent", "coding_agent"),
            ("🌐", "Web Scraper", "web_scraper"),
            ("🔒", "Anonymous Browser", "anonymous_browser"),
            ("📊", "Workspace Tracker", "workspace_tracker"),
            ("🧠", "Ollama LLM", "ollama"),
            ("🧙", "LLM Builder", "llm_builder"),
            ("🔗", "MCP Integration", "mcp"),
            ("🔄", "n8n Automation", "n8n"),
            ("💬", "LLM Chat", "llm_chat"),
            ("🔍", "Code Analysis", "code_analysis"),
            ("⚡", "Ray Cluster", "ray_cluster"),
            ("🎯", "Agent Orchestrator", "agent_orchestrator"),
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, name, component_id in component_tabs:
            # Get component widget
            component = self.component_manager.get_component(component_id)
            if component and hasattr(component, 'get_widget'):
                widget = component.get_widget()
                if widget:
                    tab_index = self.tab_widget.addTab(widget, f"{icon} {name}")
                    self.component_tabs[component_id] = tab_index
            else:
                # Create placeholder widget for missing components
                placeholder = QWidget()
                layout = QVBoxLayout(placeholder)
                label = QLabel(f"{name} - Component not available")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
                tab_index = self.tab_widget.addTab(placeholder, f"{icon} {name}")
                self.component_tabs[component_id] = tab_index
        
    def _on_tab_changed(self, index: int):
        """Handle tab change event."""
        if index == 0:
            # Welcome tab
            self.active_component = None
            self._update_status_for_component("welcome")
        else:
            # Find which component this tab belongs to
            for component_id, tab_index in self.component_tabs.items():
                if tab_index == index:
                    self.active_component = component_id
                    self.component_manager.activate_component(component_id)
                    self.componentActivated.emit(component_id)
                    self._update_status_for_component(component_id)
                    break
        
    def _setup_menu_bar(self):
        """Setup the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Add actions
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_tabs_action = QAction("Toggle &Tab Bar", self)
        toggle_tabs_action.setShortcut("Ctrl+B")
        toggle_tabs_action.triggered.connect(self._toggle_tab_bar)
        view_menu.addAction(toggle_tabs_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(lambda: self._show_component("settings"))
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _setup_toolbar(self):
        """Setup the application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Add common actions
        refresh_action = QAction("🔄", self)
        refresh_action.setToolTip("Refresh Current Component")
        refresh_action.triggered.connect(self._refresh_current_component)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Component status indicators
        self.component_status_label = QLabel("Ready")
        toolbar.addWidget(self.component_status_label)
        
        # Add theme toggle to toolbar
        self._add_theme_button_to_toolbar()
        
    def _setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Connection status
        self.connection_label = QLabel("●")
        self.connection_label.setStyleSheet("color: green;")
        self.connection_label.setToolTip("Connection Status")
        self.status_bar.addPermanentWidget(self.connection_label)
        
    def _setup_components(self):
        """Initialize and setup all AI components."""
        # Components are already initialized in ComponentManager.__init__()
        # Component tabs are added in _populate_component_tabs()
        pass
                    
    def _setup_connections(self):
        """Setup signal connections."""
        # Component manager signals
        self.component_manager.componentStatusChanged.connect(self._on_component_status_changed)
        self.component_manager.componentError.connect(self._on_component_error)
        
        # Theme manager signals
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        
    def _add_theme_button_to_toolbar(self):
        """Add theme toggle button to toolbar."""
        toolbar = self.findChild(QToolBar, "Main Toolbar")
        if toolbar:
            toolbar.addSeparator()
            theme_action = QAction("🎨 Toggle Theme", self)
            theme_action.setToolTip("Toggle between light and dark themes")
            theme_action.triggered.connect(self._toggle_theme)
            toolbar.addAction(theme_action)
        
    def _show_component(self, component_id: str):
        """Show the specified component by switching to its tab."""
        if component_id == "welcome":
            self.tab_widget.setCurrentIndex(0)
        elif component_id in self.component_tabs:
            tab_index = self.component_tabs[component_id]
            self.tab_widget.setCurrentIndex(tab_index)
        
    def _update_status_for_component(self, component_id: str):
        """Update status bar for the active component."""
        if not hasattr(self, 'status_label') or not self.status_label:
            return
            
        if component_id == "welcome":
            self.status_label.setText("Welcome to Schechter AI Platform")
        else:
            component = self.component_manager.get_component(component_id)
            if component:
                status = component.get_status()
                self.status_label.setText(f"{component_id.title()}: {status}")
                
    def _on_component_status_changed(self, component_id: str, status: str):
        """Handle component status changes."""
        if hasattr(self, 'status_label') and self.status_label and component_id == self.active_component:
            self.status_label.setText(f"{component_id.title()}: {status}")
            
        # Update component status indicator
        if hasattr(self, 'component_status_label') and self.component_status_label:
            self.component_status_label.setText(f"Components: {len(self.component_manager.get_active_components())} active")
        
    def _on_component_error(self, component_id: str, error: str):
        """Handle component errors."""
        self.logger.error(f"Component {component_id} error: {error}")
        
        # Show error in status bar
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(f"Error in {component_id}: {error}")
        
        # Show error dialog if it's the active component
        if component_id == self.active_component:
            QMessageBox.warning(
                self,
                f"{component_id.title()} Error",
                f"An error occurred in {component_id}:\\n\\n{error}"
            )
            
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        current_theme = self.config_manager.get('appearance.theme', 'dark')
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        
        self.config_manager.set('appearance.theme', new_theme)
        self.theme_manager.apply_theme(new_theme)
        
    def _on_theme_changed(self, theme: str):
        """Handle theme changes."""
        self.logger.info(f"Theme changed to: {theme}")
        
    def _toggle_tab_bar(self):
        """Toggle tab bar visibility."""
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setVisible(not tab_bar.isVisible())
        
    def _refresh_current_component(self):
        """Refresh the currently active component."""
        if self.active_component:
            component = self.component_manager.get_component(self.active_component)
            if component and hasattr(component, 'refresh'):
                component.refresh()
                
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Schechter AI Platform",
            """
            <h3>Schechter Customs LLC - AI Platform</h3>
            <p>Version 1.0.0</p>
            <p>A comprehensive AI automation platform featuring:</p>
            <ul>
            <li>Coding Agent with memory and skills</li>
            <li>Anonymous Browser for business intelligence</li>
            <li>Web Scraper for data collection</li>
            <li>Workspace management and tracking</li>
            <li>LLM integration and MCP support</li>
            </ul>
            <p>© 2025 Schechter Customs LLC</p>
            """
        )
        
    def _load_window_state(self):
        """Load window state from configuration."""
        # This will be called by the application
        pass
        
    def show_progress(self, message: str, progress: int = -1):
        """Show progress in the status bar."""
        self.status_label.setText(message)
        
        if progress >= 0:
            self.progress_bar.setValue(progress)
            self.progress_bar.setVisible(True)
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
    def hide_progress(self):
        """Hide the progress bar."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")
        
    def cleanup(self):
        """Cleanup resources before closing."""
        self.logger.info("Cleaning up main window...")
        
        # Cleanup components
        self.component_manager.cleanup()
        
    def closeEvent(self, event):
        """Handle window close event."""
        self.cleanup()
        self.closed.emit()
        event.accept()
