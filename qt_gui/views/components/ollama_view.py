"""
Ollama LLM View Component
========================

Local language model integration with Ollama.
"""

import json
import requests
from typing import Dict, List, Optional, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QProgressBar, QMessageBox,
    QGroupBox, QFormLayout, QScrollArea, QSplitter, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSlider,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer


class OllamaWorker(QObject):
    """Worker thread for Ollama operations."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    streaming_response = pyqtSignal(str)
    
    def __init__(self, operation: str, params: Dict[str, Any]):
        super().__init__()
        self.operation = operation
        self.params = params
        self.ollama_url = params.get("ollama_url", "http://localhost:11434")
    
    def run(self):
        """Execute Ollama operations."""
        try:
            if self.operation == "list_models":
                self._list_models()
            elif self.operation == "chat":
                self._chat()
            elif self.operation == "generate":
                self._generate()
            elif self.operation == "pull_model":
                self._pull_model()
            elif self.operation == "delete_model":
                self._delete_model()
            elif self.operation == "show_model_info":
                self._show_model_info()
            else:
                self.finished.emit({"status": "unknown operation"})
                
        except Exception as e:
            self.error.emit(str(e))
    
    def _list_models(self):
        """List available models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                self.error.emit(f"Failed to list models: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.error.emit("Cannot connect to Ollama. Make sure it's running.")
    
    def _chat(self):
        """Chat with a model."""
        try:
            url = f"{self.ollama_url}/api/chat"
            data = {
                "model": self.params["model"],
                "messages": self.params["messages"],
                "stream": True,
                "options": self.params.get("options", {})
            }
            
            response = requests.post(url, json=data, stream=True)
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'message' in chunk:
                        content = chunk['message'].get('content', '')
                        full_response += content
                        self.streaming_response.emit(content)
            
            self.finished.emit({"response": full_response})
            
        except Exception as e:
            self.error.emit(f"Chat error: {str(e)}")
    
    def _generate(self):
        """Generate completion."""
        try:
            url = f"{self.ollama_url}/api/generate"
            data = {
                "model": self.params["model"],
                "prompt": self.params["prompt"],
                "stream": True,
                "options": self.params.get("options", {})
            }
            
            response = requests.post(url, json=data, stream=True)
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'response' in chunk:
                        full_response += chunk['response']
                        self.streaming_response.emit(chunk['response'])
            
            self.finished.emit({"response": full_response})
            
        except Exception as e:
            self.error.emit(f"Generation error: {str(e)}")
    
    def _pull_model(self):
        """Pull a model from the registry."""
        try:
            url = f"{self.ollama_url}/api/pull"
            data = {"name": self.params["model_name"]}
            
            response = requests.post(url, json=data, stream=True)
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    status = chunk.get('status', '')
                    self.progress.emit(status)
            
            self.finished.emit({"status": "completed"})
            
        except Exception as e:
            self.error.emit(f"Pull error: {str(e)}")
    
    def _delete_model(self):
        """Delete a model."""
        try:
            url = f"{self.ollama_url}/api/delete"
            data = {"name": self.params["model_name"]}
            
            response = requests.delete(url, json=data)
            
            if response.status_code == 200:
                self.finished.emit({"status": "deleted"})
            else:
                self.error.emit(f"Failed to delete model: {response.status_code}")
                
        except Exception as e:
            self.error.emit(f"Delete error: {str(e)}")
    
    def _show_model_info(self):
        """Get model information."""
        try:
            url = f"{self.ollama_url}/api/show"
            data = {"name": self.params["model_name"]}
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                self.error.emit(f"Failed to get model info: {response.status_code}")
                
        except Exception as e:
            self.error.emit(f"Info error: {str(e)}")


class ModelSettingsDialog(QDialog):
    """Dialog for model settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Settings")
        self.setModal(True)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(70)
        self.temperature_label = QLabel("0.7")
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_label.setText(f"{v/100:.1f}")
        )
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        
        # Max tokens
        tokens_layout = QHBoxLayout()
        tokens_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 4096)
        self.max_tokens_spin.setValue(2048)
        tokens_layout.addWidget(self.max_tokens_spin)
        
        # Top P
        top_p_layout = QHBoxLayout()
        top_p_layout.addWidget(QLabel("Top P:"))
        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(90)
        self.top_p_label = QLabel("0.9")
        self.top_p_slider.valueChanged.connect(
            lambda v: self.top_p_label.setText(f"{v/100:.1f}")
        )
        top_p_layout.addWidget(self.top_p_slider)
        top_p_layout.addWidget(self.top_p_label)
        
        # System prompt
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlaceholderText("System prompt (optional)")
        self.system_prompt.setMaximumHeight(100)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(temp_layout)
        layout.addLayout(tokens_layout)
        layout.addLayout(top_p_layout)
        layout.addWidget(QLabel("System Prompt:"))
        layout.addWidget(self.system_prompt)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get the current settings."""
        return {
            "temperature": self.temperature_slider.value() / 100,
            "num_predict": self.max_tokens_spin.value(),
            "top_p": self.top_p_slider.value() / 100,
            "system": self.system_prompt.toPlainText()
        }


class OllamaView(QWidget):
    """Main view for the Ollama LLM component."""
    
    # Signals
    status_updated = pyqtSignal(str)
    model_loaded = pyqtSignal(str)
    
    def __init__(self, config_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_model = None
        self.chat_history = []
        self.worker_thread = None
        self.worker = None
        self.model_settings = {}
        
        self.setWindowTitle("Ollama LLM")
        self._init_ui()
        self._check_ollama_status()
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Connection status
        status_layout = QHBoxLayout()
        self.connection_label = QLabel("Ollama Status: Checking...")
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setStyleSheet("color: gray;")
        
        self.ollama_url = QLineEdit("http://localhost:11434")
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._check_ollama_status)
        
        status_layout.addWidget(self.connection_label)
        status_layout.addWidget(self.connection_indicator)
        status_layout.addStretch()
        status_layout.addWidget(QLabel("URL:"))
        status_layout.addWidget(self.ollama_url)
        status_layout.addWidget(self.connect_btn)
        
        # Model selection
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        
        self.refresh_models_btn = QPushButton("Refresh")
        self.refresh_models_btn.clicked.connect(self._refresh_models)
        
        self.model_settings_btn = QPushButton("Settings")
        self.model_settings_btn.clicked.connect(self._show_model_settings)
        
        model_layout.addWidget(QLabel("Model:"))
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.refresh_models_btn)
        model_layout.addWidget(self.model_settings_btn)
        model_layout.addStretch()
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Chat tab
        self.chat_tab = self._create_chat_tab()
        self.tab_widget.addTab(self.chat_tab, "💬 Chat")
        
        # Generation tab
        self.generation_tab = self._create_generation_tab()
        self.tab_widget.addTab(self.generation_tab, "✨ Generation")
        
        # Model management tab
        self.models_tab = self._create_models_tab()
        self.tab_widget.addTab(self.models_tab, "📦 Models")
        
        # API testing tab
        self.api_tab = self._create_api_tab()
        self.tab_widget.addTab(self.api_tab, "🔌 API")
        
        # Layout
        main_layout.addLayout(status_layout)
        main_layout.addLayout(model_layout)
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("QLabel { padding: 5px; }")
        main_layout.addWidget(self.status_label)
    
    def _create_chat_tab(self) -> QWidget:
        """Create the chat interface tab."""
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
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(100)
        self.chat_input.setPlaceholderText("Type your message here...")
        
        button_layout = QVBoxLayout()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self._send_chat_message)
        
        self.clear_chat_btn = QPushButton("Clear")
        self.clear_chat_btn.clicked.connect(self._clear_chat)
        
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.clear_chat_btn)
        button_layout.addStretch()
        
        input_layout.addWidget(self.chat_input)
        input_layout.addLayout(button_layout)
        
        # Chat options
        options_layout = QHBoxLayout()
        self.stream_checkbox = QCheckBox("Stream responses")
        self.stream_checkbox.setChecked(True)
        
        self.context_checkbox = QCheckBox("Maintain context")
        self.context_checkbox.setChecked(True)
        
        options_layout.addWidget(self.stream_checkbox)
        options_layout.addWidget(self.context_checkbox)
        options_layout.addStretch()
        
        layout.addWidget(QLabel("Chat:"))
        layout.addWidget(self.chat_display)
        layout.addLayout(options_layout)
        layout.addLayout(input_layout)
        
        return widget
    
    def _create_generation_tab(self) -> QWidget:
        """Create the text generation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Prompt input
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout()
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Enter your prompt here...")
        
        prompt_layout.addWidget(self.prompt_input)
        prompt_group.setLayout(prompt_layout)
        
        # Generation options
        options_group = QGroupBox("Options")
        options_layout = QFormLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "None",
            "Code Generation",
            "Creative Writing",
            "Technical Documentation",
            "Q&A",
            "Summarization"
        ])
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Plain Text", "Markdown", "JSON", "Code"])
        
        options_layout.addRow("Template:", self.template_combo)
        options_layout.addRow("Format:", self.format_combo)
        
        options_group.setLayout(options_layout)
        
        # Generate button
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self._generate_text)
        
        # Output
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        self.generation_output = QTextEdit()
        self.generation_output.setReadOnly(True)
        
        output_actions = QHBoxLayout()
        self.copy_output_btn = QPushButton("Copy")
        self.save_output_btn = QPushButton("Save")
        
        output_actions.addWidget(self.copy_output_btn)
        output_actions.addWidget(self.save_output_btn)
        output_actions.addStretch()
        
        output_layout.addWidget(self.generation_output)
        output_layout.addLayout(output_actions)
        
        output_group.setLayout(output_layout)
        
        # Layout
        layout.addWidget(prompt_group)
        layout.addWidget(options_group)
        layout.addWidget(self.generate_btn)
        layout.addWidget(output_group)
        
        return widget
    
    def _create_models_tab(self) -> QWidget:
        """Create the model management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Available models
        available_group = QGroupBox("Available Models")
        available_layout = QVBoxLayout()
        
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(4)
        self.models_table.setHorizontalHeaderLabels(["Name", "Size", "Modified", "Actions"])
        header = self.models_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        available_layout.addWidget(self.models_table)
        available_group.setLayout(available_layout)
        
        # Model actions
        actions_layout = QHBoxLayout()
        
        self.pull_model_input = QLineEdit()
        self.pull_model_input.setPlaceholderText("Model name (e.g., llama2:7b)")
        
        self.pull_model_btn = QPushButton("Pull Model")
        self.pull_model_btn.clicked.connect(self._pull_model)
        
        actions_layout.addWidget(QLabel("Pull:"))
        actions_layout.addWidget(self.pull_model_input)
        actions_layout.addWidget(self.pull_model_btn)
        actions_layout.addStretch()
        
        # Model info
        info_group = QGroupBox("Model Information")
        info_layout = QVBoxLayout()
        
        self.model_info_display = QTextEdit()
        self.model_info_display.setReadOnly(True)
        self.model_info_display.setMaximumHeight(200)
        
        info_layout.addWidget(self.model_info_display)
        info_group.setLayout(info_layout)
        
        layout.addWidget(available_group)
        layout.addLayout(actions_layout)
        layout.addWidget(info_group)
        
        return widget
    
    def _create_api_tab(self) -> QWidget:
        """Create the API testing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API endpoint
        endpoint_layout = QHBoxLayout()
        self.endpoint_combo = QComboBox()
        self.endpoint_combo.addItems([
            "/api/generate",
            "/api/chat",
            "/api/embeddings",
            "/api/tags",
            "/api/show",
            "/api/pull",
            "/api/push",
            "/api/delete"
        ])
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["GET", "POST", "DELETE"])
        
        endpoint_layout.addWidget(QLabel("Endpoint:"))
        endpoint_layout.addWidget(self.endpoint_combo)
        endpoint_layout.addWidget(QLabel("Method:"))
        endpoint_layout.addWidget(self.method_combo)
        endpoint_layout.addStretch()
        
        # Request body
        request_group = QGroupBox("Request")
        request_layout = QVBoxLayout()
        
        self.request_body = QTextEdit()
        self.request_body.setPlaceholderText("JSON request body...")
        self.request_body.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        
        request_layout.addWidget(self.request_body)
        request_group.setLayout(request_layout)
        
        # Send button
        self.send_api_btn = QPushButton("Send Request")
        self.send_api_btn.clicked.connect(self._send_api_request)
        
        # Response
        response_group = QGroupBox("Response")
        response_layout = QVBoxLayout()
        
        self.response_display = QTextEdit()
        self.response_display.setReadOnly(True)
        self.response_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        
        response_layout.addWidget(self.response_display)
        response_group.setLayout(response_layout)
        
        layout.addLayout(endpoint_layout)
        layout.addWidget(request_group)
        layout.addWidget(self.send_api_btn)
        layout.addWidget(response_group)
        
        return widget
    
    def _check_ollama_status(self):
        """Check if Ollama is running."""
        self._refresh_models()
    
    def _refresh_models(self):
        """Refresh the list of available models."""
        self._run_operation("list_models", {"ollama_url": self.ollama_url.text()})
    
    def _on_model_changed(self, model_name: str):
        """Handle model selection change."""
        if model_name:
            self.current_model = model_name
            self.model_loaded.emit(model_name)
            self.update_status(f"Selected model: {model_name}")
    
    def _show_model_settings(self):
        """Show model settings dialog."""
        dialog = ModelSettingsDialog(self)
        if dialog.exec():
            self.model_settings = dialog.get_settings()
    
    def _send_chat_message(self):
        """Send a chat message."""
        message = self.chat_input.toPlainText().strip()
        if not message or not self.current_model:
            return
        
        # Add to display
        self.chat_display.append(f"<b>You:</b> {message}")
        self.chat_input.clear()
        
        # Add to history
        self.chat_history.append({"role": "user", "content": message})
        
        # Prepare messages
        messages = self.chat_history if self.context_checkbox.isChecked() else [self.chat_history[-1]]
        
        params = {
            "model": self.current_model,
            "messages": messages,
            "ollama_url": self.ollama_url.text(),
            "options": self.model_settings
        }
        
        self._run_operation("chat", params)
    
    def _clear_chat(self):
        """Clear chat history."""
        self.chat_display.clear()
        self.chat_history.clear()
    
    def _generate_text(self):
        """Generate text based on prompt."""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt or not self.current_model:
            return
        
        params = {
            "model": self.current_model,
            "prompt": prompt,
            "ollama_url": self.ollama_url.text(),
            "options": self.model_settings
        }
        
        self.generation_output.clear()
        self._run_operation("generate", params)
    
    def _pull_model(self):
        """Pull a new model."""
        model_name = self.pull_model_input.text().strip()
        if not model_name:
            return
        
        params = {
            "model_name": model_name,
            "ollama_url": self.ollama_url.text()
        }
        
        self._run_operation("pull_model", params)
    
    def _send_api_request(self):
        """Send a custom API request."""
        # Implementation would send custom API requests
        self.response_display.setPlainText("API request feature coming soon...")
    
    def _run_operation(self, operation: str, params: Dict[str, Any]):
        """Run an Ollama operation in a worker thread."""
        if self.worker_thread and self.worker_thread.isRunning():
            return
        
        self.update_status(f"Running {operation}...")
        
        self.worker_thread = QThread()
        self.worker = OllamaWorker(operation, params)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_operation_finished)
        self.worker.error.connect(self._on_operation_error)
        self.worker.progress.connect(self.update_status)
        self.worker.streaming_response.connect(self._on_streaming_response)
        
        # Cleanup
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()
    
    def _on_operation_finished(self, result: Any):
        """Handle operation completion."""
        if isinstance(result, dict):
            if "models" in result:
                # Update models list
                self.model_combo.clear()
                for model in result["models"]:
                    self.model_combo.addItem(model["name"])
                
                # Update models table
                self.models_table.setRowCount(len(result["models"]))
                for i, model in enumerate(result["models"]):
                    self.models_table.setItem(i, 0, QTableWidgetItem(model["name"]))
                    self.models_table.setItem(i, 1, QTableWidgetItem(model.get("size", "Unknown")))
                    self.models_table.setItem(i, 2, QTableWidgetItem(model.get("modified_at", "Unknown")))
                
                self.connection_label.setText("Ollama Status: Connected")
                self.connection_indicator.setStyleSheet("color: green;")
                
            elif "response" in result:
                # Add assistant response to chat
                if self.tab_widget.currentWidget() == self.chat_tab:
                    self.chat_history.append({"role": "assistant", "content": result["response"]})
        
        self.update_status("Ready")
    
    def _on_operation_error(self, error: str):
        """Handle operation error."""
        if "Cannot connect" in error:
            self.connection_label.setText("Ollama Status: Not Connected")
            self.connection_indicator.setStyleSheet("color: red;")
        
        QMessageBox.critical(self, "Error", f"Operation failed: {error}")
        self.update_status("Error occurred")
    
    def _on_streaming_response(self, text: str):
        """Handle streaming response text."""
        if self.tab_widget.currentWidget() == self.chat_tab:
            # Append to chat display
            cursor = self.chat_display.textCursor()
            if cursor.position() == 0 or self.chat_display.toPlainText().endswith("\\n"):
                self.chat_display.append("<b>Assistant:</b> ")
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(text)
        else:
            # Append to generation output
            cursor = self.generation_output.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.insertText(text)
    
    def update_status(self, message: str):
        """Update the status label."""
        self.status_label.setText(f"Status: {message}")
        self.status_updated.emit(message)
    
    def cleanup(self):
        """Clean up resources."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()