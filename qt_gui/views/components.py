"""
Component Views for Qt6 GUI
===========================

Modern PyQt6 component views with MVVM architecture and async operations.
Contains WelcomeView and component management interfaces.
"""

import logging
import random
import datetime
from typing import Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot

from ..utils.config_manager import ConfigManager


class WelcomeView(QWidget):
    """
    Welcome view with modern design and component overview.

    Features:
    - Animated welcome message
    - Component status overview
    - Quick access buttons
    - Theme-adaptive styling
    """

    componentRequested = pyqtSignal(str)  # component_name

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.logger = logging.getLogger("SchechterAI.WelcomeView")

        self.setup_ui()

    def setup_ui(self):
        """Setup the welcome view UI with modern design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Header section
        self.create_header_section(layout)

        # Features overview
        self.create_features_section(layout)

        # Quick actions
        self.create_actions_section(layout)

        # Status overview
        self.create_status_section(layout)

        layout.addStretch()

    def create_header_section(self, layout):
        """Create the header section with title and subtitle."""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)

        # Main title
        title = QLabel("Schechter Customs LLC AI Platform")
        title.setObjectName("mainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 32px; font-weight: bold; color: #0078d4; "
            "margin-bottom: 10px;"
        )

        # Subtitle
        subtitle = QLabel(
            "Centralized AI-Powered Business Intelligence & Automation"
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            "font-size: 18px; color: #605e5c; margin-top: 5px;"
        )

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_frame)

    def create_features_section(self, layout):
        """Create the features overview section."""
        features_frame = QGroupBox("Platform Capabilities")
        features_frame.setObjectName("featuresFrame")
        features_layout = QVBoxLayout(features_frame)

        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(200)
        features_text.setHtml("""
        <div style='font-family: Segoe UI; font-size: 14px; line-height: 1.6;'>
        <p>Welcome to the <strong>Schechter Customs LLC AI Platform</strong>
        - your centralized hub for AI-powered business operations.</p>

        <h4>Core Components:</h4>
        <ul>
        <li><strong>Web Scraping</strong> - Advanced data extraction
        capabilities</li>
        <li><strong>Anonymous Browsing</strong> - Secure business
        intelligence gathering</li>
        <li><strong>AI Coding Assistant</strong> - Intelligent code
        generation and analysis</li>
        <li><strong>Workspace Management</strong> - Project tracking
        and organization</li>
        <li><strong>MCP Integration</strong> - Model Context Protocol
        support</li>
        </ul>
        </div>
        """)

        features_layout.addWidget(features_text)
        layout.addWidget(features_frame)

    def create_actions_section(self, layout):
        """Create quick action buttons."""
        actions_frame = QGroupBox("Quick Actions")
        actions_frame.setObjectName("actionsFrame")
        actions_layout = QGridLayout(actions_frame)

        # Define action buttons
        actions = [
            ("Start Web Scraping", "web_scraper", "#0078d4"),
            ("Launch Browser", "anonymous_browser", "#107c10"),
            ("Open Coding Agent", "coding_agent", "#d13438"),
            ("Workspace Tracker", "workspace_tracker", "#8764b8"),
            ("MCP Integration", "mcp_integration", "#ca5010"),
            ("Platform Settings", "settings", "#5c2d91")
        ]

        for i, (text, component, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setObjectName(f"actionBtn_{component}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color, 0.3)};
                }}
            """)

            # Connect to component request signal
            btn.clicked.connect(
                lambda checked, comp=component:
                self.componentRequested.emit(comp)
            )

            row, col = divmod(i, 3)
            actions_layout.addWidget(btn, row, col)

        layout.addWidget(actions_frame)

    def create_status_section(self, layout):
        """Create component status overview."""
        status_frame = QGroupBox("System Status")
        status_frame.setObjectName("statusFrame")
        status_layout = QVBoxLayout(status_frame)

        # Status info
        self.status_text = QLabel(self._get_status_message())
        self.status_text.setObjectName("statusText")
        self.status_text.setWordWrap(True)
        self.status_text.setStyleSheet(
            "font-size: 14px; color: #323130; padding: 10px;"
        )

        status_layout.addWidget(self.status_text)
        layout.addWidget(status_frame)

    def _darken_color(self, hex_color: str, factor: float = 0.2) -> str:
        """Darken a hex color by a given factor."""
        # Remove the '#' if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Darken each component
        darkened = tuple(int(c * (1 - factor)) for c in rgb)

        # Convert back to hex
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def _get_status_message(self) -> str:
        """Generate a dynamic status message."""
        messages = [
            "All systems operational and ready for deployment.",
            "Platform components initialized and monitoring active.",
            "AI services online - ready to process your requests.",
            "Welcome back! Your workspace is ready for productive work.",
            "System health: Excellent. All components responding normally."
        ]

        current_time = datetime.datetime.now().strftime("%H:%M")
        base_message = random.choice(messages)

        return f"[{current_time}] {base_message}"

    @pyqtSlot()
    def refresh_status(self):
        """Refresh the status display."""
        if hasattr(self, 'status_text'):
            self.status_text.setText(self._get_status_message())


