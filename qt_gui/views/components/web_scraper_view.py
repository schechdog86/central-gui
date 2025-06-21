import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
                             QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
import requests # For Firecrawl
import time

# Assuming WebScraperManager is accessible, adjust import if necessary
# from .....web_scraper.scraper_manager import WebScraperManager # Placeholder

class FirecrawlWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, url, mode="scrape", params=None):
        super().__init__()
        self.url = url
        self.mode = mode # "scrape" or "crawl"
        self.params = params if params is not None else {}
        # Assuming firecrawl is running on localhost:3002 as per your docker setup
        self.firecrawl_base_url = "http://localhost:3002" 

    def run(self):
        try:
            self.progress.emit(f"Starting Firecrawl {self.mode} for: {self.url}")
            endpoint = f"{self.firecrawl_base_url}/{self.mode}"
            
            payload = {'url': self.url}
            if self.params:
                payload.update(self.params)

            headers = {'Content-Type': 'application/json'}
            # The API key is configured in the .env file for the self-hosted Firecrawl Docker instance,
            # so it doesn't need to be sent in the request headers here.
            
            response = requests.post(endpoint, json=payload, headers=headers, timeout=300) # 5 min timeout
            
            if response.status_code == 200:
                self.progress.emit(f"Firecrawl {self.mode} successful.")
                self.finished.emit(response.json())
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                self.progress.emit(error_msg)
                self.error.emit(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Firecrawl request failed: {e}"
            self.progress.emit(error_msg)
            self.error.emit(error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred with Firecrawl: {e}"
            self.progress.emit(error_msg)
            self.error.emit(error_msg)

class WebScraperView(QWidget):
    status_updated = pyqtSignal(str)
    results_updated = pyqtSignal(str)

    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        # self.scraper_manager = WebScraperManager() # Initialize your existing scraper
        self.scraper_manager = None # Placeholder for now, to be integrated
        self.firecrawl_thread = None
        self.firecrawl_worker = None
        
        self.setWindowTitle("Web Scraper")
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Input Group - Common for all scrapers
        input_group = QGroupBox("Input")
        input_layout = QFormLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL (e.g., https://example.com)")
        input_layout.addRow(QLabel("URL:"), self.url_input)
        # main_layout.addWidget(input_group) # Add this once at the top

        # --- Controls Area ---
        controls_widget = QWidget()
        controls_main_layout = QVBoxLayout(controls_widget)

        # --- WebScraperManager Section (Placeholder) ---
        ws_manager_group = QGroupBox("Standard Scraper (Not Yet Implemented)")
        ws_manager_layout = QVBoxLayout()
        self.scrape_button_standard = QPushButton("Scrape with Standard Scraper")
        self.scrape_button_standard.clicked.connect(self.start_standard_scrape)
        self.scrape_button_standard.setEnabled(False) # Disabled until implemented
        ws_manager_layout.addWidget(self.scrape_button_standard)
        ws_manager_group.setLayout(ws_manager_layout)
        # controls_main_layout.addWidget(ws_manager_group) # Keep for future

        # --- Firecrawl Section ---
        firecrawl_group = QGroupBox("Firecrawl Web Scraper/Crawler")
        firecrawl_main_layout = QVBoxLayout()

        firecrawl_options_layout = QFormLayout()
        self.firecrawl_mode_combo = QComboBox()
        self.firecrawl_mode_combo.addItems(["scrape", "crawl"])
        firecrawl_options_layout.addRow(QLabel("Mode:"), self.firecrawl_mode_combo)
        
        # Firecrawl Scrape Options
        self.firecrawl_scrape_options_group = QGroupBox("Scrape Options")
        scrape_options_layout = QFormLayout()
        self.page_options_checkbox = QCheckBox("Include Page Options (e.g., onlyMainContent)")
        self.page_options_checkbox.setChecked(True)
        self.extractor_options_checkbox = QCheckBox("Include Extractor Options (e.g., llmExtraction)")
        scrape_options_layout.addRow(self.page_options_checkbox)
        scrape_options_layout.addRow(self.extractor_options_checkbox)
        self.firecrawl_scrape_options_group.setLayout(scrape_options_layout)
        
        # Firecrawl Crawl Options
        self.firecrawl_crawl_options_group = QGroupBox("Crawl Options")
        crawl_options_layout = QFormLayout()
        self.crawler_options_checkbox = QCheckBox("Include Crawler Options (e.g., maxDepth, maxPages)")
        self.crawler_options_checkbox.setChecked(True)
        self.page_options_crawl_checkbox = QCheckBox("Include Page Options for Crawl (e.g. onlyMainContent)")
        self.page_options_crawl_checkbox.setChecked(True)
        crawl_options_layout.addRow(self.crawler_options_checkbox)
        crawl_options_layout.addRow(self.page_options_crawl_checkbox)
        self.firecrawl_crawl_options_group.setLayout(crawl_options_layout)
        self.firecrawl_crawl_options_group.setVisible(False) # Initially hidden

        firecrawl_main_layout.addLayout(firecrawl_options_layout)
        firecrawl_main_layout.addWidget(self.firecrawl_scrape_options_group)
        firecrawl_main_layout.addWidget(self.firecrawl_crawl_options_group)

        self.firecrawl_mode_combo.currentTextChanged.connect(self.toggle_firecrawl_options)

        self.scrape_button_firecrawl = QPushButton("Start Firecrawl Task")
        self.scrape_button_firecrawl.clicked.connect(self.start_firecrawl_task)
        firecrawl_main_layout.addWidget(self.scrape_button_firecrawl)
        
        firecrawl_group.setLayout(firecrawl_main_layout)
        controls_main_layout.addWidget(firecrawl_group)
        
        # --- Results and Status Area ---
        results_group = QGroupBox("Results & Status")
        results_layout = QVBoxLayout()
        self.status_label = QLabel("Status: Idle")
        results_layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        results_layout.addWidget(self.progress_bar)
        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) # For better JSON display
        results_layout.addWidget(self.results_area)
        results_group.setLayout(results_layout)
        
        # Splitter for controls and results
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(controls_widget) # Contains input_group and firecrawl_group
        splitter.addWidget(results_group)
        splitter.setSizes([350, 650]) # Adjust initial sizes

        main_layout.addWidget(input_group) # URL input at the very top
        main_layout.addWidget(splitter)

        self.setLayout(main_layout)
        self.toggle_firecrawl_options(self.firecrawl_mode_combo.currentText()) # Set initial visibility

    def toggle_firecrawl_options(self, mode):
        if mode == "scrape":
            self.firecrawl_scrape_options_group.setVisible(True)
            self.firecrawl_crawl_options_group.setVisible(False)
        elif mode == "crawl":
            self.firecrawl_scrape_options_group.setVisible(False)
            self.firecrawl_crawl_options_group.setVisible(True)

    def get_firecrawl_params(self):
        params = {}
        mode = self.firecrawl_mode_combo.currentText()

        if mode == "scrape":
            if self.page_options_checkbox.isChecked():
                params['pageOptions'] = {
                    "onlyMainContent": True, 
                    # "includeHtml": False 
                }
            if self.extractor_options_checkbox.isChecked():
                # User would need to fill these in more detail, or we provide more UI
                params['extractorOptions'] = {
                    "mode": "llm-extraction", 
                    "extractionPrompt": "Extract the main title and the first paragraph of this article.",
                    "extractionSchema": {"title": "string", "first_paragraph": "string"}
                }
        elif mode == "crawl":
            if self.crawler_options_checkbox.isChecked():
                params['crawlerOptions'] = {
                    "maxDepth": 2, 
                    "maxPages": 5, 
                    # "includeDomains": ["example.com"], 
                    # "excludePaths": ["/login", "/profile"], 
                }
            if self.page_options_crawl_checkbox.isChecked():
                 params['pageOptions'] = { 
                    "onlyMainContent": True
                }
        return params

    def start_standard_scrape(self):
        # This is a placeholder for your existing WebScraperManager integration
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            return
        self.update_status(f"Standard scrape for: {url} (Not Implemented Yet)")
        self.results_area.setText("Standard WebScraperManager integration is pending.")
        QMessageBox.information(self, "Pending", "Standard WebScraperManager integration is not yet complete.")


    def start_firecrawl_task(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL.")
            return

        if not (url.startswith("http://") or url.startswith("https://")):
            QMessageBox.warning(self, "Input Error", "URL must start with http:// or https://")
            return

        if self.firecrawl_thread and self.firecrawl_thread.isRunning():
            QMessageBox.warning(self, "Busy", "A Firecrawl operation is already in progress. Please wait.")
            return

        self.update_status("Initiating Firecrawl request...")
        self.results_area.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0) # Indeterminate progress

        mode = self.firecrawl_mode_combo.currentText()
        params = self.get_firecrawl_params()

        self.firecrawl_thread = QThread(self) # Parent it to self for better lifetime management
        self.firecrawl_worker = FirecrawlWorker(url, mode, params)
        self.firecrawl_worker.moveToThread(self.firecrawl_thread)

        # Connect signals
        self.firecrawl_worker.finished.connect(self.on_firecrawl_finished)
        self.firecrawl_worker.error.connect(self.on_firecrawl_error)
        self.firecrawl_worker.progress.connect(self.update_status)
        self.firecrawl_thread.started.connect(self.firecrawl_worker.run)
        
        # Clean up thread and worker
        self.firecrawl_worker.finished.connect(self.firecrawl_thread.quit)
        self.firecrawl_worker.error.connect(self.firecrawl_thread.quit)
        self.firecrawl_thread.finished.connect(self.firecrawl_thread.deleteLater)
        self.firecrawl_worker.finished.connect(self.firecrawl_worker.deleteLater) # Worker deletes itself after finishing
        self.firecrawl_worker.error.connect(self.firecrawl_worker.deleteLater)   # Or after erroring

        self.firecrawl_thread.start()
        self.scrape_button_firecrawl.setEnabled(False) # Disable button while running

    def on_firecrawl_finished(self, data):
        self.update_status("Firecrawl operation completed.")
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0,100) 
        try:
            if isinstance(data, list): # Expected from crawl
                self.results_area.append(f"Received {len(data)} items from crawl.\n")
                # Display a summary or first few items due to potential size
                for i, item in enumerate(data[:10]): # Display up to 10 items
                    self.results_area.append(f"--- Item {i+1} ---\n{json.dumps(item, indent=2)}\n")
                if len(data) > 10:
                    self.results_area.append(f"\n... and {len(data)-10} more items (not displayed).")
            elif isinstance(data, dict): # Expected from scrape
                 self.results_area.setText(json.dumps(data, indent=2))
            else:
                self.results_area.setText(str(data))
        except Exception as e:
            self.results_area.setText(f"Error formatting Firecrawl results: {e}\n\nRaw data:\n{data}")
        
        self.scrape_button_firecrawl.setEnabled(True) # Re-enable button
        self.firecrawl_thread = None 
        self.firecrawl_worker = None

    def on_firecrawl_error(self, error_message):
        self.update_status(f"Firecrawl Error.")
        self.results_area.setText(f"Error: {error_message}")
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0,100)
        QMessageBox.critical(self, "Firecrawl Error", error_message)
        
        self.scrape_button_firecrawl.setEnabled(True) # Re-enable button
        self.firecrawl_thread = None 
        self.firecrawl_worker = None


    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")
        # self.status_updated.emit(message) # If other parts of app need this

    def display_results(self, results_text): # General purpose, might be used by standard scraper
        self.results_area.setText(results_text)
        # self.results_updated.emit(results_text)

    def cleanup(self):
        self.update_status("Cleaning up WebScraperView...")
        if self.firecrawl_thread and self.firecrawl_thread.isRunning():
            self.update_status("Attempting to stop active Firecrawl thread...")
            # Disconnect signals to prevent issues during forced shutdown
            try:
                self.firecrawl_worker.finished.disconnect()
                self.firecrawl_worker.error.disconnect()
                self.firecrawl_worker.progress.disconnect()
            except TypeError: # Signals might not be connected
                pass

            self.firecrawl_thread.quit()
            if not self.firecrawl_thread.wait(3000): # Wait up to 3 seconds
                self.update_status("Firecrawl thread did not stop gracefully, terminating.")
                self.firecrawl_thread.terminate() 
                self.firecrawl_thread.wait() 
            self.update_status("Firecrawl thread stopped.")
        
        # if self.scraper_manager:
        #     self.scraper_manager.shutdown() 
        self.update_status("WebScraperView cleanup complete.")

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    
    # This is how you would normally run it within the main application
    # For standalone testing, ensure your Firecrawl Docker container is running.
    # And that localhost:3002 is accessible.
    
    view = WebScraperView()
    view.resize(1000, 700) # Give it a decent size for testing
    view.show()
    
    exit_code = app.exec()
    view.cleanup() # Ensure cleanup is called on exit
    sys.exit(exit_code)
