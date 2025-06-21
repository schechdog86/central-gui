"""
Settings View Component
======================

Comprehensive settings management for all components.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QColorDialog, QFontDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QColor, QPalette


class SettingsView(QWidget):
    """Settings view for managing all application configurations."""
    
    # Signals
    settings_changed = pyqtSignal(str, object)  # category, value
    theme_changed = pyqtSignal(str)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.settings = QSettings("SchechterCustomsLLC", "CentralizedAI")
        
        self.setWindowTitle("Settings")
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        
        # General settings
        self.general_tab = self._create_general_tab()
        self.tab_widget.addTab(self.general_tab, "⚙️ General")
        
        # Appearance settings
        self.appearance_tab = self._create_appearance_tab()
        self.tab_widget.addTab(self.appearance_tab, "🎨 Appearance")
        
        # Component settings
        self.components_tab = self._create_components_tab()
        self.tab_widget.addTab(self.components_tab, "🧩 Components")
        
        # Network settings
        self.network_tab = self._create_network_tab()
        self.tab_widget.addTab(self.network_tab, "🌐 Network")
        
        # Advanced settings
        self.advanced_tab = self._create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "🔧 Advanced")
        
        # About tab
        self.about_tab = self._create_about_tab()
        self.tab_widget.addTab(self.about_tab, "ℹ️ About")
        
        main_layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self._save_settings)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_settings)
        
        self.export_btn = QPushButton("Export Settings")
        self.export_btn.clicked.connect(self._export_settings)
        
        self.import_btn = QPushButton("Import Settings")
        self.import_btn.clicked.connect(self._import_settings)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.import_btn)
        
        main_layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create the general settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout()
        
        self.startup_checkbox = QCheckBox("Launch on system startup")
        self.minimize_to_tray = QCheckBox("Minimize to system tray")
        self.check_updates = QCheckBox("Check for updates automatically")
        self.check_updates.setChecked(True)
        
        app_layout.addRow("Startup:", self.startup_checkbox)
        app_layout.addRow("", self.minimize_to_tray)
        app_layout.addRow("Updates:", self.check_updates)
        
        app_group.setLayout(app_layout)
        
        # Workspace settings
        workspace_group = QGroupBox("Workspace")
        workspace_layout = QFormLayout()
        
        self.default_workspace = QLineEdit()
        self.browse_workspace_btn = QPushButton("Browse...")
        self.browse_workspace_btn.clicked.connect(self._browse_workspace)
        
        workspace_row = QHBoxLayout()
        workspace_row.addWidget(self.default_workspace)
        workspace_row.addWidget(self.browse_workspace_btn)
        
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(5)
        self.auto_save_interval.setSuffix(" minutes")
        
        workspace_layout.addRow("Default Workspace:", workspace_row)
        workspace_layout.addRow("Auto-save Interval:", self.auto_save_interval)
        
        workspace_group.setLayout(workspace_layout)
        
        # Language settings
        language_group = QGroupBox("Language & Region")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German", "Chinese", "Japanese"])
        
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"])
        
        language_layout.addRow("Language:", self.language_combo)
        language_layout.addRow("Date Format:", self.date_format_combo)
        
        language_group.setLayout(language_layout)
        
        layout.addWidget(app_group)
        layout.addWidget(workspace_group)
        layout.addWidget(language_group)
        layout.addStretch()
        
        return widget
    
    def _create_appearance_tab(self) -> QWidget:
        """Create the appearance settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        
        self.accent_color_btn = QPushButton("Choose...")
        self.accent_color_btn.clicked.connect(self._choose_accent_color)
        self.accent_color_preview = QLabel()
        self.accent_color_preview.setFixedSize(30, 30)
        self.accent_color_preview.setStyleSheet("background-color: #0078d4; border: 1px solid black;")
        
        accent_layout = QHBoxLayout()
        accent_layout.addWidget(self.accent_color_preview)
        accent_layout.addWidget(self.accent_color_btn)
        accent_layout.addStretch()
        
        theme_layout.addRow("Theme:", self.theme_combo)
        theme_layout.addRow("Accent Color:", accent_layout)
        
        theme_group.setLayout(theme_layout)
        
        # Font settings
        font_group = QGroupBox("Fonts")
        font_layout = QFormLayout()
        
        self.app_font_btn = QPushButton("Choose Font...")
        self.app_font_btn.clicked.connect(lambda: self._choose_font("app"))
        self.app_font_label = QLabel("Default Font")
        
        self.code_font_btn = QPushButton("Choose Font...")
        self.code_font_btn.clicked.connect(lambda: self._choose_font("code"))
        self.code_font_label = QLabel("Consolas, 12pt")
        
        font_layout.addRow("Application Font:", self.app_font_btn)
        font_layout.addRow("", self.app_font_label)
        font_layout.addRow("Code Font:", self.code_font_btn)
        font_layout.addRow("", self.code_font_label)
        
        font_group.setLayout(font_layout)
        
        # Window settings
        window_group = QGroupBox("Window")
        window_layout = QFormLayout()
        
        self.window_opacity = QSpinBox()
        self.window_opacity.setRange(50, 100)
        self.window_opacity.setValue(100)
        self.window_opacity.setSuffix("%")
        
        self.show_toolbar = QCheckBox("Show toolbar")
        self.show_toolbar.setChecked(True)
        
        self.show_statusbar = QCheckBox("Show status bar")
        self.show_statusbar.setChecked(True)
        
        window_layout.addRow("Opacity:", self.window_opacity)
        window_layout.addRow("Display:", self.show_toolbar)
        window_layout.addRow("", self.show_statusbar)
        
        window_group.setLayout(window_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addWidget(window_group)
        layout.addStretch()
        
        return widget
    
    def _create_components_tab(self) -> QWidget:
        """Create the components settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Component list
        self.component_tree = QTreeWidget()
        self.component_tree.setHeaderLabels(["Component", "Status", "Auto-start"])
        
        # Add components
        components = [
            ("Coding Agent", "Enabled", True),
            ("Web Scraper", "Enabled", False),
            ("Anonymous Browser", "Enabled", False),
            ("Workspace Tracker", "Enabled", True),
            ("Ollama LLM", "Enabled", True),
            ("MCP Integration", "Enabled", False),
            ("Code Analysis", "Enabled", False),
            ("Ray Cluster", "Disabled", False)
        ]
        
        for name, status, autostart in components:
            item = QTreeWidgetItem([name, status, "Yes" if autostart else "No"])
            self.component_tree.addTopLevelItem(item)
        
        # Component settings
        settings_group = QGroupBox("Component Settings")
        settings_layout = QVBoxLayout()
        
        self.component_settings = QTextEdit()
        self.component_settings.setPlaceholderText("Select a component to view its settings...")
        
        settings_layout.addWidget(self.component_settings)
        settings_group.setLayout(settings_layout)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.component_tree)
        splitter.addWidget(settings_group)
        splitter.setSizes([300, 200])
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_network_tab(self) -> QWidget:
        """Create the network settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Proxy settings
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QFormLayout()
        
        self.use_proxy = QCheckBox("Use proxy server")
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "HTTPS", "SOCKS5"])
        
        self.proxy_host_input = QLineEdit()
        self.proxy_host_input.setPlaceholderText("proxy.example.com")
        
        self.proxy_port_input = QSpinBox()
        self.proxy_port_input.setRange(1, 65535)
        self.proxy_port_input.setValue(8080)
        
        self.proxy_auth = QCheckBox("Proxy requires authentication")
        self.proxy_user_input = QLineEdit()
        self.proxy_pass_input = QLineEdit()
        self.proxy_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        proxy_layout.addRow("Enable Proxy:", self.use_proxy)
        proxy_layout.addRow("Proxy Type:", self.proxy_type_combo)
        proxy_layout.addRow("Host:", self.proxy_host_input)
        proxy_layout.addRow("Port:", self.proxy_port_input)
        proxy_layout.addRow("Authentication:", self.proxy_auth)
        proxy_layout.addRow("Username:", self.proxy_user_input)
        proxy_layout.addRow("Password:", self.proxy_pass_input)
        
        proxy_group.setLayout(proxy_layout)
        
        # API settings
        api_group = QGroupBox("API Settings")
        api_layout = QFormLayout()
        
        self.api_timeout = QSpinBox()
        self.api_timeout.setRange(5, 300)
        self.api_timeout.setValue(30)
        self.api_timeout.setSuffix(" seconds")
        
        self.max_retries = QSpinBox()
        self.max_retries.setRange(0, 10)
        self.max_retries.setValue(3)
        
        self.verify_ssl = QCheckBox("Verify SSL certificates")
        self.verify_ssl.setChecked(True)
        
        api_layout.addRow("Timeout:", self.api_timeout)
        api_layout.addRow("Max Retries:", self.max_retries)
        api_layout.addRow("Security:", self.verify_ssl)
        
        api_group.setLayout(api_layout)
        
        layout.addWidget(proxy_group)
        layout.addWidget(api_group)
        layout.addStretch()
        
        return widget
    
    def _create_advanced_tab(self) -> QWidget:
        """Create the advanced settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance settings
        perf_group = QGroupBox("Performance")
        perf_layout = QFormLayout()
        
        self.thread_pool_size = QSpinBox()
        self.thread_pool_size.setRange(1, 32)
        self.thread_pool_size.setValue(4)
        
        self.cache_size = QSpinBox()
        self.cache_size.setRange(10, 1000)
        self.cache_size.setValue(100)
        self.cache_size.setSuffix(" MB")
        
        self.gpu_acceleration = QCheckBox("Enable GPU acceleration")
        
        perf_layout.addRow("Thread Pool Size:", self.thread_pool_size)
        perf_layout.addRow("Cache Size:", self.cache_size)
        perf_layout.addRow("GPU:", self.gpu_acceleration)
        
        perf_group.setLayout(perf_layout)
        
        # Logging settings
        log_group = QGroupBox("Logging")
        log_layout = QFormLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        
        self.log_to_file = QCheckBox("Log to file")
        self.log_to_file.setChecked(True)
        
        self.log_file_path = QLineEdit()
        self.browse_log_btn = QPushButton("Browse...")
        
        log_path_layout = QHBoxLayout()
        log_path_layout.addWidget(self.log_file_path)
        log_path_layout.addWidget(self.browse_log_btn)
        
        log_layout.addRow("Log Level:", self.log_level_combo)
        log_layout.addRow("Output:", self.log_to_file)
        log_layout.addRow("Log File:", log_path_layout)
        
        log_group.setLayout(log_layout)
        
        # Developer settings
        dev_group = QGroupBox("Developer Options")
        dev_layout = QFormLayout()
        
        self.debug_mode = QCheckBox("Enable debug mode")
        self.show_console = QCheckBox("Show developer console")
        self.enable_plugins = QCheckBox("Enable third-party plugins")
        
        dev_layout.addRow("Debug:", self.debug_mode)
        dev_layout.addRow("", self.show_console)
        dev_layout.addRow("Plugins:", self.enable_plugins)
        
        dev_group.setLayout(dev_layout)
        
        layout.addWidget(perf_group)
        layout.addWidget(log_group)
        layout.addWidget(dev_group)
        layout.addStretch()
        
        return widget
    
    def _create_about_tab(self) -> QWidget:
        """Create the about tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Application info
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
        <h2>Schechter Customs LLC - Centralized AI UI</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Build Date:</b> 2025-06-18</p>
        <br>
        <p>A comprehensive AI automation platform integrating multiple tools and services.</p>
        
        <h3>Components:</h3>
        <ul>
            <li><b>Coding Agent:</b> AI-powered coding assistant with memory and skills</li>
            <li><b>Web Scraper:</b> Advanced web scraping with Firecrawl</li>
            <li><b>Anonymous Browser:</b> Docker-based anonymous browsing</li>
            <li><b>Workspace Tracker:</b> Project and workspace management</li>
            <li><b>Ollama LLM:</b> Local language model integration</li>
            <li><b>MCP Integration:</b> Model Context Protocol support</li>
            <li><b>Code Analysis:</b> Static code analysis tools</li>
            <li><b>Ray Cluster:</b> Distributed computing capabilities</li>
        </ul>
        
        <h3>License:</h3>
        <p>© 2025 Schechter Customs LLC. All rights reserved.</p>
        
        <h3>Credits:</h3>
        <p>Built with PyQt6, Ollama, Firecrawl, and other open-source technologies.</p>
        """)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.check_updates_btn = QPushButton("Check for Updates")
        self.view_license_btn = QPushButton("View License")
        self.report_bug_btn = QPushButton("Report Bug")
        
        button_layout.addWidget(self.check_updates_btn)
        button_layout.addWidget(self.view_license_btn)
        button_layout.addWidget(self.report_bug_btn)
        button_layout.addStretch()
        
        layout.addWidget(info_text)
        layout.addLayout(button_layout)
        
        return widget
    
    def _browse_workspace(self):
        """Browse for workspace directory."""
        path = QFileDialog.getExistingDirectory(self, "Select Workspace Directory")
        if path:
            self.default_workspace.setText(path)
    
    def _on_theme_changed(self, theme: str):
        """Handle theme change."""
        self.theme_changed.emit(theme.lower())
    
    def _choose_accent_color(self):
        """Choose accent color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.accent_color_preview.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid black;"
            )
    
    def _choose_font(self, font_type: str):
        """Choose font."""
        font, ok = QFontDialog.getFont()
        if ok:
            if font_type == "app":
                self.app_font_label.setText(f"{font.family()}, {font.pointSize()}pt")
            else:
                self.code_font_label.setText(f"{font.family()}, {font.pointSize()}pt")
    
    def _save_settings(self):
        """Save all settings."""
        # Save general settings
        self.settings.setValue("general/startup", self.startup_checkbox.isChecked())
        self.settings.setValue("general/minimize_to_tray", self.minimize_to_tray.isChecked())
        self.settings.setValue("general/check_updates", self.check_updates.isChecked())
        self.settings.setValue("general/workspace", self.default_workspace.text())
        self.settings.setValue("general/auto_save_interval", self.auto_save_interval.value())
        
        # Save appearance settings
        self.settings.setValue("appearance/theme", self.theme_combo.currentText())
        self.settings.setValue("appearance/window_opacity", self.window_opacity.value())
        
        # Save network settings
        self.settings.setValue("network/use_proxy", self.use_proxy.isChecked())
        self.settings.setValue("network/proxy_type", self.proxy_type_combo.currentText())
        self.settings.setValue("network/proxy_host", self.proxy_host_input.text())
        self.settings.setValue("network/proxy_port", self.proxy_port_input.value())
        
        # Save advanced settings
        self.settings.setValue("advanced/thread_pool_size", self.thread_pool_size.value())
        self.settings.setValue("advanced/cache_size", self.cache_size.value())
        self.settings.setValue("advanced/log_level", self.log_level_combo.currentText())
        
        QMessageBox.information(self, "Settings Saved", "All settings have been saved successfully.")
    
    def _reset_settings(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self._load_settings()
            QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults.")
    
    def _export_settings(self):
        """Export settings to file."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            "settings.json",
            "JSON Files (*.json)"
        )
        
        if path:
            settings_dict = {}
            for key in self.settings.allKeys():
                settings_dict[key] = self.settings.value(key)
            
            with open(path, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            
            QMessageBox.information(self, "Export Complete", "Settings exported successfully.")
    
    def _import_settings(self):
        """Import settings from file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            "",
            "JSON Files (*.json)"
        )
        
        if path:
            try:
                with open(path, 'r') as f:
                    settings_dict = json.load(f)
                
                for key, value in settings_dict.items():
                    self.settings.setValue(key, value)
                
                self._load_settings()
                QMessageBox.information(self, "Import Complete", "Settings imported successfully.")
                
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Failed to import settings: {str(e)}")
    
    def _load_settings(self):
        """Load settings from storage."""
        # Load general settings
        self.startup_checkbox.setChecked(self.settings.value("general/startup", False, bool))
        self.minimize_to_tray.setChecked(self.settings.value("general/minimize_to_tray", False, bool))
        self.check_updates.setChecked(self.settings.value("general/check_updates", True, bool))
        self.default_workspace.setText(self.settings.value("general/workspace", "", str))
        self.auto_save_interval.setValue(self.settings.value("general/auto_save_interval", 5, int))
        
        # Load appearance settings
        theme = self.settings.value("appearance/theme", "Dark", str)
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Load other settings...
        # (Similar pattern for other settings)