"""
Agent Orchestrator View Component
=================================

Manages multiple AI agents, orchestrates workflows, and handles model training.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QSlider, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QColor, QPen, QPainter

# Try to import charts, but make it optional
try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False


class TrainingWorker(QObject):
    """Worker thread for model training operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # percentage, message
    metrics_update = pyqtSignal(dict)  # training metrics
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
        self.is_cancelled = False
    
    def run(self):
        """Execute training operations."""
        try:
            if self.operation == "train_model":
                self._train_model()
            elif self.operation == "fine_tune":
                self._fine_tune_model()
            elif self.operation == "evaluate_model":
                self._evaluate_model()
            elif self.operation == "export_model":
                self._export_model()
            else:
                self.finished.emit({"status": "unknown operation"})
                
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        """Cancel the current operation."""
        self.is_cancelled = True
    
    def _train_model(self):
        """Train a new model."""
        # Simulate training process
        epochs = self.params.get("epochs", 10)
        for epoch in range(epochs):
            if self.is_cancelled:
                break
                
            progress = int((epoch + 1) / epochs * 100)
            self.progress.emit(progress, f"Training epoch {epoch + 1}/{epochs}")
            
            # Simulate metrics
            metrics = {
                "epoch": epoch + 1,
                "loss": 2.5 - (epoch * 0.2),
                "accuracy": 0.6 + (epoch * 0.04),
                "val_loss": 2.8 - (epoch * 0.15),
                "val_accuracy": 0.55 + (epoch * 0.035)
            }
            self.metrics_update.emit(metrics)
            
            # Simulate time for training
            QThread.msleep(1000)
        
        if not self.is_cancelled:
            self.finished.emit({"status": "completed", "model_path": "/path/to/model"})
    
    def _fine_tune_model(self):
        """Fine-tune an existing model."""
        self.progress.emit(50, "Fine-tuning model...")
        QThread.msleep(2000)
        self.finished.emit({"status": "fine-tuned"})
    
    def _evaluate_model(self):
        """Evaluate model performance."""
        self.progress.emit(50, "Evaluating model...")
        QThread.msleep(1500)
        self.finished.emit({
            "status": "evaluated",
            "metrics": {
                "accuracy": 0.92,
                "precision": 0.89,
                "recall": 0.91,
                "f1_score": 0.90
            }
        })
    
    def _export_model(self):
        """Export trained model."""
        self.progress.emit(50, "Exporting model...")
        QThread.msleep(1000)
        self.finished.emit({"status": "exported", "path": self.params.get("export_path")})