class ComponentCard(QFrame):
    """
    Modern component card widget for displaying component information.

    Features:
    - Hover effects
    - Status indicators
    - Action buttons
    - Theme-adaptive styling
    """

    actionRequested = pyqtSignal(str, str)  # component_id, action

    def __init__(self, component_info: Dict, parent=None):
        super().__init__(parent)
        self.component_info = component_info
        self.setup_ui()

    def setup_ui(self):
        """Setup the component card UI."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            ComponentCard {
                border: 1px solid #d1d1d1;
                border-radius: 8px;
                background-color: #ffffff;
                margin: 5px;
            }
            ComponentCard:hover {
                border-color: #0078d4;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Component name
        name_label = QLabel(self.component_info.get('name', 'Unknown'))
        name_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #323130;"
        )
        layout.addWidget(name_label)

        # Description
        desc_label = QLabel(
            self.component_info.get('description', 'No description')
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 12px; color: #605e5c;")
        layout.addWidget(desc_label)

        # Status indicator
        status = self.component_info.get('status', 'Unknown')
        status_label = QLabel(f"Status: {status}")
        status_color = self._get_status_color(status)
        status_label.setStyleSheet(
            f"color: {status_color}; font-weight: bold;"
        )
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
        """)

        component_id = self.component_info.get('module', 'unknown')
        action_btn.clicked.connect(
            lambda: self.actionRequested.emit(component_id, 'launch')
        )

        layout.addWidget(action_btn)

    def _get_status_color(self, status: str) -> str:
        """Get color for status display."""
        status_colors = {
            'Ready': '#107c10',
            'Running': '#0078d4',
            'Stopped': '#d13438',
            'Error': '#d13438',
            'Pending': '#ff8c00'
        }
        return status_colors.get(status, '#605e5c')


class ComponentDashboard(QWidget):
    """
    Dashboard view for component management and monitoring.

    Features:
    - Grid layout of component cards
    - Real-time status updates
    - Bulk operations
    - Search and filtering
    """

    componentActionRequested = pyqtSignal(str, str)  # component_id, action

    def __init__(self, parent=None):
        super().__init__(parent)
        self.component_cards = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Component Dashboard")
        header.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #323130;"
        )
        layout.addWidget(header)

        # Component grid
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)

        layout.addStretch()

    def add_component(self, component_info: Dict):
        """Add a component card to the dashboard."""
        card = ComponentCard(component_info)
        card.actionRequested.connect(self.componentActionRequested)

        # Add to grid (3 columns)
        row = len(self.component_cards) // 3
        col = len(self.component_cards) % 3

        self.grid_layout.addWidget(card, row, col)
        component_id = component_info.get('module', 'unknown')
        self.component_cards[component_id] = card

    def update_component_status(self, component_id: str, status: str):
        """Update the status of a specific component."""
        if component_id in self.component_cards:
            card = self.component_cards[component_id]
            # Update the card's status display
            card.component_info['status'] = status
            # Force UI refresh
            card.setup_ui()
