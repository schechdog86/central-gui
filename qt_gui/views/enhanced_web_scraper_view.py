"""
Enhanced Web Scraper View using MVVM Architecture
===============================================

Modern implementation with proper separation of concerns and error handling.
"""

import logging
from typing import Dict, Any, List
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QTabWidget, QFormLayout,
    QGroupBox, QComboBox, QCheckBox, QSpinBox, QProgressBar,
    QSplitter, QMessageBox
)
from PyQt6.QtCore import QObject, pyqtSignal, QThread, Qt

from ..utils.async_error_handling import (
    ErrorHandler, AsyncOperationManager, handle_errors,
    NetworkError, ValidationError
)


class WebScraperViewModel(QObject):
    """
    ViewModel for web scraper with enhanced error handling and async operations.
    """

    # Signals
    scrapingStarted = pyqtSignal()
    scrapingFinished = pyqtSignal(dict)
    scrapingError = pyqtSignal(str)
    progressUpdated = pyqtSignal(int)
    statusChanged = pyqtSignal(str)

    def __init__(self, error_handler: ErrorHandler,
                 async_manager: AsyncOperationManager, parent=None):
        super().__init__(parent)

        self.error_handler = error_handler
        self.async_manager = async_manager
        self.logger = logging.getLogger("SchechterAI.WebScraperViewModel")

        # State
        self.is_scraping = False
        self.current_operation_id = None

        # Scraper instances
        self.web_scraper_manager = None
        self.firecrawl_api_key = "fc-372845c4cc3348c0a9086a9693938b82"
        self.firecrawl_base_url = "http://localhost:3002"

        # Connect async manager signals
        self.async_manager.operationStarted.connect(self._on_operation_started)
        self.async_manager.operationFinished.connect(self._on_operation_finished)
        self.async_manager.operationError.connect(self._on_operation_error)

    @handle_errors(component="WebScraper", show_user=True)
    def start_scraping(self, method: str, url: str, options: Dict = None):
        """Start scraping operation."""
        if self.is_scraping:
            raise ValidationError("Scraping operation already in progress")

        if not url or not url.strip():
            raise ValidationError("URL cannot be empty")

        if not self._validate_url(url):
            raise ValidationError("Invalid URL format")

        self.is_scraping = True
        self.statusChanged.emit("Starting scraping operation...")

        if method == "firecrawl":
            operation = self._firecrawl_scrape
        else:
            operation = self._webscraper_manager_scrape

        self.current_operation_id = self.async_manager.start_operation(
            operation, f"scrape_{method}", url, options or {}
        )

    def stop_scraping(self):
        """Stop current scraping operation."""
        if self.current_operation_id:
            self.async_manager.cancel_operation(self.current_operation_id)
            self.is_scraping = False
            self.statusChanged.emit("Scraping stopped")

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    def _firecrawl_scrape(self, url: str, options: Dict) -> Dict:
        """Perform Firecrawl scraping."""
        import requests

        headers = {
            'Authorization': f'Bearer {self.firecrawl_api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'url': url,
            'formats': ['markdown', 'html'],
            'onlyMainContent': True
        }
        payload.update(options)

        try:
            response = requests.post(
                f"{self.firecrawl_base_url}/v1/scrape",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise NetworkError(
                    f"Firecrawl API error: {response.status_code} - {response.text}",
                    component="WebScraper"
                )

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}", component="WebScraper")

    def _webscraper_manager_scrape(self, url: str, options: Dict) -> Dict:
        """Perform WebScraperManager scraping."""
        # Import WebScraperManager dynamically
        try:
            from ....web_scraper.scraper_manager import WebScraperManager
            
            if not self.web_scraper_manager:
                self.web_scraper_manager = WebScraperManager()

            result = self.web_scraper_manager.scrape_url(url, **options)
            return {
                'success': True,
                'data': result,
                'method': 'WebScraperManager'
            }

        except ImportError as e:
            raise ValidationError(f"WebScraperManager not available: {e}")
        except Exception as e:
            raise NetworkError(f"Scraping failed: {e}")

    def _on_operation_started(self, operation_id: str):
        """Handle operation started."""
        if operation_id == self.current_operation_id:
            self.scrapingStarted.emit()
            self.progressUpdated.emit(0)

    def _on_operation_finished(self, operation_id: str):
        """Handle operation finished."""
        if operation_id == self.current_operation_id:
            self.is_scraping = False
            self.current_operation_id = None
            self.progressUpdated.emit(100)
            self.statusChanged.emit("Scraping completed")

    def _on_operation_error(self, operation_id: str, error: Exception):
        """Handle operation error."""
        if operation_id == self.current_operation_id:
            self.is_scraping = False
            self.current_operation_id = None
            self.scrapingError.emit(str(error))
            self.statusChanged.emit("Scraping failed")


