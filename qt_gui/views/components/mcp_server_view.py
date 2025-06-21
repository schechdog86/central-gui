"""
MCP Server/Manager View Component
================================

Comprehensive UI for Model Context Protocol server management.
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
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QColor


class MCPServerWorker(QObject):
    """Worker thread for MCP server operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    server_status_update = pyqtSignal(dict)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the MCP server operation."""
        try:
            self.progress.emit(f"Starting {self.operation}...")
            
            # Simulate operations for now
            # In production, this would connect to actual MCP servers
            
            if self.operation == "start_server":
                result = {
                    "status": "started",
                    "server_id": self.params.get("server_id"),
                    "port": self.params.get("port", 3000),
                    "pid": 12345
                }
            elif self.operation == "stop_server":
                result = {
                    "status": "stopped",
                    "server_id": self.params.get("server_id")
                }
            elif self.operation == "list_servers":
                result = {
                    "servers": [
                        {"id": "filesystem", "name": "Filesystem", "status": "running", "port": 3001},
                        {"id": "browser", "name": "Browser Automation", "status": "running", "port": 3002},
                        {"id": "github", "name": "GitHub", "status": "stopped", "port": 3003},
                        {"id": "slack", "name": "Slack", "status": "running", "port": 3004}
                    ]
                }
            elif self.operation == "install_server":
                result = {
                    "status": "installed",
                    "server": self.params.get("server_name")
                }
            else:
                result = {"status": "completed"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class MCPServerView(QWidget):
    """Main view for the MCP Server/Manager component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    server_started = pyqtSignal(str)
    server_stopped = pyqtSignal(str)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.worker_thread = None
        self.worker = None
        self.servers = {}
        
        self.setWindowTitle("MCP Server Manager")
        self._init_ui()
        self._init_mcp()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Server Management Tab
        self.servers_tab = self._create_servers_tab()
        self.tab_widget.addTab(self.servers_tab, "🖥️ Servers")
        
        # Configuration Tab
        self.config_tab = self._create_config_tab()
        self.tab_widget.addTab(self.config_tab, "⚙️ Configuration")
        
        # Tools & Resources Tab
        self.tools_tab = self._create_tools_tab()
        self.tab_widget.addTab(self.tools_tab, "🛠️ Tools")
        
        # Client Connections Tab
        self.clients_tab = self._create_clients_tab()
        self.tab_widget.addTab(self.clients_tab, "🔌 Clients")
        
        # Monitoring Tab
        self.monitoring_tab = self._create_monitoring_tab()
        self.tab_widget.addTab(self.monitoring_tab, "📊 Monitoring")
        
        # Smithery Integration Tab
        self.smithery_tab = self._create_smithery_tab()
        self.tab_widget.addTab(self.smithery_tab, "🏪 Smithery")
        
        # Logs Tab
        self.logs_tab = self._create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "📜 Logs")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("MCP Manager: Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_servers_tab(self) -> QWidget:
        """Create the server management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Server controls
        controls_layout = QHBoxLayout()
        self.add_server_btn = QPushButton("➕ Add Server")
        self.install_server_btn = QPushButton("📥 Install from NPM")
        self.refresh_servers_btn = QPushButton("🔄 Refresh")
        self.refresh_servers_btn.clicked.connect(self._refresh_servers)
        
        controls_layout.addWidget(self.add_server_btn)
        controls_layout.addWidget(self.install_server_btn)
        controls_layout.addWidget(self.refresh_servers_btn)
        controls_layout.addStretch()
        
        # Server list
        self.servers_table = QTableWidget()
        self.servers_table.setColumnCount(7)
        self.servers_table.setHorizontalHeaderLabels([
            "Server", "Type", "Status", "Port", "PID", "Uptime", "Actions"
        ])
        header = self.servers_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Add sample servers
        servers = [
            ("Filesystem", "Built-in", "Running", "3001", "12345", "2h 15m", ""),
            ("Browser Automation", "Custom", "Running", "3002", "12346", "1h 30m", ""),
            ("GitHub", "NPM", "Stopped", "3003", "-", "-", ""),
            ("Slack", "NPM", "Running", "3004", "12347", "45m", ""),
            ("Database", "Custom", "Running", "3005", "12348", "3h 20m", "")
        ]
        
        self.servers_table.setRowCount(len(servers))
        for i, server in enumerate(servers):
            for j, value in enumerate(server[:-1]):  # Skip actions column
                item = QTableWidgetItem(value)
                if j == 2:  # Status column
                    if value == "Running":
                        item.setBackground(QColor(200, 255, 200))
                    else:
                        item.setBackground(QColor(255, 200, 200))
                self.servers_table.setItem(i, j, item)
        
        # Server details
        details_group = QGroupBox("Server Details")
        details_layout = QFormLayout()
        
        self.server_name_label = QLabel("Select a server")
        self.server_command_label = QLabel("-")
        self.server_args_label = QLabel("-")
        self.server_env_text = QTextEdit()
        self.server_env_text.setMaximumHeight(80)
        self.server_env_text.setPlaceholderText("Environment variables...")
        
        details_layout.addRow("Name:", self.server_name_label)
        details_layout.addRow("Command:", self.server_command_label)
        details_layout.addRow("Arguments:", self.server_args_label)
        details_layout.addRow("Environment:", self.server_env_text)
        
        details_group.setLayout(details_layout)
        
        # Server actions
        actions_layout = QHBoxLayout()
        self.start_server_btn = QPushButton("▶️ Start")
        self.start_server_btn.clicked.connect(self._start_server)
        self.stop_server_btn = QPushButton("⏹️ Stop")
        self.stop_server_btn.clicked.connect(self._stop_server)
        self.restart_server_btn = QPushButton("🔄 Restart")
        self.edit_server_btn = QPushButton("✏️ Edit")
        self.delete_server_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.start_server_btn)
        actions_layout.addWidget(self.stop_server_btn)
        actions_layout.addWidget(self.restart_server_btn)
        actions_layout.addWidget(self.edit_server_btn)
        actions_layout.addWidget(self.delete_server_btn)
        actions_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.servers_table)
        layout.addWidget(details_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_config_tab(self) -> QWidget:
        """Create the configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Global configuration
        global_group = QGroupBox("Global Configuration")
        global_layout = QFormLayout()
        
        self.mcp_home_input = QLineEdit()
        self.mcp_home_input.setText(str(Path.home() / ".mcp"))
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        
        self.max_servers_spin = QSpinBox()
        self.max_servers_spin.setRange(1, 50)
        self.max_servers_spin.setValue(10)
        
        self.auto_restart_checkbox = QCheckBox("Auto-restart crashed servers")
        self.auto_restart_checkbox.setChecked(True)
        
        global_layout.addRow("MCP Home:", self.mcp_home_input)
        global_layout.addRow("Log Level:", self.log_level_combo)
        global_layout.addRow("Max Servers:", self.max_servers_spin)
        global_layout.addRow(self.auto_restart_checkbox)
        
        global_group.setLayout(global_layout)
        
        # Server templates
        templates_group = QGroupBox("Server Templates")
        templates_layout = QVBoxLayout()
        
        template_controls = QHBoxLayout()
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Basic Node.js Server",
            "Python MCP Server",
            "TypeScript Server",
            "Custom Template"
        ])
        self.create_from_template_btn = QPushButton("Create Server")
        
        template_controls.addWidget(self.template_combo)
        template_controls.addWidget(self.create_from_template_btn)
        
        self.template_preview = QPlainTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(200)
        self.template_preview.setPlainText("""// Basic Node.js MCP Server Template
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

const server = new Server({
  name: 'my-mcp-server',
  version: '1.0.0',
});

// Register tools
server.setRequestHandler('tools/list', async () => ({
  tools: [
    {
      name: 'example_tool',
      description: 'An example MCP tool',
      inputSchema: {
        type: 'object',
        properties: {
          input: { type: 'string' }
        }
      }
    }
  ]
}));

// Start server
const transport = new StdioServerTransport();
server.connect(transport);
""")
        
        templates_layout.addLayout(template_controls)
        templates_layout.addWidget(self.template_preview)
        templates_group.setLayout(templates_layout)
        
        # Configuration actions
        actions_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("💾 Save Configuration")
        self.export_config_btn = QPushButton("📤 Export")
        self.import_config_btn = QPushButton("📥 Import")
        
        actions_layout.addWidget(self.save_config_btn)
        actions_layout.addWidget(self.export_config_btn)
        actions_layout.addWidget(self.import_config_btn)
        actions_layout.addStretch()
        
        layout.addWidget(global_group)
        layout.addWidget(templates_group)
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        return widget
    
    def _create_tools_tab(self) -> QWidget:
        """Create the tools and resources tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Available tools
        tools_group = QGroupBox("Available Tools")
        tools_layout = QVBoxLayout()
        
        self.tools_tree = QTreeWidget()
        self.tools_tree.setHeaderLabels(["Tool", "Server", "Description"])
        
        # Add sample tools by category
        tool_categories = {
            "File System": [
                ("read_file", "filesystem", "Read file contents"),
                ("write_file", "filesystem", "Write to file"),
                ("list_directory", "filesystem", "List directory contents")
            ],
            "Browser": [
                ("navigate", "browser", "Navigate to URL"),
                ("screenshot", "browser", "Take screenshot"),
                ("click", "browser", "Click element")
            ],
            "Development": [
                ("create_issue", "github", "Create GitHub issue"),
                ("run_command", "terminal", "Execute shell command"),
                ("search_code", "codebase", "Search in codebase")
            ]
        }
        
        for category, tools in tool_categories.items():
            cat_item = QTreeWidgetItem(self.tools_tree)
            cat_item.setText(0, category)
            
            for tool in tools:
                tool_item = QTreeWidgetItem(cat_item)
                for i, value in enumerate(tool):
                    tool_item.setText(i, value)
        
        tools_layout.addWidget(self.tools_tree)
        tools_group.setLayout(tools_layout)
        
        # Resources
        resources_group = QGroupBox("Resources")
        resources_layout = QVBoxLayout()
        
        self.resources_tree = QTreeWidget()
        self.resources_tree.setHeaderLabels(["Resource", "Server", "Type"])
        
        resources = [
            ("Project Files", "filesystem", "Directory"),
            ("Chrome Browser", "browser", "Application"),
            ("GitHub API", "github", "API"),
            ("Local Database", "database", "SQLite")
        ]
        
        for resource in resources:
            item = QTreeWidgetItem(self.resources_tree)
            for i, value in enumerate(resource):
                item.setText(i, value)
        
        resources_layout.addWidget(self.resources_tree)
        resources_group.setLayout(resources_layout)
        
        # Tool testing
        test_group = QGroupBox("Test Tool")
        test_layout = QVBoxLayout()
        
        test_controls = QHBoxLayout()
        self.test_server_combo = QComboBox()
        self.test_server_combo.addItems(["filesystem", "browser", "github"])
        self.test_tool_combo = QComboBox()
        self.test_tool_combo.addItems(["read_file", "write_file", "list_directory"])
        self.test_tool_btn = QPushButton("🧪 Test")
        
        test_controls.addWidget(QLabel("Server:"))
        test_controls.addWidget(self.test_server_combo)
        test_controls.addWidget(QLabel("Tool:"))
        test_controls.addWidget(self.test_tool_combo)
        test_controls.addWidget(self.test_tool_btn)
        test_controls.addStretch()
        
        self.test_params_text = QPlainTextEdit()
        self.test_params_text.setMaximumHeight(80)
        self.test_params_text.setPlaceholderText('{"path": "/home/user/file.txt"}')
        
        self.test_result_text = QPlainTextEdit()
        self.test_result_text.setReadOnly(True)
        self.test_result_text.setMaximumHeight(100)
        self.test_result_text.setPlaceholderText("Test results will appear here...")
        
        test_layout.addLayout(test_controls)
        test_layout.addWidget(QLabel("Parameters (JSON):"))
        test_layout.addWidget(self.test_params_text)
        test_layout.addWidget(QLabel("Result:"))
        test_layout.addWidget(self.test_result_text)
        
        test_group.setLayout(test_layout)
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(tools_group)
        splitter.addWidget(resources_group)
        splitter.addWidget(test_group)
        splitter.setSizes([200, 100, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_clients_tab(self) -> QWidget:
        """Create the client connections tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Connected clients
        clients_group = QGroupBox("Connected Clients")
        clients_layout = QVBoxLayout()
        
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6)
        self.clients_table.setHorizontalHeaderLabels([
            "Client", "Server", "Connected Since", "Requests", "Status", "Actions"
        ])
        
        # Add sample clients
        clients = [
            ("Claude Desktop", "filesystem", "10:15 AM", "45", "Active", ""),
            ("VS Code Extension", "browser", "09:30 AM", "123", "Active", ""),
            ("Python Script", "github", "11:00 AM", "12", "Idle", ""),
            ("Test Client", "database", "10:45 AM", "5", "Active", "")
        ]
        
        self.clients_table.setRowCount(len(clients))
        for i, client in enumerate(clients):
            for j, value in enumerate(client[:-1]):
                item = QTableWidgetItem(value)
                if j == 4:  # Status column
                    if value == "Active":
                        item.setBackground(QColor(200, 255, 200))
                    else:
                        item.setBackground(QColor(255, 255, 200))
                self.clients_table.setItem(i, j, item)
        
        clients_layout.addWidget(self.clients_table)
        clients_group.setLayout(clients_layout)
        
        # Client configuration
        config_group = QGroupBox("Client Configuration")
        config_layout = QFormLayout()
        
        self.max_clients_spin = QSpinBox()
        self.max_clients_spin.setRange(1, 100)
        self.max_clients_spin.setValue(20)
        
        self.client_timeout_spin = QSpinBox()
        self.client_timeout_spin.setRange(10, 600)
        self.client_timeout_spin.setValue(60)
        self.client_timeout_spin.setSuffix(" seconds")
        
        self.allow_remote_checkbox = QCheckBox("Allow remote connections")
        self.require_auth_checkbox = QCheckBox("Require authentication")
        self.require_auth_checkbox.setChecked(True)
        
        config_layout.addRow("Max Clients:", self.max_clients_spin)
        config_layout.addRow("Idle Timeout:", self.client_timeout_spin)
        config_layout.addRow(self.allow_remote_checkbox)
        config_layout.addRow(self.require_auth_checkbox)
        
        config_group.setLayout(config_layout)
        
        # Client actions
        actions_layout = QHBoxLayout()
        self.disconnect_client_btn = QPushButton("🔌 Disconnect")
        self.block_client_btn = QPushButton("🚫 Block")
        self.view_client_logs_btn = QPushButton("📜 View Logs")
        
        actions_layout.addWidget(self.disconnect_client_btn)
        actions_layout.addWidget(self.block_client_btn)
        actions_layout.addWidget(self.view_client_logs_btn)
        actions_layout.addStretch()
        
        layout.addWidget(clients_group)
        layout.addWidget(config_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_monitoring_tab(self) -> QWidget:
        """Create the monitoring tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Server metrics
        metrics_group = QGroupBox("Server Metrics")
        metrics_layout = QVBoxLayout()
        
        # Metric cards
        cards_layout = QHBoxLayout()
        
        # Total requests card
        requests_card = QGroupBox("Total Requests")
        requests_layout = QVBoxLayout()
        self.total_requests_label = QLabel("1,234")
        self.total_requests_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.requests_rate_label = QLabel("15 req/min")
        requests_layout.addWidget(self.total_requests_label)
        requests_layout.addWidget(self.requests_rate_label)
        requests_card.setLayout(requests_layout)
        
        # Active connections card
        connections_card = QGroupBox("Active Connections")
        connections_layout = QVBoxLayout()
        self.active_connections_label = QLabel("8")
        self.active_connections_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.peak_connections_label = QLabel("Peak: 12")
        connections_layout.addWidget(self.active_connections_label)
        connections_layout.addWidget(self.peak_connections_label)
        connections_card.setLayout(connections_layout)
        
        # Uptime card
        uptime_card = QGroupBox("Uptime")
        uptime_layout = QVBoxLayout()
        self.uptime_label = QLabel("3d 14h 25m")
        self.uptime_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.availability_label = QLabel("99.9% availability")
        uptime_layout.addWidget(self.uptime_label)
        uptime_layout.addWidget(self.availability_label)
        uptime_card.setLayout(uptime_layout)
        
        cards_layout.addWidget(requests_card)
        cards_layout.addWidget(connections_card)
        cards_layout.addWidget(uptime_card)
        
        metrics_layout.addLayout(cards_layout)
        metrics_group.setLayout(metrics_layout)
        
        # Performance metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QFormLayout()
        
        self.avg_response_label = QLabel("45ms")
        self.p95_response_label = QLabel("120ms")
        self.p99_response_label = QLabel("250ms")
        self.error_rate_label = QLabel("0.02%")
        
        perf_layout.addRow("Avg Response Time:", self.avg_response_label)
        perf_layout.addRow("95th Percentile:", self.p95_response_label)
        perf_layout.addRow("99th Percentile:", self.p99_response_label)
        perf_layout.addRow("Error Rate:", self.error_rate_label)
        
        perf_group.setLayout(perf_layout)
        
        # Recent errors
        errors_group = QGroupBox("Recent Errors")
        errors_layout = QVBoxLayout()
        
        self.errors_list = QListWidget()
        errors = [
            "❌ [10:30:15] filesystem: Permission denied - /etc/passwd",
            "⚠️ [10:25:42] browser: Timeout waiting for element",
            "❌ [10:15:33] github: API rate limit exceeded"
        ]
        self.errors_list.addItems(errors)
        self.errors_list.setMaximumHeight(150)
        
        errors_layout.addWidget(self.errors_list)
        errors_group.setLayout(errors_layout)
        
        layout.addWidget(metrics_group)
        layout.addWidget(perf_group)
        layout.addWidget(errors_group)
        layout.addStretch()
        
        return widget
    
    def _create_smithery_tab(self) -> QWidget:
        """Create the Smithery integration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Smithery browser
        browser_group = QGroupBox("Browse Smithery")
        browser_layout = QVBoxLayout()
        
        # Search
        search_layout = QHBoxLayout()
        self.smithery_search_input = QLineEdit()
        self.smithery_search_input.setPlaceholderText("Search MCP servers...")
        self.search_smithery_btn = QPushButton("🔍 Search")
        
        search_layout.addWidget(self.smithery_search_input)
        search_layout.addWidget(self.search_smithery_btn)
        
        # Server list
        self.smithery_list = QTreeWidget()
        self.smithery_list.setHeaderLabels(["Server", "Author", "Downloads", "Rating"])
        
        # Add sample servers
        servers = [
            ("Filesystem Extended", "mcp-community", "15.2k", "⭐⭐⭐⭐⭐"),
            ("AWS Integration", "aws-official", "8.7k", "⭐⭐⭐⭐"),
            ("Docker Manager", "docker-team", "6.3k", "⭐⭐⭐⭐⭐"),
            ("Kubernetes Tools", "k8s-contrib", "4.1k", "⭐⭐⭐⭐"),
            ("Database Toolkit", "db-tools", "3.2k", "⭐⭐⭐")
        ]
        
        for server in servers:
            item = QTreeWidgetItem(self.smithery_list)
            for i, value in enumerate(server):
                item.setText(i, value)
        
        browser_layout.addLayout(search_layout)
        browser_layout.addWidget(self.smithery_list)
        browser_group.setLayout(browser_layout)
        
        # Server details
        details_group = QGroupBox("Server Details")
        details_layout = QVBoxLayout()
        
        self.smithery_details_text = QTextEdit()
        self.smithery_details_text.setReadOnly(True)
        self.smithery_details_text.setMaximumHeight(150)
        self.smithery_details_text.setHtml("""
        <h3>Filesystem Extended</h3>
        <p><b>Author:</b> mcp-community</p>
        <p><b>Version:</b> 2.1.0</p>
        <p><b>Description:</b> Extended filesystem operations with advanced features like file watching, batch operations, and compression support.</p>
        <p><b>Tools:</b> 25 tools available</p>
        <p><b>License:</b> MIT</p>
        """)
        
        details_layout.addWidget(self.smithery_details_text)
        details_group.setLayout(details_layout)
        
        # Installation
        install_layout = QHBoxLayout()
        self.install_smithery_btn = QPushButton("📥 Install Selected")
        self.update_smithery_btn = QPushButton("🔄 Update")
        self.view_docs_btn = QPushButton("📚 View Documentation")
        
        install_layout.addWidget(self.install_smithery_btn)
        install_layout.addWidget(self.update_smithery_btn)
        install_layout.addWidget(self.view_docs_btn)
        install_layout.addStretch()
        
        layout.addWidget(browser_group)
        layout.addWidget(details_group)
        layout.addLayout(install_layout)
        
        return widget
    
    def _create_logs_tab(self) -> QWidget:
        """Create the logs viewing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log filters
        filter_layout = QHBoxLayout()
        self.log_server_filter = QComboBox()
        self.log_server_filter.addItems(["All Servers", "filesystem", "browser", "github"])
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["All", "DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_search_input = QLineEdit()
        self.log_search_input.setPlaceholderText("Search logs...")
        
        filter_layout.addWidget(QLabel("Server:"))
        filter_layout.addWidget(self.log_server_filter)
        filter_layout.addWidget(QLabel("Level:"))
        filter_layout.addWidget(self.log_level_filter)
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
        sample_logs = """[2025-01-18 10:30:15] [filesystem] INFO: Server started on port 3001
[2025-01-18 10:30:16] [filesystem] INFO: Registered 15 tools
[2025-01-18 10:30:20] [browser] INFO: Server started on port 3002
[2025-01-18 10:30:21] [browser] INFO: Chrome browser initialized
[2025-01-18 10:30:25] [filesystem] DEBUG: Received request: tools/list
[2025-01-18 10:30:26] [filesystem] DEBUG: Response sent in 15ms
[2025-01-18 10:30:30] [github] INFO: Server started on port 3003
[2025-01-18 10:30:31] [github] WARNING: Rate limit: 4500/5000 remaining
[2025-01-18 10:30:35] [browser] ERROR: Failed to take screenshot: element not found
[2025-01-18 10:30:40] [filesystem] INFO: Client connected: Claude Desktop
[2025-01-18 10:30:45] [filesystem] DEBUG: Executing tool: read_file
[2025-01-18 10:30:46] [filesystem] INFO: File read successfully: /home/user/document.txt"""
        
        self.log_display.setPlainText(sample_logs)
        
        # Log actions
        actions_layout = QHBoxLayout()
        self.clear_logs_btn = QPushButton("🗑️ Clear Logs")
        self.export_logs_btn = QPushButton("💾 Export Logs")
        self.pause_logs_checkbox = QCheckBox("Pause")
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        
        actions_layout.addWidget(self.clear_logs_btn)
        actions_layout.addWidget(self.export_logs_btn)
        actions_layout.addWidget(self.pause_logs_checkbox)
        actions_layout.addWidget(self.auto_scroll_checkbox)
        actions_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.log_display)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _init_mcp(self):
        """Initialize MCP server manager."""
        # In production, this would connect to actual MCP servers
        self.update_status("MCP Manager initialized")
        
        # Setup periodic status check
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_server_status)
        self.status_timer.start(5000)  # Check every 5 seconds
        
        # Initial server refresh
        QTimer.singleShot(1000, self._refresh_servers)
    
    def _refresh_servers(self):
        """Refresh the server list."""
        self._run_operation("list_servers", {})
    
    def _start_server(self):
        """Start selected server."""
        current_row = self.servers_table.currentRow()
        if current_row >= 0:
            server_name = self.servers_table.item(current_row, 0).text()
            server_port = self.servers_table.item(current_row, 3).text()
            
            self._run_operation("start_server", {
                "server_id": server_name.lower().replace(" ", "_"),
                "port": int(server_port) if server_port.isdigit() else 3000
            })
    
    def _stop_server(self):
        """Stop selected server."""
        current_row = self.servers_table.currentRow()
        if current_row >= 0:
            server_name = self.servers_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Confirm Stop",
                f"Stop server '{server_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._run_operation("stop_server", {
                    "server_id": server_name.lower().replace(" ", "_")
                })
    
    def _check_server_status(self):
        """Check status of all servers."""
        # In production, this would check actual server status
        pass
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = MCPServerWorker(operation, params)
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
                server_id = result.get("server_id", "unknown")
                QMessageBox.information(
                    self, "Server Started",
                    f"Server '{server_id}' started on port {result.get('port', 'unknown')}"
                )
                self.server_started.emit(server_id)
            elif result["status"] == "stopped":
                server_id = result.get("server_id", "unknown")
                QMessageBox.information(
                    self, "Server Stopped",
                    f"Server '{server_id}' stopped successfully"
                )
                self.server_stopped.emit(server_id)
        
        if "servers" in result:
            # Update server table
            servers = result["servers"]
            self.servers_table.setRowCount(len(servers))
            for i, server in enumerate(servers):
                self.servers_table.setItem(i, 0, QTableWidgetItem(server["name"]))
                self.servers_table.setItem(i, 1, QTableWidgetItem("NPM"))
                
                status_item = QTableWidgetItem(server["status"].title())
                if server["status"] == "running":
                    status_item.setBackground(QColor(200, 255, 200))
                else:
                    status_item.setBackground(QColor(255, 200, 200))
                self.servers_table.setItem(i, 2, status_item)
                
                self.servers_table.setItem(i, 3, QTableWidgetItem(str(server["port"])))
                self.servers_table.setItem(i, 4, QTableWidgetItem("-"))
                self.servers_table.setItem(i, 5, QTableWidgetItem("-"))
        
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