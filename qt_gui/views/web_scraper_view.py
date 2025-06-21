from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QScrollArea, QFormLayout, 
                             QGroupBox, QTabWidget, QComboBox, QCheckBox, QSpinBox)
from PyQt6.QtCore import pyqtSignal, QThread, QObject, pyqtSlot
import requests
import json
import time

class FirecrawlWorker(QObject):
    """Worker thread for Firecrawl API calls to avoid blocking the UI"""
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_key="fc-372845c4cc3348c0a9086a9693938b82"):
        super().__init__()
        self.api_key = api_key
        self.base_url = "http://localhost:3002"
        
    def scrape_url(self, url, options=None):
        """Scrape a single URL using Firecrawl"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': url,
                'formats': ['markdown', 'html'],
                'onlyMainContent': True
            }
            
            if options:
                payload.update(options)
            
            response = requests.post(f"{self.base_url}/v1/scrape", 
                                   headers=headers, 
                                   json=payload,
                                   timeout=30)
            
            if response.status_code == 200:
                self.result_ready.emit(response.json())
            else:
                self.error_occurred.emit(f"Scrape failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Scrape error: {str(e)}")
    
    def crawl_website(self, url, options=None):
        """Crawl a website using Firecrawl"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': url,
                'crawlerOptions': {
                    'includes': [],
                    'excludes': [],
                    'maxDepth': 2,
                    'limit': 10
                },
                'pageOptions': {
                    'formats': ['markdown', 'html'],
                    'onlyMainContent': True
                }
            }
            
            if options:
                if 'maxDepth' in options:
                    payload['crawlerOptions']['maxDepth'] = options['maxDepth']
                if 'limit' in options:
                    payload['crawlerOptions']['limit'] = options['limit']
                if 'includes' in options:
                    payload['crawlerOptions']['includes'] = options['includes']
                if 'excludes' in options:
                    payload['crawlerOptions']['excludes'] = options['excludes']
            
            response = requests.post(f"{self.base_url}/v1/crawl", 
                                   headers=headers, 
                                   json=payload,
                                   timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                job_id = result.get('id')
                
                # Poll for completion
                while True:
                    status_response = requests.get(f"{self.base_url}/v1/crawl/{job_id}", 
                                                 headers=headers, timeout=30)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data.get('status') == 'completed':
                            self.result_ready.emit(status_data)
                            break
                        elif status_data.get('status') == 'failed':
                            self.error_occurred.emit(f"Crawl failed: {status_data.get('error', 'Unknown error')}")
                            break
                        else:
                            time.sleep(2)  # Wait before next poll
                    else:
                        self.error_occurred.emit(f"Status check failed: {status_response.status_code}")
                        break
            else:
                self.error_occurred.emit(f"Crawl failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Crawl error: {str(e)}")

class WebScraperView(QWidget):
class WebScraperView(QWidget):
    create_job_signal = pyqtSignal(str, dict)
    get_status_signal = pyqtSignal(str)

    def __init__(self, view_model, parent=None):
        super().__init__(parent)
        self.view_model = view_model
        self.setWindowTitle("Web Scraper")
        
        # Firecrawl worker setup
        self.firecrawl_worker = FirecrawlWorker()
        self.firecrawl_thread = QThread()
        self.firecrawl_worker.moveToThread(self.firecrawl_thread)
        self.firecrawl_worker.result_ready.connect(self._handle_firecrawl_result)
        self.firecrawl_worker.error_occurred.connect(self._handle_firecrawl_error)
        self.firecrawl_thread.start()
        
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different scraping methods
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # WebScraperManager Tab
        self._create_web_scraper_tab()
        
        # Firecrawl Tab
        self._create_firecrawl_tab()

    def _create_web_scraper_tab(self):
        """Create tab for existing WebScraperManager functionality"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Input Group
        input_group = QGroupBox("Create Scraping Job")
        input_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to scrape")
        input_layout.addRow("URL:", self.url_input)

        self.selectors_input = QLineEdit()
        self.selectors_input.setPlaceholderText("Optional: CSS selectors (e.g., {\'title\': \'h1.title\'})")
        input_layout.addRow("Selectors (JSON):", self.selectors_input)
        
        self.create_job_button = QPushButton("Create Job")
        input_layout.addRow(self.create_job_button)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Status Group
        status_group = QGroupBox("Job Status & Results")
        status_layout = QVBoxLayout()

        self.job_id_input = QLineEdit()
        self.job_id_input.setPlaceholderText("Enter Job ID to get status/results")
        status_layout.addWidget(self.job_id_input)

        self.get_status_button = QPushButton("Get Job Status/Results")
        status_layout.addWidget(self.get_status_button)
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        status_layout.addWidget(self.status_display)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Overall Status
        overall_status_group = QGroupBox("Overall Scraper Status")
        overall_status_layout = QVBoxLayout()
        self.overall_status_button = QPushButton("Get Overall Scraper Status")
        overall_status_layout.addWidget(self.overall_status_button)
        self.overall_status_display = QTextEdit()
        self.overall_status_display.setReadOnly(True)
        overall_status_layout.addWidget(self.overall_status_display)
        overall_status_group.setLayout(overall_status_layout)
        layout.addWidget(overall_status_group)
        
        self.tab_widget.addTab(tab, "WebScraperManager")

    def _create_firecrawl_tab(self):
        """Create tab for Firecrawl functionality"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Firecrawl Scrape Group
        scrape_group = QGroupBox("Firecrawl - Single Page Scraping")
        scrape_layout = QFormLayout()
        
        self.firecrawl_url_input = QLineEdit()
        self.firecrawl_url_input.setPlaceholderText("Enter URL to scrape with Firecrawl")
        scrape_layout.addRow("URL:", self.firecrawl_url_input)
        
        self.main_content_only = QCheckBox("Extract main content only")
        self.main_content_only.setChecked(True)
        scrape_layout.addRow("Options:", self.main_content_only)
        
        self.scrape_button = QPushButton("Scrape Page")
        scrape_layout.addRow(self.scrape_button)
        
        scrape_group.setLayout(scrape_layout)
        layout.addWidget(scrape_group)
        
        # Firecrawl Crawl Group
        crawl_group = QGroupBox("Firecrawl - Website Crawling")
        crawl_layout = QFormLayout()
        
        self.crawl_url_input = QLineEdit()
        self.crawl_url_input.setPlaceholderText("Enter website URL to crawl")
        crawl_layout.addRow("URL:", self.crawl_url_input)
        
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setMinimum(1)
        self.max_depth_spin.setMaximum(10)
        self.max_depth_spin.setValue(2)
        crawl_layout.addRow("Max Depth:", self.max_depth_spin)
        
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setMinimum(1)
        self.max_pages_spin.setMaximum(100)
        self.max_pages_spin.setValue(10)
        crawl_layout.addRow("Max Pages:", self.max_pages_spin)
        
        self.includes_input = QLineEdit()
        self.includes_input.setPlaceholderText("Include patterns (comma-separated)")
        crawl_layout.addRow("Include:", self.includes_input)
        
        self.excludes_input = QLineEdit()
        self.excludes_input.setPlaceholderText("Exclude patterns (comma-separated)")
        crawl_layout.addRow("Exclude:", self.excludes_input)
        
        self.crawl_button = QPushButton("Crawl Website")
        crawl_layout.addRow(self.crawl_button)
        
        crawl_group.setLayout(crawl_layout)
        layout.addWidget(crawl_group)
        
        # Firecrawl Results
        results_group = QGroupBox("Firecrawl Results")
        results_layout = QVBoxLayout()
        
        self.firecrawl_results = QTextEdit()
        self.firecrawl_results.setReadOnly(True)
        results_layout.addWidget(self.firecrawl_results)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(tab, "Firecrawl")

    def _connect_signals(self):
        # WebScraperManager signals
        self.create_job_button.clicked.connect(self._on_create_job)
        self.get_status_button.clicked.connect(self._on_get_job_status)
        self.overall_status_button.clicked.connect(self._on_get_overall_status)
        
        # Firecrawl signals
        self.scrape_button.clicked.connect(self._on_firecrawl_scrape)
        self.crawl_button.clicked.connect(self._on_firecrawl_crawl)
        
        # ViewModel signals
        self.view_model.job_created_signal.connect(self._handle_job_created)
        self.view_model.status_updated_signal.connect(self._handle_status_updated)
        self.view_model.overall_status_signal.connect(self._handle_overall_status)
        self.view_model.error_signal.connect(self._handle_error)

    # WebScraperManager methods
    def _on_create_job(self):
        url = self.url_input.text()
        selectors_str = self.selectors_input.text()
        options = {}
        if selectors_str:
            try:
                options['selectors'] = json.loads(selectors_str)
            except json.JSONDecodeError:
                self.status_display.setText("Error: Invalid JSON in selectors.")
                return
        if url:
            self.create_job_signal.emit(url, options)
        else:
            self.status_display.setText("Error: URL cannot be empty.")

    def _on_get_job_status(self):
        job_id = self.job_id_input.text()
        if job_id:
            self.get_status_signal.emit(job_id)
        else:
            self.status_display.setText("Error: Job ID cannot be empty to get status.")

    def _on_get_overall_status(self):
        self.get_status_signal.emit("")

    # Firecrawl methods
    def _on_firecrawl_scrape(self):
        url = self.firecrawl_url_input.text()
        if not url:
            self.firecrawl_results.setText("Error: URL cannot be empty.")
            return
            
        options = {
            'onlyMainContent': self.main_content_only.isChecked()
        }
        
        self.firecrawl_results.setText("Scraping in progress...")
        self.firecrawl_worker.scrape_url(url, options)

    def _on_firecrawl_crawl(self):
        url = self.crawl_url_input.text()
        if not url:
            self.firecrawl_results.setText("Error: URL cannot be empty.")
            return
            
        options = {
            'maxDepth': self.max_depth_spin.value(),
            'limit': self.max_pages_spin.value()
        }
        
        if self.includes_input.text():
            options['includes'] = [p.strip() for p in self.includes_input.text().split(',')]
        if self.excludes_input.text():
            options['excludes'] = [p.strip() for p in self.excludes_input.text().split(',')]
        
        self.firecrawl_results.setText("Crawling in progress...")
        self.firecrawl_worker.crawl_website(url, options)

    # Signal handlers
    def _handle_job_created(self, job_id: str):
        self.status_display.setText(f"Job created with ID: {job_id}")
        self.job_id_input.setText(job_id)

    def _handle_status_updated(self, status_data: dict):
        self.status_display.setText(json.dumps(status_data, indent=2))

    def _handle_overall_status(self, status_data: dict):
        self.overall_status_display.setText(json.dumps(status_data, indent=2))

    def _handle_error(self, error_message: str):
        self.status_display.append(f"\nERROR: {error_message}")

    def _handle_firecrawl_result(self, result: dict):
        self.firecrawl_results.setText(json.dumps(result, indent=2))

    def _handle_firecrawl_error(self, error_message: str):
        self.firecrawl_results.setText(f"ERROR: {error_message}")

    def cleanup(self):
        # Stop Firecrawl thread
        if hasattr(self, 'firecrawl_thread') and self.firecrawl_thread.isRunning():
            self.firecrawl_thread.quit()
            self.firecrawl_thread.wait()
