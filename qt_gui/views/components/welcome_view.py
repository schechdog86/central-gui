"""
Welcome View for Qt6 GUI
========================

Welcome screen with platform overview and quick actions.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout, QScrollArea, QTextEdit, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPalette, QPainter, QLinearGradient, QColor

from ...utils.config_manager import ConfigManager


class WelcomeView(QWidget):
    """
    Welcome screen with platform overview and component status.
    
    Features:
    - Platform overview
    - Component status grid
    - Quick action buttons
    - System health indicators
    - Recent activity log
    """
    
    # Signals
    componentSelected = pyqtSignal(str)  # component_id
    quickActionRequested = pyqtSignal(str)  # action_name
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.logger = logging.getLogger("SchechterAI.WelcomeView")
        
        # Animation properties
        self.fade_animation = None
        
        self._setup_ui()
        self._setup_animations()
        
        # Update timer for dynamic content
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_dynamic_content)
        self.update_timer.start(5000)  # Update every 5 seconds
        
        self.logger.info("WelcomeView initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(25)
        
        # Header section
        header_widget = self._create_header_section()
        content_layout.addWidget(header_widget)
        
        # Quick stats section
        stats_widget = self._create_stats_section()
        content_layout.addWidget(stats_widget)
        
        # Component status section
        components_widget = self._create_components_section()
        content_layout.addWidget(components_widget)
        
        # Quick actions section
        actions_widget = self._create_actions_section()
        content_layout.addWidget(actions_widget)
        
        # Recent activity section
        activity_widget = self._create_activity_section()
        content_layout.addWidget(activity_widget)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def _create_header_section(self) -> QWidget:
        """Create the header section with logo and welcome message."""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo/Title
        title_label = QLabel("🏢 Schechter Customs LLC")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                margin: 20px;
                padding: 10px;
            }
        """)
        
        # Subtitle
        subtitle_label = QLabel("Centralized AI Platform")
        subtitle_font = QFont()
        subtitle_font.setPointSize(16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #666666;
                margin-bottom: 10px;
            }
        """)
        
        # Welcome message
        welcome_label = QLabel("Welcome to your integrated AI development environment")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                margin-bottom: 20px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(welcome_label)
        
        return header_widget
    
    def _create_stats_section(self) -> QWidget:
        """Create the statistics section."""
        stats_widget = QGroupBox("System Overview")
        stats_layout = QGridLayout(stats_widget)
        
        # System stats
        stats_data = [
            ("Active Components", "3/8", "#4CAF50"),
            ("Total Projects", "12", "#2196F3"),
            ("Tasks Completed", "847", "#FF9800"),
            ("System Health", "98%", "#4CAF50")
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            # Create stat card
            stat_card = self._create_stat_card(label, value, color)
            row = i // 2
            col = i % 2
            stats_layout.addWidget(stat_card, row, col)
        
        return stats_widget
    
    def _create_stat_card(self, label: str, value: str, color: str) -> QWidget:
        """Create a statistics card widget."""
        card_widget = QFrame()
        card_widget.setFrameShape(QFrame.Shape.Box)
        card_widget.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid {color};
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        card_layout = QVBoxLayout(card_widget)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Value
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        
        # Label
        label_widget = QLabel(label)
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_widget.setStyleSheet("color: #888888; font-size: 12px;")
        
        card_layout.addWidget(value_label)
        card_layout.addWidget(label_widget)
        
        return card_widget
    
    def _create_components_section(self) -> QWidget:
        """Create the components status section."""
        components_widget = QGroupBox("Component Status")
        components_layout = QGridLayout(components_widget)
        
        # Component data (will be updated from ComponentManager)
        self.component_cards = {}
        component_data = [
            ("coding-agent", "Coding Agent", "🤖", "stopped"),
            ("anonymous-browser", "Anonymous Browser", "🌐", "stopped"),
            ("web-scraper", "Web Scraper", "🕷️", "stopped"),
            ("workspace-tracker", "Workspace Tracker", "📁", "stopped"),
            ("ollama-llm", "Ollama LLM", "🧠", "stopped"),
            ("mcp-integration", "MCP Integration", "🔗", "stopped"),
            ("code-analysis", "Code Analysis", "🔍", "stopped"),
            ("ray-cluster", "Ray Cluster", "⚡", "stopped")
        ]
        
        for i, (comp_id, name, icon, status) in enumerate(component_data):
            # Create component card
            card = self._create_component_card(comp_id, name, icon, status)
            self.component_cards[comp_id] = card
            
            row = i // 4
            col = i % 4
            components_layout.addWidget(card, row, col)
        
        return components_widget
    
    def _create_component_card(self, comp_id: str, name: str, icon: str, status: str) -> QWidget:
        """Create a component status card."""
        card_widget = QFrame()
        card_widget.setFrameShape(QFrame.Shape.Box)
        card_widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Status colors
        status_colors = {
            'running': '#4CAF50',
            'stopped': '#757575',
            'error': '#F44336',
            'starting': '#FF9800'
        }
        
        color = status_colors.get(status, '#757575')
        card_widget.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
                margin: 3px;
            }}
            QFrame:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                border-color: #2196F3;
            }}
        """)
        
        card_layout = QVBoxLayout(card_widget)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Name
        name_label = QLabel(name)
        name_font = QFont()
        name_font.setPointSize(10)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        
        # Status
        status_label = QLabel(status.title())
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        
        card_layout.addWidget(icon_label)
        card_layout.addWidget(name_label)
        card_layout.addWidget(status_label)
        
        # Store component ID for click handling
        card_widget.comp_id = comp_id
        card_widget.mousePressEvent = lambda event: self.componentSelected.emit(comp_id)
        
        return card_widget
    
    def _create_actions_section(self) -> QWidget:
        """Create the quick actions section."""
        actions_widget = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Quick action buttons
        actions = [
            ("🚀 Start All", "start_all", "#4CAF50"),
            ("⏹️ Stop All", "stop_all", "#F44336"),
            ("🔄 Refresh", "refresh", "#2196F3"),
            ("⚙️ Settings", "settings", "#FF9800"),
            ("📊 Monitor", "monitor", "#9C27B0")
        ]
        
        for text, action, color in actions:
            button = QPushButton(text)
            button.setMinimumSize(120, 50)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 10px;
                    margin: 5px;
                }}
                QPushButton:hover {{
                    background-color: {color}DD;
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background-color: {color}AA;
                }}
            """)
            button.clicked.connect(lambda checked, a=action: self.quickActionRequested.emit(a))
            actions_layout.addWidget(button)
        
        return actions_widget
    
    def _create_activity_section(self) -> QWidget:
        """Create the recent activity section."""
        activity_widget = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_widget)
        
        # Activity log
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setReadOnly(True)
        self.activity_log.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.2);
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                color: #CCCCCC;
            }
        """)
        
        # Add some sample activity
        self._add_activity_entry("System initialized successfully")
        self._add_activity_entry("Configuration loaded from settings")
        self._add_activity_entry("Component registry updated")
        
        activity_layout.addWidget(self.activity_log)
        
        return activity_widget
    
    def _setup_animations(self):
        """Setup UI animations."""
        # Fade animation for dynamic updates
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def _update_dynamic_content(self):
        """Update dynamic content like stats and activity."""
        # This would be connected to real data sources
        # For now, just simulate some activity
        import random
        import datetime
        
        activities = [
            "Health check completed for all components",
            "Configuration auto-saved",
            "Background tasks processed",
            "Memory usage optimized",
            "Cache cleanup performed"
        ]
        
        if random.random() < 0.3:  # 30% chance to add activity
            activity = random.choice(activities)
            self._add_activity_entry(activity)
    
    def _add_activity_entry(self, message: str):
        """Add an entry to the activity log."""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        
        # Add to log
        self.activity_log.append(entry)
        
        # Keep only last 20 entries
        text = self.activity_log.toPlainText()
        lines = text.split('\n')
        if len(lines) > 20:
            lines = lines[-20:]
            self.activity_log.setPlainText('\n'.join(lines))
        
        # Scroll to bottom
        cursor = self.activity_log.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.activity_log.setTextCursor(cursor)
    
    def update_component_status(self, component_id: str, status: str):
        """Update the status of a component card."""
        if component_id in self.component_cards:
            card = self.component_cards[component_id]
            
            # Find status label and update
            for child in card.findChildren(QLabel):
                if hasattr(child, 'text') and child.text().lower() in ['stopped', 'running', 'error', 'starting']:
                    child.setText(status.title())
                    
                    # Update colors
                    status_colors = {
                        'running': '#4CAF50',
                        'stopped': '#757575',
                        'error': '#F44336',
                        'starting': '#FF9800'
                    }
                    
                    color = status_colors.get(status, '#757575')
                    child.setStyleSheet(f"""
                        QLabel {{
                            color: {color};
                            font-size: 10px;
                            font-weight: bold;
                            padding: 2px 6px;
                            border-radius: 3px;
                            background-color: rgba(255, 255, 255, 0.1);
                        }}
                    """)
                    
                    # Update card border
                    card.setStyleSheet(f"""
                        QFrame {{
                            background-color: rgba(255, 255, 255, 0.05);
                            border: 2px solid {color};
                            border-radius: 8px;
                            padding: 10px;
                            margin: 3px;
                        }}
                        QFrame:hover {{
                            background-color: rgba(255, 255, 255, 0.1);
                            border-color: #2196F3;
                        }}
                    """)
                    break
            
            # Add activity log entry
            self._add_activity_entry(f"Component {component_id} status changed to {status}")
    
    def add_activity(self, message: str):
        """Public method to add activity from external sources."""
        self._add_activity_entry(message)
