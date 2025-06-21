"""
Enhanced Error Handling and Async Operations for Qt6 GUI
=======================================================

Modern PyQt6 patterns for robust error handling and async operations.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional
from enum import Enum

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox


class ErrorSeverity(Enum):
    """Error severity levels for categorized handling."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AIComponentError(Exception):
    """Base exception for AI component errors."""

    def __init__(self, message: str,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 component: Optional[str] = None,
                 details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.component = component
        self.details = details or {}


class NetworkError(AIComponentError):
    """Network-related errors."""
    pass


class ConfigurationError(AIComponentError):
    """Configuration-related errors."""
    pass


class ValidationError(AIComponentError):
    """Data validation errors."""
    pass


class ErrorHandler(QObject):
    """
    Centralized error handling with logging and user notification.

    Based on PyQt6 best practices for error management.
    """

    errorOccurred = pyqtSignal(str, str, str)  # severity, component, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("SchechterAI.ErrorHandler")

        # Setup structured logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup structured logging for different error types."""
        # Note: formatter would be used in actual handler setup
        # formatter = logging.Formatter(
        #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        # )

        # Component-specific loggers
        self.component_loggers = {
            'web_scraper': logging.getLogger("SchechterAI.WebScraper"),
            'browser': logging.getLogger("SchechterAI.Browser"),
            'coding_agent': logging.getLogger("SchechterAI.CodingAgent"),
            'workspace': logging.getLogger("SchechterAI.Workspace"),
            'mcp': logging.getLogger("SchechterAI.MCP")
        }

    def handle_error(self, error: Exception,
                     component: str = "Unknown",
                     show_user: bool = True) -> None:
        """
        Handle errors with appropriate logging and user notification.

        Args:
            error: The exception that occurred
            component: Component where error occurred
            show_user: Whether to show user-facing notification
        """
        if isinstance(error, AIComponentError):
            severity = error.severity
            message = error.message
            details = error.details
        else:
            severity = ErrorSeverity.ERROR
            message = str(error)
            details = {"traceback": traceback.format_exc()}

        # Log the error
        self._log_error(severity, component, message, details)

        # Emit signal for UI handling
        self.errorOccurred.emit(severity.value, component, message)

        # Show user notification if requested
        if show_user:
            self._show_user_notification(severity, component, message)

    def _log_error(self, severity: ErrorSeverity,
                   component: str,
                   message: str,
                   details: Dict) -> None:
        """Log error with appropriate level and context."""
        logger = self.component_loggers.get(component, self.logger)

        log_message = f"[{component}] {message}"
        if details:
            log_message += f" | Details: {details}"

        if severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)

    def _show_user_notification(self,
                                severity: ErrorSeverity,
                                component: str,
                                message: str) -> None:
        """Show user-friendly error notification."""
        if severity in [ErrorSeverity.INFO, ErrorSeverity.WARNING]:
            return  # Don't show notifications for info/warning

        title = f"{component} Error"

        if severity == ErrorSeverity.CRITICAL:
            QMessageBox.critical(None, title, message)
        else:
            QMessageBox.warning(None, title, message)


