"""
Enhanced Error Handling and Async Operations
===========================================

Modern PyQt6 error handling patterns and async operation management
based on Context7 best practices and signal/slot architecture.
"""

import logging
import traceback
from typing import Optional, Any, Callable, Dict
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QMessageBox, QWidget


class ErrorSeverity(Enum):
    """Error severity levels for categorization and handling."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization and handling."""
    NETWORK = "network"
    VALIDATION = "validation"
    COMPONENT = "component"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    API = "api"


class ErrorContext:
    """Container for error context information."""
    
    def __init__(self, 
                 error: Exception,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 component: str = "unknown",
                 operation: str = "unknown",
                 user_message: Optional[str] = None,
                 technical_details: Optional[str] = None,
                 recovery_action: Optional[Callable] = None):
        self.error = error
        self.severity = severity
        self.category = category
        self.component = component
        self.operation = operation
        self.user_message = user_message or str(error)
        self.technical_details = technical_details or traceback.format_exc()
        self.recovery_action = recovery_action
        self.timestamp = logging.getLogger().handlers[0].formatter.formatTime(
            logging.LogRecord(
                name="", level=0, pathname="", lineno=0, 
                msg="", args=(), exc_info=None
            )
        ) if logging.getLogger().handlers else ""


class ErrorHandler(QObject):
    """
    Centralized error handling system with Qt6 signal/slot integration.
    
    Features:
    - Categorized error handling
    - User-friendly error display
    - Automatic recovery attempts
    - Error logging and reporting
    - Signal-based error communication
    """
    
    # Signals
    errorOccurred = pyqtSignal(ErrorContext)
    errorResolved = pyqtSignal(str, str)  # component, operation
    recoveryAttempted = pyqtSignal(str, bool)  # operation, success
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("SchechterAI.ErrorHandler")
        self.error_history: Dict[str, list] = {}
        
    def handle_error(self, error_context: ErrorContext):
        """Handle an error with appropriate response based on context."""
        try:
            # Log the error
            self._log_error(error_context)
            
            # Store in history
            self._store_error(error_context)
            
            # Emit signal for UI handling
            self.errorOccurred.emit(error_context)
            
            # Attempt recovery if available
            if error_context.recovery_action:
                self._attempt_recovery(error_context)
                
        except Exception as e:
            # Fallback error handling
            self.logger.critical(f"Error in error handler: {e}")
            
    def _log_error(self, context: ErrorContext):
        """Log error with appropriate level."""
        log_message = (
            f"[{context.component}:{context.operation}] "
            f"{context.user_message}"
        )
        
        if context.severity == ErrorSeverity.INFO:
            self.logger.info(log_message)
        elif context.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message)
        elif context.severity == ErrorSeverity.ERROR:
            self.logger.error(log_message, exc_info=context.error)
        elif context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, exc_info=context.error)
            
    def _store_error(self, context: ErrorContext):
        """Store error in history for analysis."""
        key = f"{context.component}:{context.operation}"
        if key not in self.error_history:
            self.error_history[key] = []
        self.error_history[key].append(context)
        
        # Limit history size
        if len(self.error_history[key]) > 100:
            self.error_history[key] = self.error_history[key][-100:]
            
    def _attempt_recovery(self, context: ErrorContext):
        """Attempt automatic recovery."""
        try:
            if context.recovery_action:
                success = context.recovery_action()
                self.recoveryAttempted.emit(
                    f"{context.component}:{context.operation}", 
                    success
                )
                if success:
                    self.errorResolved.emit(context.component, context.operation)
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")


class AsyncWorker(QObject):
    """
    Base class for async operations with proper error handling.
    
    Features:
    - Signal-based communication
    - Progress reporting
    - Error handling integration
    - Cancellation support
    """
    
    # Signals
    started = pyqtSignal()
    finished = pyqtSignal()
    progress = pyqtSignal(int, str)  # percentage, message
    result = pyqtSignal(object)  # result data
    error = pyqtSignal(ErrorContext)
    cancelled = pyqtSignal()
    
    def __init__(self, operation_name: str = "unknown", parent=None):
        super().__init__(parent)
        self.operation_name = operation_name
        self.component_name = "AsyncWorker"
        self.is_cancelled = False
        self.logger = logging.getLogger(f"SchechterAI.{self.component_name}")
        
    def process(self):
        """Override this method to implement the actual work."""
        raise NotImplementedError("Subclasses must implement process()")
        
    def run(self):
        """Execute the async operation with error handling."""
        try:
            self.started.emit()
            
            if self.is_cancelled:
                self.cancelled.emit()
                return
                
            result = self.process()
            
            if not self.is_cancelled:
                self.result.emit(result)
                
        except Exception as e:
            error_context = ErrorContext(
                error=e,
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.COMPONENT,
                component=self.component_name,
                operation=self.operation_name,
                user_message=f"Operation '{self.operation_name}' failed"
            )
            self.error.emit(error_context)
            
        finally:
            if not self.is_cancelled:
                self.finished.emit()
                
    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True
        
    def report_progress(self, percentage: int, message: str = ""):
        """Report progress during long-running operations."""
        if not self.is_cancelled:
            self.progress.emit(percentage, message)


