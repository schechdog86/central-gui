"""
Component Views for Qt6 GUI
===========================

Contains component management and welcome view implementations.
"""

import logging
from typing import Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal


class ComponentManager(QWidget):
    """
    Manages AI components and their integration with the GUI.
    
    Features:
    - Component discovery and loading
    - Status monitoring
    - Configuration management
    - Plugin architecture support
    """
    
    componentStatusChanged = pyqtSignal(str, str)  # component_name, status
    componentLoaded = pyqtSignal(str)  # component_name
    componentError = pyqtSignal(str, str)  # component_name, error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("SchechterAI.ComponentManager")
        self.components = {}
        self.component_status = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the component manager UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("AI Component Manager")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #0078d4;"
        )
        layout.addWidget(title)
        
        # Component grid
        self.component_grid = QGridLayout()
        layout.addLayout(self.component_grid)
        
        # Initialize components
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize available AI components."""
        component_info = [
            {
                'name': 'Web Scraper',
                'description': 'Advanced web scraping with manager pattern',
                'status': 'Ready',
                'module': 'web_scraper'
            },
            {
                'name': 'Anonymous Browser',
                'description': 'Business intelligence browser with Docker',
                'status': 'Ready',
                'module': 'anonymous_browser'
            },
            {
                'name': 'Coding Agent',
                'description': 'AI-powered coding assistant',
                'status': 'Pending',
                'module': 'coding_agent'
            },
            {
                'name': 'Workspace Tracker',
                'description': 'Project management and tracking',
                'status': 'Ready',
                'module': 'workspace_tracker'
            },
            {
                'name': 'MCP Integration',
                'description': 'Model Context Protocol integration',
                'status': 'Ready',
                'module': 'mcp_integration'
            }
        ]
        
        for i, comp in enumerate(component_info):
            self.add_component_card(comp, i // 2, i % 2)
            
    def add_component_card(self, component_info: Dict, row: int, col: int):
        """Add a component card to the grid."""
        card = QGroupBox(component_info['name'])
        card.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e1dfdd;
                border-radius: 8px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Description
        desc_label = QLabel(component_info['description'])
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #605e5c; margin: 5px 0;")
        layout.addWidget(desc_label)
        
        # Status
        status_label = QLabel(f"Status: {component_info['status']}")
        if component_info['status'] == 'Ready':
            status_label.setStyleSheet("color: #107c10; font-weight: bold;")
        elif component_info['status'] == 'Pending':
            status_label.setStyleSheet("color: #ff8c00; font-weight: bold;")
        else:
            status_label.setStyleSheet("color: #d13438; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Action button
        action_btn = QPushButton("Launch")
        action_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        action_btn.clicked.connect(lambda: self.launch_component(component_info['module']))
        layout.addWidget(action_btn)
        
        self.component_grid.addWidget(card, row, col)
        
    def launch_component(self, module_name: str):
        """Launch a specific component."""
        self.logger.info(f"Launching component: {module_name}")
        # Implementation will be added as components are integrated
        pass


class WelcomeView(QWidget):
    """
    Welcome screen for the Schechter AI Platform.
    
    Features:
    - Platform overview
    - Quick access to main features
    - System status display
    - Getting started guide
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("SchechterAI.WelcomeView")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the welcome view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Welcome header
        self.create_header(layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Overview
        left_panel = self.create_overview_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Quick actions
        right_panel = self.create_actions_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([2, 1])
        
    def create_header(self, layout):
        """Create the welcome header section."""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Logo/Icon space (placeholder)
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(logo_label)
        
        # Title and subtitle
        title_layout = QVBoxLayout()
        
        title = QLabel("Schechter Customs LLC")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #0078d4;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Centralized AI Platform")
        subtitle.setStyleSheet("font-size: 18px; color: #605e5c; margin-top: 5px;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
    def create_overview_panel(self) -> QWidget:
        """Create the platform overview panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Overview title
        title = QLabel("Platform Overview")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Description
        description = QTextEdit()
        description.setReadOnly(True)
        description.setMaximumHeight(150)
        description.setHtml("""
        <p>Welcome to the <strong>Schechter Customs LLC AI Platform</strong> - your centralized 
        hub for advanced AI-powered tools and services.</p>
        
        <p>This platform integrates multiple AI components including:</p>
        <ul>
        <li><strong>Web Scraping</strong> - Advanced data extraction capabilities</li>
        <li><strong>Anonymous Browsing</strong> - Secure business intelligence gathering</li>
        <li><strong>AI Coding Assistant</strong> - Intelligent code generation and analysis</li>
        <li><strong>Workspace Management</strong> - Project tracking and organization</li>
        <li><strong>MCP Integration</strong> - Model Context Protocol support</li>
        </ul>
        """)
        layout.addWidget(description)
        
        # System status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        # Status indicators
        statuses = [
            ("Core System", "Online", "#107c10"),
            ("AI Components", "Ready", "#107c10"),
            ("Network", "Connected", "#107c10"),
            ("Storage", "Available", "#107c10")
        ]
        
        for name, status, color in statuses:
            status_item = QHBoxLayout()
            status_item.addWidget(QLabel(name))
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            status_item.addWidget(status_label)
            status_item.addStretch()
            status_layout.addLayout(status_item)
            
        layout.addWidget(status_group)
        layout.addStretch()
        
        return panel
        
    def create_actions_panel(self) -> QWidget:
        """Create the quick actions panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Actions title
        title = QLabel("Quick Actions")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Quick action buttons
        actions = [
            ("🌐 Launch Web Scraper", self.launch_web_scraper),
            ("🔒 Anonymous Browser", self.launch_browser),
            ("💻 Coding Assistant", self.launch_coding_agent),
            ("📊 Workspace Tracker", self.launch_workspace),
            ("⚙️ Settings", self.open_settings)
        ]
        
        for text, callback in actions:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    border: 1px solid #e1dfdd;
                    padding: 12px 20px;
                    text-align: left;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e8f4fd;
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #deecf9;
                }
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
            
        layout.addStretch()
        
        return panel
        
    def launch_web_scraper(self):
        """Launch web scraper component."""
        self.logger.info("Launching Web Scraper")
        
    def launch_browser(self):
        """Launch anonymous browser component."""
        self.logger.info("Launching Anonymous Browser")
        
    def launch_coding_agent(self):
        """Launch coding agent component."""
        self.logger.info("Launching Coding Agent")
        
    def launch_workspace(self):
        """Launch workspace tracker component."""
        self.logger.info("Launching Workspace Tracker")
        
    def open_settings(self):
        """Open application settings."""
        self.logger.info("Opening Settings")
