"""
Workspace Tracker View Component
===============================

Comprehensive UI for project and workspace management with activity tracking.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QCalendarWidget, QDateEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer, QDate
from PyQt6.QtGui import QFont, QColor, QIcon


class WorkspaceTrackerWorker(QObject):
    """Worker thread for workspace tracker operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    project_scanned = pyqtSignal(dict)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
    
    def run(self):
        """Execute the workspace tracker operation."""
        try:
            self.progress.emit(f"Starting {self.operation}...")
            
            # Simulate operations for now
            # In production, this would connect to actual workspace tracker
            
            if self.operation == "scan_workspace":
                result = {
                    "projects": 5,
                    "total_files": 234,
                    "total_size": "145 MB",
                    "languages": ["Python", "JavaScript", "HTML", "CSS"]
                }
            elif self.operation == "analyze_project":
                result = {
                    "name": self.params.get("path", "Unknown"),
                    "files": 45,
                    "lines": 3456,
                    "complexity": "Medium",
                    "issues": 12
                }
            elif self.operation == "create_task":
                result = {
                    "task_id": "TASK-001",
                    "status": "created",
                    "assigned_to": "Current User"
                }
            else:
                result = {"status": "completed"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class WorkspaceTrackerView(QWidget):
    """Main view for the Workspace Tracker component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    project_loaded = pyqtSignal(str)
    task_created = pyqtSignal(dict)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.worker_thread = None
        self.worker = None
        self.current_workspace = None
        self.current_project = None
        
        self.setWindowTitle("Workspace Tracker")
        self._init_ui()
        self._init_tracker()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different features
        self.tab_widget = QTabWidget()
        
        # Workspace Overview Tab
        self.overview_tab = self._create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Projects Tab
        self.projects_tab = self._create_projects_tab()
        self.tab_widget.addTab(self.projects_tab, "📁 Projects")
        
        # Tasks & Issues Tab
        self.tasks_tab = self._create_tasks_tab()
        self.tab_widget.addTab(self.tasks_tab, "✅ Tasks")
        
        # Activity Timeline Tab
        self.activity_tab = self._create_activity_tab()
        self.tab_widget.addTab(self.activity_tab, "📈 Activity")
        
        # Notes & Documentation Tab
        self.notes_tab = self._create_notes_tab()
        self.tab_widget.addTab(self.notes_tab, "📝 Notes")
        
        # Research & References Tab
        self.research_tab = self._create_research_tab()
        self.tab_widget.addTab(self.research_tab, "🔍 Research")
        
        # Reports & Analytics Tab
        self.reports_tab = self._create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "📊 Reports")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar at bottom
        self.status_label = QLabel("Workspace Tracker: Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_overview_tab(self) -> QWidget:
        """Create the workspace overview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Workspace selector
        workspace_layout = QHBoxLayout()
        self.workspace_combo = QComboBox()
        self.workspace_combo.addItems([
            "Default Workspace",
            "Development Projects",
            "Client Work",
            "Personal Projects"
        ])
        self.load_workspace_btn = QPushButton("📂 Load Workspace")
        self.new_workspace_btn = QPushButton("➕ New Workspace")
        
        workspace_layout.addWidget(QLabel("Current Workspace:"))
        workspace_layout.addWidget(self.workspace_combo)
        workspace_layout.addWidget(self.load_workspace_btn)
        workspace_layout.addWidget(self.new_workspace_btn)
        workspace_layout.addStretch()
        
        # Workspace statistics
        stats_group = QGroupBox("Workspace Statistics")
        stats_layout = QFormLayout()
        
        self.total_projects_label = QLabel("0")
        self.active_tasks_label = QLabel("0")
        self.completed_tasks_label = QLabel("0")
        self.total_notes_label = QLabel("0")
        self.workspace_size_label = QLabel("0 MB")
        self.last_activity_label = QLabel("Never")
        
        stats_layout.addRow("Total Projects:", self.total_projects_label)
        stats_layout.addRow("Active Tasks:", self.active_tasks_label)
        stats_layout.addRow("Completed Tasks:", self.completed_tasks_label)
        stats_layout.addRow("Total Notes:", self.total_notes_label)
        stats_layout.addRow("Workspace Size:", self.workspace_size_label)
        stats_layout.addRow("Last Activity:", self.last_activity_label)
        
        stats_group.setLayout(stats_layout)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        
        self.recent_activity_list = QListWidget()
        sample_activities = [
            "🔄 Updated project documentation - 2 hours ago",
            "✅ Completed task: Fix authentication bug - 5 hours ago",
            "📝 Added note: API design considerations - 1 day ago",
            "📁 Created new project: Mobile App - 2 days ago",
            "🔍 Added research: React best practices - 3 days ago"
        ]
        self.recent_activity_list.addItems(sample_activities)
        
        activity_layout.addWidget(self.recent_activity_list)
        activity_group.setLayout(activity_layout)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        self.scan_workspace_btn = QPushButton("🔍 Scan Workspace")
        self.scan_workspace_btn.clicked.connect(self._scan_workspace)
        self.backup_workspace_btn = QPushButton("💾 Backup")
        self.export_workspace_btn = QPushButton("📤 Export")
        self.settings_btn = QPushButton("⚙️ Settings")
        
        actions_layout.addWidget(self.scan_workspace_btn)
        actions_layout.addWidget(self.backup_workspace_btn)
        actions_layout.addWidget(self.export_workspace_btn)
        actions_layout.addWidget(self.settings_btn)
        
        actions_group.setLayout(actions_layout)
        
        layout.addLayout(workspace_layout)
        layout.addWidget(stats_group)
        layout.addWidget(activity_group)
        layout.addWidget(actions_group)
        
        return widget
    
    def _create_projects_tab(self) -> QWidget:
        """Create the projects management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Project controls
        controls_layout = QHBoxLayout()
        self.new_project_btn = QPushButton("➕ New Project")
        self.import_project_btn = QPushButton("📥 Import Project")
        self.refresh_projects_btn = QPushButton("🔄 Refresh")
        
        controls_layout.addWidget(self.new_project_btn)
        controls_layout.addWidget(self.import_project_btn)
        controls_layout.addWidget(self.refresh_projects_btn)
        controls_layout.addStretch()
        
        # Project tree
        self.projects_tree = QTreeWidget()
        self.projects_tree.setHeaderLabels([
            "Project", "Status", "Tasks", "Files", "Last Modified"
        ])
        
        # Add sample projects
        projects = [
            ("Centralized AI UI", "Active", "12", "234", "Today"),
            ("Web Scraper Module", "Active", "5", "45", "Yesterday"),
            ("Mobile App", "Planning", "8", "0", "3 days ago"),
            ("Data Pipeline", "Completed", "0", "156", "1 week ago"),
            ("Documentation Site", "On Hold", "3", "78", "2 weeks ago")
        ]
        
        for project in projects:
            item = QTreeWidgetItem(self.projects_tree)
            for i, value in enumerate(project):
                item.setText(i, value)
            
            # Add sub-items
            if project[0] == "Centralized AI UI":
                modules = [
                    ("Frontend", "Active", "5", "89"),
                    ("Backend", "Active", "4", "123"),
                    ("Database", "Active", "3", "22")
                ]
                for module in modules:
                    child = QTreeWidgetItem(item)
                    child.setText(0, module[0])
                    child.setText(1, module[1])
                    child.setText(2, module[2])
                    child.setText(3, module[3])
        
        # Project details
        details_group = QGroupBox("Project Details")
        details_layout = QFormLayout()
        
        self.project_name_label = QLabel("Select a project")
        self.project_path_label = QLabel("-")
        self.project_desc_text = QTextEdit()
        self.project_desc_text.setMaximumHeight(100)
        self.project_desc_text.setPlaceholderText("Project description...")
        
        details_layout.addRow("Name:", self.project_name_label)
        details_layout.addRow("Path:", self.project_path_label)
        details_layout.addRow("Description:", self.project_desc_text)
        
        details_group.setLayout(details_layout)
        
        # Project actions
        actions_layout = QHBoxLayout()
        self.open_project_btn = QPushButton("📂 Open in IDE")
        self.analyze_project_btn = QPushButton("🔍 Analyze")
        self.analyze_project_btn.clicked.connect(self._analyze_project)
        self.archive_project_btn = QPushButton("📦 Archive")
        self.delete_project_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.open_project_btn)
        actions_layout.addWidget(self.analyze_project_btn)
        actions_layout.addWidget(self.archive_project_btn)
        actions_layout.addWidget(self.delete_project_btn)
        actions_layout.addStretch()
        
        # Splitter for tree and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.addLayout(controls_layout)
        tree_layout.addWidget(self.projects_tree)
        
        details_widget = QWidget()
        details_widget_layout = QVBoxLayout(details_widget)
        details_widget_layout.addWidget(details_group)
        details_widget_layout.addLayout(actions_layout)
        
        splitter.addWidget(tree_widget)
        splitter.addWidget(details_widget)
        splitter.setSizes([400, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_tasks_tab(self) -> QWidget:
        """Create the tasks and issues tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Task creation
        create_group = QGroupBox("Create New Task")
        create_layout = QFormLayout()
        
        self.task_title_input = QLineEdit()
        self.task_title_input.setPlaceholderText("Task title...")
        
        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(["Task", "Bug", "Feature", "Enhancement", "Documentation"])
        
        self.task_priority_combo = QComboBox()
        self.task_priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        
        self.task_project_combo = QComboBox()
        self.task_project_combo.addItems([
            "Centralized AI UI",
            "Web Scraper Module",
            "Mobile App"
        ])
        
        self.task_desc_text = QTextEdit()
        self.task_desc_text.setMaximumHeight(80)
        self.task_desc_text.setPlaceholderText("Task description...")
        
        create_layout.addRow("Title:", self.task_title_input)
        create_layout.addRow("Type:", self.task_type_combo)
        create_layout.addRow("Priority:", self.task_priority_combo)
        create_layout.addRow("Project:", self.task_project_combo)
        create_layout.addRow("Description:", self.task_desc_text)
        
        create_group.setLayout(create_layout)
        
        self.create_task_btn = QPushButton("➕ Create Task")
        self.create_task_btn.clicked.connect(self._create_task)
        
        # Task filters
        filter_layout = QHBoxLayout()
        self.task_status_filter = QComboBox()
        self.task_status_filter.addItems([
            "All", "Open", "In Progress", "Completed", "Blocked"
        ])
        self.task_project_filter = QComboBox()
        self.task_project_filter.addItems([
            "All Projects", "Centralized AI UI", "Web Scraper Module"
        ])
        
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.task_status_filter)
        filter_layout.addWidget(QLabel("Project:"))
        filter_layout.addWidget(self.task_project_filter)
        filter_layout.addStretch()
        
        # Task list
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(6)
        self.tasks_table.setHorizontalHeaderLabels([
            "ID", "Title", "Type", "Priority", "Status", "Project"
        ])
        header = self.tasks_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Add sample tasks
        tasks = [
            ("TASK-001", "Implement user authentication", "Feature", "High", "In Progress", "Centralized AI UI"),
            ("TASK-002", "Fix memory leak in scraper", "Bug", "Critical", "Open", "Web Scraper Module"),
            ("TASK-003", "Add dark mode support", "Enhancement", "Medium", "Completed", "Mobile App"),
            ("TASK-004", "Update API documentation", "Documentation", "Low", "Open", "Centralized AI UI"),
            ("TASK-005", "Optimize database queries", "Task", "High", "Blocked", "Centralized AI UI")
        ]
        
        self.tasks_table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            for j, value in enumerate(task):
                item = QTableWidgetItem(value)
                if j == 3 and value == "Critical":  # Priority column
                    item.setBackground(QColor(255, 200, 200))
                elif j == 4:  # Status column
                    if value == "Completed":
                        item.setBackground(QColor(200, 255, 200))
                    elif value == "Blocked":
                        item.setBackground(QColor(255, 200, 200))
                self.tasks_table.setItem(i, j, item)
        
        # Layout
        layout.addWidget(create_group)
        layout.addWidget(self.create_task_btn)
        layout.addLayout(filter_layout)
        layout.addWidget(self.tasks_table)
        
        return widget
    
    def _create_activity_tab(self) -> QWidget:
        """Create the activity timeline tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Date range selector
        date_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        self.refresh_activity_btn = QPushButton("🔄 Refresh")
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.end_date_edit)
        date_layout.addWidget(self.refresh_activity_btn)
        date_layout.addStretch()
        
        # Activity timeline
        self.activity_tree = QTreeWidget()
        self.activity_tree.setHeaderLabels([
            "Time", "Activity", "Project", "Details"
        ])
        
        # Add sample activities by day
        today = QTreeWidgetItem(self.activity_tree)
        today.setText(0, "Today")
        today.setExpanded(True)
        
        today_activities = [
            ("09:15 AM", "Started working on", "Centralized AI UI", "Opened project in IDE"),
            ("10:30 AM", "Created task", "TASK-006", "Add user preferences"),
            ("11:45 AM", "Committed code", "Centralized AI UI", "Fixed authentication bug"),
            ("02:00 PM", "Added note", "Architecture", "Microservices design pattern")
        ]
        
        for activity in today_activities:
            item = QTreeWidgetItem(today)
            for i, value in enumerate(activity):
                item.setText(i, value)
        
        yesterday = QTreeWidgetItem(self.activity_tree)
        yesterday.setText(0, "Yesterday")
        
        # Activity summary
        summary_group = QGroupBox("Activity Summary")
        summary_layout = QFormLayout()
        
        self.total_hours_label = QLabel("24.5 hours")
        self.productive_hours_label = QLabel("18.3 hours")
        self.commits_count_label = QLabel("12")
        self.tasks_completed_label = QLabel("5")
        
        summary_layout.addRow("Total Time:", self.total_hours_label)
        summary_layout.addRow("Productive Time:", self.productive_hours_label)
        summary_layout.addRow("Commits:", self.commits_count_label)
        summary_layout.addRow("Tasks Completed:", self.tasks_completed_label)
        
        summary_group.setLayout(summary_layout)
        
        # Split layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        timeline_widget = QWidget()
        timeline_layout = QVBoxLayout(timeline_widget)
        timeline_layout.addLayout(date_layout)
        timeline_layout.addWidget(self.activity_tree)
        
        splitter.addWidget(timeline_widget)
        splitter.addWidget(summary_group)
        splitter.setSizes([500, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_notes_tab(self) -> QWidget:
        """Create the notes and documentation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Note controls
        controls_layout = QHBoxLayout()
        self.new_note_btn = QPushButton("📝 New Note")
        self.import_note_btn = QPushButton("📥 Import")
        self.search_notes_input = QLineEdit()
        self.search_notes_input.setPlaceholderText("Search notes...")
        
        controls_layout.addWidget(self.new_note_btn)
        controls_layout.addWidget(self.import_note_btn)
        controls_layout.addWidget(self.search_notes_input)
        controls_layout.addStretch()
        
        # Notes list and editor splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Notes list
        notes_widget = QWidget()
        notes_layout = QVBoxLayout(notes_widget)
        
        self.notes_tree = QTreeWidget()
        self.notes_tree.setHeaderLabels(["Title", "Category", "Modified"])
        
        # Add sample notes
        categories = {
            "Architecture": [
                ("System Design Overview", "2 hours ago"),
                ("API Documentation", "1 day ago"),
                ("Database Schema", "3 days ago")
            ],
            "Meeting Notes": [
                ("Sprint Planning", "Yesterday"),
                ("Client Review", "3 days ago")
            ],
            "Ideas": [
                ("Feature: AI Assistant", "1 week ago"),
                ("Performance Optimization", "2 weeks ago")
            ]
        }
        
        for category, notes in categories.items():
            cat_item = QTreeWidgetItem(self.notes_tree)
            cat_item.setText(0, category)
            cat_item.setExpanded(True)
            
            for title, modified in notes:
                note_item = QTreeWidgetItem(cat_item)
                note_item.setText(0, title)
                note_item.setText(2, modified)
        
        notes_layout.addWidget(self.notes_tree)
        
        # Note editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Note metadata
        metadata_layout = QHBoxLayout()
        self.note_title_input = QLineEdit()
        self.note_title_input.setPlaceholderText("Note title...")
        self.note_category_combo = QComboBox()
        self.note_category_combo.addItems([
            "Architecture", "Meeting Notes", "Ideas", "Documentation", "Research"
        ])
        
        metadata_layout.addWidget(self.note_title_input)
        metadata_layout.addWidget(self.note_category_combo)
        
        # Note content
        self.note_editor = QTextEdit()
        self.note_editor.setPlaceholderText("Write your note here...")
        
        # Note actions
        actions_layout = QHBoxLayout()
        self.save_note_btn = QPushButton("💾 Save")
        self.export_note_btn = QPushButton("📤 Export")
        self.delete_note_btn = QPushButton("🗑️ Delete")
        
        actions_layout.addWidget(self.save_note_btn)
        actions_layout.addWidget(self.export_note_btn)
        actions_layout.addWidget(self.delete_note_btn)
        actions_layout.addStretch()
        
        editor_layout.addLayout(metadata_layout)
        editor_layout.addWidget(self.note_editor)
        editor_layout.addLayout(actions_layout)
        
        splitter.addWidget(notes_widget)
        splitter.addWidget(editor_widget)
        splitter.setSizes([300, 500])
        
        layout.addLayout(controls_layout)
        layout.addWidget(splitter)
        
        return widget
    
    def _create_research_tab(self) -> QWidget:
        """Create the research and references tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Research controls
        controls_layout = QHBoxLayout()
        self.add_research_btn = QPushButton("➕ Add Research")
        self.add_link_btn = QPushButton("🔗 Add Link")
        self.import_research_btn = QPushButton("📥 Import")
        
        controls_layout.addWidget(self.add_research_btn)
        controls_layout.addWidget(self.add_link_btn)
        controls_layout.addWidget(self.import_research_btn)
        controls_layout.addStretch()
        
        # Research categories
        self.research_tabs = QTabWidget()
        
        # Articles tab
        articles_widget = QWidget()
        articles_layout = QVBoxLayout(articles_widget)
        
        self.articles_list = QListWidget()
        articles = [
            "📄 Best Practices for Python Async Programming",
            "📄 Microservices Architecture Patterns",
            "📄 Machine Learning in Production",
            "📄 React Performance Optimization Guide"
        ]
        self.articles_list.addItems(articles)
        
        articles_layout.addWidget(self.articles_list)
        self.research_tabs.addTab(articles_widget, "📄 Articles")
        
        # Links tab
        links_widget = QWidget()
        links_layout = QVBoxLayout(links_widget)
        
        self.links_table = QTableWidget()
        self.links_table.setColumnCount(3)
        self.links_table.setHorizontalHeaderLabels(["Title", "URL", "Tags"])
        
        links = [
            ("Python Documentation", "https://docs.python.org", "python, reference"),
            ("React Docs", "https://react.dev", "react, frontend"),
            ("Ray Documentation", "https://docs.ray.io", "distributed, computing")
        ]
        
        self.links_table.setRowCount(len(links))
        for i, (title, url, tags) in enumerate(links):
            self.links_table.setItem(i, 0, QTableWidgetItem(title))
            self.links_table.setItem(i, 1, QTableWidgetItem(url))
            self.links_table.setItem(i, 2, QTableWidgetItem(tags))
        
        links_layout.addWidget(self.links_table)
        self.research_tabs.addTab(links_widget, "🔗 Links")
        
        # Code Snippets tab
        snippets_widget = QWidget()
        snippets_layout = QVBoxLayout(snippets_widget)
        
        self.snippets_tree = QTreeWidget()
        self.snippets_tree.setHeaderLabels(["Name", "Language", "Description"])
        
        snippet_categories = {
            "Python": [
                ("Async Context Manager", "Python", "Reusable async context manager"),
                ("Decorator Pattern", "Python", "Custom decorator implementation")
            ],
            "JavaScript": [
                ("Promise Handler", "JavaScript", "Error handling for promises"),
                ("React Hook", "JavaScript", "Custom React hook example")
            ]
        }
        
        for category, snippets in snippet_categories.items():
            cat_item = QTreeWidgetItem(self.snippets_tree)
            cat_item.setText(0, category)
            
            for snippet in snippets:
                snippet_item = QTreeWidgetItem(cat_item)
                for i, value in enumerate(snippet):
                    snippet_item.setText(i, value)
        
        snippets_layout.addWidget(self.snippets_tree)
        self.research_tabs.addTab(snippets_widget, "💻 Code Snippets")
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.research_tabs)
        
        return widget
    
    def _create_reports_tab(self) -> QWidget:
        """Create the reports and analytics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Report type selector
        report_layout = QHBoxLayout()
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Weekly Summary",
            "Project Progress",
            "Task Analytics",
            "Time Tracking",
            "Code Metrics"
        ])
        self.generate_report_btn = QPushButton("📊 Generate Report")
        self.export_report_btn = QPushButton("📤 Export")
        
        report_layout.addWidget(QLabel("Report Type:"))
        report_layout.addWidget(self.report_type_combo)
        report_layout.addWidget(self.generate_report_btn)
        report_layout.addWidget(self.export_report_btn)
        report_layout.addStretch()
        
        # Report preview
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setHtml("""
        <h2>Weekly Summary Report</h2>
        <p><strong>Period:</strong> Jan 15 - Jan 21, 2025</p>
        
        <h3>Overview</h3>
        <ul>
            <li>Total Projects: 5</li>
            <li>Active Tasks: 12</li>
            <li>Completed Tasks: 8</li>
            <li>Time Logged: 42.5 hours</li>
        </ul>
        
        <h3>Project Progress</h3>
        <table border="1" cellpadding="5">
            <tr>
                <th>Project</th>
                <th>Progress</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>Centralized AI UI</td>
                <td>75%</td>
                <td>On Track</td>
            </tr>
            <tr>
                <td>Web Scraper Module</td>
                <td>90%</td>
                <td>Ahead of Schedule</td>
            </tr>
        </table>
        
        <h3>Key Achievements</h3>
        <ul>
            <li>Completed authentication system</li>
            <li>Fixed 5 critical bugs</li>
            <li>Deployed beta version</li>
        </ul>
        """)
        
        # Quick stats
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QFormLayout()
        
        self.week_hours_label = QLabel("42.5 hours")
        self.week_tasks_label = QLabel("8 completed")
        self.week_commits_label = QLabel("23 commits")
        self.productivity_label = QLabel("87%")
        
        stats_layout.addRow("This Week:", self.week_hours_label)
        stats_layout.addRow("Tasks:", self.week_tasks_label)
        stats_layout.addRow("Commits:", self.week_commits_label)
        stats_layout.addRow("Productivity:", self.productivity_label)
        
        stats_group.setLayout(stats_layout)
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        report_widget = QWidget()
        report_widget_layout = QVBoxLayout(report_widget)
        report_widget_layout.addLayout(report_layout)
        report_widget_layout.addWidget(self.report_preview)
        
        splitter.addWidget(report_widget)
        splitter.addWidget(stats_group)
        splitter.setSizes([600, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _init_tracker(self):
        """Initialize the workspace tracker."""
        # In production, this would connect to actual tracker
        self.update_status("Workspace Tracker initialized")
        
        # Load initial data
        self._update_statistics()
    
    def _update_statistics(self):
        """Update workspace statistics."""
        # In production, this would fetch real data
        self.total_projects_label.setText("5")
        self.active_tasks_label.setText("12")
        self.completed_tasks_label.setText("45")
        self.total_notes_label.setText("23")
        self.workspace_size_label.setText("145 MB")
        self.last_activity_label.setText("Just now")
    
    def _scan_workspace(self):
        """Scan the current workspace."""
        self._run_operation("scan_workspace", {"path": self.current_workspace})
    
    def _analyze_project(self):
        """Analyze the selected project."""
        # Get selected project from tree
        current_item = self.projects_tree.currentItem()
        if current_item and not current_item.parent():  # Top-level item
            project_name = current_item.text(0)
            self._run_operation("analyze_project", {"path": project_name})
    
    def _create_task(self):
        """Create a new task."""
        title = self.task_title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Input Required", "Please provide a task title.")
            return
        
        params = {
            "title": title,
            "type": self.task_type_combo.currentText(),
            "priority": self.task_priority_combo.currentText(),
            "project": self.task_project_combo.currentText(),
            "description": self.task_desc_text.toPlainText()
        }
        
        self._run_operation("create_task", params)
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            QMessageBox.warning(self, "Busy", "An operation is already in progress.")
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = WorkspaceTrackerWorker(operation, params)
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
        if "projects" in result:
            # Workspace scan completed
            QMessageBox.information(
                self, "Scan Complete",
                f"Found {result['projects']} projects\\n"
                f"Total files: {result['total_files']}\\n"
                f"Total size: {result['total_size']}"
            )
        elif "task_id" in result:
            # Task created
            QMessageBox.information(
                self, "Task Created",
                f"Task '{result['task_id']}' created successfully!"
            )
            # Clear form
            self.task_title_input.clear()
            self.task_desc_text.clear()
        elif "complexity" in result:
            # Project analyzed
            QMessageBox.information(
                self, "Analysis Complete",
                f"Project: {result['name']}\\n"
                f"Files: {result['files']}\\n"
                f"Lines: {result['lines']}\\n"
                f"Complexity: {result['complexity']}\\n"
                f"Issues: {result['issues']}"
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
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()