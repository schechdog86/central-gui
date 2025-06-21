"""
Ray Cluster View Component
=========================

Comprehensive UI for distributed computing with Ray cluster management.
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
    QTableWidgetItem, QHeaderView, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QColor


class RayClusterWorker(QObject):
    """Worker thread for Ray cluster operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    node_status_update = pyqtSignal(dict)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the Ray cluster operation."""
        try:
            self.progress.emit(f"Starting {self.operation}...")
            
            # Simulate operations for now
            # In production, this would connect to actual Ray cluster
            
            if self.operation == "start_cluster":
                result = {
                    "status": "started",
                    "head_node": "ray://localhost:10001",
                    "dashboard": "http://localhost:8265"
                }
            elif self.operation == "stop_cluster":
                result = {"status": "stopped"}
            elif self.operation == "get_cluster_status":
                result = {
                    "status": "running",
                    "nodes": 3,
                    "cpus": 16,
                    "gpus": 2,
                    "memory": "32GB"
                }
            elif self.operation == "submit_job":
                result = {
                    "job_id": "job_12345",
                    "status": "submitted",
                    "estimated_time": "5 minutes"
                }
            else:
                result = {"status": "completed"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class RayClusterView(QWidget):
    """Main view for the Ray Cluster component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    job_submitted = pyqtSignal(dict)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.worker_thread = None
        self.worker = None
        self.cluster_status = "Stopped"
        
        self.setWindowTitle("Ray Cluster Manager")
        self._init_ui()
        self._init_ray()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Cluster Overview Tab
        self.overview_tab = self._create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Node Management Tab
        self.nodes_tab = self._create_nodes_tab()
        self.tab_widget.addTab(self.nodes_tab, "🖥️ Nodes")
        
        # Job Submission Tab
        self.jobs_tab = self._create_jobs_tab()
        self.tab_widget.addTab(self.jobs_tab, "📋 Jobs")
        
        # Task Monitor Tab
        self.tasks_tab = self._create_tasks_tab()
        self.tab_widget.addTab(self.tasks_tab, "⚡ Tasks")
        
        # Resource Allocation Tab
        self.resources_tab = self._create_resources_tab()
        self.tab_widget.addTab(self.resources_tab, "💾 Resources")
        
        # Configuration Tab
        self.config_tab = self._create_config_tab()
        self.tab_widget.addTab(self.config_tab, "⚙️ Configuration")
        
        # Logs Tab
        self.logs_tab = self._create_logs_tab()
        self.tab_widget.addTab(self.logs_tab, "📜 Logs")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("Ray Cluster: Stopped")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_overview_tab(self) -> QWidget:
        """Create the cluster overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Cluster control buttons
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶️ Start Cluster")
        self.start_btn.clicked.connect(self._start_cluster)
        self.stop_btn = QPushButton("⏹️ Stop Cluster")
        self.stop_btn.clicked.connect(self._stop_cluster)
        self.stop_btn.setEnabled(False)
        self.restart_btn = QPushButton("🔄 Restart Cluster")
        self.restart_btn.clicked.connect(self._restart_cluster)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.restart_btn)
        control_layout.addStretch()
        
        # Cluster status
        status_group = QGroupBox("Cluster Status")
        status_layout = QFormLayout()
        
        self.cluster_status_label = QLabel("Stopped")
        self.head_node_label = QLabel("N/A")
        self.dashboard_label = QLabel("N/A")
        self.nodes_count_label = QLabel("0")
        self.total_cpus_label = QLabel("0")
        self.total_gpus_label = QLabel("0")
        self.total_memory_label = QLabel("0 GB")
        
        status_layout.addRow("Status:", self.cluster_status_label)
        status_layout.addRow("Head Node:", self.head_node_label)
        status_layout.addRow("Dashboard:", self.dashboard_label)
        status_layout.addRow("Total Nodes:", self.nodes_count_label)
        status_layout.addRow("Total CPUs:", self.total_cpus_label)
        status_layout.addRow("Total GPUs:", self.total_gpus_label)
        status_layout.addRow("Total Memory:", self.total_memory_label)
        
        status_group.setLayout(status_layout)
        
        # Real-time metrics
        metrics_group = QGroupBox("Real-time Metrics")
        metrics_layout = QVBoxLayout()
        
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_progress)
        self.cpu_percent_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_percent_label)
        
        # Memory Usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Usage:"))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        memory_layout.addWidget(self.memory_progress)
        self.memory_percent_label = QLabel("0%")
        memory_layout.addWidget(self.memory_percent_label)
        
        # GPU Usage
        gpu_layout = QHBoxLayout()
        gpu_layout.addWidget(QLabel("GPU Usage:"))
        self.gpu_progress = QProgressBar()
        self.gpu_progress.setRange(0, 100)
        gpu_layout.addWidget(self.gpu_progress)
        self.gpu_percent_label = QLabel("0%")
        gpu_layout.addWidget(self.gpu_percent_label)
        
        metrics_layout.addLayout(cpu_layout)
        metrics_layout.addLayout(memory_layout)
        metrics_layout.addLayout(gpu_layout)
        
        metrics_group.setLayout(metrics_layout)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        self.open_dashboard_btn = QPushButton("🌐 Open Dashboard")
        self.scale_up_btn = QPushButton("⬆️ Scale Up")
        self.scale_down_btn = QPushButton("⬇️ Scale Down")
        self.autoscale_checkbox = QCheckBox("Enable Autoscaling")
        
        actions_layout.addWidget(self.open_dashboard_btn)
        actions_layout.addWidget(self.scale_up_btn)
        actions_layout.addWidget(self.scale_down_btn)
        actions_layout.addWidget(self.autoscale_checkbox)
        
        actions_group.setLayout(actions_layout)
        
        layout.addLayout(control_layout)
        layout.addWidget(status_group)
        layout.addWidget(metrics_group)
        layout.addWidget(actions_group)
        layout.addStretch()
        
        return widget
    
    def _create_nodes_tab(self) -> QWidget:
        """Create the node management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Node list
        self.nodes_table = QTableWidget()
        self.nodes_table.setColumnCount(7)
        self.nodes_table.setHorizontalHeaderLabels([
            "Node ID", "Type", "Status", "CPUs", "GPUs", "Memory", "Load"
        ])
        header = self.nodes_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Add sample nodes
        self._add_sample_nodes()
        
        # Node controls
        controls_layout = QHBoxLayout()
        self.add_node_btn = QPushButton("➕ Add Node")
        self.remove_node_btn = QPushButton("➖ Remove Node")
        self.refresh_nodes_btn = QPushButton("🔄 Refresh")
        self.node_details_btn = QPushButton("📋 Details")
        
        controls_layout.addWidget(self.add_node_btn)
        controls_layout.addWidget(self.remove_node_btn)
        controls_layout.addWidget(self.refresh_nodes_btn)
        controls_layout.addWidget(self.node_details_btn)
        controls_layout.addStretch()
        
        # Node configuration
        config_group = QGroupBox("Node Configuration")
        config_layout = QFormLayout()
        
        self.node_cpus_spin = QSpinBox()
        self.node_cpus_spin.setRange(1, 64)
        self.node_cpus_spin.setValue(4)
        
        self.node_memory_spin = QSpinBox()
        self.node_memory_spin.setRange(1, 256)
        self.node_memory_spin.setValue(8)
        self.node_memory_spin.setSuffix(" GB")
        
        self.node_gpus_spin = QSpinBox()
        self.node_gpus_spin.setRange(0, 8)
        self.node_gpus_spin.setValue(0)
        
        config_layout.addRow("CPUs:", self.node_cpus_spin)
        config_layout.addRow("Memory:", self.node_memory_spin)
        config_layout.addRow("GPUs:", self.node_gpus_spin)
        
        config_group.setLayout(config_layout)
        
        layout.addWidget(QLabel("Cluster Nodes:"))
        layout.addWidget(self.nodes_table)
        layout.addLayout(controls_layout)
        layout.addWidget(config_group)
        
        return widget
    
    def _create_jobs_tab(self) -> QWidget:
        """Create the job submission tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Job submission form
        submit_group = QGroupBox("Submit New Job")
        submit_layout = QFormLayout()
        
        self.job_name_input = QLineEdit()
        self.job_name_input.setPlaceholderText("my_job")
        
        self.job_script_text = QTextEdit()
        self.job_script_text.setPlaceholderText(
            "# Python script or Ray task\\n"
            "import ray\\n\\n"
            "@ray.remote\\n"
            "def my_task():\\n"
            "    return 'Hello from Ray!'"
        )
        self.job_script_text.setMaximumHeight(150)
        
        self.job_cpus_spin = QSpinBox()
        self.job_cpus_spin.setRange(1, 64)
        self.job_cpus_spin.setValue(1)
        
        self.job_gpus_spin = QSpinBox()
        self.job_gpus_spin.setRange(0, 8)
        self.job_gpus_spin.setValue(0)
        
        self.job_memory_spin = QSpinBox()
        self.job_memory_spin.setRange(1, 64)
        self.job_memory_spin.setValue(2)
        self.job_memory_spin.setSuffix(" GB")
        
        submit_layout.addRow("Job Name:", self.job_name_input)
        submit_layout.addRow("Script:", self.job_script_text)
        submit_layout.addRow("CPUs:", self.job_cpus_spin)
        submit_layout.addRow("GPUs:", self.job_gpus_spin)
        submit_layout.addRow("Memory:", self.job_memory_spin)
        
        submit_group.setLayout(submit_layout)
        
        # Submit button
        self.submit_job_btn = QPushButton("🚀 Submit Job")
        self.submit_job_btn.clicked.connect(self._submit_job)
        
        # Active jobs
        jobs_group = QGroupBox("Active Jobs")
        jobs_layout = QVBoxLayout()
        
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(6)
        self.jobs_table.setHorizontalHeaderLabels([
            "Job ID", "Name", "Status", "Progress", "Runtime", "Actions"
        ])
        header = self.jobs_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        jobs_layout.addWidget(self.jobs_table)
        jobs_group.setLayout(jobs_layout)
        
        # Job actions
        actions_layout = QHBoxLayout()
        self.cancel_job_btn = QPushButton("❌ Cancel Selected")
        self.view_output_btn = QPushButton("📄 View Output")
        self.export_results_btn = QPushButton("💾 Export Results")
        
        actions_layout.addWidget(self.cancel_job_btn)
        actions_layout.addWidget(self.view_output_btn)
        actions_layout.addWidget(self.export_results_btn)
        actions_layout.addStretch()
        
        layout.addWidget(submit_group)
        layout.addWidget(self.submit_job_btn)
        layout.addWidget(jobs_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_tasks_tab(self) -> QWidget:
        """Create the task monitoring tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Task filters
        filter_layout = QHBoxLayout()
        self.task_filter_combo = QComboBox()
        self.task_filter_combo.addItems([
            "All Tasks", "Running", "Pending", "Completed", "Failed"
        ])
        self.task_search_input = QLineEdit()
        self.task_search_input.setPlaceholderText("Search tasks...")
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.task_filter_combo)
        filter_layout.addWidget(self.task_search_input)
        filter_layout.addStretch()
        
        # Task tree
        self.tasks_tree = QTreeWidget()
        self.tasks_tree.setHeaderLabels([
            "Task ID", "Function", "Status", "Node", "Duration", "Result"
        ])
        
        # Task statistics
        stats_group = QGroupBox("Task Statistics")
        stats_layout = QFormLayout()
        
        self.total_tasks_label = QLabel("0")
        self.running_tasks_label = QLabel("0")
        self.completed_tasks_label = QLabel("0")
        self.failed_tasks_label = QLabel("0")
        self.avg_duration_label = QLabel("0s")
        
        stats_layout.addRow("Total Tasks:", self.total_tasks_label)
        stats_layout.addRow("Running:", self.running_tasks_label)
        stats_layout.addRow("Completed:", self.completed_tasks_label)
        stats_layout.addRow("Failed:", self.failed_tasks_label)
        stats_layout.addRow("Avg Duration:", self.avg_duration_label)
        
        stats_group.setLayout(stats_layout)
        
        # Split view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(filter_layout)
        left_layout.addWidget(self.tasks_tree)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(stats_group)
        splitter.setSizes([600, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_resources_tab(self) -> QWidget:
        """Create the resource allocation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Resource pools
        pools_group = QGroupBox("Resource Pools")
        pools_layout = QVBoxLayout()
        
        self.pools_table = QTableWidget()
        self.pools_table.setColumnCount(5)
        self.pools_table.setHorizontalHeaderLabels([
            "Pool Name", "CPUs", "GPUs", "Memory", "Utilization"
        ])
        
        # Add sample pools
        pools = [
            ("default", "16", "2", "32 GB", "45%"),
            ("gpu-pool", "8", "4", "64 GB", "78%"),
            ("cpu-pool", "32", "0", "128 GB", "23%")
        ]
        
        self.pools_table.setRowCount(len(pools))
        for i, (name, cpus, gpus, memory, util) in enumerate(pools):
            self.pools_table.setItem(i, 0, QTableWidgetItem(name))
            self.pools_table.setItem(i, 1, QTableWidgetItem(cpus))
            self.pools_table.setItem(i, 2, QTableWidgetItem(gpus))
            self.pools_table.setItem(i, 3, QTableWidgetItem(memory))
            self.pools_table.setItem(i, 4, QTableWidgetItem(util))
        
        pools_layout.addWidget(self.pools_table)
        pools_group.setLayout(pools_layout)
        
        # Resource allocation
        alloc_group = QGroupBox("Resource Allocation Policy")
        alloc_layout = QFormLayout()
        
        self.alloc_strategy = QComboBox()
        self.alloc_strategy.addItems([
            "Best Fit", "First Fit", "Round Robin", "Priority Based"
        ])
        
        self.cpu_overcommit_slider = QSlider(Qt.Orientation.Horizontal)
        self.cpu_overcommit_slider.setRange(100, 200)
        self.cpu_overcommit_slider.setValue(100)
        self.cpu_overcommit_label = QLabel("100%")
        self.cpu_overcommit_slider.valueChanged.connect(
            lambda v: self.cpu_overcommit_label.setText(f"{v}%")
        )
        
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(1, 1024)
        self.memory_limit_spin.setValue(256)
        self.memory_limit_spin.setSuffix(" GB")
        
        alloc_layout.addRow("Strategy:", self.alloc_strategy)
        alloc_layout.addRow("CPU Overcommit:", self.cpu_overcommit_slider)
        alloc_layout.addRow("", self.cpu_overcommit_label)
        alloc_layout.addRow("Memory Limit:", self.memory_limit_spin)
        
        alloc_group.setLayout(alloc_layout)
        
        # Resource actions
        actions_layout = QHBoxLayout()
        self.create_pool_btn = QPushButton("➕ Create Pool")
        self.delete_pool_btn = QPushButton("➖ Delete Pool")
        self.optimize_btn = QPushButton("⚡ Optimize Allocation")
        
        actions_layout.addWidget(self.create_pool_btn)
        actions_layout.addWidget(self.delete_pool_btn)
        actions_layout.addWidget(self.optimize_btn)
        actions_layout.addStretch()
        
        layout.addWidget(pools_group)
        layout.addWidget(alloc_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_config_tab(self) -> QWidget:
        """Create the configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Ray configuration
        config_group = QGroupBox("Ray Configuration")
        config_layout = QFormLayout()
        
        self.head_address_input = QLineEdit("localhost:10001")
        self.dashboard_port_input = QLineEdit("8265")
        self.object_store_memory_spin = QSpinBox()
        self.object_store_memory_spin.setRange(1, 64)
        self.object_store_memory_spin.setValue(8)
        self.object_store_memory_spin.setSuffix(" GB")
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        
        config_layout.addRow("Head Address:", self.head_address_input)
        config_layout.addRow("Dashboard Port:", self.dashboard_port_input)
        config_layout.addRow("Object Store Memory:", self.object_store_memory_spin)
        config_layout.addRow("Log Level:", self.log_level_combo)
        
        config_group.setLayout(config_layout)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()
        
        self.enable_gcs_checkbox = QCheckBox("Enable Global Control Store")
        self.enable_gcs_checkbox.setChecked(True)
        self.enable_plasma_checkbox = QCheckBox("Enable Plasma Store")
        self.enable_plasma_checkbox.setChecked(True)
        self.enable_dashboard_checkbox = QCheckBox("Enable Dashboard")
        self.enable_dashboard_checkbox.setChecked(True)
        
        self.worker_timeout_spin = QSpinBox()
        self.worker_timeout_spin.setRange(10, 600)
        self.worker_timeout_spin.setValue(60)
        self.worker_timeout_spin.setSuffix(" seconds")
        
        advanced_layout.addRow("GCS:", self.enable_gcs_checkbox)
        advanced_layout.addRow("Plasma:", self.enable_plasma_checkbox)
        advanced_layout.addRow("Dashboard:", self.enable_dashboard_checkbox)
        advanced_layout.addRow("Worker Timeout:", self.worker_timeout_spin)
        
        advanced_group.setLayout(advanced_layout)
        
        # Configuration actions
        actions_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("💾 Save Configuration")
        self.load_config_btn = QPushButton("📂 Load Configuration")
        self.reset_config_btn = QPushButton("🔄 Reset to Defaults")
        
        actions_layout.addWidget(self.save_config_btn)
        actions_layout.addWidget(self.load_config_btn)
        actions_layout.addWidget(self.reset_config_btn)
        actions_layout.addStretch()
        
        layout.addWidget(config_group)
        layout.addWidget(advanced_group)
        layout.addLayout(actions_layout)
        layout.addStretch()
        
        return widget
    
    def _create_logs_tab(self) -> QWidget:
        """Create the logs viewing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Log filters
        filter_layout = QHBoxLayout()
        self.log_level_filter = QComboBox()
        self.log_level_filter.addItems(["All", "DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_search_input = QLineEdit()
        self.log_search_input.setPlaceholderText("Search logs...")
        self.auto_scroll_checkbox = QCheckBox("Auto-scroll")
        self.auto_scroll_checkbox.setChecked(True)
        
        filter_layout.addWidget(QLabel("Level:"))
        filter_layout.addWidget(self.log_level_filter)
        filter_layout.addWidget(self.log_search_input)
        filter_layout.addWidget(self.auto_scroll_checkbox)
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
        
        # Log actions
        actions_layout = QHBoxLayout()
        self.clear_logs_btn = QPushButton("🗑️ Clear Logs")
        self.export_logs_btn = QPushButton("💾 Export Logs")
        self.refresh_logs_btn = QPushButton("🔄 Refresh")
        
        actions_layout.addWidget(self.clear_logs_btn)
        actions_layout.addWidget(self.export_logs_btn)
        actions_layout.addWidget(self.refresh_logs_btn)
        actions_layout.addStretch()
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.log_display)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _init_ray(self):
        """Initialize Ray connection."""
        # In production, this would connect to actual Ray cluster
        self.update_status("Ray Cluster: Ready to start")
        
        # Setup periodic status updates
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_cluster_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def _add_sample_nodes(self):
        """Add sample nodes to the table."""
        nodes = [
            ("node-001", "Head", "Running", "8", "1", "16 GB", "45%"),
            ("node-002", "Worker", "Running", "4", "0", "8 GB", "67%"),
            ("node-003", "Worker", "Running", "4", "1", "8 GB", "23%")
        ]
        
        self.nodes_table.setRowCount(len(nodes))
        for i, node_data in enumerate(nodes):
            for j, value in enumerate(node_data):
                self.nodes_table.setItem(i, j, QTableWidgetItem(value))
    
    def _start_cluster(self):
        """Start the Ray cluster."""
        self._run_operation("start_cluster", {})
    
    def _stop_cluster(self):
        """Stop the Ray cluster."""
        reply = QMessageBox.question(
            self, "Confirm Stop",
            "Are you sure you want to stop the Ray cluster?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._run_operation("stop_cluster", {})
    
    def _restart_cluster(self):
        """Restart the Ray cluster."""
        self._stop_cluster()
        QTimer.singleShot(1000, self._start_cluster)
    
    def _submit_job(self):
        """Submit a job to the Ray cluster."""
        job_name = self.job_name_input.text().strip()
        if not job_name:
            QMessageBox.warning(self, "Input Required", "Please provide a job name.")
            return
        
        params = {
            "name": job_name,
            "script": self.job_script_text.toPlainText(),
            "cpus": self.job_cpus_spin.value(),
            "gpus": self.job_gpus_spin.value(),
            "memory": self.job_memory_spin.value()
        }
        
        self._run_operation("submit_job", params)
    
    def _update_cluster_status(self):
        """Update cluster status periodically."""
        if self.cluster_status == "Running":
            # Simulate updating metrics
            import random
            cpu_usage = random.randint(20, 80)
            memory_usage = random.randint(30, 70)
            gpu_usage = random.randint(10, 90)
            
            self.cpu_progress.setValue(cpu_usage)
            self.cpu_percent_label.setText(f"{cpu_usage}%")
            
            self.memory_progress.setValue(memory_usage)
            self.memory_percent_label.setText(f"{memory_usage}%")
            
            self.gpu_progress.setValue(gpu_usage)
            self.gpu_percent_label.setText(f"{gpu_usage}%")
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = RayClusterWorker(operation, params)
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
                self.cluster_status = "Running"
                self.cluster_status_label.setText("Running")
                self.cluster_status_label.setStyleSheet("color: green;")
                self.head_node_label.setText(result.get("head_node", "N/A"))
                self.dashboard_label.setText(result.get("dashboard", "N/A"))
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.update_status("Ray Cluster: Running")
            elif result["status"] == "stopped":
                self.cluster_status = "Stopped"
                self.cluster_status_label.setText("Stopped")
                self.cluster_status_label.setStyleSheet("color: red;")
                self.head_node_label.setText("N/A")
                self.dashboard_label.setText("N/A")
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.update_status("Ray Cluster: Stopped")
            elif result["status"] == "submitted":
                QMessageBox.information(
                    self, "Job Submitted",
                    f"Job '{result.get('job_id', 'unknown')}' submitted successfully!\\n"
                    f"Estimated time: {result.get('estimated_time', 'unknown')}"
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