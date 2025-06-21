"""
N8N Integration View Component
============================

Comprehensive UI for n8n workflow automation integration.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QPlainTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer, QUrl
from PyQt6.QtGui import QFont, QColor, QDesktopServices


class N8NWorker(QObject):
    """Worker thread for n8n operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    workflow_updated = pyqtSignal(dict)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the n8n operation."""
        try:
            self.progress.emit(f"Starting {self.operation}...")
            
            # Simulate operations for now
            # In production, this would connect to actual n8n instance
            
            if self.operation == "start_n8n":
                result = {
                    "status": "started",
                    "url": "http://localhost:5678",
                    "api_endpoint": "http://localhost:5678/api/v1"
                }
            elif self.operation == "stop_n8n":
                result = {"status": "stopped"}
            elif self.operation == "list_workflows":
                result = {
                    "workflows": [
                        {"id": "1", "name": "Data Processing", "active": True},
                        {"id": "2", "name": "Email Automation", "active": True},
                        {"id": "3", "name": "Web Scraping", "active": False}
                    ]
                }
            elif self.operation == "execute_workflow":
                result = {
                    "execution_id": "exec_12345",
                    "status": "running",
                    "workflow": self.params.get("workflow_id")
                }
            else:
                result = {"status": "completed"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class N8NIntegrationView(QWidget):
    """Main view for the n8n Integration component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    workflow_executed = pyqtSignal(dict)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.worker_thread = None
        self.worker = None
        self.n8n_status = "Stopped"
        self.n8n_url = "http://localhost:5678"
        
        self.setWindowTitle("n8n Workflow Automation")
        self._init_ui()
        self._init_n8n()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Overview Tab
        self.overview_tab = self._create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Workflows Tab
        self.workflows_tab = self._create_workflows_tab()
        self.tab_widget.addTab(self.workflows_tab, "🔄 Workflows")
        
        # Executions Tab
        self.executions_tab = self._create_executions_tab()
        self.tab_widget.addTab(self.executions_tab, "▶️ Executions")
        
        # Credentials Tab
        self.credentials_tab = self._create_credentials_tab()
        self.tab_widget.addTab(self.credentials_tab, "🔐 Credentials")
        
        # Nodes & Integrations Tab
        self.nodes_tab = self._create_nodes_tab()
        self.tab_widget.addTab(self.nodes_tab, "🔌 Nodes")
        
        # API Integration Tab
        self.api_tab = self._create_api_tab()
        self.tab_widget.addTab(self.api_tab, "🔗 API")
        
        # Logs Tab
        self.logs_tab = self._create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "📜 Logs")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("n8n: Stopped")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_overview_tab(self) -> QWidget:
        """Create the overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # n8n controls
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶️ Start n8n")
        self.start_btn.clicked.connect(self._start_n8n)
        self.stop_btn = QPushButton("⏹️ Stop n8n")
        self.stop_btn.clicked.connect(self._stop_n8n)
        self.stop_btn.setEnabled(False)
        self.restart_btn = QPushButton("🔄 Restart n8n")
        self.open_ui_btn = QPushButton("🌐 Open n8n UI")
        self.open_ui_btn.clicked.connect(self._open_n8n_ui)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.restart_btn)
        control_layout.addWidget(self.open_ui_btn)
        control_layout.addStretch()
        
        # Status information
        status_group = QGroupBox("n8n Status")
        status_layout = QFormLayout()
        
        self.n8n_status_label = QLabel("Stopped")
        self.n8n_url_label = QLabel(self.n8n_url)
        self.api_endpoint_label = QLabel(f"{self.n8n_url}/api/v1")
        self.version_label = QLabel("n8n v1.0.0")
        self.workflows_count_label = QLabel("0")
        self.active_workflows_label = QLabel("0")
        self.executions_today_label = QLabel("0")
        
        status_layout.addRow("Status:", self.n8n_status_label)
        status_layout.addRow("URL:", self.n8n_url_label)
        status_layout.addRow("API Endpoint:", self.api_endpoint_label)
        status_layout.addRow("Version:", self.version_label)
        status_layout.addRow("Total Workflows:", self.workflows_count_label)
        status_layout.addRow("Active Workflows:", self.active_workflows_label)
        status_layout.addRow("Executions Today:", self.executions_today_label)
        
        status_group.setLayout(status_layout)
        
        # Quick stats
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        # Execution stats
        exec_layout = QHBoxLayout()
        self.success_rate_label = QLabel("Success Rate: 95%")
        self.avg_exec_time_label = QLabel("Avg Time: 2.3s")
        self.total_nodes_label = QLabel("Total Nodes: 156")
        
        exec_layout.addWidget(self.success_rate_label)
        exec_layout.addWidget(self.avg_exec_time_label)
        exec_layout.addWidget(self.total_nodes_label)
        
        stats_layout.addLayout(exec_layout)
        
        # Recent activity
        self.recent_activity_list = QListWidget()
        sample_activities = [
            "✅ Workflow 'Data Processing' executed successfully - 5 min ago",
            "⚠️ Workflow 'Email Alert' triggered warning - 15 min ago",
            "✅ Credential 'API Key' updated - 1 hour ago",
            "🔄 Workflow 'Backup' scheduled - 2 hours ago"
        ]
        self.recent_activity_list.addItems(sample_activities)
        self.recent_activity_list.setMaximumHeight(150)
        
        stats_layout.addWidget(QLabel("Recent Activity:"))
        stats_layout.addWidget(self.recent_activity_list)
        
        stats_group.setLayout(stats_layout)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        self.create_workflow_btn = QPushButton("➕ Create Workflow")
        self.import_workflow_btn = QPushButton("📥 Import")
        self.backup_btn = QPushButton("💾 Backup")
        self.settings_btn = QPushButton("⚙️ Settings")
        
        actions_layout.addWidget(self.create_workflow_btn)
        actions_layout.addWidget(self.import_workflow_btn)
        actions_layout.addWidget(self.backup_btn)
        actions_layout.addWidget(self.settings_btn)
        
        actions_group.setLayout(actions_layout)
        
        layout.addLayout(control_layout)
        layout.addWidget(status_group)
        layout.addWidget(stats_group)
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return widget
    
    def _create_workflows_tab(self) -> QWidget:
        """Create the workflows management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Workflow controls
        controls_layout = QHBoxLayout()
        self.new_workflow_btn = QPushButton("➕ New Workflow")
        self.duplicate_workflow_btn = QPushButton("📋 Duplicate")
        self.refresh_workflows_btn = QPushButton("🔄 Refresh")
        self.refresh_workflows_btn.clicked.connect(self._refresh_workflows)
        
        controls_layout.addWidget(self.new_workflow_btn)
        controls_layout.addWidget(self.duplicate_workflow_btn)
        controls_layout.addWidget(self.refresh_workflows_btn)
        controls_layout.addStretch()
        
        # Workflow list
        self.workflows_table = QTableWidget()
        self.workflows_table.setColumnCount(6)
        self.workflows_table.setHorizontalHeaderLabels([
            "ID", "Name", "Status", "Nodes", "Last Run", "Actions"
        ])
        header = self.workflows_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Add sample workflows
        workflows = [
            ("1", "Data Processing Pipeline", "Active", "12", "5 min ago", ""),
            ("2", "Email Automation", "Active", "8", "1 hour ago", ""),
            ("3", "Web Scraping Job", "Inactive", "15", "Yesterday", ""),
            ("4", "API Integration", "Active", "6", "2 hours ago", ""),
            ("5", "Backup Automation", "Active", "4", "3 hours ago", "")
        ]
        
        self.workflows_table.setRowCount(len(workflows))
        for i, workflow in enumerate(workflows):
            for j, value in enumerate(workflow[:-1]):  # Skip actions column
                item = QTableWidgetItem(value)
                if j == 2:  # Status column
                    if value == "Active":
                        item.setBackground(QColor(200, 255, 200))
                    else:
                        item.setBackground(QColor(255, 200, 200))
                self.workflows_table.setItem(i, j, item)
        
        # Workflow details
        details_group = QGroupBox("Workflow Details")
        details_layout = QFormLayout()
        
        self.workflow_name_label = QLabel("Select a workflow")
        self.workflow_desc_text = QTextEdit()
        self.workflow_desc_text.setMaximumHeight(100)
        self.workflow_desc_text.setPlaceholderText("Workflow description...")
        
        self.workflow_tags_input = QLineEdit()
        self.workflow_tags_input.setPlaceholderText("Tags (comma-separated)")
        
        details_layout.addRow("Name:", self.workflow_name_label)
        details_layout.addRow("Description:", self.workflow_desc_text)
        details_layout.addRow("Tags:", self.workflow_tags_input)
        
        details_group.setLayout(details_layout)
        
        # Workflow actions
        actions_layout = QHBoxLayout()
        self.execute_workflow_btn = QPushButton("▶️ Execute")
        self.execute_workflow_btn.clicked.connect(self._execute_workflow)
        self.edit_workflow_btn = QPushButton("✏️ Edit in n8n")
        self.export_workflow_btn = QPushButton("📤 Export")
        self.delete_workflow_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.execute_workflow_btn)
        actions_layout.addWidget(self.edit_workflow_btn)
        actions_layout.addWidget(self.export_workflow_btn)
        actions_layout.addWidget(self.delete_workflow_btn)
        actions_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.workflows_table)
        layout.addWidget(details_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_executions_tab(self) -> QWidget:
        """Create the executions monitoring tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Execution filters
        filter_layout = QHBoxLayout()
        self.exec_status_filter = QComboBox()
        self.exec_status_filter.addItems([
            "All", "Success", "Error", "Running", "Waiting"
        ])
        self.exec_workflow_filter = QComboBox()
        self.exec_workflow_filter.addItems([
            "All Workflows", "Data Processing", "Email Automation"
        ])
        self.exec_search_input = QLineEdit()
        self.exec_search_input.setPlaceholderText("Search executions...")
        
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.exec_status_filter)
        filter_layout.addWidget(QLabel("Workflow:"))
        filter_layout.addWidget(self.exec_workflow_filter)
        filter_layout.addWidget(self.exec_search_input)
        filter_layout.addStretch()
        
        # Execution list
        self.executions_table = QTableWidget()
        self.executions_table.setColumnCount(7)
        self.executions_table.setHorizontalHeaderLabels([
            "ID", "Workflow", "Status", "Start Time", "Duration", "Mode", "Error"
        ])
        
        # Add sample executions
        executions = [
            ("exec_001", "Data Processing", "Success", "10:30 AM", "2.3s", "Production", ""),
            ("exec_002", "Email Automation", "Running", "10:28 AM", "-", "Production", ""),
            ("exec_003", "Web Scraping", "Error", "10:15 AM", "45s", "Production", "Timeout"),
            ("exec_004", "API Integration", "Success", "10:00 AM", "1.2s", "Test", ""),
            ("exec_005", "Backup", "Success", "09:45 AM", "15s", "Production", "")
        ]
        
        self.executions_table.setRowCount(len(executions))
        for i, execution in enumerate(executions):
            for j, value in enumerate(execution):
                item = QTableWidgetItem(value)
                if j == 2:  # Status column
                    if value == "Success":
                        item.setBackground(QColor(200, 255, 200))
                    elif value == "Error":
                        item.setBackground(QColor(255, 200, 200))
                    elif value == "Running":
                        item.setBackground(QColor(255, 255, 200))
                self.executions_table.setItem(i, j, item)
        
        # Execution details
        details_group = QGroupBox("Execution Details")
        details_layout = QVBoxLayout()
        
        self.execution_log = QPlainTextEdit()
        self.execution_log.setReadOnly(True)
        self.execution_log.setMaximumHeight(200)
        self.execution_log.setPlainText(
            "Select an execution to view details...\n\n"
            "Execution logs will appear here."
        )
        
        details_layout.addWidget(self.execution_log)
        details_group.setLayout(details_layout)
        
        # Execution actions
        actions_layout = QHBoxLayout()
        self.retry_execution_btn = QPushButton("🔄 Retry")
        self.stop_execution_btn = QPushButton("⏹️ Stop")
        self.view_details_btn = QPushButton("📋 View Details")
        
        actions_layout.addWidget(self.retry_execution_btn)
        actions_layout.addWidget(self.stop_execution_btn)
        actions_layout.addWidget(self.view_details_btn)
        actions_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.executions_table)
        layout.addWidget(details_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_credentials_tab(self) -> QWidget:
        """Create the credentials management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Credential controls
        controls_layout = QHBoxLayout()
        self.add_credential_btn = QPushButton("➕ Add Credential")
        self.import_credentials_btn = QPushButton("📥 Import")
        self.test_credential_btn = QPushButton("🧪 Test")
        
        controls_layout.addWidget(self.add_credential_btn)
        controls_layout.addWidget(self.import_credentials_btn)
        controls_layout.addWidget(self.test_credential_btn)
        controls_layout.addStretch()
        
        # Credentials list
        self.credentials_tree = QTreeWidget()
        self.credentials_tree.setHeaderLabels(["Name", "Type", "Used In", "Status"])
        
        # Add sample credentials by type
        cred_types = {
            "API Keys": [
                ("OpenAI API", "API Key", "3 workflows", "Valid"),
                ("SendGrid API", "API Key", "1 workflow", "Valid"),
                ("Stripe API", "API Key", "2 workflows", "Expired")
            ],
            "OAuth2": [
                ("Google OAuth", "OAuth2", "2 workflows", "Valid"),
                ("GitHub OAuth", "OAuth2", "1 workflow", "Valid")
            ],
            "Database": [
                ("PostgreSQL Dev", "Database", "5 workflows", "Valid"),
                ("MongoDB Prod", "Database", "3 workflows", "Valid")
            ]
        }
        
        for cred_type, credentials in cred_types.items():
            type_item = QTreeWidgetItem(self.credentials_tree)
            type_item.setText(0, cred_type)
            
            for cred in credentials:
                cred_item = QTreeWidgetItem(type_item)
                for i, value in enumerate(cred):
                    cred_item.setText(i, value)
                if cred[3] == "Expired":
                    cred_item.setBackground(3, QColor(255, 200, 200))
        
        # Credential form
        form_group = QGroupBox("Credential Details")
        form_layout = QFormLayout()
        
        self.cred_name_input = QLineEdit()
        self.cred_name_input.setPlaceholderText("Credential name...")
        
        self.cred_type_combo = QComboBox()
        self.cred_type_combo.addItems([
            "API Key", "OAuth2", "Basic Auth", "Database", "SSH", "Custom"
        ])
        
        self.cred_data_text = QTextEdit()
        self.cred_data_text.setMaximumHeight(150)
        self.cred_data_text.setPlaceholderText("Credential data (JSON format)...")
        
        form_layout.addRow("Name:", self.cred_name_input)
        form_layout.addRow("Type:", self.cred_type_combo)
        form_layout.addRow("Data:", self.cred_data_text)
        
        form_group.setLayout(form_layout)
        
        # Actions
        actions_layout = QHBoxLayout()
        self.save_credential_btn = QPushButton("💾 Save")
        self.delete_credential_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.save_credential_btn)
        actions_layout.addWidget(self.delete_credential_btn)
        actions_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.credentials_tree)
        layout.addWidget(form_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_nodes_tab(self) -> QWidget:
        """Create the nodes and integrations tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Node search
        search_layout = QHBoxLayout()
        self.node_search_input = QLineEdit()
        self.node_search_input.setPlaceholderText("Search nodes...")
        self.node_category_filter = QComboBox()
        self.node_category_filter.addItems([
            "All", "Core", "Data", "Communication", "Development", "Analytics"
        ])
        
        search_layout.addWidget(self.node_search_input)
        search_layout.addWidget(self.node_category_filter)
        search_layout.addStretch()
        
        # Available nodes
        self.nodes_list = QListWidget()
        nodes = [
            "📊 Airtable - Database operations",
            "📧 Email - Send and receive emails",
            "🔗 HTTP Request - Make API calls",
            "📁 Google Drive - File operations",
            "💬 Slack - Send messages",
            "🐙 GitHub - Repository operations",
            "📈 Google Sheets - Spreadsheet operations",
            "🗄️ PostgreSQL - Database queries",
            "🤖 OpenAI - AI operations",
            "📅 Google Calendar - Calendar events"
        ]
        self.nodes_list.addItems(nodes)
        
        # Node details
        details_group = QGroupBox("Node Information")
        details_layout = QVBoxLayout()
        
        self.node_info_text = QTextEdit()
        self.node_info_text.setReadOnly(True)
        self.node_info_text.setMaximumHeight(150)
        self.node_info_text.setHtml("""
        <h3>HTTP Request Node</h3>
        <p><b>Description:</b> Make HTTP requests to any API or web service.</p>
        <p><b>Operations:</b> GET, POST, PUT, DELETE, PATCH</p>
        <p><b>Authentication:</b> Basic, Bearer Token, OAuth2</p>
        <p><b>Usage:</b> Used in 15 workflows</p>
        """)
        
        details_layout.addWidget(self.node_info_text)
        details_group.setLayout(details_layout)
        
        # Custom nodes
        custom_group = QGroupBox("Custom Nodes")
        custom_layout = QVBoxLayout()
        
        custom_controls = QHBoxLayout()
        self.create_node_btn = QPushButton("➕ Create Custom Node")
        self.import_node_btn = QPushButton("📥 Import Node")
        
        custom_controls.addWidget(self.create_node_btn)
        custom_controls.addWidget(self.import_node_btn)
        custom_controls.addStretch()
        
        self.custom_nodes_list = QListWidget()
        custom_nodes = [
            "🔧 Custom API Wrapper",
            "📊 Data Transformer",
            "🔐 Custom Auth Handler"
        ]
        self.custom_nodes_list.addItems(custom_nodes)
        self.custom_nodes_list.setMaximumHeight(100)
        
        custom_layout.addLayout(custom_controls)
        custom_layout.addWidget(self.custom_nodes_list)
        custom_group.setLayout(custom_layout)
        
        layout.addLayout(search_layout)
        layout.addWidget(QLabel("Available Nodes:"))
        layout.addWidget(self.nodes_list)
        layout.addWidget(details_group)
        layout.addWidget(custom_group)
        
        return widget
    
    def _create_api_tab(self) -> QWidget:
        """Create the API integration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API configuration
        config_group = QGroupBox("API Configuration")
        config_layout = QFormLayout()
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Your n8n API key...")
        
        self.api_endpoint_input = QLineEdit()
        self.api_endpoint_input.setText(f"{self.n8n_url}/api/v1")
        
        self.webhook_url_input = QLineEdit()
        self.webhook_url_input.setText(f"{self.n8n_url}/webhook")
        self.webhook_url_input.setReadOnly(True)
        
        config_layout.addRow("API Key:", self.api_key_input)
        config_layout.addRow("API Endpoint:", self.api_endpoint_input)
        config_layout.addRow("Webhook URL:", self.webhook_url_input)
        
        config_group.setLayout(config_layout)
        
        # API examples
        examples_group = QGroupBox("API Examples")
        examples_layout = QVBoxLayout()
        
        self.api_examples_text = QPlainTextEdit()
        self.api_examples_text.setReadOnly(True)
        self.api_examples_text.setPlainText("""# List all workflows
curl -X GET http://localhost:5678/api/v1/workflows \\
  -H "X-N8N-API-KEY: your-api-key"

# Execute workflow
curl -X POST http://localhost:5678/api/v1/workflows/{id}/execute \\
  -H "X-N8N-API-KEY: your-api-key" \\
  -H "Content-Type: application/json" \\
  -d '{"data": {"key": "value"}}'

# Create webhook trigger
curl -X POST http://localhost:5678/webhook/your-webhook-id \\
  -H "Content-Type: application/json" \\
  -d '{"event": "user.created", "data": {...}}'
""")
        
        examples_layout.addWidget(self.api_examples_text)
        examples_group.setLayout(examples_layout)
        
        # Test API
        test_group = QGroupBox("Test API")
        test_layout = QVBoxLayout()
        
        test_controls = QHBoxLayout()
        self.test_method_combo = QComboBox()
        self.test_method_combo.addItems(["GET", "POST", "PUT", "DELETE"])
        
        self.test_endpoint_input = QLineEdit()
        self.test_endpoint_input.setPlaceholderText("/workflows")
        
        self.test_api_btn = QPushButton("🧪 Test")
        
        test_controls.addWidget(self.test_method_combo)
        test_controls.addWidget(self.test_endpoint_input)
        test_controls.addWidget(self.test_api_btn)
        
        self.test_result_text = QPlainTextEdit()
        self.test_result_text.setReadOnly(True)
        self.test_result_text.setMaximumHeight(150)
        self.test_result_text.setPlaceholderText("API response will appear here...")
        
        test_layout.addLayout(test_controls)
        test_layout.addWidget(self.test_result_text)
        test_group.setLayout(test_layout)
        
        layout.addWidget(config_group)
        layout.addWidget(examples_group)
        layout.addWidget(test_group)
        layout.addStretch()
        
        return widget
    
    def _create_logs_tab(self) -> QWidget:
        """Create the logs viewing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log filters
        filter_layout = QHBoxLayout()
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["All", "Info", "Warning", "Error", "Debug"])
        self.log_source_filter = QComboBox()
        self.log_source_filter.addItems(["All", "Workflows", "System", "API", "Nodes"])
        self.log_search_input = QLineEdit()
        self.log_search_input.setPlaceholderText("Search logs...")
        
        filter_layout.addWidget(QLabel("Level:"))
        filter_layout.addWidget(self.log_level_filter)
        filter_layout.addWidget(QLabel("Source:"))
        filter_layout.addWidget(self.log_source_filter)
        filter_layout.addWidget(self.log_search_input)
        filter_layout.addStretch()
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        # Add sample logs
        sample_logs = """[2025-01-18 10:30:15] INFO: Workflow 'Data Processing' started
[2025-01-18 10:30:17] INFO: Node 'HTTP Request' executed successfully
[2025-01-18 10:30:18] INFO: Node 'Transform Data' executed successfully
[2025-01-18 10:30:20] INFO: Workflow 'Data Processing' completed in 5s
[2025-01-18 10:28:00] INFO: Workflow 'Email Automation' started
[2025-01-18 10:28:02] WARNING: Node 'Email' retry attempt 1/3
[2025-01-18 10:15:00] ERROR: Workflow 'Web Scraping' failed: Timeout error
[2025-01-18 10:00:00] INFO: n8n server started on port 5678
[2025-01-18 09:59:50] INFO: Loading workflows from database
[2025-01-18 09:59:45] INFO: Initializing n8n..."""
        
        self.log_display.setPlainText(sample_logs)
        
        # Log actions
        actions_layout = QHBoxLayout()
        self.clear_logs_btn = QPushButton("🗑️ Clear Logs")
        self.export_logs_btn = QPushButton("💾 Export Logs")
        self.refresh_logs_btn = QPushButton("🔄 Refresh")
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        
        actions_layout.addWidget(self.clear_logs_btn)
        actions_layout.addWidget(self.export_logs_btn)
        actions_layout.addWidget(self.refresh_logs_btn)
        actions_layout.addWidget(self.auto_scroll_checkbox)
        actions_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.log_display)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _init_n8n(self):
        """Initialize n8n connection."""
        # In production, this would connect to actual n8n instance
        self.update_status("n8n: Ready to start")
        
        # Setup periodic status check
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_n8n_status)
        self.status_timer.start(10000)  # Check every 10 seconds
    
    def _start_n8n(self):
        """Start n8n server."""
        self._run_operation("start_n8n", {})
    
    def _stop_n8n(self):
        """Stop n8n server."""
        reply = QMessageBox.question(
            self, "Confirm Stop",
            "Are you sure you want to stop n8n?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._run_operation("stop_n8n", {})
    
    def _open_n8n_ui(self):
        """Open n8n UI in browser."""
        QDesktopServices.openUrl(QUrl(self.n8n_url))
    
    def _refresh_workflows(self):
        """Refresh workflows list."""
        self._run_operation("list_workflows", {})
    
    def _execute_workflow(self):
        """Execute selected workflow."""
        # Get selected workflow
        current_row = self.workflows_table.currentRow()
        if current_row >= 0:
            workflow_id = self.workflows_table.item(current_row, 0).text()
            workflow_name = self.workflows_table.item(current_row, 1).text()
            
            reply = QMessageBox.question(
                self, "Execute Workflow",
                f"Execute workflow '{workflow_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._run_operation("execute_workflow", {"workflow_id": workflow_id})
    
    def _check_n8n_status(self):
        """Check n8n server status."""
        # In production, this would ping the n8n server
        pass
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = N8NWorker(operation, params)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_operation_finished)
        self.worker.error.connect(self._on_operation_error)
        self.worker.progress.connect(self.update_status)
        
        # Cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()
    
    def _on_operation_finished(self, result: Dict[str, Any]):
        """Handle operation completion."""
        if "status" in result:
            if result["status"] == "started":
                self.n8n_status = "Running"
                self.n8n_status_label.setText("Running")
                self.n8n_status_label.setStyleSheet("color: green;")
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.update_status("n8n: Running")
            elif result["status"] == "stopped":
                self.n8n_status = "Stopped"
                self.n8n_status_label.setText("Stopped")
                self.n8n_status_label.setStyleSheet("color: red;")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.update_status("n8n: Stopped")
        
        if "workflows" in result:
            # Update workflow statistics
            workflows = result["workflows"]
            self.workflows_count_label.setText(str(len(workflows)))
            active_count = sum(1 for w in workflows if w.get("active"))
            self.active_workflows_label.setText(str(active_count))
        
        if "execution_id" in result:
            QMessageBox.information(
                self, "Workflow Executed",
                f"Workflow execution started.\nExecution ID: {result['execution_id']}"
            )
        
        self.update_status("Ready")
    
    def _on_operation_error(self, error: str):
        """Handle operation error."""
        QMessageBox.critical(self, "Error", f"Operation failed: {error}")
        self.update_status("Error occurred")
    
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {message}")
        self.status_updated.emit(message)
    
    def cleanup(self):
        """Clean up resources."""
        if self.status_timer:
            self.status_timer.stop()
        
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()