class AgentCreationDialog(QDialog):
    """Dialog for creating a new agent."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Agent")
        self.setModal(True)
        self.resize(600, 500)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Agent details
        details_group = QGroupBox("Agent Details")
        details_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "General Purpose",
            "Code Assistant",
            "Data Analyst",
            "Creative Writer",
            "Research Assistant",
            "Custom"
        ])
        
        details_layout.addRow("Name:", self.name_input)
        details_layout.addRow("Type:", self.type_combo)
        details_layout.addRow("Description:", self.description_input)
        
        details_group.setLayout(details_layout)
        
        # Model selection
        model_group = QGroupBox("Model Configuration")
        model_layout = QFormLayout()
        
        self.base_model_combo = QComboBox()
        self.base_model_combo.addItems([
            "gpt-4",
            "claude-3-opus",
            "llama2-70b",
            "codellama-34b",
            "mixtral-8x7b",
            "custom-trained"
        ])
        
        self.model_size_combo = QComboBox()
        self.model_size_combo.addItems(["Small", "Medium", "Large", "XL"])
        
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        self.temperature_label = QLabel("0.7")
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(f"{v/100:.1f}")
        )
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        
        model_layout.addRow("Base Model:", self.base_model_combo)
        model_layout.addRow("Model Size:", self.model_size_combo)
        model_layout.addRow("Temperature:", temp_layout)
        
        model_group.setLayout(model_layout)
        
        # Capabilities
        capabilities_group = QGroupBox("Capabilities")
        capabilities_layout = QVBoxLayout()
        
        self.cap_coding = QCheckBox("Code generation and analysis")
        self.cap_research = QCheckBox("Research and information gathering")
        self.cap_data = QCheckBox("Data analysis and visualization")
        self.cap_creative = QCheckBox("Creative writing and content")
        self.cap_reasoning = QCheckBox("Complex reasoning and planning")
        
        capabilities_layout.addWidget(self.cap_coding)
        capabilities_layout.addWidget(self.cap_research)
        capabilities_layout.addWidget(self.cap_data)
        capabilities_layout.addWidget(self.cap_creative)
        capabilities_layout.addWidget(self.cap_reasoning)
        
        capabilities_group.setLayout(capabilities_layout)
        
        # Resources
        resources_group = QGroupBox("Resource Allocation")
        resources_layout = QFormLayout()
        
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(512, 32768)
        self.memory_spin.setValue(4096)
        self.memory_spin.setSuffix(" MB")
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Normal", "High", "Critical"])
        self.priority_combo.setCurrentText("Normal")
        
        resources_layout.addRow("Memory:", self.memory_spin)
        resources_layout.addRow("Priority:", self.priority_combo)
        
        resources_group.setLayout(resources_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(details_group)
        layout.addWidget(model_group)
        layout.addWidget(capabilities_group)
        layout.addWidget(resources_group)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get the agent configuration."""
        return {
            "name": self.name_input.text(),
            "type": self.type_combo.currentText(),
            "description": self.description_input.toPlainText(),
            "model": {
                "base": self.base_model_combo.currentText(),
                "size": self.model_size_combo.currentText(),
                "temperature": self.temperature_slider.value() / 100
            },
            "capabilities": {
                "coding": self.cap_coding.isChecked(),
                "research": self.cap_research.isChecked(),
                "data_analysis": self.cap_data.isChecked(),
                "creative": self.cap_creative.isChecked(),
                "reasoning": self.cap_reasoning.isChecked()
            },
            "resources": {
                "memory": self.memory_spin.value(),
                "priority": self.priority_combo.currentText()
            }
        }


