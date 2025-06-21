"""
LLM Custom Builder View Component
================================

Comprehensive UI for creating and training custom language models with wizard interface.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QStackedWidget, QRadioButton,
    QButtonGroup, QDoubleSpinBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap


class LLMBuilderWorker(QObject):
    """Worker thread for LLM building operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, str)  # percent, message
    log_message = pyqtSignal(str)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the LLM builder operation."""
        try:
            if self.operation == "prepare_dataset":
                self._prepare_dataset()
            elif self.operation == "train_model":
                self._train_model()
            elif self.operation == "evaluate_model":
                self._evaluate_model()
            elif self.operation == "export_model":
                self._export_model()
            else:
                self.finished.emit({"status": "completed"})
            
        except Exception as e:
            self.error.emit(str(e))
    
    def _prepare_dataset(self):
        """Simulate dataset preparation."""
        steps = [
            (10, "Loading data files..."),
            (25, "Parsing and cleaning data..."),
            (40, "Tokenizing text..."),
            (60, "Creating train/validation splits..."),
            (80, "Generating dataset statistics..."),
            (100, "Dataset preparation complete!")
        ]
        
        for progress, message in steps:
            self.progress.emit(progress, message)
            self.log_message.emit(f"[INFO] {message}")
            QThread.msleep(500)  # Simulate work
        
        result = {
            "status": "success",
            "total_samples": 10000,
            "train_samples": 8000,
            "val_samples": 2000,
            "vocab_size": 50000
        }
        self.finished.emit(result)
    
    def _train_model(self):
        """Simulate model training."""
        epochs = self.params.get("epochs", 10)
        
        for epoch in range(1, epochs + 1):
            progress = int((epoch / epochs) * 100)
            self.progress.emit(progress, f"Training epoch {epoch}/{epochs}")
            self.log_message.emit(f"[TRAIN] Epoch {epoch}: loss=0.{100-progress:02d}, accuracy={90+progress/10:.1f}%")
            QThread.msleep(1000)  # Simulate training time
        
        result = {
            "status": "success",
            "final_loss": 0.05,
            "final_accuracy": 0.95,
            "model_size": "124MB"
        }
        self.finished.emit(result)
    
    def _evaluate_model(self):
        """Simulate model evaluation."""
        self.progress.emit(50, "Running evaluation on test set...")
        QThread.msleep(2000)
        
        result = {
            "status": "success",
            "perplexity": 12.5,
            "bleu_score": 0.87,
            "rouge_score": 0.91
        }
        self.finished.emit(result)
    
    def _export_model(self):
        """Simulate model export."""
        self.progress.emit(50, "Exporting model...")
        QThread.msleep(1500)
        
        result = {
            "status": "success",
            "export_path": self.params.get("path", "/models/custom_model.bin")
        }
        self.finished.emit(result)


class LLMBuilderView(QWidget):
    """Main view for the LLM Custom Builder component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    model_created = pyqtSignal(dict)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.worker_thread = None
        self.worker = None
        self.current_step = 0
        self.model_config = {}
        
        self.setWindowTitle("LLM Custom Builder & Trainer")
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Model Wizard Tab
        self.wizard_tab = self._create_wizard_tab()
        self.tab_widget.addTab(self.wizard_tab, "🧙 Model Wizard")
        
        # Dataset Management Tab
        self.dataset_tab = self._create_dataset_tab()
        self.tab_widget.addTab(self.dataset_tab, "📊 Datasets")
        
        # Training Configuration Tab
        self.training_tab = self._create_training_tab()
        self.tab_widget.addTab(self.training_tab, "⚡ Training")
        
        # Model Library Tab
        self.library_tab = self._create_library_tab()
        self.tab_widget.addTab(self.library_tab, "📚 Model Library")
        
        # Fine-tuning Tab
        self.finetune_tab = self._create_finetune_tab()
        self.tab_widget.addTab(self.finetune_tab, "🎯 Fine-tuning")
        
        # Evaluation & Testing Tab
        self.evaluation_tab = self._create_evaluation_tab()
        self.tab_widget.addTab(self.evaluation_tab, "🔍 Evaluation")
        
        # Deployment Tab
        self.deployment_tab = self._create_deployment_tab()
        self.tab_widget.addTab(self.deployment_tab, "🚀 Deployment")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("LLM Builder: Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_wizard_tab(self) -> QWidget:
        """Create the model creation wizard tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Wizard header
        header_layout = QHBoxLayout()
        self.wizard_title = QLabel("Create Custom Language Model")
        self.wizard_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(self.wizard_title)
        header_layout.addStretch()
        
        # Step indicator
        self.step_indicator = QLabel("Step 1 of 5")
        self.step_indicator.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(self.step_indicator)
        
        # Wizard pages
        self.wizard_stack = QStackedWidget()
        
        # Step 1: Model Type
        self.wizard_stack.addWidget(self._create_wizard_step1())
        
        # Step 2: Architecture
        self.wizard_stack.addWidget(self._create_wizard_step2())
        
        # Step 3: Dataset
        self.wizard_stack.addWidget(self._create_wizard_step3())
        
        # Step 4: Training
        self.wizard_stack.addWidget(self._create_wizard_step4())
        
        # Step 5: Review
        self.wizard_stack.addWidget(self._create_wizard_step5())
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._wizard_previous)
        self.prev_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._wizard_next)
        
        self.finish_btn = QPushButton("✓ Finish")
        self.finish_btn.clicked.connect(self._wizard_finish)
        self.finish_btn.setVisible(False)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        nav_layout.addWidget(self.finish_btn)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.wizard_stack)
        layout.addLayout(nav_layout)
        
        return widget
    
    def _create_wizard_step1(self) -> QWidget:
        """Create wizard step 1: Model Type."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Select Model Type")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Model type options
        self.model_type_group = QButtonGroup()
        
        types = [
            ("Text Generation", "Generate creative text, stories, and articles", "gpt"),
            ("Code Generation", "Generate and complete code in multiple languages", "codegen"),
            ("Question Answering", "Answer questions based on context", "qa"),
            ("Translation", "Translate between multiple languages", "translation"),
            ("Summarization", "Create concise summaries of long texts", "summarization"),
            ("Custom Task", "Define your own specific task", "custom")
        ]
        
        for i, (name, desc, value) in enumerate(types):
            radio = QRadioButton(name)
            radio.setProperty("model_type", value)
            if i == 0:
                radio.setChecked(True)
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #666; margin-left: 25px; margin-bottom: 10px;")
            
            self.model_type_group.addButton(radio, i)
            layout.addWidget(radio)
            layout.addWidget(desc_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_wizard_step2(self) -> QWidget:
        """Create wizard step 2: Architecture."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Configure Model Architecture")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Architecture settings
        form_layout = QFormLayout()
        
        self.base_model_combo = QComboBox()
        self.base_model_combo.addItems([
            "GPT-2 Small (124M)",
            "GPT-2 Medium (355M)",
            "GPT-2 Large (774M)",
            "BERT Base (110M)",
            "T5 Small (60M)",
            "Custom Architecture"
        ])
        
        self.model_size_spin = QSpinBox()
        self.model_size_spin.setRange(1, 10000)
        self.model_size_spin.setValue(124)
        self.model_size_spin.setSuffix(" M parameters")
        
        self.layers_spin = QSpinBox()
        self.layers_spin.setRange(1, 48)
        self.layers_spin.setValue(12)
        
        self.hidden_size_spin = QSpinBox()
        self.hidden_size_spin.setRange(64, 4096)
        self.hidden_size_spin.setValue(768)
        self.hidden_size_spin.setSingleStep(64)
        
        self.attention_heads_spin = QSpinBox()
        self.attention_heads_spin.setRange(1, 64)
        self.attention_heads_spin.setValue(12)
        
        form_layout.addRow("Base Model:", self.base_model_combo)
        form_layout.addRow("Model Size:", self.model_size_spin)
        form_layout.addRow("Number of Layers:", self.layers_spin)
        form_layout.addRow("Hidden Size:", self.hidden_size_spin)
        form_layout.addRow("Attention Heads:", self.attention_heads_spin)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout()
        
        self.dropout_spin = QDoubleSpinBox()
        self.dropout_spin.setRange(0.0, 0.5)
        self.dropout_spin.setValue(0.1)
        self.dropout_spin.setSingleStep(0.05)
        
        self.vocab_size_spin = QSpinBox()
        self.vocab_size_spin.setRange(1000, 100000)
        self.vocab_size_spin.setValue(50000)
        self.vocab_size_spin.setSingleStep(1000)
        
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(64, 4096)
        self.max_length_spin.setValue(512)
        self.max_length_spin.setSingleStep(64)
        
        advanced_layout.addRow("Dropout Rate:", self.dropout_spin)
        advanced_layout.addRow("Vocabulary Size:", self.vocab_size_spin)
        advanced_layout.addRow("Max Sequence Length:", self.max_length_spin)
        
        advanced_group.setLayout(advanced_layout)
        
        layout.addLayout(form_layout)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        return widget
    
    def _create_wizard_step3(self) -> QWidget:
        """Create wizard step 3: Dataset."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Select Training Dataset")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Dataset source
        source_group = QGroupBox("Dataset Source")
        source_layout = QVBoxLayout()
        
        self.dataset_source_group = QButtonGroup()
        
        # Predefined datasets
        predefined_radio = QRadioButton("Use Predefined Dataset")
        predefined_radio.setChecked(True)
        self.dataset_source_group.addButton(predefined_radio, 0)
        
        self.predefined_dataset_combo = QComboBox()
        self.predefined_dataset_combo.addItems([
            "Wikipedia (English)",
            "Common Crawl",
            "BookCorpus",
            "OpenWebText",
            "Stack Overflow (Code)",
            "arXiv Papers"
        ])
        
        # Custom dataset
        custom_radio = QRadioButton("Upload Custom Dataset")
        self.dataset_source_group.addButton(custom_radio, 1)
        
        self.dataset_path_input = QLineEdit()
        self.dataset_path_input.setPlaceholderText("Path to dataset...")
        self.dataset_path_input.setEnabled(False)
        
        self.browse_dataset_btn = QPushButton("Browse...")
        self.browse_dataset_btn.setEnabled(False)
        self.browse_dataset_btn.clicked.connect(self._browse_dataset)
        
        # Connect radio buttons
        predefined_radio.toggled.connect(
            lambda checked: self.predefined_dataset_combo.setEnabled(checked)
        )
        custom_radio.toggled.connect(
            lambda checked: (
                self.dataset_path_input.setEnabled(checked),
                self.browse_dataset_btn.setEnabled(checked)
            )
        )
        
        source_layout.addWidget(predefined_radio)
        source_layout.addWidget(self.predefined_dataset_combo)
        source_layout.addSpacing(10)
        source_layout.addWidget(custom_radio)
        
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.dataset_path_input)
        custom_layout.addWidget(self.browse_dataset_btn)
        source_layout.addLayout(custom_layout)
        
        source_group.setLayout(source_layout)
        
        # Dataset preprocessing
        preprocess_group = QGroupBox("Preprocessing Options")
        preprocess_layout = QFormLayout()
        
        self.clean_text_checkbox = QCheckBox("Clean and normalize text")
        self.clean_text_checkbox.setChecked(True)
        
        self.remove_duplicates_checkbox = QCheckBox("Remove duplicates")
        self.remove_duplicates_checkbox.setChecked(True)
        
        self.filter_length_checkbox = QCheckBox("Filter by length")
        self.filter_length_checkbox.setChecked(True)
        
        self.min_length_spin = QSpinBox()
        self.min_length_spin.setRange(1, 1000)
        self.min_length_spin.setValue(10)
        
        self.max_length_spin = QSpinBox()
        self.max_length_spin.setRange(10, 10000)
        self.max_length_spin.setValue(1000)
        
        preprocess_layout.addRow(self.clean_text_checkbox)
        preprocess_layout.addRow(self.remove_duplicates_checkbox)
        preprocess_layout.addRow(self.filter_length_checkbox)
        preprocess_layout.addRow("Min Length:", self.min_length_spin)
        preprocess_layout.addRow("Max Length:", self.max_length_spin)
        
        preprocess_group.setLayout(preprocess_layout)
        
        layout.addWidget(source_group)
        layout.addWidget(preprocess_group)
        layout.addStretch()
        
        return widget
    
    def _create_wizard_step4(self) -> QWidget:
        """Create wizard step 4: Training Configuration."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Configure Training Parameters")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Basic training settings
        basic_group = QGroupBox("Basic Settings")
        basic_layout = QFormLayout()
        
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 100)
        self.epochs_spin.setValue(10)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 256)
        self.batch_size_spin.setValue(32)
        
        self.learning_rate_spin = QDoubleSpinBox()
        self.learning_rate_spin.setRange(0.00001, 0.1)
        self.learning_rate_spin.setValue(0.0001)
        self.learning_rate_spin.setDecimals(5)
        self.learning_rate_spin.setSingleStep(0.00001)
        
        self.warmup_steps_spin = QSpinBox()
        self.warmup_steps_spin.setRange(0, 10000)
        self.warmup_steps_spin.setValue(500)
        
        basic_layout.addRow("Epochs:", self.epochs_spin)
        basic_layout.addRow("Batch Size:", self.batch_size_spin)
        basic_layout.addRow("Learning Rate:", self.learning_rate_spin)
        basic_layout.addRow("Warmup Steps:", self.warmup_steps_spin)
        
        basic_group.setLayout(basic_layout)
        
        # Optimization settings
        opt_group = QGroupBox("Optimization")
        opt_layout = QFormLayout()
        
        self.optimizer_combo = QComboBox()
        self.optimizer_combo.addItems([
            "AdamW", "Adam", "SGD", "RMSprop", "Adagrad"
        ])
        
        self.scheduler_combo = QComboBox()
        self.scheduler_combo.addItems([
            "Linear", "Cosine", "Polynomial", "Constant", "None"
        ])
        
        self.gradient_clip_spin = QDoubleSpinBox()
        self.gradient_clip_spin.setRange(0.0, 10.0)
        self.gradient_clip_spin.setValue(1.0)
        self.gradient_clip_spin.setSingleStep(0.1)
        
        self.weight_decay_spin = QDoubleSpinBox()
        self.weight_decay_spin.setRange(0.0, 0.1)
        self.weight_decay_spin.setValue(0.01)
        self.weight_decay_spin.setSingleStep(0.001)
        
        opt_layout.addRow("Optimizer:", self.optimizer_combo)
        opt_layout.addRow("LR Scheduler:", self.scheduler_combo)
        opt_layout.addRow("Gradient Clipping:", self.gradient_clip_spin)
        opt_layout.addRow("Weight Decay:", self.weight_decay_spin)
        
        opt_group.setLayout(opt_layout)
        
        # Hardware settings
        hardware_group = QGroupBox("Hardware Configuration")
        hardware_layout = QFormLayout()
        
        self.device_combo = QComboBox()
        self.device_combo.addItems([
            "Auto (Best Available)",
            "GPU (CUDA)",
            "CPU",
            "TPU (if available)"
        ])
        
        self.mixed_precision_checkbox = QCheckBox("Use Mixed Precision (FP16)")
        self.gradient_accumulation_spin = QSpinBox()
        self.gradient_accumulation_spin.setRange(1, 64)
        self.gradient_accumulation_spin.setValue(1)
        
        hardware_layout.addRow("Device:", self.device_combo)
        hardware_layout.addRow(self.mixed_precision_checkbox)
        hardware_layout.addRow("Gradient Accumulation:", self.gradient_accumulation_spin)
        
        hardware_group.setLayout(hardware_layout)
        
        layout.addWidget(basic_group)
        layout.addWidget(opt_group)
        layout.addWidget(hardware_group)
        layout.addStretch()
        
        return widget
    
    def _create_wizard_step5(self) -> QWidget:
        """Create wizard step 5: Review and Confirm."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("Review Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Configuration summary
        self.config_summary = QTextEdit()
        self.config_summary.setReadOnly(True)
        self.config_summary.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        
        # Model name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Model Name:"))
        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("my-custom-model")
        name_layout.addWidget(self.model_name_input)
        
        # Start training button
        self.start_training_btn = QPushButton("🚀 Start Training")
        self.start_training_btn.clicked.connect(self._start_training)
        self.start_training_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        layout.addWidget(self.config_summary)
        layout.addLayout(name_layout)
        layout.addWidget(self.start_training_btn)
        
        return widget
    
    def _create_dataset_tab(self) -> QWidget:
        """Create the dataset management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Dataset controls
        controls_layout = QHBoxLayout()
        self.add_dataset_btn = QPushButton("➕ Add Dataset")
        self.import_dataset_btn = QPushButton("📥 Import")
        self.create_dataset_btn = QPushButton("🔨 Create New")
        
        controls_layout.addWidget(self.add_dataset_btn)
        controls_layout.addWidget(self.import_dataset_btn)
        controls_layout.addWidget(self.create_dataset_btn)
        controls_layout.addStretch()
        
        # Dataset list
        self.datasets_table = QTableWidget()
        self.datasets_table.setColumnCount(6)
        self.datasets_table.setHorizontalHeaderLabels([
            "Name", "Type", "Size", "Samples", "Format", "Status"
        ])
        
        # Add sample datasets
        datasets = [
            ("Wikipedia EN", "Text", "45 GB", "6M", "JSON", "Ready"),
            ("Code Dataset", "Code", "12 GB", "2M", "Python", "Ready"),
            ("QA Pairs", "Q&A", "3 GB", "500K", "CSV", "Processing"),
            ("Custom Docs", "Text", "1.2 GB", "100K", "TXT", "Ready")
        ]
        
        self.datasets_table.setRowCount(len(datasets))
        for i, dataset in enumerate(datasets):
            for j, value in enumerate(dataset):
                self.datasets_table.setItem(i, j, QTableWidgetItem(value))
        
        # Dataset details
        details_group = QGroupBox("Dataset Details")
        details_layout = QFormLayout()
        
        self.dataset_stats_text = QTextEdit()
        self.dataset_stats_text.setReadOnly(True)
        self.dataset_stats_text.setMaximumHeight(150)
        self.dataset_stats_text.setPlainText(
            "Select a dataset to view details...\n\n"
            "Statistics:\n"
            "- Total tokens: -\n"
            "- Unique tokens: -\n"
            "- Average length: -\n"
            "- Language: -"
        )
        
        details_layout.addRow("Statistics:", self.dataset_stats_text)
        details_group.setLayout(details_layout)
        
        # Dataset actions
        actions_layout = QHBoxLayout()
        self.prepare_dataset_btn = QPushButton("⚙️ Prepare Dataset")
        self.prepare_dataset_btn.clicked.connect(self._prepare_dataset)
        self.analyze_dataset_btn = QPushButton("📊 Analyze")
        self.export_dataset_btn = QPushButton("📤 Export")
        
        actions_layout.addWidget(self.prepare_dataset_btn)
        actions_layout.addWidget(self.analyze_dataset_btn)
        actions_layout.addWidget(self.export_dataset_btn)
        actions_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.datasets_table)
        layout.addWidget(details_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_training_tab(self) -> QWidget:
        """Create the training configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Training status
        status_group = QGroupBox("Training Status")
        status_layout = QVBoxLayout()
        
        # Progress bar
        self.training_progress = QProgressBar()
        self.training_progress.setRange(0, 100)
        
        # Status info
        info_layout = QFormLayout()
        self.current_epoch_label = QLabel("0/0")
        self.current_loss_label = QLabel("0.000")
        self.learning_rate_label = QLabel("0.0001")
        self.time_remaining_label = QLabel("--:--:--")
        
        info_layout.addRow("Epoch:", self.current_epoch_label)
        info_layout.addRow("Loss:", self.current_loss_label)
        info_layout.addRow("Learning Rate:", self.learning_rate_label)
        info_layout.addRow("Time Remaining:", self.time_remaining_label)
        
        status_layout.addWidget(self.training_progress)
        status_layout.addLayout(info_layout)
        status_group.setLayout(status_layout)
        
        # Training log
        log_group = QGroupBox("Training Log")
        log_layout = QVBoxLayout()
        
        self.training_log = QTextEdit()
        self.training_log.setReadOnly(True)
        self.training_log.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        log_layout.addWidget(self.training_log)
        log_group.setLayout(log_layout)
        
        # Training controls
        controls_layout = QHBoxLayout()
        self.pause_training_btn = QPushButton("⏸️ Pause")
        self.resume_training_btn = QPushButton("▶️ Resume")
        self.stop_training_btn = QPushButton("⏹️ Stop")
        self.save_checkpoint_btn = QPushButton("💾 Save Checkpoint")
        
        controls_layout.addWidget(self.pause_training_btn)
        controls_layout.addWidget(self.resume_training_btn)
        controls_layout.addWidget(self.stop_training_btn)
        controls_layout.addWidget(self.save_checkpoint_btn)
        controls_layout.addStretch()
        
        # Metrics visualization placeholder
        metrics_group = QGroupBox("Training Metrics")
        metrics_layout = QVBoxLayout()
        metrics_placeholder = QLabel("Training metrics visualization will appear here")
        metrics_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        metrics_placeholder.setStyleSheet("color: #666; padding: 50px;")
        metrics_layout.addWidget(metrics_placeholder)
        metrics_group.setLayout(metrics_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(status_group)
        splitter.addWidget(log_group)
        splitter.addWidget(metrics_group)
        splitter.setSizes([150, 300, 200])
        
        layout.addWidget(splitter)
        layout.addLayout(controls_layout)
        
        return widget
    
    def _create_library_tab(self) -> QWidget:
        """Create the model library tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model filters
        filter_layout = QHBoxLayout()
        self.model_search_input = QLineEdit()
        self.model_search_input.setPlaceholderText("Search models...")
        
        self.model_type_filter = QComboBox()
        self.model_type_filter.addItems([
            "All Types", "Text Generation", "Code", "Q&A", "Translation"
        ])
        
        filter_layout.addWidget(self.model_search_input)
        filter_layout.addWidget(self.model_type_filter)
        filter_layout.addStretch()
        
        # Model grid
        self.models_tree = QTreeWidget()
        self.models_tree.setHeaderLabels([
            "Model", "Type", "Size", "Performance", "Created", "Status"
        ])
        
        # Add sample models
        models = [
            ("custom-gpt-v1", "Text Gen", "124M", "PPL: 15.2", "2 days ago", "Ready"),
            ("code-assistant", "Code", "355M", "BLEU: 0.87", "1 week ago", "Ready"),
            ("qa-model-v2", "Q&A", "110M", "F1: 0.92", "3 days ago", "Training"),
            ("translator-en-es", "Translation", "220M", "BLEU: 0.91", "5 days ago", "Ready")
        ]
        
        for model in models:
            item = QTreeWidgetItem(self.models_tree)
            for i, value in enumerate(model):
                item.setText(i, value)
        
        # Model actions
        actions_group = QGroupBox("Model Actions")
        actions_layout = QHBoxLayout()
        
        self.load_model_btn = QPushButton("📂 Load Model")
        self.test_model_btn = QPushButton("🧪 Test")
        self.export_model_btn = QPushButton("📤 Export")
        self.export_model_btn.clicked.connect(self._export_model)
        self.delete_model_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.load_model_btn)
        actions_layout.addWidget(self.test_model_btn)
        actions_layout.addWidget(self.export_model_btn)
        actions_layout.addWidget(self.delete_model_btn)
        
        actions_group.setLayout(actions_layout)
        
        # Model details
        details_group = QGroupBox("Model Details")
        details_layout = QFormLayout()
        
        self.model_info_text = QTextEdit()
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(200)
        
        details_layout.addRow(self.model_info_text)
        details_group.setLayout(details_layout)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.models_tree)
        layout.addWidget(actions_group)
        layout.addWidget(details_group)
        
        return widget
    
    def _create_finetune_tab(self) -> QWidget:
        """Create the fine-tuning tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Base model selection
        base_group = QGroupBox("Select Base Model")
        base_layout = QFormLayout()
        
        self.finetune_base_combo = QComboBox()
        self.finetune_base_combo.addItems([
            "custom-gpt-v1 (Local)",
            "gpt2-medium (HuggingFace)",
            "bert-base-uncased (HuggingFace)",
            "t5-small (HuggingFace)"
        ])
        
        self.finetune_task_combo = QComboBox()
        self.finetune_task_combo.addItems([
            "Domain Adaptation",
            "Task-Specific",
            "Style Transfer",
            "Language Adaptation"
        ])
        
        base_layout.addRow("Base Model:", self.finetune_base_combo)
        base_layout.addRow("Fine-tune Task:", self.finetune_task_combo)
        base_group.setLayout(base_layout)
        
        # Fine-tuning data
        data_group = QGroupBox("Fine-tuning Data")
        data_layout = QVBoxLayout()
        
        data_controls = QHBoxLayout()
        self.finetune_data_path = QLineEdit()
        self.finetune_data_path.setPlaceholderText("Path to fine-tuning data...")
        self.browse_finetune_btn = QPushButton("Browse...")
        
        data_controls.addWidget(self.finetune_data_path)
        data_controls.addWidget(self.browse_finetune_btn)
        
        # Data preview
        self.data_preview_text = QTextEdit()
        self.data_preview_text.setMaximumHeight(150)
        self.data_preview_text.setPlaceholderText("Data preview will appear here...")
        
        data_layout.addLayout(data_controls)
        data_layout.addWidget(self.data_preview_text)
        data_group.setLayout(data_layout)
        
        # Fine-tuning parameters
        params_group = QGroupBox("Fine-tuning Parameters")
        params_layout = QFormLayout()
        
        self.finetune_epochs_spin = QSpinBox()
        self.finetune_epochs_spin.setRange(1, 50)
        self.finetune_epochs_spin.setValue(5)
        
        self.finetune_lr_spin = QDoubleSpinBox()
        self.finetune_lr_spin.setRange(0.000001, 0.001)
        self.finetune_lr_spin.setValue(0.00005)
        self.finetune_lr_spin.setDecimals(6)
        
        self.freeze_layers_spin = QSpinBox()
        self.freeze_layers_spin.setRange(0, 24)
        self.freeze_layers_spin.setValue(0)
        
        params_layout.addRow("Epochs:", self.finetune_epochs_spin)
        params_layout.addRow("Learning Rate:", self.finetune_lr_spin)
        params_layout.addRow("Freeze Layers:", self.freeze_layers_spin)
        
        params_group.setLayout(params_layout)
        
        # Start fine-tuning
        self.start_finetune_btn = QPushButton("🎯 Start Fine-tuning")
        self.start_finetune_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        layout.addWidget(base_group)
        layout.addWidget(data_group)
        layout.addWidget(params_group)
        layout.addWidget(self.start_finetune_btn)
        layout.addStretch()
        
        return widget
    
    def _create_evaluation_tab(self) -> QWidget:
        """Create the evaluation and testing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model to Evaluate:"))
        self.eval_model_combo = QComboBox()
        self.eval_model_combo.addItems([
            "custom-gpt-v1", "code-assistant", "qa-model-v2"
        ])
        self.run_evaluation_btn = QPushButton("🔍 Run Evaluation")
        self.run_evaluation_btn.clicked.connect(self._run_evaluation)
        
        model_layout.addWidget(self.eval_model_combo)
        model_layout.addWidget(self.run_evaluation_btn)
        model_layout.addStretch()
        
        # Test input
        test_group = QGroupBox("Interactive Testing")
        test_layout = QVBoxLayout()
        
        self.test_input_text = QTextEdit()
        self.test_input_text.setMaximumHeight(100)
        self.test_input_text.setPlaceholderText("Enter test prompt here...")
        
        test_controls = QHBoxLayout()
        self.test_model_btn = QPushButton("🧪 Test Model")
        self.clear_test_btn = QPushButton("🗑️ Clear")
        
        test_controls.addWidget(self.test_model_btn)
        test_controls.addWidget(self.clear_test_btn)
        test_controls.addStretch()
        
        self.test_output_text = QTextEdit()
        self.test_output_text.setReadOnly(True)
        self.test_output_text.setPlaceholderText("Model output will appear here...")
        
        test_layout.addWidget(QLabel("Input:"))
        test_layout.addWidget(self.test_input_text)
        test_layout.addLayout(test_controls)
        test_layout.addWidget(QLabel("Output:"))
        test_layout.addWidget(self.test_output_text)
        
        test_group.setLayout(test_layout)
        
        # Evaluation metrics
        metrics_group = QGroupBox("Evaluation Metrics")
        metrics_layout = QFormLayout()
        
        self.perplexity_label = QLabel("-")
        self.bleu_score_label = QLabel("-")
        self.rouge_score_label = QLabel("-")
        self.accuracy_label = QLabel("-")
        self.f1_score_label = QLabel("-")
        
        metrics_layout.addRow("Perplexity:", self.perplexity_label)
        metrics_layout.addRow("BLEU Score:", self.bleu_score_label)
        metrics_layout.addRow("ROUGE Score:", self.rouge_score_label)
        metrics_layout.addRow("Accuracy:", self.accuracy_label)
        metrics_layout.addRow("F1 Score:", self.f1_score_label)
        
        metrics_group.setLayout(metrics_layout)
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(model_layout)
        left_layout.addWidget(test_group)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(metrics_group)
        splitter.setSizes([500, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_deployment_tab(self) -> QWidget:
        """Create the deployment tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Deployment options
        deploy_group = QGroupBox("Deployment Options")
        deploy_layout = QFormLayout()
        
        self.deploy_format_combo = QComboBox()
        self.deploy_format_combo.addItems([
            "ONNX", "TorchScript", "TensorFlow SavedModel", 
            "Hugging Face", "GGUF (llama.cpp)", "Custom Format"
        ])
        
        self.quantization_combo = QComboBox()
        self.quantization_combo.addItems([
            "None (FP32)", "FP16", "INT8", "INT4"
        ])
        
        self.optimize_checkbox = QCheckBox("Optimize for inference")
        self.optimize_checkbox.setChecked(True)
        
        deploy_layout.addRow("Export Format:", self.deploy_format_combo)
        deploy_layout.addRow("Quantization:", self.quantization_combo)
        deploy_layout.addRow(self.optimize_checkbox)
        
        deploy_group.setLayout(deploy_layout)
        
        # API deployment
        api_group = QGroupBox("API Deployment")
        api_layout = QFormLayout()
        
        self.api_endpoint_input = QLineEdit()
        self.api_endpoint_input.setPlaceholderText("http://localhost:8000/predict")
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("API key (optional)")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.max_requests_spin = QSpinBox()
        self.max_requests_spin.setRange(1, 1000)
        self.max_requests_spin.setValue(100)
        
        api_layout.addRow("Endpoint:", self.api_endpoint_input)
        api_layout.addRow("API Key:", self.api_key_input)
        api_layout.addRow("Max Requests/min:", self.max_requests_spin)
        
        api_group.setLayout(api_layout)
        
        # Deployment actions
        actions_layout = QHBoxLayout()
        self.deploy_local_btn = QPushButton("💻 Deploy Locally")
        self.deploy_cloud_btn = QPushButton("☁️ Deploy to Cloud")
        self.generate_api_btn = QPushButton("🔧 Generate API")
        self.export_btn = QPushButton("📦 Export Package")
        
        actions_layout.addWidget(self.deploy_local_btn)
        actions_layout.addWidget(self.deploy_cloud_btn)
        actions_layout.addWidget(self.generate_api_btn)
        actions_layout.addWidget(self.export_btn)
        
        # Deployment status
        status_group = QGroupBox("Deployment Status")
        status_layout = QVBoxLayout()
        
        self.deployment_log = QTextEdit()
        self.deployment_log.setReadOnly(True)
        self.deployment_log.setMaximumHeight(200)
        self.deployment_log.setPlaceholderText("Deployment logs will appear here...")
        
        status_layout.addWidget(self.deployment_log)
        status_group.setLayout(status_layout)
        
        layout.addWidget(deploy_group)
        layout.addWidget(api_group)
        layout.addLayout(actions_layout)
        layout.addWidget(status_group)
        layout.addStretch()
        
        return widget
    
    def _wizard_previous(self):
        """Go to previous wizard step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.wizard_stack.setCurrentIndex(self.current_step)
            self._update_wizard_navigation()
    
    def _wizard_next(self):
        """Go to next wizard step."""
        if self.current_step < 4:
            # Collect data from current step
            self._collect_wizard_data()
            
            self.current_step += 1
            self.wizard_stack.setCurrentIndex(self.current_step)
            self._update_wizard_navigation()
            
            # Update summary on last step
            if self.current_step == 4:
                self._update_config_summary()
    
    def _wizard_finish(self):
        """Finish the wizard and start training."""
        self._collect_wizard_data()
        self._update_config_summary()
        QMessageBox.information(
            self, "Wizard Complete",
            "Model configuration is ready! Click 'Start Training' to begin."
        )
    
    def _update_wizard_navigation(self):
        """Update wizard navigation buttons."""
        self.prev_btn.setEnabled(self.current_step > 0)
        self.next_btn.setVisible(self.current_step < 4)
        self.finish_btn.setVisible(self.current_step == 4)
        self.step_indicator.setText(f"Step {self.current_step + 1} of 5")
    
    def _collect_wizard_data(self):
        """Collect data from current wizard step."""
        if self.current_step == 0:
            # Model type
            selected = self.model_type_group.checkedButton()
            if selected:
                self.model_config["type"] = selected.property("model_type")
        elif self.current_step == 1:
            # Architecture
            self.model_config["base_model"] = self.base_model_combo.currentText()
            self.model_config["layers"] = self.layers_spin.value()
            self.model_config["hidden_size"] = self.hidden_size_spin.value()
            self.model_config["attention_heads"] = self.attention_heads_spin.value()
        elif self.current_step == 2:
            # Dataset
            if self.dataset_source_group.checkedButton() == self.dataset_source_group.buttons()[0]:
                self.model_config["dataset"] = self.predefined_dataset_combo.currentText()
            else:
                self.model_config["dataset"] = self.dataset_path_input.text()
        elif self.current_step == 3:
            # Training
            self.model_config["epochs"] = self.epochs_spin.value()
            self.model_config["batch_size"] = self.batch_size_spin.value()
            self.model_config["learning_rate"] = self.learning_rate_spin.value()
            self.model_config["optimizer"] = self.optimizer_combo.currentText()
    
    def _update_config_summary(self):
        """Update the configuration summary."""
        summary = f"""Model Configuration Summary
========================

Model Type: {self.model_config.get('type', 'N/A')}
Base Model: {self.model_config.get('base_model', 'N/A')}

Architecture:
- Layers: {self.model_config.get('layers', 'N/A')}
- Hidden Size: {self.model_config.get('hidden_size', 'N/A')}
- Attention Heads: {self.model_config.get('attention_heads', 'N/A')}

Dataset: {self.model_config.get('dataset', 'N/A')}

Training Configuration:
- Epochs: {self.model_config.get('epochs', 'N/A')}
- Batch Size: {self.model_config.get('batch_size', 'N/A')}
- Learning Rate: {self.model_config.get('learning_rate', 'N/A')}
- Optimizer: {self.model_config.get('optimizer', 'N/A')}
"""
        self.config_summary.setPlainText(summary)
    
    def _browse_dataset(self):
        """Browse for dataset file."""
        path = QFileDialog.getOpenFileName(
            self, "Select Dataset",
            "", "All Files (*);;JSON (*.json);;CSV (*.csv);;Text (*.txt)"
        )[0]
        if path:
            self.dataset_path_input.setText(path)
    
    def _start_training(self):
        """Start model training."""
        model_name = self.model_name_input.text().strip()
        if not model_name:
            QMessageBox.warning(self, "Input Required", "Please provide a model name.")
            return
        
        self.model_config["name"] = model_name
        
        # Switch to training tab
        self.tab_widget.setCurrentIndex(2)
        
        # Start training
        self._run_operation("train_model", self.model_config)
    
    def _prepare_dataset(self):
        """Prepare dataset for training."""
        self._run_operation("prepare_dataset", {"dataset": "selected"})
    
    def _run_evaluation(self):
        """Run model evaluation."""
        self._run_operation("evaluate_model", {
            "model": self.eval_model_combo.currentText()
        })
    
    def _export_model(self):
        """Export the selected model."""
        path = QFileDialog.getSaveFileName(
            self, "Export Model",
            "", "Model Files (*.bin *.onnx *.pt)"
        )[0]
        if path:
            self._run_operation("export_model", {"path": path})
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = LLMBuilderWorker(operation, params)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_operation_finished)
        self.worker.error.connect(self._on_operation_error)
        self.worker.progress.connect(self._on_progress_update)
        self.worker.log_message.connect(self._on_log_message)
        
        # Cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()
    
    def _on_operation_finished(self, result: Dict[str, Any]):
        """Handle operation completion."""
        if result.get("status") == "success":
            if "total_samples" in result:
                # Dataset preparation complete
                QMessageBox.information(
                    self, "Dataset Ready",
                    f"Dataset prepared successfully!\\n"
                    f"Total samples: {result['total_samples']}\\n"
                    f"Training samples: {result['train_samples']}\\n"
                    f"Validation samples: {result['val_samples']}"
                )
            elif "final_accuracy" in result:
                # Training complete
                QMessageBox.information(
                    self, "Training Complete",
                    f"Model training completed!\\n"
                    f"Final loss: {result['final_loss']}\\n"
                    f"Final accuracy: {result['final_accuracy']}\\n"
                    f"Model size: {result['model_size']}"
                )
            elif "perplexity" in result:
                # Evaluation complete
                self.perplexity_label.setText(str(result['perplexity']))
                self.bleu_score_label.setText(str(result['bleu_score']))
                self.rouge_score_label.setText(str(result['rouge_score']))
            elif "export_path" in result:
                # Export complete
                QMessageBox.information(
                    self, "Export Complete",
                    f"Model exported successfully to:\\n{result['export_path']}"
                )
        
        self.update_status("Ready")
    
    def _on_operation_error(self, error: str):
        """Handle operation error."""
        QMessageBox.critical(self, "Error", f"Operation failed: {error}")
        self.update_status("Error occurred")
    
    def _on_progress_update(self, percent: int, message: str):
        """Update progress bar and status."""
        self.training_progress.setValue(percent)
        self.update_status(message)
    
    def _on_log_message(self, message: str):
        """Add message to training log."""
        self.training_log.append(message)
    
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {message}")
        self.status_updated.emit(message)
    
    def cleanup(self):
        """Clean up resources."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()