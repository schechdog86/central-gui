"""
LLM Chat Interface View Component
================================

Comprehensive chat interface for interacting with language models.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QSlider, QTextBrowser,
    QDoubleSpinBox, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor


class LLMChatWorker(QObject):
    """Worker thread for LLM chat operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    response_chunk = pyqtSignal(str)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the LLM chat operation."""
        try:
            self.progress.emit(f"Processing {self.operation}...")
            
            # Simulate operations for now
            # In production, this would connect to actual LLM
            
            if self.operation == "send_message":
                # Simulate streaming response
                response = "I understand your request. Let me help you with that. "
                response += "Based on the information provided, here's what I can tell you: "
                response += "This is a simulated response from the language model. "
                response += "In a real implementation, this would connect to your chosen LLM backend."
                
                # Simulate streaming
                words = response.split()
                for i, word in enumerate(words):
                    self.response_chunk.emit(word + " ")
                    QThread.msleep(50)  # Simulate typing delay
                
                result = {
                    "status": "success",
                    "message": response,
                    "model": self.params.get("model", "gpt-3.5-turbo"),
                    "tokens": len(response.split())
                }
            elif self.operation == "load_conversation":
                result = {
                    "status": "success",
                    "messages": self.params.get("messages", [])
                }
            elif self.operation == "export_chat":
                result = {
                    "status": "success",
                    "path": self.params.get("path", "chat_export.json")
                }
            else:
                result = {"status": "completed"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class LLMChatView(QWidget):
    """Main view for the LLM Chat interface."""
    
    # Signals
    status_updated = pyqtSignal(str)
    message_sent = pyqtSignal(str)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.worker_thread = None
        self.worker = None
        self.conversation_history = []
        self.current_model = "gpt-3.5-turbo"
        
        self.setWindowTitle("LLM Chat Interface")
        self._init_ui()
        self._init_chat()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Chat Tab
        self.chat_tab = self._create_chat_tab()
        self.tab_widget.addTab(self.chat_tab, "💬 Chat")
        
        # Conversations Tab
        self.conversations_tab = self._create_conversations_tab()
        self.tab_widget.addTab(self.conversations_tab, "📚 Conversations")
        
        # Prompts Tab
        self.prompts_tab = self._create_prompts_tab()
        self.tab_widget.addTab(self.prompts_tab, "📝 Prompts")
        
        # Models Tab
        self.models_tab = self._create_models_tab()
        self.tab_widget.addTab(self.models_tab, "🤖 Models")
        
        # Settings Tab
        self.settings_tab = self._create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        # Analytics Tab
        self.analytics_tab = self._create_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "📊 Analytics")
        
        # Tools Tab
        self.tools_tab = self._create_tools_tab()
        self.tab_widget.addTab(self.tools_tab, "🛠️ Tools")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("LLM Chat: Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_chat_tab(self) -> QWidget:
        """Create the main chat interface tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model selector and chat controls
        controls_layout = QHBoxLayout()
        
        # Model selector
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet",
            "llama-2-70b", "mistral-large", "gemini-pro", "custom-model"
        ])
        self.model_combo.setCurrentText(self.current_model)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)
        
        # Temperature control
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        self.temperature_label = QLabel("0.7")
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(f"{v/100:.1f}")
        )
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        
        # Chat actions
        self.clear_chat_btn = QPushButton("🗑️ Clear")
        self.clear_chat_btn.clicked.connect(self._clear_chat)
        self.export_chat_btn = QPushButton("💾 Export")
        self.export_chat_btn.clicked.connect(self._export_chat)
        
        controls_layout.addLayout(model_layout)
        controls_layout.addLayout(temp_layout)
        controls_layout.addStretch()
        controls_layout.addWidget(self.clear_chat_btn)
        controls_layout.addWidget(self.export_chat_btn)
        
        # Chat display
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 14px;
                line-height: 1.5;
                padding: 10px;
            }
        """)
        
        # Input area
        input_group = QGroupBox("Message")
        input_layout = QVBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Type your message here... (Shift+Enter for new line)")
        
        # Input controls
        input_controls = QHBoxLayout()
        
        # System prompt toggle
        self.use_system_prompt = QCheckBox("Use System Prompt")
        self.use_system_prompt.setChecked(True)
        
        # Max tokens
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 4096)
        self.max_tokens_spin.setValue(1024)
        tokens_layout.addWidget(self.max_tokens_spin)
        
        # Send button
        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self._send_message)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        input_controls.addWidget(self.use_system_prompt)
        input_controls.addLayout(tokens_layout)
        input_controls.addStretch()
        input_controls.addWidget(self.send_btn)
        
        input_layout.addWidget(self.message_input)
        input_layout.addLayout(input_controls)
        input_group.setLayout(input_layout)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        self.copy_last_btn = QPushButton("📋 Copy Last")
        self.copy_last_btn.clicked.connect(self._copy_last_response)
        self.regenerate_btn = QPushButton("🔄 Regenerate")
        self.continue_btn = QPushButton("➡️ Continue")
        
        actions_layout.addWidget(self.copy_last_btn)
        actions_layout.addWidget(self.regenerate_btn)
        actions_layout.addWidget(self.continue_btn)
        actions_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.chat_display)
        layout.addWidget(input_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_conversations_tab(self) -> QWidget:
        """Create the conversations management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Conversation controls
        controls_layout = QHBoxLayout()
        self.new_conversation_btn = QPushButton("➕ New Conversation")
        self.new_conversation_btn.clicked.connect(self._new_conversation)
        self.load_conversation_btn = QPushButton("📂 Load")
        self.delete_conversation_btn = QPushButton("🗑️ Delete")
        
        controls_layout.addWidget(self.new_conversation_btn)
        controls_layout.addWidget(self.load_conversation_btn)
        controls_layout.addWidget(self.delete_conversation_btn)
        controls_layout.addStretch()
        
        # Conversation list
        self.conversations_table = QTableWidget()
        self.conversations_table.setColumnCount(5)
        self.conversations_table.setHorizontalHeaderLabels([
            "Title", "Model", "Messages", "Created", "Last Modified"
        ])
        header = self.conversations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Add sample conversations
        conversations = [
            ("Python Code Review", "gpt-4", "15", "2 hours ago", "30 min ago"),
            ("API Design Discussion", "claude-3-opus", "23", "Yesterday", "Yesterday"),
            ("Bug Investigation", "gpt-3.5-turbo", "8", "3 days ago", "2 days ago"),
            ("Feature Planning", "gemini-pro", "12", "1 week ago", "5 days ago")
        ]
        
        self.conversations_table.setRowCount(len(conversations))
        for i, conv in enumerate(conversations):
            for j, value in enumerate(conv):
                self.conversations_table.setItem(i, j, QTableWidgetItem(value))
        
        # Conversation preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        
        self.conversation_preview = QTextEdit()
        self.conversation_preview.setReadOnly(True)
        self.conversation_preview.setMaximumHeight(200)
        self.conversation_preview.setPlainText("Select a conversation to preview...")
        
        preview_layout.addWidget(self.conversation_preview)
        preview_group.setLayout(preview_layout)
        
        # Search and filter
        filter_layout = QHBoxLayout()
        self.conversation_search = QLineEdit()
        self.conversation_search.setPlaceholderText("Search conversations...")
        self.model_filter = QComboBox()
        self.model_filter.addItems(["All Models", "GPT-4", "GPT-3.5", "Claude", "Llama"])
        
        filter_layout.addWidget(self.conversation_search)
        filter_layout.addWidget(self.model_filter)
        filter_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.conversations_table)
        layout.addWidget(preview_group)
        
        return widget
    
    def _create_prompts_tab(self) -> QWidget:
        """Create the prompts library tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Prompt categories
        self.prompts_tree = QTreeWidget()
        self.prompts_tree.setHeaderLabels(["Prompt", "Description", "Tags"])
        
        # Add sample prompts by category
        prompt_categories = {
            "Development": [
                ("Code Review", "Review code for best practices and issues", "code, review"),
                ("Debug Helper", "Help debug and fix code issues", "debug, fix"),
                ("Architecture Design", "Design software architecture", "design, architecture")
            ],
            "Writing": [
                ("Technical Documentation", "Write clear technical docs", "docs, technical"),
                ("API Documentation", "Document API endpoints", "api, docs"),
                ("User Guide", "Create user-friendly guides", "guide, user")
            ],
            "Analysis": [
                ("Data Analysis", "Analyze data and provide insights", "data, analysis"),
                ("Performance Review", "Review system performance", "performance, review"),
                ("Security Audit", "Audit for security issues", "security, audit")
            ],
            "Creative": [
                ("Brainstorming", "Generate creative ideas", "ideas, creative"),
                ("Story Writing", "Write engaging stories", "story, creative"),
                ("Content Creation", "Create various content", "content, creative")
            ]
        }
        
        for category, prompts in prompt_categories.items():
            cat_item = QTreeWidgetItem(self.prompts_tree)
            cat_item.setText(0, category)
            
            for prompt in prompts:
                prompt_item = QTreeWidgetItem(cat_item)
                for i, value in enumerate(prompt):
                    prompt_item.setText(i, value)
        
        # Prompt editor
        editor_group = QGroupBox("Prompt Editor")
        editor_layout = QVBoxLayout()
        
        # Prompt name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.prompt_name_input = QLineEdit()
        self.prompt_name_input.setPlaceholderText("Prompt name...")
        name_layout.addWidget(self.prompt_name_input)
        
        # System prompt
        self.system_prompt_text = QTextEdit()
        self.system_prompt_text.setMaximumHeight(150)
        self.system_prompt_text.setPlaceholderText(
            "System prompt (sets the behavior and context)..."
        )
        
        # User prompt template
        self.user_prompt_text = QTextEdit()
        self.user_prompt_text.setMaximumHeight(150)
        self.user_prompt_text.setPlaceholderText(
            "User prompt template (use {variable} for placeholders)..."
        )
        
        # Variables
        vars_layout = QHBoxLayout()
        vars_layout.addWidget(QLabel("Variables:"))
        self.variables_input = QLineEdit()
        self.variables_input.setPlaceholderText("variable1, variable2, ...")
        vars_layout.addWidget(self.variables_input)
        
        editor_layout.addLayout(name_layout)
        editor_layout.addWidget(QLabel("System Prompt:"))
        editor_layout.addWidget(self.system_prompt_text)
        editor_layout.addWidget(QLabel("User Prompt:"))
        editor_layout.addWidget(self.user_prompt_text)
        editor_layout.addLayout(vars_layout)
        
        editor_group.setLayout(editor_layout)
        
        # Prompt actions
        actions_layout = QHBoxLayout()
        self.save_prompt_btn = QPushButton("💾 Save Prompt")
        self.use_prompt_btn = QPushButton("✅ Use Prompt")
        self.test_prompt_btn = QPushButton("🧪 Test")
        self.delete_prompt_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.save_prompt_btn)
        actions_layout.addWidget(self.use_prompt_btn)
        actions_layout.addWidget(self.test_prompt_btn)
        actions_layout.addWidget(self.delete_prompt_btn)
        actions_layout.addStretch()
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        prompts_widget = QWidget()
        prompts_layout = QVBoxLayout(prompts_widget)
        prompts_layout.addWidget(QLabel("Prompt Library:"))
        prompts_layout.addWidget(self.prompts_tree)
        
        splitter.addWidget(prompts_widget)
        splitter.addWidget(editor_group)
        splitter.setSizes([300, 300])
        
        layout.addWidget(splitter)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_models_tab(self) -> QWidget:
        """Create the models configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model list
        models_group = QGroupBox("Available Models")
        models_layout = QVBoxLayout()
        
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels([
            "Model", "Provider", "Type", "Context", "Status", "Cost"
        ])
        
        # Add sample models
        models = [
            ("gpt-4", "OpenAI", "Chat", "128k", "Active", "$0.03/1k"),
            ("gpt-3.5-turbo", "OpenAI", "Chat", "16k", "Active", "$0.0015/1k"),
            ("claude-3-opus", "Anthropic", "Chat", "200k", "Active", "$0.015/1k"),
            ("claude-3-sonnet", "Anthropic", "Chat", "200k", "Active", "$0.003/1k"),
            ("llama-2-70b", "Local", "Chat", "4k", "Ready", "Free"),
            ("mistral-large", "Mistral", "Chat", "32k", "API Key Required", "$0.008/1k"),
            ("gemini-pro", "Google", "Chat", "32k", "Active", "$0.001/1k")
        ]
        
        self.models_table.setRowCount(len(models))
        for i, model in enumerate(models):
            for j, value in enumerate(model):
                item = QTableWidgetItem(value)
                if j == 4:  # Status column
                    if value == "Active":
                        item.setBackground(QColor(200, 255, 200))
                    elif value == "API Key Required":
                        item.setBackground(QColor(255, 255, 200))
                self.models_table.setItem(i, j, item)
        
        models_layout.addWidget(self.models_table)
        models_group.setLayout(models_layout)
        
        # Model configuration
        config_group = QGroupBox("Model Configuration")
        config_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter API key...")
        
        self.api_endpoint_input = QLineEdit()
        self.api_endpoint_input.setPlaceholderText("Custom endpoint (optional)")
        
        self.default_model_combo = QComboBox()
        self.default_model_combo.addItems([
            "gpt-3.5-turbo", "gpt-4", "claude-3-sonnet", "llama-2-70b"
        ])
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setSuffix(" seconds")
        
        config_layout.addRow("API Key:", self.api_key_input)
        config_layout.addRow("Endpoint:", self.api_endpoint_input)
        config_layout.addRow("Default Model:", self.default_model_combo)
        config_layout.addRow("Timeout:", self.timeout_spin)
        
        config_group.setLayout(config_layout)
        
        # Model actions
        actions_layout = QHBoxLayout()
        self.add_model_btn = QPushButton("➕ Add Model")
        self.test_model_btn = QPushButton("🧪 Test Connection")
        self.save_config_btn = QPushButton("💾 Save Configuration")
        
        actions_layout.addWidget(self.add_model_btn)
        actions_layout.addWidget(self.test_model_btn)
        actions_layout.addWidget(self.save_config_btn)
        actions_layout.addStretch()
        
        layout.addWidget(models_group)
        layout.addWidget(config_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()
        
        self.auto_save_checkbox = QCheckBox("Auto-save conversations")
        self.auto_save_checkbox.setChecked(True)
        
        self.stream_response_checkbox = QCheckBox("Stream responses")
        self.stream_response_checkbox.setChecked(True)
        
        self.show_tokens_checkbox = QCheckBox("Show token count")
        self.show_tokens_checkbox.setChecked(True)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        
        general_layout.addRow(self.auto_save_checkbox)
        general_layout.addRow(self.stream_response_checkbox)
        general_layout.addRow(self.show_tokens_checkbox)
        general_layout.addRow("Theme:", self.theme_combo)
        
        general_group.setLayout(general_layout)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()
        
        self.max_history_spin = QSpinBox()
        self.max_history_spin.setRange(1, 100)
        self.max_history_spin.setValue(10)
        self.max_history_spin.setSuffix(" messages")
        
        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(0, 5)
        self.retry_attempts_spin.setValue(3)
        
        self.rate_limit_spin = QSpinBox()
        self.rate_limit_spin.setRange(1, 100)
        self.rate_limit_spin.setValue(10)
        self.rate_limit_spin.setSuffix(" req/min")
        
        advanced_layout.addRow("Context History:", self.max_history_spin)
        advanced_layout.addRow("Retry Attempts:", self.retry_attempts_spin)
        advanced_layout.addRow("Rate Limit:", self.rate_limit_spin)
        
        advanced_group.setLayout(advanced_layout)
        
        # Response formatting
        format_group = QGroupBox("Response Formatting")
        format_layout = QVBoxLayout()
        
        self.format_code_checkbox = QCheckBox("Format code blocks")
        self.format_code_checkbox.setChecked(True)
        
        self.syntax_highlight_checkbox = QCheckBox("Syntax highlighting")
        self.syntax_highlight_checkbox.setChecked(True)
        
        self.render_markdown_checkbox = QCheckBox("Render markdown")
        self.render_markdown_checkbox.setChecked(True)
        
        self.wrap_text_checkbox = QCheckBox("Word wrap")
        self.wrap_text_checkbox.setChecked(True)
        
        format_layout.addWidget(self.format_code_checkbox)
        format_layout.addWidget(self.syntax_highlight_checkbox)
        format_layout.addWidget(self.render_markdown_checkbox)
        format_layout.addWidget(self.wrap_text_checkbox)
        
        format_group.setLayout(format_layout)
        
        # Save settings
        save_layout = QHBoxLayout()
        self.save_settings_btn = QPushButton("💾 Save Settings")
        self.reset_settings_btn = QPushButton("🔄 Reset to Defaults")
        
        save_layout.addWidget(self.save_settings_btn)
        save_layout.addWidget(self.reset_settings_btn)
        save_layout.addStretch()
        
        layout.addWidget(general_group)
        layout.addWidget(advanced_group)
        layout.addWidget(format_group)
        layout.addLayout(save_layout)
        layout.addStretch()
        
        return widget
    
    def _create_analytics_tab(self) -> QWidget:
        """Create the analytics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Usage statistics
        stats_group = QGroupBox("Usage Statistics")
        stats_layout = QFormLayout()
        
        self.total_conversations_label = QLabel("156")
        self.total_messages_label = QLabel("2,847")
        self.total_tokens_label = QLabel("458,392")
        self.avg_response_time_label = QLabel("2.3s")
        self.total_cost_label = QLabel("$12.45")
        
        stats_layout.addRow("Total Conversations:", self.total_conversations_label)
        stats_layout.addRow("Total Messages:", self.total_messages_label)
        stats_layout.addRow("Total Tokens:", self.total_tokens_label)
        stats_layout.addRow("Avg Response Time:", self.avg_response_time_label)
        stats_layout.addRow("Total Cost:", self.total_cost_label)
        
        stats_group.setLayout(stats_layout)
        
        # Model usage
        model_group = QGroupBox("Model Usage")
        model_layout = QVBoxLayout()
        
        self.model_usage_table = QTableWidget()
        self.model_usage_table.setColumnCount(4)
        self.model_usage_table.setHorizontalHeaderLabels([
            "Model", "Messages", "Tokens", "Cost"
        ])
        
        model_usage = [
            ("gpt-3.5-turbo", "1,523", "234,567", "$3.52"),
            ("gpt-4", "324", "89,234", "$7.14"),
            ("claude-3-sonnet", "456", "78,345", "$1.18"),
            ("llama-2-70b", "544", "56,246", "$0.00")
        ]
        
        self.model_usage_table.setRowCount(len(model_usage))
        for i, usage in enumerate(model_usage):
            for j, value in enumerate(usage):
                self.model_usage_table.setItem(i, j, QTableWidgetItem(value))
        
        model_layout.addWidget(self.model_usage_table)
        model_group.setLayout(model_layout)
        
        # Time-based analytics
        time_group = QGroupBox("Activity Over Time")
        time_layout = QVBoxLayout()
        
        time_placeholder = QLabel("📊 Activity chart will be displayed here")
        time_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_placeholder.setStyleSheet("padding: 50px; color: #666;")
        
        time_layout.addWidget(time_placeholder)
        time_group.setLayout(time_layout)
        
        # Export options
        export_layout = QHBoxLayout()
        self.export_analytics_btn = QPushButton("📊 Export Analytics")
        self.clear_analytics_btn = QPushButton("🗑️ Clear Data")
        
        export_layout.addWidget(self.export_analytics_btn)
        export_layout.addWidget(self.clear_analytics_btn)
        export_layout.addStretch()
        
        layout.addWidget(stats_group)
        layout.addWidget(model_group)
        layout.addWidget(time_group)
        layout.addLayout(export_layout)
        
        return widget
    
    def _create_tools_tab(self) -> QWidget:
        """Create the tools tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Text processing tools
        text_group = QGroupBox("Text Processing")
        text_layout = QVBoxLayout()
        
        # Token counter
        token_layout = QHBoxLayout()
        self.token_input = QTextEdit()
        self.token_input.setMaximumHeight(100)
        self.token_input.setPlaceholderText("Enter text to count tokens...")
        
        self.count_tokens_btn = QPushButton("Count Tokens")
        self.token_count_label = QLabel("Tokens: 0")
        
        token_layout.addWidget(self.token_input)
        
        token_controls = QVBoxLayout()
        token_controls.addWidget(self.count_tokens_btn)
        token_controls.addWidget(self.token_count_label)
        token_layout.addLayout(token_controls)
        
        text_layout.addLayout(token_layout)
        text_group.setLayout(text_layout)
        
        # Prompt templates
        templates_group = QGroupBox("Quick Templates")
        templates_layout = QVBoxLayout()
        
        template_buttons = [
            ("📝 Summarize", "Summarize the following text:"),
            ("🌐 Translate", "Translate to [language]:"),
            ("✨ Improve", "Improve the following text:"),
            ("🔍 Explain", "Explain this in simple terms:"),
            ("💡 Ideas", "Generate ideas for:"),
            ("❓ Questions", "Generate questions about:")
        ]
        
        templates_grid = QHBoxLayout()
        for i, (label, template) in enumerate(template_buttons):
            btn = QPushButton(label)
            btn.setProperty("template", template)
            btn.clicked.connect(lambda checked, t=template: self._use_template(t))
            
            if i % 3 == 0 and i > 0:
                templates_layout.addLayout(templates_grid)
                templates_grid = QHBoxLayout()
            templates_grid.addWidget(btn)
        
        if templates_grid.count() > 0:
            templates_layout.addLayout(templates_grid)
        
        templates_group.setLayout(templates_layout)
        
        # Context management
        context_group = QGroupBox("Context Management")
        context_layout = QVBoxLayout()
        
        context_controls = QHBoxLayout()
        self.save_context_btn = QPushButton("💾 Save Context")
        self.load_context_btn = QPushButton("📂 Load Context")
        self.clear_context_btn = QPushButton("🗑️ Clear Context")
        
        context_controls.addWidget(self.save_context_btn)
        context_controls.addWidget(self.load_context_btn)
        context_controls.addWidget(self.clear_context_btn)
        
        self.context_info_label = QLabel("Current context: 0 messages, 0 tokens")
        
        context_layout.addLayout(context_controls)
        context_layout.addWidget(self.context_info_label)
        context_group.setLayout(context_layout)
        
        layout.addWidget(text_group)
        layout.addWidget(templates_group)
        layout.addWidget(context_group)
        layout.addStretch()
        
        return widget
    
    def _init_chat(self):
        """Initialize the chat interface."""
        self.update_status("Chat interface ready")
        self._add_system_message("Welcome! I'm ready to assist you.")
    
    def _add_system_message(self, message: str):
        """Add a system message to the chat."""
        timestamp = datetime.now().strftime("%H:%M")
        html = f"""
        <div style="margin: 10px 0;">
            <span style="color: #666; font-size: 12px;">{timestamp}</span>
            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 8px; margin-top: 5px;">
                <em>{message}</em>
            </div>
        </div>
        """
        self.chat_display.append(html)
    
    def _add_user_message(self, message: str):
        """Add a user message to the chat."""
        timestamp = datetime.now().strftime("%H:%M")
        html = f"""
        <div style="margin: 10px 0;">
            <span style="color: #666; font-size: 12px;">{timestamp} - You</span>
            <div style="background-color: #e3f2fd; padding: 10px; border-radius: 8px; margin-top: 5px;">
                {message}
            </div>
        </div>
        """
        self.chat_display.append(html)
        self.conversation_history.append({"role": "user", "content": message})
    
    def _add_assistant_message(self, message: str):
        """Add an assistant message to the chat."""
        timestamp = datetime.now().strftime("%H:%M")
        model = self.model_combo.currentText()
        html = f"""
        <div style="margin: 10px 0;">
            <span style="color: #666; font-size: 12px;">{timestamp} - {model}</span>
            <div style="background-color: #fff; border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-top: 5px;">
                {message}
            </div>
        </div>
        """
        self.chat_display.append(html)
        self.conversation_history.append({"role": "assistant", "content": message})
    
    def _send_message(self):
        """Send a message to the LLM."""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        # Clear input
        self.message_input.clear()
        
        # Add user message to chat
        self._add_user_message(message)
        
        # Prepare parameters
        params = {
            "message": message,
            "model": self.model_combo.currentText(),
            "temperature": self.temperature_slider.value() / 100,
            "max_tokens": self.max_tokens_spin.value(),
            "history": self.conversation_history[-10:]  # Last 10 messages for context
        }
        
        # Clear any existing response area
        self.chat_display.append('<div id="current_response" style="margin: 10px 0;"></div>')
        
        # Send message
        self._run_operation("send_message", params)
    
    def _clear_chat(self):
        """Clear the chat history."""
        reply = QMessageBox.question(
            self, "Clear Chat",
            "Are you sure you want to clear the chat history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            self.conversation_history.clear()
            self._add_system_message("Chat cleared. Starting new conversation.")
    
    def _export_chat(self):
        """Export the chat history."""
        path = QFileDialog.getSaveFileName(
            self, "Export Chat",
            f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;Text Files (*.txt)"
        )[0]
        
        if path:
            self._run_operation("export_chat", {
                "path": path,
                "messages": self.conversation_history
            })
    
    def _copy_last_response(self):
        """Copy the last assistant response to clipboard."""
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant":
                clipboard = QApplication.clipboard()
                clipboard.setText(msg["content"])
                self.update_status("Response copied to clipboard")
                break
    
    def _new_conversation(self):
        """Start a new conversation."""
        self._clear_chat()
    
    def _on_model_changed(self, model: str):
        """Handle model change."""
        self.current_model = model
        self.update_status(f"Switched to {model}")
    
    def _use_template(self, template: str):
        """Use a quick template."""
        current_text = self.message_input.toPlainText()
        self.message_input.setPlainText(template + "\n\n" + current_text)
        self.message_input.moveCursor(QTextCursor.MoveOperation.End)
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "Please wait for the current operation to complete.")
            return
        
        self.update_status(f"Processing...")
        
        self.worker_thread = QThread()
        self.worker = LLMChatWorker(operation, params)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_operation_finished)
        self.worker.error.connect(self._on_operation_error)
        self.worker.progress.connect(self.update_status)
        self.worker.response_chunk.connect(self._on_response_chunk)
        
        # Cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Track streaming response
        self.streaming_response = ""
        self.response_start_time = datetime.now()
        
        self.worker_thread.start()
    
    def _on_response_chunk(self, chunk: str):
        """Handle streaming response chunk."""
        self.streaming_response += chunk
        
        # Update the response in real-time
        timestamp = self.response_start_time.strftime("%H:%M")
        model = self.model_combo.currentText()
        
        # Find and update the current response div
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # This is a simplified version - in production you'd update the existing div
        if not hasattr(self, '_response_started'):
            self._response_started = True
            html = f"""
            <div style="margin: 10px 0;">
                <span style="color: #666; font-size: 12px;">{timestamp} - {model}</span>
                <div style="background-color: #fff; border: 1px solid #ddd; padding: 10px; border-radius: 8px; margin-top: 5px;">
            """
            self.chat_display.append(html)
        
        self.chat_display.insertPlainText(chunk)
    
    def _on_operation_finished(self, result: Dict[str, Any]):
        """Handle operation completion."""
        if result.get("status") == "success":
            if "message" in result:
                # Response complete
                if hasattr(self, '_response_started'):
                    self.chat_display.append("</div></div>")
                    delattr(self, '_response_started')
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": self.streaming_response
                })
                
                # Show token count if enabled
                if self.show_tokens_checkbox.isChecked():
                    tokens = result.get("tokens", 0)
                    self.update_status(f"Response complete - {tokens} tokens")
                else:
                    self.update_status("Response complete")
                    
            elif "path" in result:
                # Export complete
                QMessageBox.information(
                    self, "Export Complete",
                    f"Chat exported to: {result['path']}"
                )
        
        self.update_status("Ready")
    
    def _on_operation_error(self, error: str):
        """Handle operation error."""
        QMessageBox.critical(self, "Error", f"Operation failed: {error}")
        self._add_system_message(f"Error: {error}")
        self.update_status("Error occurred")
    
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {message}")
        self.status_updated.emit(message)
    
    def cleanup(self):
        """Clean up resources."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()


# Import QApplication for clipboard functionality
from PyQt6.QtWidgets import QApplication