class AsyncWorker(QObject):
    """
    Generic async worker for long-running operations.

    Based on PyQt6 best practices for threading.
    """

    # Signals
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    progress = pyqtSignal(int)  # Progress percentage
    result = pyqtSignal(object)  # Operation result

    def __init__(self, operation: Callable, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.is_cancelled = False

    def run(self):
        """Execute the operation in worker thread."""
        try:
            self.started.emit()

            # Execute the operation
            result = self.operation(*self.args, **self.kwargs)

            if not self.is_cancelled:
                self.result.emit(result)

        except Exception as e:
            if not self.is_cancelled:
                self.error.emit(e)
        finally:
            self.finished.emit()

    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True


class AsyncOperationManager(QObject):
    """
    Manages async operations with proper thread handling.

    Features:
    - Automatic thread management
    - Progress tracking
    - Error handling
    - Operation cancellation
    """

    operationStarted = pyqtSignal(str)  # operation_id
    operationFinished = pyqtSignal(str)  # operation_id
    operationError = pyqtSignal(str, Exception)  # operation_id, error
    operationProgress = pyqtSignal(str, int)  # operation_id, progress

    def __init__(self, error_handler: ErrorHandler, parent=None):
        super().__init__(parent)
        self.error_handler = error_handler
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.operation_counter = 0

    def start_operation(self,
                        operation: Callable,
                        operation_name: str,
                        *args, **kwargs) -> str:
        """
        Start an async operation.

        Args:
            operation: The function to execute
            operation_name: Human-readable operation name
            *args, **kwargs: Arguments for the operation

        Returns:
            operation_id: Unique identifier for tracking
        """
        operation_id = f"{operation_name}_{self.operation_counter}"
        self.operation_counter += 1

        # Create worker and thread
        worker = AsyncWorker(operation, *args, **kwargs)
        thread = QThread()

        # Move worker to thread
        worker.moveToThread(thread)

        # Connect signals
        thread.started.connect(worker.run)
        worker.started.connect(
            lambda: self.operationStarted.emit(operation_id)
        )
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(
            lambda: self.operationFinished.emit(operation_id)
        )
        worker.error.connect(
            lambda e: self.operationError.emit(operation_id, e)
        )
        worker.progress.connect(
            lambda p: self.operationProgress.emit(operation_id, p)
        )
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(
            lambda: self._cleanup_operation(operation_id)
        )

        # Store operation info
        self.active_operations[operation_id] = {
            'worker': worker,
            'thread': thread,
            'name': operation_name
        }

        # Start the operation
        thread.start()

        return operation_id

    def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel an active operation.

        Args:
            operation_id: The operation to cancel

        Returns:
            bool: True if operation was cancelled, False if not found
        """
        if operation_id in self.active_operations:
            worker = self.active_operations[operation_id]['worker']
            worker.cancel()
            return True
        return False

    def _cleanup_operation(self, operation_id: str):
        """Clean up finished operation."""
        if operation_id in self.active_operations:
            del self.active_operations[operation_id]

    def get_active_operations(self) -> Dict[str, str]:
        """Get list of active operations."""
        return {
            op_id: info['name']
            for op_id, info in self.active_operations.items()
        }


class RetryManager(QObject):
    """
    Manages retry logic for failed operations.

    Features:
    - Exponential backoff
    - Maximum retry limits
    - Retry condition checking
    """

    retryAttempted = pyqtSignal(str, int)  # operation_name, attempt_number
    retryExhausted = pyqtSignal(str)  # operation_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.retry_configs: Dict[str, Dict] = {}

    def configure_retry(self,
                        operation_name: str,
                        max_retries: int = 3,
                        base_delay: float = 1.0,
                        max_delay: float = 60.0,
                        retry_condition: Optional[Callable[[Exception], bool]] = None):
        """
        Configure retry parameters for an operation.

        Args:
            operation_name: Name of the operation
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            retry_condition: Function to check if retry should be attempted
        """
        self.retry_configs[operation_name] = {
            'max_retries': max_retries,
            'base_delay': base_delay,
            'max_delay': max_delay,
            'retry_condition': (retry_condition or
                                self._default_retry_condition)
        }

    def should_retry(self,
                     operation_name: str,
                     error: Exception,
                     attempt: int) -> bool:
        """
        Check if operation should be retried.

        Args:
            operation_name: Name of the operation
            error: The error that occurred
            attempt: Current attempt number (0-based)

        Returns:
            bool: True if should retry, False otherwise
        """
        config = self.retry_configs.get(operation_name, {})
        max_retries = config.get('max_retries', 0)
        retry_condition = config.get('retry_condition',
                                     self._default_retry_condition)

        if attempt >= max_retries:
            self.retryExhausted.emit(operation_name)
            return False

        if not retry_condition(error):
            return False

        self.retryAttempted.emit(operation_name, attempt + 1)
        return True

    def get_retry_delay(self, operation_name: str, attempt: int) -> float:
        """
        Calculate retry delay using exponential backoff.

        Args:
            operation_name: Name of the operation
            attempt: Current attempt number (0-based)

        Returns:
            float: Delay in seconds
        """
        config = self.retry_configs.get(operation_name, {})
        base_delay = config.get('base_delay', 1.0)
        max_delay = config.get('max_delay', 60.0)

        delay = base_delay * (2 ** attempt)
        return min(delay, max_delay)

    def _default_retry_condition(self, error: Exception) -> bool:
        """Default retry condition - retry on network errors."""
        return isinstance(error, (NetworkError, ConnectionError, TimeoutError))


# Decorator for automatic error handling
def handle_errors(component: str = "Unknown",
                  show_user: bool = True,
                  error_handler: Optional[ErrorHandler] = None):
    """
    Decorator for automatic error handling in component methods.

    Args:
        component: Component name for error context
        show_user: Whether to show user notifications
        error_handler: ErrorHandler instance to use
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_handler:
                    error_handler.handle_error(e, component, show_user)
                else:
                    # Fallback to basic logging
                    logging.getLogger(f"SchechterAI.{component}").error(
                        f"Error in {func.__name__}: {e}"
                    )
                raise
        return wrapper
    return decorator
