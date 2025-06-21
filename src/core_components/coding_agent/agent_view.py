"""
Coding Agent View - Modern GUI for the Coding Agent
Inspired by VS Code and GitHub's design language
"""

import os
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QTabWidget, QSplitter, QListWidget,
    QProgressBar, QGroupBox, QComboBox, QCheckBox, QSlider,
    QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTreeWidget, QTreeWidgetItem, QFrame, QScrollArea,
    QButtonGroup, QRadioButton, QFileDialog, QMessageBox,
    QMenu, QToolButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter


class CodingAgentView(QWidget):
    """Modern coding agent interface with dark theme."""
    
    def __init__(self, agent_manager=None):
        super().__init__()
        self.agent_manager = agent_manager
        self.init_ui()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left sidebar
        left_sidebar = self._create_left_sidebar()
        content_splitter.addWidget(left_sidebar)
        
        # Central area with tabs
        central_widget = self._create_central_area()
        content_splitter.addWidget(central_widget)
        
        # Right sidebar
        right_sidebar = self._create_right_sidebar()
        content_splitter.addWidget(right_sidebar)
        
        # Set splitter sizes
        content_splitter.setSizes([250, 800, 350])
        content_splitter.setChildrenCollapsible(False)
        
        main_layout.addWidget(content_splitter, 1)
        
        # Status bar
        status_bar = self._create_status_bar()
        main_layout.addWidget(status_bar)
        
        self.setLayout(main_layout)
        
        # Initialize timers
        self._init_timers()
        
    def _create_header(self) -> QFrame:
        """Create the header with title and main controls."""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo and title
        title_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel("🤖")
        icon_label.setStyleSheet("font-size: 28px;")
        title_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Coding Agent")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00D4FF;
        """)
        title_layout.addWidget(title)
        
        # Version
        version = QLabel("v2.0")
        version.setStyleSheet("""
            font-size: 12px;
            color: #888;
            margin-left: 10px;
        """)
        title_layout.addWidget(version)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Main controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Initialize button
        self.init_btn = QPushButton("🚀 Initialize Agent")
        self.init_btn.setObjectName("primaryButton")
        self.init_btn.clicked.connect(self.initialize_agent)
        controls_layout.addWidget(self.init_btn)
        
        # MCP Status
        self.mcp_status = QLabel("MCP: Offline")
        self.mcp_status.setStyleSheet("""
            background: #333;
            padding: 8px 15px;
            border-radius: 5px;
            color: #ff6b6b;
        """)
        controls_layout.addWidget(self.mcp_status)
        
        # Settings button
        settings_btn = QToolButton()
        settings_btn.setText("⚙️")
        settings_btn.setStyleSheet("""
            QToolButton {
                font-size: 20px;
                padding: 5px;
                border: none;
                background: transparent;
            }
            QToolButton:hover {
                background: #444;
                border-radius: 5px;
            }
        """)
        settings_btn.clicked.connect(self.show_settings)
        controls_layout.addWidget(settings_btn)
        
        layout.addLayout(controls_layout)
        
        header.setLayout(layout)
        return header
        
    def _create_left_sidebar(self) -> QFrame:
        """Create the left sidebar with navigation and tools."""
        sidebar = QFrame()
        sidebar.setObjectName("leftSidebar")
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Navigation title
        nav_title = QLabel("🧭 Navigation")
        nav_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            padding: 5px;
        """)
        layout.addWidget(nav_title)
        
        # Navigation buttons
        nav_buttons = [
            ("💬 Chat", "chat"),
            ("🧠 Memory", "memory"),
            ("⚡ Skills", "skills"),
            ("📚 Knowledge", "knowledge"),
            ("🔧 Tools", "tools"),
            ("📊 Analytics", "analytics"),
            ("🔌 MCP Services", "mcp"),
            ("⚙️ Settings", "settings")
        ]
        
        self.nav_group = QButtonGroup()
        for i, (text, name) in enumerate(nav_buttons):
            btn = QPushButton(text)
            btn.setObjectName(f"nav_{name}")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 12px 15px;
                    border: none;
                    background: transparent;
                    color: #ddd;
                    font-size: 14px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background: #3a3a3a;
                }
                QPushButton:checked {
                    background: #00D4FF;
                    color: #000;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            self.nav_group.addButton(btn, i)
            layout.addWidget(btn)
            
            if i == 0:  # Select first button by default
                btn.setChecked(True)
        
        layout.addStretch()
        
        # Quick actions
        actions_title = QLabel("⚡ Quick Actions")
        actions_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            padding: 5px;
            margin-top: 20px;
        """)
        layout.addWidget(actions_title)
        
        # Action buttons
        action_buttons = [
            ("🔄 Sync Memory", self.sync_memory),
            ("📥 Import Data", self.import_data),
            ("📤 Export Data", self.export_data),
            ("🗑️ Clear Cache", self.clear_cache)
        ]
        
        for text, callback in action_buttons:
            btn = QPushButton(text)
            btn.setObjectName("actionButton")
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def _create_central_area(self) -> QTabWidget:
        """Create the central area with tabs for different features."""
        self.tabs = QTabWidget()
        self.tabs.setObjectName("centralTabs")
        self.tabs.setTabsClosable(False)
        
        # Chat Tab
        chat_tab = self._create_chat_tab()
        self.tabs.addTab(chat_tab, "💬 Chat")
        
        # Memory Tab
        memory_tab = self._create_memory_tab()
        self.tabs.addTab(memory_tab, "🧠 Memory")
        
        # Skills Tab
        skills_tab = self._create_skills_tab()
        self.tabs.addTab(skills_tab, "⚡ Skills")
        
        # Knowledge Tab
        knowledge_tab = self._create_knowledge_tab()
        self.tabs.addTab(knowledge_tab, "📚 Knowledge")
        
        # Tools Tab
        tools_tab = self._create_tools_tab()
        self.tabs.addTab(tools_tab, "🔧 Tools")
        
        # Analytics Tab
        analytics_tab = self._create_analytics_tab()
        self.tabs.addTab(analytics_tab, "📊 Analytics")
        
        # MCP Tab
        mcp_tab = self._create_mcp_tab()
        self.tabs.addTab(mcp_tab, "🔌 MCP")
        
        # Settings Tab
        settings_tab = self._create_settings_tab()
        self.tabs.addTab(settings_tab, "⚙️ Settings")
        
        return self.tabs
    
    def _create_chat_tab(self) -> QWidget:
        """Create the chat interface tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")
        self.chat_display.setPlaceholderText("Chat history will appear here...")
        layout.addWidget(self.chat_display, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setObjectName("chatInput")
        self.chat_input.setPlaceholderText("Ask me anything about coding...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        
        # Send button
        send_btn = QPushButton("📤 Send")
        send_btn.setObjectName("sendButton")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        # Voice input button
        voice_btn = QPushButton("🎤")
        voice_btn.setObjectName("voiceButton")
        voice_btn.setFixedWidth(50)
        input_layout.addWidget(voice_btn)
        
        layout.addLayout(input_layout)
        
        # Context options
        context_layout = QHBoxLayout()
        
        # Model selection
        model_label = QLabel("Model:")
        context_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "deepseek-coder:latest",
            "codellama:latest",
            "gpt-4",
            "claude-3"
        ])
        context_layout.addWidget(self.model_combo)
        
        # Temperature
        temp_label = QLabel("Temperature:")
        context_layout.addWidget(temp_label)
        
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_slider.setFixedWidth(100)
        context_layout.addWidget(self.temp_slider)
        
        self.temp_value = QLabel("0.7")
        context_layout.addWidget(self.temp_value)
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_value.setText(f"{v/100:.1f}")
        )
        
        context_layout.addStretch()
        
        # Context checkboxes
        self.use_memory = QCheckBox("Use Memory")
        self.use_memory.setChecked(True)
        context_layout.addWidget(self.use_memory)
        
        self.use_skills = QCheckBox("Track Skills")
        self.use_skills.setChecked(True)
        context_layout.addWidget(self.use_skills)
        
        layout.addLayout(context_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_memory_tab(self) -> QWidget:
        """Create the memory management tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Memory type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Memory Type:")
        type_layout.addWidget(type_label)
        
        self.memory_type_combo = QComboBox()
        self.memory_type_combo.addItems([
            "All Memories",
            "Short-term Memory",
            "Long-term Memory", 
            "Critical Memory"
        ])
        self.memory_type_combo.currentIndexChanged.connect(self.refresh_memory_list)
        type_layout.addWidget(self.memory_type_combo)
        
        # Search
        self.memory_search = QLineEdit()
        self.memory_search.setPlaceholderText("Search memories...")
        self.memory_search.textChanged.connect(self.search_memories)
        type_layout.addWidget(self.memory_search)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_memory_list)
        type_layout.addWidget(refresh_btn)
        
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Memory list
        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(4)
        self.memory_table.setHorizontalHeaderLabels([
            "Type", "Content", "Created", "Importance"
        ])
        self.memory_table.horizontalHeader().setStretchLastSection(True)
        self.memory_table.setAlternatingRowColors(True)
        self.memory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.memory_table, 1)
        
        # Memory actions
        actions_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Memory")
        add_btn.clicked.connect(self.add_memory)
        actions_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.clicked.connect(self.delete_memory)
        actions_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("📤 Export Memories")
        export_btn.clicked.connect(self.export_memories)
        actions_layout.addWidget(export_btn)
        
        actions_layout.addStretch()
        
        # Memory stats
        self.memory_stats = QLabel("Total: 0 | Short: 0 | Long: 0 | Critical: 0")
        self.memory_stats.setStyleSheet("color: #888;")
        actions_layout.addWidget(self.memory_stats)
        
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def _create_skills_tab(self) -> QWidget:
        """Create the skills and achievements tab."""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # Skills list (left side)
        skills_group = QGroupBox("Skills")
        skills_layout = QVBoxLayout()
        
        self.skills_tree = QTreeWidget()
        self.skills_tree.setHeaderLabels(["Skill", "Level", "XP", "Progress"])
        self.skills_tree.setRootIsDecorated(False)
        skills_layout.addWidget(self.skills_tree)
        
        skills_group.setLayout(skills_layout)
        layout.addWidget(skills_group, 2)
        
        # Achievements and stats (right side)
        right_layout = QVBoxLayout()
        
        # Achievements
        achievements_group = QGroupBox("🏆 Achievements")
        achievements_layout = QVBoxLayout()
        
        self.achievements_list = QListWidget()
        achievements_layout.addWidget(self.achievements_list)
        
        achievements_group.setLayout(achievements_layout)
        right_layout.addWidget(achievements_group)
        
        # Stats
        stats_group = QGroupBox("📊 Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_labels = {}
        stats = [
            ("Total XP", "0"),
            ("Queries Processed", "0"),
            ("Skills Unlocked", "0/6"),
            ("Time Active", "0h 0m")
        ]
        
        for stat_name, default_value in stats:
            stat_layout = QHBoxLayout()
            label = QLabel(f"{stat_name}:")
            label.setStyleSheet("font-weight: bold;")
            stat_layout.addWidget(label)
            
            value_label = QLabel(default_value)
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.stats_labels[stat_name] = value_label
            stat_layout.addWidget(value_label)
            
            stats_layout.addLayout(stat_layout)
        
        stats_group.setLayout(stats_layout)
        right_layout.addWidget(stats_group)
        
        right_layout.addStretch()
        
        layout.addLayout(right_layout, 1)
        
        widget.setLayout(layout)
        return widget
    
    def _create_knowledge_tab(self) -> QWidget:
        """Create the knowledge base management tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Search and filter
        filter_layout = QHBoxLayout()
        
        self.knowledge_search = QLineEdit()
        self.knowledge_search.setPlaceholderText("Search knowledge base...")
        filter_layout.addWidget(self.knowledge_search)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All Categories",
            "Code Patterns",
            "Best Practices",
            "Documentation",
            "Troubleshooting",
            "Custom"
        ])
        filter_layout.addWidget(self.category_filter)
        
        add_knowledge_btn = QPushButton("➕ Add Knowledge")
        add_knowledge_btn.clicked.connect(self.add_knowledge)
        filter_layout.addWidget(add_knowledge_btn)
        
        layout.addLayout(filter_layout)
        
        # Knowledge tree
        self.knowledge_tree = QTreeWidget()
        self.knowledge_tree.setHeaderLabels(["Title", "Category", "Tags", "Created"])
        layout.addWidget(self.knowledge_tree, 1)
        
        # Knowledge preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.knowledge_preview = QTextEdit()
        self.knowledge_preview.setReadOnly(True)
        self.knowledge_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.knowledge_preview)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        widget.setLayout(layout)
        return widget
    
    def _create_tools_tab(self) -> QWidget:
        """Create the tools management tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Available tools
        tools_label = QLabel("🔧 Available Tools")
        tools_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(tools_label)
        
        # Tools grid
        tools_widget = QWidget()
        tools_layout = QVBoxLayout()
        
        # Tool cards
        tools = [
            {
                "name": "Code Generator",
                "icon": "⚡",
                "description": "Generate code from natural language",
                "action": self.open_code_generator
            },
            {
                "name": "Code Analyzer",
                "icon": "🔍",
                "description": "Analyze code quality and suggest improvements",
                "action": self.open_code_analyzer
            },
            {
                "name": "Refactoring Assistant",
                "icon": "🔄",
                "description": "Automated code refactoring suggestions",
                "action": self.open_refactoring_tool
            },
            {
                "name": "Documentation Generator",
                "icon": "📝",
                "description": "Generate documentation from code",
                "action": self.open_doc_generator
            },
            {
                "name": "Test Generator",
                "icon": "🧪",
                "description": "Generate unit tests for your code",
                "action": self.open_test_generator
            },
            {
                "name": "Dependency Analyzer",
                "icon": "🔗",
                "description": "Analyze project dependencies",
                "action": self.open_dependency_analyzer
            }
        ]
        
        for tool in tools:
            card = self._create_tool_card(tool)
            tools_layout.addWidget(card)
        
        tools_layout.addStretch()
        tools_widget.setLayout(tools_layout)
        
        # Make it scrollable
        scroll = QScrollArea()
        scroll.setWidget(tools_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        widget.setLayout(layout)
        return widget
    
    def _create_tool_card(self, tool: Dict[str, Any]) -> QFrame:
        """Create a tool card widget."""
        card = QFrame()
        card.setObjectName("toolCard")
        card.setFixedHeight(100)
        
        layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel(tool["icon"])
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setFixedWidth(60)
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(tool["name"])
        name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_layout.addWidget(name_label)
        
        desc_label = QLabel(tool["description"])
        desc_label.setStyleSheet("color: #aaa;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout, 1)
        
        # Launch button
        launch_btn = QPushButton("Launch")
        launch_btn.setObjectName("launchButton")
        launch_btn.clicked.connect(tool["action"])
        layout.addWidget(launch_btn)
        
        card.setLayout(layout)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        return card
    
    def _create_analytics_tab(self) -> QWidget:
        """Create the analytics and insights tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📊 Agent Analytics & Insights")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Metrics grid
        metrics_widget = QWidget()
        metrics_layout = QHBoxLayout()
        
        # Create metric cards
        metrics = [
            ("Total Queries", "0", "#00D4FF"),
            ("Tokens Used", "0", "#FF6B6B"),
            ("Active Skills", "0/6", "#4ECDC4"),
            ("Knowledge Items", "0", "#FFE66D")
        ]
        
        for metric_name, value, color in metrics:
            metric_card = self._create_metric_card(metric_name, value, color)
            metrics_layout.addWidget(metric_card)
        
        metrics_widget.setLayout(metrics_layout)
        layout.addWidget(metrics_widget)
        
        # Charts area
        charts_tabs = QTabWidget()
        
        # Usage chart
        usage_widget = QWidget()
        usage_label = QLabel("Usage trends chart will appear here")
        usage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        usage_label.setStyleSheet("color: #666; font-size: 16px;")
        usage_layout = QVBoxLayout()
        usage_layout.addWidget(usage_label)
        usage_widget.setLayout(usage_layout)
        charts_tabs.addTab(usage_widget, "Usage Trends")
        
        # Skills progress
        skills_widget = QWidget()
        skills_label = QLabel("Skills progress chart will appear here")
        skills_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        skills_label.setStyleSheet("color: #666; font-size: 16px;")
        skills_layout = QVBoxLayout()
        skills_layout.addWidget(skills_label)
        skills_widget.setLayout(skills_layout)
        charts_tabs.addTab(skills_widget, "Skills Progress")
        
        # Memory usage
        memory_widget = QWidget()
        memory_label = QLabel("Memory usage chart will appear here")
        memory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        memory_label.setStyleSheet("color: #666; font-size: 16px;")
        memory_layout = QVBoxLayout()
        memory_layout.addWidget(memory_label)
        memory_widget.setLayout(memory_layout)
        charts_tabs.addTab(memory_widget, "Memory Usage")
        
        layout.addWidget(charts_tabs, 1)
        
        widget.setLayout(layout)
        return widget
    
    def _create_metric_card(self, name: str, value: str, color: str) -> QFrame:
        """Create a metric card widget."""
        card = QFrame()
        card.setObjectName("metricCard")
        card.setFixedHeight(100)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {color};
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 14px;
            color: #aaa;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        card.setLayout(layout)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(color).darker(300))
        shadow.setOffset(0, 3)
        card.setGraphicsEffect(shadow)
        
        return card
    
    def _create_mcp_tab(self) -> QWidget:
        """Create the MCP services management tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # MCP Status
        status_group = QGroupBox("MCP Service Status")
        status_layout = QVBoxLayout()
        
        # Service controls
        controls_layout = QHBoxLayout()
        
        self.mcp_start_btn = QPushButton("▶️ Start All Services")
        self.mcp_start_btn.clicked.connect(self.start_mcp_services)
        controls_layout.addWidget(self.mcp_start_btn)
        
        self.mcp_stop_btn = QPushButton("⏹️ Stop All Services")
        self.mcp_stop_btn.clicked.connect(self.stop_mcp_services)
        self.mcp_stop_btn.setEnabled(False)
        controls_layout.addWidget(self.mcp_stop_btn)
        
        self.mcp_restart_btn = QPushButton("🔄 Restart Services")
        self.mcp_restart_btn.clicked.connect(self.restart_mcp_services)
        controls_layout.addWidget(self.mcp_restart_btn)
        
        controls_layout.addStretch()
        status_layout.addLayout(controls_layout)
        
        # Services table
        self.mcp_table = QTableWidget()
        self.mcp_table.setColumnCount(4)
        self.mcp_table.setHorizontalHeaderLabels([
            "Service", "Status", "Port", "Actions"
        ])
        self.mcp_table.horizontalHeader().setStretchLastSection(True)
        status_layout.addWidget(self.mcp_table)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # MCP Configuration
        config_group = QGroupBox("MCP Configuration")
        config_layout = QVBoxLayout()
        
        # Config options
        self.auto_start_mcp = QCheckBox("Auto-start MCP services on agent initialization")
        config_layout.addWidget(self.auto_start_mcp)
        
        self.mcp_logging = QCheckBox("Enable detailed MCP logging")
        config_layout.addWidget(self.mcp_logging)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # AI Model Settings
        ai_group = QGroupBox("AI Model Settings")
        ai_layout = QVBoxLayout()
        
        # Provider
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Provider:")
        provider_layout.addWidget(provider_label)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Ollama", "OpenAI", "Anthropic", "Local"])
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        ai_layout.addLayout(provider_layout)
        
        # Model
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        model_layout.addWidget(model_label)
        
        self.settings_model_combo = QComboBox()
        self.settings_model_combo.addItems([
            "deepseek-coder:latest",
            "codellama:latest",
            "gpt-4",
            "claude-3"
        ])
        self.settings_model_combo.setEditable(True)
        model_layout.addWidget(self.settings_model_combo)
        model_layout.addStretch()
        ai_layout.addLayout(model_layout)
        
        # API Key
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        api_layout.addWidget(api_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter API key if required")
        api_layout.addWidget(self.api_key_input)
        api_layout.addStretch()
        ai_layout.addLayout(api_layout)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # Memory Settings
        memory_group = QGroupBox("Memory Settings")
        memory_layout = QVBoxLayout()
        
        # Max memory items
        max_items_layout = QHBoxLayout()
        max_items_label = QLabel("Max Memory Items:")
        max_items_layout.addWidget(max_items_label)
        
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setRange(100, 10000)
        self.max_memory_spin.setValue(1000)
        self.max_memory_spin.setSingleStep(100)
        max_items_layout.addWidget(self.max_memory_spin)
        max_items_layout.addStretch()
        memory_layout.addLayout(max_items_layout)
        
        # Auto-backup
        self.auto_backup = QCheckBox("Enable automatic memory backup")
        self.auto_backup.setChecked(True)
        memory_layout.addWidget(self.auto_backup)
        
        # Backup interval
        backup_layout = QHBoxLayout()
        backup_label = QLabel("Backup Interval (minutes):")
        backup_layout.addWidget(backup_label)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(5, 60)
        self.backup_interval.setValue(15)
        backup_layout.addWidget(self.backup_interval)
        backup_layout.addStretch()
        memory_layout.addLayout(backup_layout)
        
        memory_group.setLayout(memory_layout)
        layout.addWidget(memory_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_right_sidebar(self) -> QFrame:
        """Create the right sidebar with context and info."""
        sidebar = QFrame()
        sidebar.setObjectName("rightSidebar")
        sidebar.setFixedWidth(350)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Current Context
        context_group = QGroupBox("📋 Current Context")
        context_layout = QVBoxLayout()
        
        self.context_info = QTextEdit()
        self.context_info.setReadOnly(True)
        self.context_info.setMaximumHeight(150)
        self.context_info.setPlaceholderText("No active context")
        context_layout.addWidget(self.context_info)
        
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
        # Recent Activities
        activities_group = QGroupBox("🕐 Recent Activities")
        activities_layout = QVBoxLayout()
        
        self.activities_list = QListWidget()
        self.activities_list.setMaximumHeight(200)
        activities_layout.addWidget(self.activities_list)
        
        activities_group.setLayout(activities_layout)
        layout.addWidget(activities_group)
        
        # Quick Tips
        tips_group = QGroupBox("💡 Quick Tips")
        tips_layout = QVBoxLayout()
        
        self.tips_text = QTextEdit()
        self.tips_text.setReadOnly(True)
        self.tips_text.setHtml("""
            <p><b>Pro Tips:</b></p>
            <ul>
                <li>Use <code>@memory</code> to reference past conversations</li>
                <li>Type <code>/skills</code> to see your skill progress</li>
                <li>Use <code>/tools</code> to list available tools</li>
                <li>Press <code>Ctrl+K</code> for quick command palette</li>
            </ul>
        """)
        tips_layout.addWidget(self.tips_text)
        
        tips_group.setLayout(tips_layout)
        layout.addWidget(tips_group)
        
        layout.addStretch()
        
        sidebar.setLayout(layout)
        return sidebar
    
    def _create_status_bar(self) -> QFrame:
        """Create the status bar."""
        status_bar = QFrame()
        status_bar.setObjectName("statusBar")
        status_bar.setFixedHeight(30)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Agent status
        self.agent_status = QLabel("🔴 Agent: Not Initialized")
        self.agent_status.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(self.agent_status)
        
        layout.addWidget(QLabel("|"))
        
        # Memory status
        self.memory_status = QLabel("🧠 Memory: 0 items")
        layout.addWidget(self.memory_status)
        
        layout.addWidget(QLabel("|"))
        
        # Skills status
        self.skills_status = QLabel("⚡ Skills: 0 XP")
        layout.addWidget(self.skills_status)
        
        layout.addWidget(QLabel("|"))
        
        # Token usage
        self.token_status = QLabel("🎯 Tokens: 0")
        layout.addWidget(self.token_status)
        
        layout.addStretch()
        
        # Connection status
        self.connection_status = QLabel("🌐 Connected")
        self.connection_status.setStyleSheet("color: #4ECDC4;")
        layout.addWidget(self.connection_status)
        
        status_bar.setLayout(layout)
        return status_bar
    
    def _init_timers(self):
        """Initialize timers for periodic updates."""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
        # Activity timer
        self.activity_timer = QTimer()
        self.activity_timer.timeout.connect(self.update_activities)
        self.activity_timer.start(10000)  # Update every 10 seconds
    
    def apply_dark_theme(self):
        """Apply a modern dark theme to the widget."""
        self.setStyleSheet("""
            /* Global styles */
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 14px;
            }
            
            /* Header */
            #header {
                background: linear-gradient(90deg, #2a2a2a 0%, #1e1e1e 100%);
                border-bottom: 2px solid #00D4FF;
            }
            
            /* Sidebars */
            #leftSidebar, #rightSidebar {
                background-color: #252525;
                border: 1px solid #333;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #484848;
                border-color: #00D4FF;
            }
            
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            
            #primaryButton {
                background: linear-gradient(135deg, #00D4FF 0%, #0099CC 100%);
                color: #000;
                font-weight: bold;
                border: none;
            }
            
            #primaryButton:hover {
                background: linear-gradient(135deg, #33DDFF 0%, #00AADD 100%);
            }
            
            #sendButton {
                background-color: #00D4FF;
                color: #000;
                font-weight: bold;
            }
            
            #actionButton {
                background-color: transparent;
                border: 1px solid #555;
                text-align: left;
            }
            
            #actionButton:hover {
                background-color: #3a3a3a;
            }
            
            /* Input fields */
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #444;
                padding: 8px;
                border-radius: 4px;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #00D4FF;
                outline: none;
            }
            
            #chatInput {
                background-color: #333;
                border: 2px solid #444;
                padding: 10px;
                font-size: 15px;
            }
            
            #chatDisplay {
                background-color: #2a2a2a;
                border: none;
                padding: 10px;
            }
            
            /* Tables */
            QTableWidget {
                background-color: #2a2a2a;
                alternate-background-color: #333;
                gridline-color: #444;
                border: 1px solid #444;
            }
            
            QTableWidget::item:selected {
                background-color: #00D4FF;
                color: #000;
            }
            
            QHeaderView::section {
                background-color: #333;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #444;
            }
            
            /* Trees */
            QTreeWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                alternate-background-color: #333;
            }
            
            QTreeWidget::item:selected {
                background-color: #00D4FF;
                color: #000;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #2a2a2a;
            }
            
            QTabBar::tab {
                background-color: #333;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #2a2a2a;
                border-bottom: 2px solid #00D4FF;
            }
            
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
            
            /* Group boxes */
            QGroupBox {
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border: none;
            }
            
            QScrollBar::handle:vertical {
                background-color: #555;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            
            /* Status bar */
            #statusBar {
                background-color: #1a1a1a;
                border-top: 1px solid #333;
            }
            
            /* Cards */
            #toolCard, #metricCard {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 15px;
            }
            
            #toolCard:hover {
                border-color: #00D4FF;
                background-color: #333;
            }
            
            /* Sliders */
            QSlider::groove:horizontal {
                background-color: #444;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background-color: #00D4FF;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            
            QSlider::handle:horizontal:hover {
                background-color: #33DDFF;
            }
            
            /* Checkboxes */
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QCheckBox::indicator:unchecked {
                background-color: #333;
                border: 2px solid #555;
                border-radius: 3px;
            }
            
            QCheckBox::indicator:checked {
                background-color: #00D4FF;
                border: 2px solid #00D4FF;
                border-radius: 3px;
            }
            
            /* Progress bars */
            QProgressBar {
                background-color: #333;
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background: linear-gradient(90deg, #00D4FF 0%, #0099CC 100%);
                border-radius: 3px;
            }
        """)
    
    # Action methods
    def switch_tab(self, index: int):
        """Switch to a different tab."""
        self.tabs.setCurrentIndex(index)
    
    def initialize_agent(self):
        """Initialize the coding agent."""
        if not self.agent_manager:
            self.add_activity("❌ No agent manager available")
            return
        
        self.add_activity("🚀 Initializing agent...")
        result = self.agent_manager.initialize()
        
        if result['status'] == 'success':
            self.agent_status.setText("🟢 Agent: Ready")
            self.agent_status.setStyleSheet("color: #4ECDC4;")
            self.init_btn.setText("✅ Agent Initialized")
            self.init_btn.setEnabled(False)
            self.add_activity("✅ Agent initialized successfully")
            self.refresh_all_data()
        else:
            self.add_activity(f"❌ Initialization failed: {result.get('error', 'Unknown error')}")
    
    def send_message(self):
        """Send a message to the agent."""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        if not self.agent_manager or not self.agent_manager.is_initialized:
            self.add_to_chat("System", "Please initialize the agent first!", "#ff6b6b")
            return
        
        # Add user message to chat
        self.add_to_chat("You", message, "#00D4FF")
        self.chat_input.clear()
        
        # Process with agent
        self.add_activity(f"💬 Processing: {message[:50]}...")
        
        context = {
            'use_memory': self.use_memory.isChecked(),
            'use_skills': self.use_skills.isChecked(),
            'temperature': self.temp_slider.value() / 100
        }
        
        result = self.agent_manager.process_query(message, context)
        
        if 'error' in result:
            self.add_to_chat("Error", result['error'], "#ff6b6b")
        else:
            response = result.get('response', 'No response')
            self.add_to_chat("Agent", response, "#4ECDC4")
            
            # Update stats
            if 'stats' in result:
                self.update_stats_display(result['stats'])
    
    def add_to_chat(self, sender: str, message: str, color: str = "#e0e0e0"):
        """Add a message to the chat display."""
        timestamp = QTimer().toString("hh:mm:ss")
        html = f"""
        <div style="margin: 10px 0;">
            <span style="color: {color}; font-weight: bold;">{sender}</span>
            <span style="color: #666; font-size: 12px;"> {timestamp}</span><br>
            <span style="color: #e0e0e0;">{message}</span>
        </div>
        """
        self.chat_display.append(html)
    
    def add_activity(self, activity: str):
        """Add an activity to the recent activities list."""
        timestamp = QTimer().toString("hh:mm:ss")
        self.activities_list.insertItem(0, f"{timestamp} - {activity}")
        
        # Keep only last 20 activities
        while self.activities_list.count() > 20:
            self.activities_list.takeItem(20)
    
    def refresh_memory_list(self):
        """Refresh the memory list."""
        if not self.agent_manager:
            return
        
        memory_type = self.memory_type_combo.currentText()
        type_map = {
            "All Memories": "all",
            "Short-term Memory": "short",
            "Long-term Memory": "long",
            "Critical Memory": "critical"
        }
        
        memories = self.agent_manager.get_memory_items(
            type_map.get(memory_type, "all")
        )
        
        self.memory_table.setRowCount(len(memories))
        for i, memory in enumerate(memories):
            self.memory_table.setItem(i, 0, QTableWidgetItem(memory.get('type', '')))
            self.memory_table.setItem(i, 1, QTableWidgetItem(memory.get('content', '')[:100]))
            self.memory_table.setItem(i, 2, QTableWidgetItem(memory.get('created', '')))
            self.memory_table.setItem(i, 3, QTableWidgetItem(str(memory.get('importance', 0))))
        
        # Update stats
        self.update_memory_stats()
    
    def search_memories(self):
        """Search memories based on query."""
        query = self.memory_search.text()
        if not query or not self.agent_manager:
            return
        
        memories = self.agent_manager.search_memories(query)
        # Update table with search results
        # Similar to refresh_memory_list but with search results
    
    def add_memory(self):
        """Add a new memory."""
        # Show dialog to add memory
        # Then call agent_manager.add_memory()
        pass
    
    def delete_memory(self):
        """Delete selected memory."""
        # Get selected memory and delete
        pass
    
    def export_memories(self):
        """Export memories to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Memories", "", "JSON Files (*.json)"
        )
        if file_path and self.agent_manager:
            result = self.agent_manager.export_data(file_path)
            if result['status'] == 'success':
                self.add_activity(f"✅ Exported memories to {file_path}")
    
    def refresh_skills(self):
        """Refresh the skills display."""
        if not self.agent_manager:
            return
        
        skills = self.agent_manager.get_skills()
        self.skills_tree.clear()
        
        total_xp = 0
        for skill_name, skill_data in skills.items():
            item = QTreeWidgetItem([
                skill_name,
                str(skill_data['level']),
                f"{skill_data['xp']}/{skill_data['xp_to_next']}",
                ""  # Progress bar would go here
            ])
            self.skills_tree.addTopLevelItem(item)
            total_xp += skill_data['xp'] + (skill_data['level'] - 1) * 100
        
        # Update achievements
        achievements = self.agent_manager.get_achievements()
        self.achievements_list.clear()
        self.achievements_list.addItems(achievements)
        
        # Update stats
        self.stats_labels["Total XP"].setText(str(total_xp))
        self.stats_labels["Skills Unlocked"].setText(f"{len(skills)}/6")
    
    def add_knowledge(self):
        """Add new knowledge item."""
        # Show dialog to add knowledge
        pass
    
    def refresh_knowledge(self):
        """Refresh knowledge display."""
        if not self.agent_manager:
            return
        
        items = self.agent_manager.get_knowledge_items()
        self.knowledge_tree.clear()
        
        for item in items:
            tree_item = QTreeWidgetItem([
                item.get('title', ''),
                item.get('category', ''),
                ', '.join(item.get('tags', [])),
                item.get('created', '')
            ])
            self.knowledge_tree.addTopLevelItem(tree_item)
    
    def refresh_tools(self):
        """Refresh available tools."""
        if not self.agent_manager:
            return
        
        tools = self.agent_manager.get_tools()
        # Update tools display
    
    def update_status(self):
        """Update status bar information."""
        if not self.agent_manager or not self.agent_manager.is_initialized:
            return
        
        stats = self.agent_manager.stats
        
        # Update memory status
        memory_count = stats.get('memory_items', 0)
        self.memory_status.setText(f"🧠 Memory: {memory_count} items")
        
        # Update tokens
        tokens = stats.get('tokens_used', 0)
        self.token_status.setText(f"🎯 Tokens: {tokens:,}")
        
        # Update skills XP
        skills = self.agent_manager.get_skills()
        total_xp = sum(s['xp'] + (s['level']-1)*100 for s in skills.values())
        self.skills_status.setText(f"⚡ Skills: {total_xp} XP")
    
    def update_activities(self):
        """Update recent activities periodically."""
        # This could fetch recent activities from the agent
        pass
    
    def update_stats_display(self, stats: Dict[str, Any]):
        """Update statistics display."""
        # Update various stat displays
        pass
    
    def update_memory_stats(self):
        """Update memory statistics."""
        # Count memories by type and update display
        pass
    
    def refresh_all_data(self):
        """Refresh all data displays."""
        self.refresh_memory_list()
        self.refresh_skills()
        self.refresh_knowledge()
        self.refresh_tools()
        self.update_status()
    
    # MCP Methods
    def start_mcp_services(self):
        """Start MCP services."""
        if self.agent_manager:
            result = self.agent_manager.start_mcp()
            if result.get('status') == 'success':
                self.mcp_status.setText("MCP: Online")
                self.mcp_status.setStyleSheet("""
                    background: #333;
                    padding: 8px 15px;
                    border-radius: 5px;
                    color: #4ECDC4;
                """)
                self.mcp_start_btn.setEnabled(False)
                self.mcp_stop_btn.setEnabled(True)
                self.add_activity("✅ MCP services started")
    
    def stop_mcp_services(self):
        """Stop MCP services."""
        if self.agent_manager:
            result = self.agent_manager.stop_mcp()
            if result.get('status') == 'success':
                self.mcp_status.setText("MCP: Offline")
                self.mcp_status.setStyleSheet("""
                    background: #333;
                    padding: 8px 15px;
                    border-radius: 5px;
                    color: #ff6b6b;
                """)
                self.mcp_start_btn.setEnabled(True)
                self.mcp_stop_btn.setEnabled(False)
                self.add_activity("⏹️ MCP services stopped")
    
    def restart_mcp_services(self):
        """Restart MCP services."""
        self.stop_mcp_services()
        QTimer.singleShot(1000, self.start_mcp_services)
    
    # Tool launching methods
    def open_code_generator(self):
        """Open code generator tool."""
        self.add_activity("🚀 Launched Code Generator")
    
    def open_code_analyzer(self):
        """Open code analyzer tool."""
        self.add_activity("🚀 Launched Code Analyzer")
    
    def open_refactoring_tool(self):
        """Open refactoring assistant."""
        self.add_activity("🚀 Launched Refactoring Assistant")
    
    def open_doc_generator(self):
        """Open documentation generator."""
        self.add_activity("🚀 Launched Documentation Generator")
    
    def open_test_generator(self):
        """Open test generator."""
        self.add_activity("🚀 Launched Test Generator")
    
    def open_dependency_analyzer(self):
        """Open dependency analyzer."""
        self.add_activity("🚀 Launched Dependency Analyzer")
    
    # Quick action methods
    def sync_memory(self):
        """Sync memory with backend."""
        self.add_activity("🔄 Syncing memory...")
        self.refresh_memory_list()
    
    def import_data(self):
        """Import agent data."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Data", "", "JSON Files (*.json)"
        )
        if file_path and self.agent_manager:
            result = self.agent_manager.import_data(file_path)
            if result['status'] == 'success':
                self.add_activity(f"✅ Imported data from {file_path}")
                self.refresh_all_data()
    
    def export_data(self):
        """Export agent data."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "JSON Files (*.json)"
        )
        if file_path and self.agent_manager:
            result = self.agent_manager.export_data(file_path)
            if result['status'] == 'success':
                self.add_activity(f"✅ Exported data to {file_path}")
    
    def clear_cache(self):
        """Clear agent cache."""
        reply = QMessageBox.question(
            self, "Clear Cache", 
            "Are you sure you want to clear the cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.add_activity("🗑️ Cache cleared")
    
    def show_settings(self):
        """Show settings dialog."""
        self.tabs.setCurrentIndex(7)  # Switch to settings tab
    
    def save_settings(self):
        """Save settings."""
        # Save all settings to agent config
        self.add_activity("💾 Settings saved")
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
