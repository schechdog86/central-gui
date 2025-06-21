"""
Coding Agent View Component
==========================

Comprehensive UI for the AI-powered coding assistant with memory and skills.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QColor


class CodingAgentWorker(QObject):
    """Worker thread for coding agent operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the coding agent operation."""
        try:
            self.progress.emit(f"Starting {self.operation}...")
            
            # Simulate operations for now
            # In production, this would connect to the actual coding agent
            
            if self.operation == "process_query":
                result = {"response": f"Processing query: {self.params['query']}"}
            elif self.operation == "generate_code":
                result = {
                    "code": f"# Generated code for: {self.params['description']}\\n"
                           f"def example():\\n    pass"
                }
            elif self.operation == "load_project":
                result = {"success": True, "project": self.params['path']}
            else:
                result = {"status": "completed"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class CodingAgentView(QWidget):
    """Main view for the Coding Agent component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    query_submitted = pyqtSignal(str)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_project = None
        self.worker_thread = None
        self.worker = None
        
        self.setWindowTitle("Coding Agent")
        self._init_ui()
        self._init_agent()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Chat Interface Tab
        self.chat_tab = self._create_chat_tab()
        self.tab_widget.addTab(self.chat_tab, "💬 Chat")
        
        # Code Generation Tab
        self.code_gen_tab = self._create_code_generation_tab()
        self.tab_widget.addTab(self.code_gen_tab, "🔧 Code Generation")
        
        # Knowledge Base Tab
        self.knowledge_tab = self._create_knowledge_tab()
        self.tab_widget.addTab(self.knowledge_tab, "📚 Knowledge Base")
        
        # Memory Management Tab
        self.memory_tab = self._create_memory_tab()
        self.tab_widget.addTab(self.memory_tab, "🧠 Memory")
        
        # Skills & Stats Tab
        self.skills_tab = self._create_skills_tab()
        self.tab_widget.addTab(self.skills_tab, "⭐ Skills & Stats")
        
        # Project Management Tab
        self.project_tab = self._create_project_tab()
        self.tab_widget.addTab(self.project_tab, "📁 Projects")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_chat_tab(self) -> QWidget:
        """Create the main chat interface tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        
        # Input area
        input_layout = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Ask anything about coding...")
        self.query_input.returnPressed.connect(self._submit_query)
        
        self.submit_btn = QPushButton("Send")
        self.submit_btn.clicked.connect(self._submit_query)
        
        input_layout.addWidget(self.query_input)
        input_layout.addWidget(self.submit_btn)
        
        # Quick actions
        actions_layout = QHBoxLayout()
        self.explain_btn = QPushButton("Explain Selected")
        self.improve_btn = QPushButton("Suggest Improvements")
        self.refactor_btn = QPushButton("Refactor Code")
        
        actions_layout.addWidget(self.explain_btn)
        actions_layout.addWidget(self.improve_btn)
        actions_layout.addWidget(self.refactor_btn)
        
        layout.addWidget(QLabel("Chat with Coding Agent:"))
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_code_generation_tab(self) -> QWidget:
        """Create the code generation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Code generation form
        form_group = QGroupBox("Generate Code")
        form_layout = QFormLayout()
        
        self.gen_description = QTextEdit()
        self.gen_description.setMaximumHeight(100)
        self.gen_description.setPlaceholderText("Describe what you want to generate...")
        
        self.gen_language = QComboBox()
        self.gen_language.addItems([
            "Python", "JavaScript", "TypeScript", "Java", "C++",
            "C#", "Go", "Rust", "Ruby", "PHP", "Swift"
        ])
        
        self.gen_framework = QLineEdit()
        self.gen_framework.setPlaceholderText("e.g., React, Django, Flask...")
        
        self.gen_context = QTextEdit()
        self.gen_context.setMaximumHeight(100)
        self.gen_context.setPlaceholderText("Additional context or requirements...")
        
        form_layout.addRow("Description:", self.gen_description)
        form_layout.addRow("Language:", self.gen_language)
        form_layout.addRow("Framework:", self.gen_framework)
        form_layout.addRow("Context:", self.gen_context)
        
        form_group.setLayout(form_layout)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Code")
        self.generate_btn.clicked.connect(self._generate_code)
        
        # Output area
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        self.code_output.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        # Actions for generated code
        output_actions = QHBoxLayout()
        self.copy_code_btn = QPushButton("Copy Code")
        self.save_code_btn = QPushButton("Save to File")
        self.improve_code_btn = QPushButton("Improve Code")
        
        output_actions.addWidget(self.copy_code_btn)
        output_actions.addWidget(self.save_code_btn)
        output_actions.addWidget(self.improve_code_btn)
        output_actions.addStretch()
        
        layout.addWidget(form_group)
        layout.addWidget(self.generate_btn)
        layout.addWidget(QLabel("Generated Code:"))
        layout.addWidget(self.code_output)
        layout.addLayout(output_actions)
        
        return widget
    
    def _create_knowledge_tab(self) -> QWidget:
        """Create the knowledge base management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search area
        search_layout = QHBoxLayout()
        self.knowledge_search = QLineEdit()
        self.knowledge_search.setPlaceholderText("Search knowledge base...")
        self.search_knowledge_btn = QPushButton("Search")
        
        search_layout.addWidget(self.knowledge_search)
        search_layout.addWidget(self.search_knowledge_btn)
        
        # Category filter
        filter_layout = QHBoxLayout()
        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All", "Code Snippets", "Tutorials", "Best Practices",
            "Algorithms", "Design Patterns", "Libraries", "Frameworks"
        ])
        
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addStretch()
        
        # Knowledge list
        self.knowledge_list = QTreeWidget()
        self.knowledge_list.setHeaderLabels(["Title", "Category", "Tags", "Date"])
        
        # Add knowledge button
        add_layout = QHBoxLayout()
        self.add_knowledge_btn = QPushButton("Add Knowledge")
        self.import_knowledge_btn = QPushButton("Import from File")
        self.export_knowledge_btn = QPushButton("Export Selected")
        
        add_layout.addWidget(self.add_knowledge_btn)
        add_layout.addWidget(self.import_knowledge_btn)
        add_layout.addWidget(self.export_knowledge_btn)
        add_layout.addStretch()
        
        # Knowledge details
        self.knowledge_details = QTextEdit()
        self.knowledge_details.setReadOnly(True)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.knowledge_list)
        splitter.addWidget(self.knowledge_details)
        splitter.setSizes([300, 200])
        
        layout.addLayout(search_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(splitter)
        layout.addLayout(add_layout)
        
        return widget
    
    def _create_memory_tab(self) -> QWidget:
        """Create the memory management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Memory statistics
        stats_group = QGroupBox("Memory Statistics")
        stats_layout = QFormLayout()
        
        self.total_memories_label = QLabel("0")
        self.short_term_label = QLabel("0")
        self.long_term_label = QLabel("0")
        self.critical_label = QLabel("0")
        
        stats_layout.addRow("Total Memories:", self.total_memories_label)
        stats_layout.addRow("Short-term:", self.short_term_label)
        stats_layout.addRow("Long-term:", self.long_term_label)
        stats_layout.addRow("Critical:", self.critical_label)
        
        stats_group.setLayout(stats_layout)
        
        # Memory search
        search_layout = QHBoxLayout()
        self.memory_search = QLineEdit()
        self.memory_search.setPlaceholderText("Search memories...")
        self.search_memory_btn = QPushButton("Search")
        
        search_layout.addWidget(self.memory_search)
        search_layout.addWidget(self.search_memory_btn)
        
        # Memory list
        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(4)
        self.memory_table.setHorizontalHeaderLabels(["Content", "Type", "Timestamp", "Relevance"])
        header = self.memory_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        # Memory actions
        actions_layout = QHBoxLayout()
        self.backup_memory_btn = QPushButton("Backup Memory")
        self.restore_memory_btn = QPushButton("Restore from Backup")
        self.clear_memory_btn = QPushButton("Clear Old Memories")
        
        actions_layout.addWidget(self.backup_memory_btn)
        actions_layout.addWidget(self.restore_memory_btn)
        actions_layout.addWidget(self.clear_memory_btn)
        actions_layout.addStretch()
        
        layout.addWidget(stats_group)
        layout.addLayout(search_layout)
        layout.addWidget(self.memory_table)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _create_skills_tab(self) -> QWidget:
        """Create the skills and statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Skills list
        self.skills_tree = QTreeWidget()
        self.skills_tree.setHeaderLabels(["Skill", "Level", "XP", "Progress"])
        
        # Sample skills (would be loaded from agent)
        skills = [
            ("Python", "Expert", "2500/3000", 83),
            ("JavaScript", "Advanced", "1800/2000", 90),
            ("Code Review", "Intermediate", "800/1000", 80),
            ("Debugging", "Expert", "2800/3000", 93),
            ("Architecture", "Advanced", "1500/2000", 75)
        ]
        
        for skill, level, xp, progress in skills:
            item = QTreeWidgetItem([skill, level, xp, f"{progress}%"])
            self.skills_tree.addTopLevelItem(item)
        
        # Achievements
        achievements_group = QGroupBox("Achievements")
        achievements_layout = QVBoxLayout()
        
        self.achievements_list = QListWidget()
        sample_achievements = [
            "🏆 First Code Generated",
            "🌟 100 Successful Queries",
            "🚀 Advanced Python Developer",
            "🎯 Bug Hunter (50 bugs fixed)",
            "📚 Knowledge Contributor"
        ]
        self.achievements_list.addItems(sample_achievements)
        
        achievements_layout.addWidget(self.achievements_list)
        achievements_group.setLayout(achievements_layout)
        
        # Statistics
        stats_group = QGroupBox("Usage Statistics")
        stats_layout = QFormLayout()
        
        self.queries_count = QLabel("0")
        self.code_generated = QLabel("0")
        self.projects_loaded = QLabel("0")
        self.knowledge_items = QLabel("0")
        
        stats_layout.addRow("Total Queries:", self.queries_count)
        stats_layout.addRow("Code Generated:", self.code_generated)
        stats_layout.addRow("Projects Loaded:", self.projects_loaded)
        stats_layout.addRow("Knowledge Items:", self.knowledge_items)
        
        stats_group.setLayout(stats_layout)
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("Skills & Experience:"))
        left_layout.addWidget(self.skills_tree)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(achievements_group)
        right_layout.addWidget(stats_group)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 300])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_project_tab(self) -> QWidget:
        """Create the project management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Current project
        project_layout = QHBoxLayout()
        self.current_project_label = QLabel("No project loaded")
        self.load_project_btn = QPushButton("Load Project")
        self.load_project_btn.clicked.connect(self._load_project)
        
        project_layout.addWidget(QLabel("Current Project:"))
        project_layout.addWidget(self.current_project_label)
        project_layout.addStretch()
        project_layout.addWidget(self.load_project_btn)
        
        # Project insights
        insights_group = QGroupBox("Project Insights")
        insights_layout = QFormLayout()
        
        self.files_count = QLabel("0")
        self.lines_count = QLabel("0")
        self.languages_label = QLabel("None")
        self.complexity_label = QLabel("N/A")
        
        insights_layout.addRow("Files:", self.files_count)
        insights_layout.addRow("Lines of Code:", self.lines_count)
        insights_layout.addRow("Languages:", self.languages_label)
        insights_layout.addRow("Complexity:", self.complexity_label)
        
        insights_group.setLayout(insights_layout)
        
        # Recent projects
        recent_group = QGroupBox("Recent Projects")
        recent_layout = QVBoxLayout()
        
        self.recent_projects_list = QListWidget()
        recent_layout.addWidget(self.recent_projects_list)
        
        recent_group.setLayout(recent_layout)
        
        # Project actions
        actions_layout = QHBoxLayout()
        self.analyze_project_btn = QPushButton("Analyze Project")
        self.save_state_btn = QPushButton("Save Agent State")
        self.load_state_btn = QPushButton("Load Agent State")
        
        actions_layout.addWidget(self.analyze_project_btn)
        actions_layout.addWidget(self.save_state_btn)
        actions_layout.addWidget(self.load_state_btn)
        actions_layout.addStretch()
        
        layout.addLayout(project_layout)
        layout.addWidget(insights_group)
        layout.addWidget(recent_group)
        layout.addLayout(actions_layout)
        
        return widget
    
    def _init_agent(self):
        """Initialize the coding agent connection."""
        # In production, this would connect to the actual coding agent
        self.update_status("Coding Agent initialized")
    
    def _submit_query(self):
        """Submit a query to the coding agent."""
        query = self.query_input.text().strip()
        if not query:
            return
        
        # Add to chat display
        self.chat_display.append(f"<b>You:</b> {query}")
        self.query_input.clear()
        
        # Process query in thread
        self._run_operation("process_query", {"query": query})
    
    def _generate_code(self):
        """Generate code based on description."""
        description = self.gen_description.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Input Required", "Please provide a description.")
            return
        
        params = {
            "description": description,
            "language": self.gen_language.currentText(),
            "framework": self.gen_framework.text(),
            "context": self.gen_context.toPlainText()
        }
        
        self._run_operation("generate_code", params)
    
    def _load_project(self):
        """Load a project directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if path:
            self._run_operation("load_project", {"path": path})
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = CodingAgentWorker(operation, params)
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
        if "response" in result:
            self.chat_display.append(f"<b>Agent:</b> {result['response']}")
        elif "code" in result:
            self.code_output.setPlainText(result['code'])
        elif "project" in result:
            self.current_project_label.setText(Path(result['project']).name)
            self.current_project = result['project']
        
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
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()