class AgentOrchestratorView(QWidget):
    """Main view for the Agent Orchestrator component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    agent_created = pyqtSignal(dict)
    workflow_started = pyqtSignal(str)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.agents = {}  # Active agents
        self.workflows = {}  # Defined workflows
        self.training_thread = None
        self.training_worker = None
        
        self.setWindowTitle("Agent Orchestrator")
        self._init_ui()
        self._init_sample_data()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Agent Management Tab
        self.agents_tab = self._create_agents_tab()
        self.tab_widget.addTab(self.agents_tab, "🤖 Agent Management")
        
        # Workflow Orchestration Tab
        self.workflow_tab = self._create_workflow_tab()
        self.tab_widget.addTab(self.workflow_tab, "🔄 Workflows")
        
        # Model Training Tab
        self.training_tab = self._create_training_tab()
        self.tab_widget.addTab(self.training_tab, "🎯 Model Training")
        
        # Performance Monitoring Tab
        self.monitoring_tab = self._create_monitoring_tab()
        self.tab_widget.addTab(self.monitoring_tab, "📊 Performance")
        
        # Multi-Agent Chat Tab
        self.chat_tab = self._create_multi_agent_chat_tab()
        self.tab_widget.addTab(self.chat_tab, "💬 Multi-Agent Chat")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_agents_tab(self) -> QWidget:
        """Create the agent management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Agent controls
        controls_layout = QHBoxLayout()
        
        self.create_agent_btn = QPushButton("Create Agent")
        self.create_agent_btn.clicked.connect(self._create_agent)
        
        self.import_agent_btn = QPushButton("Import Agent")
        self.export_agent_btn = QPushButton("Export Agent")
        
        controls_layout.addWidget(self.create_agent_btn)
        controls_layout.addWidget(self.import_agent_btn)
        controls_layout.addWidget(self.export_agent_btn)
        controls_layout.addStretch()
        
        # Agent list
        self.agents_table = QTableWidget()
        self.agents_table.setColumnCount(6)
        self.agents_table.setHorizontalHeaderLabels([
            "Name", "Type", "Model", "Status", "Tasks", "Actions"
        ])
        header = self.agents_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Agent details
        details_group = QGroupBox("Agent Details")
        details_layout = QVBoxLayout()
        
        self.agent_details = QTextEdit()
        self.agent_details.setReadOnly(True)
        self.agent_details.setMaximumHeight(150)
        
        details_layout.addWidget(self.agent_details)
        details_group.setLayout(details_layout)
        
        # Agent actions
        actions_layout = QHBoxLayout()
        
        self.start_agent_btn = QPushButton("Start")
        self.stop_agent_btn = QPushButton("Stop")
        self.configure_agent_btn = QPushButton("Configure")
        self.delete_agent_btn = QPushButton("Delete")
        
        actions_layout.addWidget(self.start_agent_btn)
        actions_layout.addWidget(self.stop_agent_btn)
        actions_layout.addWidget(self.configure_agent_btn)
        actions_layout.addWidget(self.delete_agent_btn)
        actions_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.agents_table)
        layout.addWidget(details_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_workflow_tab(self) -> QWidget:
        """Create the workflow orchestration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Workflow designer
        designer_group = QGroupBox("Workflow Designer")
        designer_layout = QVBoxLayout()
        
        # Workflow controls
        workflow_controls = QHBoxLayout()
        
        self.new_workflow_btn = QPushButton("New Workflow")
        self.save_workflow_btn = QPushButton("Save Workflow")
        self.load_workflow_btn = QPushButton("Load Workflow")
        
        workflow_controls.addWidget(self.new_workflow_btn)
        workflow_controls.addWidget(self.save_workflow_btn)
        workflow_controls.addWidget(self.load_workflow_btn)
        workflow_controls.addStretch()
        
        # Workflow canvas (simplified representation)
        self.workflow_tree = QTreeWidget()
        self.workflow_tree.setHeaderLabels(["Step", "Agent", "Action", "Input", "Output"])
        
        designer_layout.addLayout(workflow_controls)
        designer_layout.addWidget(self.workflow_tree)
        
        designer_group.setLayout(designer_layout)
        
        # Workflow execution
        execution_group = QGroupBox("Workflow Execution")
        execution_layout = QVBoxLayout()
        
        exec_controls = QHBoxLayout()
        
        self.workflow_combo = QComboBox()
        self.workflow_combo.addItems([
            "Code Review Pipeline",
            "Data Analysis Workflow",
            "Content Generation Chain",
            "Research Assistant Flow"
        ])
        
        self.run_workflow_btn = QPushButton("Run Workflow")
        self.run_workflow_btn.clicked.connect(self._run_workflow)
        
        self.pause_workflow_btn = QPushButton("Pause")
        self.stop_workflow_btn = QPushButton("Stop")
        
        exec_controls.addWidget(QLabel("Workflow:"))
        exec_controls.addWidget(self.workflow_combo)
        exec_controls.addWidget(self.run_workflow_btn)
        exec_controls.addWidget(self.pause_workflow_btn)
        exec_controls.addWidget(self.stop_workflow_btn)
        exec_controls.addStretch()
        
        # Execution log
        self.execution_log = QTextEdit()
        self.execution_log.setReadOnly(True)
        self.execution_log.setMaximumHeight(200)
        
        execution_layout.addLayout(exec_controls)
        execution_layout.addWidget(self.execution_log)
        
        execution_group.setLayout(execution_layout)
        
        layout.addWidget(designer_group)
        layout.addWidget(execution_group)
        
        return widget
    
    def _create_training_tab(self) -> QWidget:
        """Create the model training tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Training configuration
        config_group = QGroupBox("Training Configuration")
        config_layout = QFormLayout()
        
        # Model selection
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems([
            "Language Model (LLM)",
            "Code Generation Model",
            "Classification Model",
            "Embedding Model",
            "Multi-Modal Model"
        ])
        
        # Dataset
        dataset_layout = QHBoxLayout()
        self.dataset_path = QLineEdit()
        self.browse_dataset_btn = QPushButton("Browse...")
        self.browse_dataset_btn.clicked.connect(self._browse_dataset)
        
        dataset_layout.addWidget(self.dataset_path)
        dataset_layout.addWidget(self.browse_dataset_btn)
        
        # Training parameters
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(10)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 512)
        self.batch_size_spin.setValue(32)
        
        self.learning_rate_spin = QDoubleSpinBox()
        self.learning_rate_spin.setRange(0.00001, 1.0)
        self.learning_rate_spin.setValue(0.001)
        self.learning_rate_spin.setDecimals(5)
        
        # Hardware selection
        self.device_combo = QComboBox()
        self.device_combo.addItems(["CPU", "GPU (CUDA)", "GPU (ROCm)", "TPU"])
        
        config_layout.addRow("Model Type:", self.model_type_combo)
        config_layout.addRow("Dataset:", dataset_layout)
        config_layout.addRow("Epochs:", self.epochs_spin)
        config_layout.addRow("Batch Size:", self.batch_size_spin)
        config_layout.addRow("Learning Rate:", self.learning_rate_spin)
        config_layout.addRow("Device:", self.device_combo)
        
        config_group.setLayout(config_layout)
        
        # Training controls
        train_controls = QHBoxLayout()
        
        self.start_training_btn = QPushButton("Start Training")
        self.start_training_btn.clicked.connect(self._start_training)
        
        self.pause_training_btn = QPushButton("Pause")
        self.stop_training_btn = QPushButton("Stop")
        
        train_controls.addWidget(self.start_training_btn)
        train_controls.addWidget(self.pause_training_btn)
        train_controls.addWidget(self.stop_training_btn)
        train_controls.addStretch()
        
        # Training progress
        progress_group = QGroupBox("Training Progress")
        progress_layout = QVBoxLayout()
        
        self.training_progress = QProgressBar()
        self.training_status_label = QLabel("Not training")
        
        # Metrics display
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(5)
        self.metrics_table.setHorizontalHeaderLabels([
            "Epoch", "Loss", "Accuracy", "Val Loss", "Val Accuracy"
        ])
        
        progress_layout.addWidget(self.training_progress)
        progress_layout.addWidget(self.training_status_label)
        progress_layout.addWidget(self.metrics_table)
        
        progress_group.setLayout(progress_layout)
        
        # Model evaluation
        eval_group = QGroupBox("Model Evaluation")
        eval_layout = QHBoxLayout()
        
        self.evaluate_btn = QPushButton("Evaluate Model")
        self.export_model_btn = QPushButton("Export Model")
        self.deploy_model_btn = QPushButton("Deploy Model")
        
        eval_layout.addWidget(self.evaluate_btn)
        eval_layout.addWidget(self.export_model_btn)
        eval_layout.addWidget(self.deploy_model_btn)
        eval_layout.addStretch()
        
        eval_group.setLayout(eval_layout)
        
        layout.addWidget(config_group)
        layout.addLayout(train_controls)
        layout.addWidget(progress_group)
        layout.addWidget(eval_group)
        
        return widget
    
    def _create_monitoring_tab(self) -> QWidget:
        """Create the performance monitoring tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Real-time metrics
        metrics_group = QGroupBox("Real-time Metrics")
        metrics_layout = QFormLayout()
        
        self.active_agents_label = QLabel("0")
        self.total_tasks_label = QLabel("0")
        self.avg_response_time_label = QLabel("0 ms")
        self.memory_usage_label = QLabel("0 MB")
        self.gpu_usage_label = QLabel("0%")
        
        metrics_layout.addRow("Active Agents:", self.active_agents_label)
        metrics_layout.addRow("Total Tasks:", self.total_tasks_label)
        metrics_layout.addRow("Avg Response Time:", self.avg_response_time_label)
        metrics_layout.addRow("Memory Usage:", self.memory_usage_label)
        metrics_layout.addRow("GPU Usage:", self.gpu_usage_label)
        
        metrics_group.setLayout(metrics_layout)
        
        # Performance charts
        charts_group = QGroupBox("Performance Charts")
        charts_layout = QVBoxLayout()
        
        if CHARTS_AVAILABLE:
            # Create chart
            self.performance_chart = QChart()
            self.performance_chart.setTitle("Agent Performance Over Time")
            
            # Add series
            self.response_series = QLineSeries()
            self.response_series.setName("Response Time")
            
            # Configure axes
            axis_x = QValueAxis()
            axis_x.setRange(0, 60)
            axis_x.setLabelFormat("%d")
            axis_x.setTitleText("Time (seconds)")
            
            axis_y = QValueAxis()
            axis_y.setRange(0, 1000)
            axis_y.setLabelFormat("%d")
            axis_y.setTitleText("Response Time (ms)")
            
            self.performance_chart.addSeries(self.response_series)
            self.performance_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
            self.performance_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
            self.response_series.attachAxis(axis_x)
            self.response_series.attachAxis(axis_y)
            
            chart_view = QChartView(self.performance_chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            charts_layout.addWidget(chart_view)
        else:
            # Fallback when charts are not available
            self.response_series = None
            placeholder = QLabel("Charts not available. Install PyQt6-Charts for visualization.")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            charts_layout.addWidget(placeholder)
        
        charts_group.setLayout(charts_layout)
        
        # Agent performance table
        perf_table_group = QGroupBox("Agent Performance")
        perf_table_layout = QVBoxLayout()
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(5)
        self.performance_table.setHorizontalHeaderLabels([
            "Agent", "Tasks Completed", "Success Rate", "Avg Time", "Status"
        ])
        
        perf_table_layout.addWidget(self.performance_table)
        perf_table_group.setLayout(perf_table_layout)
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(metrics_group)
        left_layout.addWidget(perf_table_group)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(charts_group)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        
        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_monitoring)
        self.update_timer.start(1000)  # Update every second
        
        return widget
    
    def _create_multi_agent_chat_tab(self) -> QWidget:
        """Create the multi-agent chat tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Agent selection
        agent_select_layout = QHBoxLayout()
        
        self.chat_agents_list = QListWidget()
        self.chat_agents_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.chat_agents_list.setMaximumHeight(100)
        
        agent_select_layout.addWidget(QLabel("Select Agents:"))
        agent_select_layout.addWidget(self.chat_agents_list)
        
        # Conversation mode
        mode_layout = QHBoxLayout()
        
        self.sequential_radio = QRadioButton("Sequential")
        self.parallel_radio = QRadioButton("Parallel")
        self.debate_radio = QRadioButton("Debate")
        self.collaborative_radio = QRadioButton("Collaborative")
        self.collaborative_radio.setChecked(True)
        
        mode_layout.addWidget(QLabel("Mode:"))
        mode_layout.addWidget(self.sequential_radio)
        mode_layout.addWidget(self.parallel_radio)
        mode_layout.addWidget(self.debate_radio)
        mode_layout.addWidget(self.collaborative_radio)
        mode_layout.addStretch()
        
        # Chat display
        self.multi_chat_display = QTextEdit()
        self.multi_chat_display.setReadOnly(True)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.multi_chat_input = QTextEdit()
        self.multi_chat_input.setMaximumHeight(100)
        self.multi_chat_input.setPlaceholderText("Enter your message for the agents...")
        
        self.send_multi_btn = QPushButton("Send to Agents")
        self.send_multi_btn.clicked.connect(self._send_multi_agent_message)
        
        input_layout.addWidget(self.multi_chat_input, 1)
        input_layout.addWidget(self.send_multi_btn)
        
        # Chat controls
        chat_controls = QHBoxLayout()
        
        self.save_conversation_btn = QPushButton("Save Conversation")
        self.clear_conversation_btn = QPushButton("Clear")
        
        chat_controls.addWidget(self.save_conversation_btn)
        chat_controls.addWidget(self.clear_conversation_btn)
        chat_controls.addStretch()
        
        layout.addLayout(agent_select_layout)
        layout.addLayout(mode_layout)
        layout.addWidget(self.multi_chat_display)
        layout.addLayout(input_layout)
        layout.addLayout(chat_controls)
        
        return widget
    
    def _init_sample_data(self):
        """Initialize with sample data."""
        # Sample agents
        sample_agents = [
            "Code Assistant",
            "Data Analyst",
            "Research Bot",
            "Creative Writer"
        ]
        
        for agent in sample_agents:
            self.chat_agents_list.addItem(agent)
            
            # Add to agents table
            row = self.agents_table.rowCount()
            self.agents_table.insertRow(row)
            self.agents_table.setItem(row, 0, QTableWidgetItem(agent))
            self.agents_table.setItem(row, 1, QTableWidgetItem("General"))
            self.agents_table.setItem(row, 2, QTableWidgetItem("gpt-4"))
            self.agents_table.setItem(row, 3, QTableWidgetItem("Ready"))
            self.agents_table.setItem(row, 4, QTableWidgetItem("0"))
    
    def _create_agent(self):
        """Create a new agent."""
        dialog = AgentCreationDialog(self)
        if dialog.exec():
            config = dialog.get_agent_config()
            self.agent_created.emit(config)
            
            # Add to UI
            row = self.agents_table.rowCount()
            self.agents_table.insertRow(row)
            self.agents_table.setItem(row, 0, QTableWidgetItem(config["name"]))
            self.agents_table.setItem(row, 1, QTableWidgetItem(config["type"]))
            self.agents_table.setItem(row, 2, QTableWidgetItem(config["model"]["base"]))
            self.agents_table.setItem(row, 3, QTableWidgetItem("Ready"))
            self.agents_table.setItem(row, 4, QTableWidgetItem("0"))
            
            self.chat_agents_list.addItem(config["name"])
            
            self.update_status(f"Created agent: {config['name']}")
    
    def _run_workflow(self):
        """Run the selected workflow."""
        workflow_name = self.workflow_combo.currentText()
        self.workflow_started.emit(workflow_name)
        
        self.execution_log.append(f"Starting workflow: {workflow_name}")
        self.execution_log.append("Step 1: Initializing agents...")
        self.execution_log.append("Step 2: Processing input...")
        self.execution_log.append("Step 3: Executing agent tasks...")
        
        self.update_status(f"Running workflow: {workflow_name}")
    
    def _browse_dataset(self):
        """Browse for training dataset."""
        path = QFileDialog.getExistingDirectory(self, "Select Dataset Directory")
        if path:
            self.dataset_path.setText(path)
    
    def _start_training(self):
        """Start model training."""
        if self.training_thread and self.training_thread.isRunning():
            QMessageBox.warning(self, "Training Active", "Training is already in progress.")
            return
        
        params = {
            "model_type": self.model_type_combo.currentText(),
            "dataset": self.dataset_path.text(),
            "epochs": self.epochs_spin.value(),
            "batch_size": self.batch_size_spin.value(),
            "learning_rate": self.learning_rate_spin.value(),
            "device": self.device_combo.currentText()
        }
        
        self.training_thread = QThread()
        self.training_worker = TrainingWorker("train_model", params)
        self.training_worker.moveToThread(self.training_thread)
        
        # Connect signals
        self.training_thread.started.connect(self.training_worker.run)
        self.training_worker.finished.connect(self._on_training_finished)
        self.training_worker.error.connect(self._on_training_error)
        self.training_worker.progress.connect(self._on_training_progress)
        self.training_worker.metrics_update.connect(self._on_metrics_update)
        
        # Cleanup
        self.training_worker.finished.connect(self.training_thread.quit)
        self.training_worker.finished.connect(self.training_worker.deleteLater)
        self.training_thread.finished.connect(self.training_thread.deleteLater)
        
        self.training_thread.start()
        
        self.start_training_btn.setEnabled(False)
        self.stop_training_btn.setEnabled(True)
    
    def _on_training_progress(self, progress: int, message: str):
        """Handle training progress update."""
        self.training_progress.setValue(progress)
        self.training_status_label.setText(message)
    
    def _on_metrics_update(self, metrics: Dict[str, Any]):
        """Handle training metrics update."""
        row = metrics["epoch"] - 1
        if row >= self.metrics_table.rowCount():
            self.metrics_table.insertRow(row)
        
        self.metrics_table.setItem(row, 0, QTableWidgetItem(str(metrics["epoch"])))
        self.metrics_table.setItem(row, 1, QTableWidgetItem(f"{metrics['loss']:.4f}"))
        self.metrics_table.setItem(row, 2, QTableWidgetItem(f"{metrics['accuracy']:.4f}"))
        self.metrics_table.setItem(row, 3, QTableWidgetItem(f"{metrics['val_loss']:.4f}"))
        self.metrics_table.setItem(row, 4, QTableWidgetItem(f"{metrics['val_accuracy']:.4f}"))
    
    def _on_training_finished(self, result: Dict[str, Any]):
        """Handle training completion."""
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        
        if result["status"] == "completed":
            QMessageBox.information(
                self,
                "Training Complete",
                f"Model training completed successfully!\\nModel saved to: {result.get('model_path', 'N/A')}"
            )
        
        self.update_status("Training completed")
    
    def _on_training_error(self, error: str):
        """Handle training error."""
        self.start_training_btn.setEnabled(True)
        self.stop_training_btn.setEnabled(False)
        
        QMessageBox.critical(self, "Training Error", f"Training failed: {error}")
        self.update_status("Training failed")
    
    def _update_monitoring(self):
        """Update monitoring metrics."""
        # Simulate metrics update
        import random
        
        self.active_agents_label.setText(str(random.randint(3, 8)))
        self.total_tasks_label.setText(str(random.randint(50, 200)))
        self.avg_response_time_label.setText(f"{random.randint(100, 500)} ms")
        self.memory_usage_label.setText(f"{random.randint(1000, 4000)} MB")
        self.gpu_usage_label.setText(f"{random.randint(20, 80)}%")
        
        # Update chart if available
        if CHARTS_AVAILABLE and self.response_series:
            if self.response_series.count() > 60:
                self.response_series.remove(0)
            
            self.response_series.append(
                self.response_series.count(),
                random.randint(100, 500)
            )
    
    def _send_multi_agent_message(self):
        """Send message to multiple agents."""
        message = self.multi_chat_input.toPlainText().strip()
        if not message:
            return
        
        selected_agents = [
            item.text() for item in self.chat_agents_list.selectedItems()
        ]
        
        if not selected_agents:
            QMessageBox.warning(self, "No Agents", "Please select at least one agent.")
            return
        
        # Add user message
        self.multi_chat_display.append(f"<b>User:</b> {message}")
        self.multi_chat_input.clear()
        
        # Simulate agent responses
        mode = "Sequential"
        if self.parallel_radio.isChecked():
            mode = "Parallel"
        elif self.debate_radio.isChecked():
            mode = "Debate"
        elif self.collaborative_radio.isChecked():
            mode = "Collaborative"
        
        self.multi_chat_display.append(f"\\n<i>Mode: {mode}</i>\\n")
        
        # Simulate responses
        for agent in selected_agents:
            self.multi_chat_display.append(
                f"<b>{agent}:</b> This is a simulated response from {agent} "
                f"regarding: {message[:50]}..."
            )
    
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {message}")
        self.status_updated.emit(message)
    
    def cleanup(self):
        """Clean up resources."""
        if self.training_thread and self.training_thread.isRunning():
            self.training_worker.cancel()
            self.training_thread.quit()
            self.training_thread.wait()
        
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()