class AsyncManager(QObject):
    """
    Manager for async operations with thread pooling and lifecycle management.
    
    Features:
    - Thread pool management
    - Operation queuing
    - Progress aggregation
    - Automatic cleanup
    """
    
    # Signals
    operationStarted = pyqtSignal(str)  # operation_id
    operationFinished = pyqtSignal(str)  # operation_id
    operationProgress = pyqtSignal(str, int, str)  # operation_id, %, message
    operationError = pyqtSignal(str, ErrorContext)  # operation_id, error
    
    def __init__(self, max_concurrent: int = 5, parent=None):
        super().__init__(parent)
        self.max_concurrent = max_concurrent
        self.active_operations: Dict[str, QThread] = {}
        self.operation_queue = []
        self.logger = logging.getLogger("SchechterAI.AsyncManager")
        
    def execute_async(self, 
                     worker: AsyncWorker, 
                     operation_id: Optional[str] = None) -> str:
        """Execute an async operation."""
        if operation_id is None:
            operation_id = f"{worker.component_name}_{worker.operation_name}_{id(worker)}"
            
        # Create thread
        thread = QThread()
        worker.moveToThread(thread)
        
        # Connect signals
        worker.started.connect(lambda: self.operationStarted.emit(operation_id))
        worker.finished.connect(lambda: self._cleanup_operation(operation_id))
        worker.progress.connect(
            lambda p, m: self.operationProgress.emit(operation_id, p, m)
        )
        worker.error.connect(
            lambda e: self.operationError.emit(operation_id, e)
        )
        
        # Connect thread signals
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        
        # Store and start
        self.active_operations[operation_id] = thread
        
        if len(self.active_operations) <= self.max_concurrent:
            thread.start()
        else:
            self.operation_queue.append((operation_id, thread))
            
        return operation_id
        
    def cancel_operation(self, operation_id: str):
        """Cancel a specific operation."""
        if operation_id in self.active_operations:
            thread = self.active_operations[operation_id]
            # Get worker from thread (if accessible)
            for obj in thread.children():
                if isinstance(obj, AsyncWorker):
                    obj.cancel()
                    break
                    
    def _cleanup_operation(self, operation_id: str):
        """Clean up completed operation and start queued ones."""
        if operation_id in self.active_operations:
            del self.active_operations[operation_id]
            
        self.operationFinished.emit(operation_id)
        
        # Start next queued operation
        if self.operation_queue and len(self.active_operations) < self.max_concurrent:
            next_id, next_thread = self.operation_queue.pop(0)
            self.active_operations[next_id] = next_thread
            next_thread.start()


class ErrorDisplayWidget(QWidget):
    """
    User-friendly error display widget with recovery options.
    
    Features:
    - Contextual error messages
    - Recovery action buttons
    - Error details expansion
    - Theme-adaptive styling
    """
    
    retryRequested = pyqtSignal()
    dismissRequested = pyqtSignal()
    
    def __init__(self, error_context: ErrorContext, parent=None):
        super().__init__(parent)
        self.error_context = error_context
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the error display UI."""
        # Implementation would go here
        # This is a placeholder for the UI setup
        pass
        
    @staticmethod
    def show_error_dialog(error_context: ErrorContext, parent=None):
        """Show a modal error dialog."""
        icon_map = {
            ErrorSeverity.INFO: QMessageBox.Icon.Information,
            ErrorSeverity.WARNING: QMessageBox.Icon.Warning,
            ErrorSeverity.ERROR: QMessageBox.Icon.Critical,
            ErrorSeverity.CRITICAL: QMessageBox.Icon.Critical
        }
        
        msg_box = QMessageBox(parent)
        msg_box.setIcon(icon_map.get(error_context.severity, QMessageBox.Icon.Warning))
        msg_box.setWindowTitle(f"{error_context.component} - {error_context.severity.value.title()}")
        msg_box.setText(error_context.user_message)
        
        if error_context.technical_details:
            msg_box.setDetailedText(error_context.technical_details)
            
        if error_context.recovery_action:
            retry_btn = msg_box.addButton("Retry", QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(QMessageBox.StandardButton.Close)
            
            result = msg_box.exec()
            if msg_box.clickedButton() == retry_btn:
                try:
                    error_context.recovery_action()
                except Exception as e:
                    logging.getLogger().error(f"Recovery action failed: {e}")
        else:
            msg_box.exec()


# Example usage and specialized workers

class NetworkWorker(AsyncWorker):
    """Specialized worker for network operations."""
    
    def __init__(self, url: str, operation_name: str = "network_request"):
        super().__init__(operation_name)
        self.component_name = "NetworkWorker"
        self.url = url
        
    def process(self):
        """Implement network request with progress reporting."""
        import requests
        
        self.report_progress(10, "Connecting...")
        
        try:
            response = requests.get(self.url, timeout=30)
            self.report_progress(50, "Downloading...")
            
            response.raise_for_status()
            self.report_progress(100, "Complete")
            
            return response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network request failed: {e}")