class EnhancedWebScraperView(QWidget):
    """
    Enhanced web scraper view with improved UX and error handling.
    """

    def __init__(self, view_model: WebScraperViewModel, parent=None):
        super().__init__(parent)

        self.view_model = view_model
        self.logger = logging.getLogger("SchechterAI.WebScraperView")

        # Connect signals
        self._connect_view_model_signals()

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Setup the enhanced UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        self.create_header(layout)

        # Main content
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Input and options
        left_panel = self.create_input_panel()
        splitter.addWidget(left_panel)

        # Right panel - Results
        right_panel = self.create_results_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([1, 2])
        layout.addWidget(splitter)

        # Status bar
        self.create_status_bar(layout)

    def create_header(self, layout):
        """Create header section."""
        header_layout = QHBoxLayout()

        title = QLabel("🌐 Advanced Web Scraper")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0078d4;
            margin-bottom: 10px;
        """)

        subtitle = QLabel("Extract data with WebScraperManager and Firecrawl")
        subtitle.setStyleSheet("color: #605e5c; font-size: 14px;")

        header_layout.addWidget(title)
        header_layout.addStretch()

        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        layout.addLayout(title_layout)

    def create_input_panel(self):
        """Create input panel with options."""
        panel = QGroupBox("Scraping Configuration")
        layout = QVBoxLayout(panel)

        # URL input
        url_group = QGroupBox("Target URL")
        url_layout = QFormLayout(url_group)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        url_layout.addRow("URL:", self.url_input)

        layout.addWidget(url_group)

        # Method selection
        method_group = QGroupBox("Scraping Method")
        method_layout = QVBoxLayout(method_group)

        self.method_combo = QComboBox()
        self.method_combo.addItems(["firecrawl", "webscraper_manager"])
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        method_layout.addWidget(self.method_combo)

        layout.addWidget(method_group)

        # Options tabs
        self.options_tabs = QTabWidget()

        # Firecrawl options
        firecrawl_widget = QWidget()
        firecrawl_layout = QFormLayout(firecrawl_widget)

        self.firecrawl_formats = QCheckBox("Include HTML")
        self.firecrawl_main_content = QCheckBox("Only Main Content")
        self.firecrawl_main_content.setChecked(True)

        firecrawl_layout.addRow("Formats:", self.firecrawl_formats)
        firecrawl_layout.addRow("Options:", self.firecrawl_main_content)

        self.options_tabs.addTab(firecrawl_widget, "Firecrawl Options")

        # WebScraperManager options
        manager_widget = QWidget()
        manager_layout = QFormLayout(manager_widget)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")

        self.follow_redirects = QCheckBox("Follow Redirects")
        self.follow_redirects.setChecked(True)

        manager_layout.addRow("Timeout:", self.timeout_spin)
        manager_layout.addRow("Options:", self.follow_redirects)

        self.options_tabs.addTab(manager_widget, "Manager Options")

        layout.addWidget(self.options_tabs)

        # Action buttons
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Scraping")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self._on_start_scraping)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a4262c;
            }
        """)
        self.stop_button.clicked.connect(self._on_stop_scraping)
        self.stop_button.setEnabled(False)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        return panel

    def create_results_panel(self):
        """Create results display panel."""
        panel = QGroupBox("Scraping Results")
        layout = QVBoxLayout(panel)

        # Results tabs
        self.results_tabs = QTabWidget()

        # Raw results
        self.raw_results = QTextEdit()
        self.raw_results.setReadOnly(True)
        self.raw_results.setPlaceholderText("Scraping results will appear here...")
        self.results_tabs.addTab(self.raw_results, "Raw Data")

        # Formatted results
        self.formatted_results = QTextEdit()
        self.formatted_results.setReadOnly(True)
        self.results_tabs.addTab(self.formatted_results, "Formatted")

        layout.addWidget(self.results_tabs)

        return panel

    def create_status_bar(self, layout):
        """Create status bar."""
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #605e5c;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)

        layout.addLayout(status_layout)

    def _connect_view_model_signals(self):
        """Connect ViewModel signals."""
        self.view_model.scrapingStarted.connect(self._on_scraping_started)
        self.view_model.scrapingFinished.connect(self._on_scraping_finished)
        self.view_model.scrapingError.connect(self._on_scraping_error)
        self.view_model.progressUpdated.connect(self._on_progress_updated)
        self.view_model.statusChanged.connect(self._on_status_changed)

    def _on_method_changed(self, method: str):
        """Handle method selection change."""
        if method == "firecrawl":
            self.options_tabs.setCurrentIndex(0)
        else:
            self.options_tabs.setCurrentIndex(1)

    def _on_start_scraping(self):
        """Handle start scraping button."""
        url = self.url_input.text().strip()
        method = self.method_combo.currentText()

        # Collect options based on method
        if method == "firecrawl":
            options = {
                'formats': ['markdown', 'html'] if self.firecrawl_formats.isChecked() else ['markdown'],
                'onlyMainContent': self.firecrawl_main_content.isChecked()
            }
        else:
            options = {
                'timeout': self.timeout_spin.value(),
                'follow_redirects': self.follow_redirects.isChecked()
            }

        try:
            self.view_model.start_scraping(method, url, options)
        except Exception as e:
            QMessageBox.warning(self, "Scraping Error", str(e))

    def _on_stop_scraping(self):
        """Handle stop scraping button."""
        self.view_model.stop_scraping()

    def _on_scraping_started(self):
        """Handle scraping started."""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.raw_results.clear()
        self.formatted_results.clear()

    def _on_scraping_finished(self, result: Dict):
        """Handle scraping finished."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        # Display results
        self.raw_results.setPlainText(json.dumps(result, indent=2))

        # Format results for better readability
        if 'data' in result:
            if isinstance(result['data'], dict):
                formatted = self._format_result_dict(result['data'])
            else:
                formatted = str(result['data'])
            self.formatted_results.setHtml(formatted)

    def _on_scraping_error(self, error: str):
        """Handle scraping error."""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        self.raw_results.setPlainText(f"Error: {error}")
        QMessageBox.critical(self, "Scraping Error", error)

    def _on_progress_updated(self, progress: int):
        """Handle progress update."""
        self.progress_bar.setValue(progress)

    def _on_status_changed(self, status: str):
        """Handle status change."""
        self.status_label.setText(status)

    def _format_result_dict(self, data: Dict) -> str:
        """Format result dictionary for display."""
        formatted = "<h3>Scraping Results</h3>"

        for key, value in data.items():
            formatted += f"<p><strong>{key}:</strong></p>"
            if isinstance(value, (dict, list)):
                formatted += f"<pre>{json.dumps(value, indent=2)}</pre>"
            else:
                formatted += f"<p>{str(value)}</p>"

        return formatted
