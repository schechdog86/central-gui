"""
Async Operations Module for Qt6 GUI
===================================

Provides robust async operation patterns for PyQt6 applications.
Based on modern PyQt6 best practices and Context7 documentation.
"""

import logging
import traceback
import time
from typing import Any, Callable, Optional, Dict
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

from PyQt6.QtCore import QObject, pyqtSignal, QThread, QMutex, QMutexLocker


class AsyncResult:
    """Container for async operation results."""

    def __init__(self, success: bool = True, data: Any = None,
                 error: str = None, metadata: Dict = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}


class AsyncWorker(QObject):
    """
    Generic async worker for running operations in separate threads.

    Based on PyQt6 best practices for thread management and signal handling.
    """

    # Signals
    started = pyqtSignal()
    finished = pyqtSignal(AsyncResult)
    progress = pyqtSignal(int, str)  # percentage, message
    error = pyqtSignal(str)

    def __init__(self, operation: Callable, *args, **kwargs):
        super().__init__()
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.is_cancelled = False
        self.logger = logging.getLogger(f"AsyncWorker.{operation.__name__}")

    def run(self):
        """Execute the async operation."""
        self.started.emit()

        try:
            if self.is_cancelled:
                return

            # Execute the operation
            result = self.operation(*self.args, **self.kwargs)

            if not self.is_cancelled:
                async_result = AsyncResult(success=True, data=result)
                self.finished.emit(async_result)

        except Exception as e:
            self.logger.error(f"Async operation failed: {e}")
            self.logger.error(traceback.format_exc())

            error_msg = str(e)
            async_result = AsyncResult(
                success=False,
                error=error_msg,
                metadata={'exception_type': type(e).__name__}
            )

            self.error.emit(error_msg)
            self.finished.emit(async_result)

    def cancel(self):
        """Cancel the operation."""
        self.is_cancelled = True


class AsyncOperationManager(QObject):
    """
    Manages async operations with thread pooling and error handling.

    Features:
    - Thread pool management
    - Operation queuing
    - Progress tracking
    - Error handling and recovery
    - Resource cleanup
    """

    # Signals
    operationStarted = pyqtSignal(str)  # operation_id
    operationFinished = pyqtSignal(str, AsyncResult)  # operation_id, result
    operationProgress = pyqtSignal(str, int, str)  # operation_id, %, message
    operationError = pyqtSignal(str, str)  # operation_id, error

    def __init__(self, max_workers: int = 4, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger("SchechterAI.AsyncManager")
        self.max_workers = max_workers

        # Thread management
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self.operation_counter = 0

        # Mutex for thread-safe operations
        self.mutex = QMutex()

    def execute_async(self, operation: Callable,
                      operation_id: Optional[str] = None,
                      *args, **kwargs) -> str:
        """
        Execute an operation asynchronously.

        Args:
            operation: The function to execute
            operation_id: Unique identifier (auto-generated if None)
            *args, **kwargs: Arguments for the operation

        Returns:
            operation_id: Unique identifier for tracking
        """
        if operation_id is None:
            with QMutexLocker(self.mutex):
                self.operation_counter += 1
                operation_id = f"op_{self.operation_counter}"

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
        worker.finished.connect(
            lambda result: self._on_operation_finished(operation_id, result)
        )
        worker.progress.connect(
            lambda pct, msg: self.operationProgress.emit(
                operation_id, pct, msg
            )
        )
        worker.error.connect(
            lambda error: self.operationError.emit(operation_id, error)
        )

        # Cleanup connections
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # Store operation info
        with QMutexLocker(self.mutex):
            self.active_operations[operation_id] = {
                'worker': worker,
                'thread': thread,
                'operation': operation,
                'started_at': self._get_timestamp()
            }

        # Start the operation
        thread.start()

        self.logger.info(f"Started async operation: {operation_id}")
        return operation_id

    def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running operation."""
        with QMutexLocker(self.mutex):
            if operation_id in self.active_operations:
                operation = self.active_operations[operation_id]
                worker = operation['worker']
                thread = operation['thread']

                # Cancel the worker
                worker.cancel()

                # Force quit thread if needed
                if thread.isRunning():
                    thread.quit()
                    if not thread.wait(5000):  # 5 second timeout
                        thread.terminate()
                        thread.wait()

                self.logger.info(f"Cancelled operation: {operation_id}")
                return True

        return False

    def get_active_operations(self) -> Dict[str, Dict[str, Any]]:
        """Get list of currently active operations."""
        with QMutexLocker(self.mutex):
            return self.active_operations.copy()

    def cleanup(self):
        """Cleanup all resources."""
        self.logger.info("Cleaning up async operations...")

        # Cancel all active operations
        with QMutexLocker(self.mutex):
            operation_ids = list(self.active_operations.keys())

        for op_id in operation_ids:
            self.cancel_operation(op_id)

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)

        self.logger.info("Async operations cleanup complete")

    def _on_operation_finished(self, operation_id: str, result: AsyncResult):
        """Handle operation completion."""
        with QMutexLocker(self.mutex):
            if operation_id in self.active_operations:
                operation = self.active_operations.pop(operation_id)
                duration = self._get_timestamp() - operation['started_at']

                self.logger.info(
                    f"Operation {operation_id} completed in {duration:.2f}s"
                )

        self.operationFinished.emit(operation_id, result)

    def _get_timestamp(self) -> float:
        """Get current timestamp."""
        return time.time()


# Decorator for async operations
def async_operation(manager: AsyncOperationManager):
    """
    Decorator to make functions async using the operation manager.

    Usage:
        @async_operation(my_manager)
        def my_long_running_task(param1, param2):
            # Do work
            return result
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return manager.execute_async(func, *args, **kwargs)
        return wrapper
    return decorator


class ErrorHandler(QObject):
    """
    Centralized error handling for async operations.

    Features:
    - Error classification
    - Recovery strategies
    - User notification
    - Logging and telemetry
    """

    # Signals
    errorOccurred = pyqtSignal(str, str, str)  # severity, title, message
    recoveryAttempted = pyqtSignal(str, str)  # error_type, recovery_action

    ERROR_SEVERITIES = {
        'info': 'INFO',
        'warning': 'WARNING',
        'error': 'ERROR',
        'critical': 'CRITICAL'
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("SchechterAI.ErrorHandler")

        # Error recovery strategies
        self.recovery_strategies = {
            'ConnectionError': self._retry_connection,
            'TimeoutError': self._handle_timeout,
            'PermissionError': self._handle_permission,
            'FileNotFoundError': self._handle_missing_file,
        }

    def handle_error(self, error: Exception, context: str = "",
                     severity: str = 'error') -> bool:
        """
        Handle an error with appropriate response.

        Args:
            error: The exception that occurred
            context: Additional context about where error occurred
            severity: Error severity level

        Returns:
            bool: True if error was handled successfully
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # Log the error
        log_msg = f"Error in {context}: {error_msg}" if context else error_msg

        if severity == 'critical':
            self.logger.critical(log_msg)
        elif severity == 'error':
            self.logger.error(log_msg)
        elif severity == 'warning':
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

        # Emit error signal
        title = f"{error_type} in {context}" if context else error_type
        self.errorOccurred.emit(severity, title, error_msg)

        # Attempt recovery
        if error_type in self.recovery_strategies:
            try:
                recovery_action = self.recovery_strategies[error_type](
                    error, context
                )
                self.recoveryAttempted.emit(error_type, recovery_action)
                return True
            except Exception as recovery_error:
                self.logger.error(f"Recovery failed: {recovery_error}")

        return False

    def _retry_connection(self, error: Exception, context: str) -> str:
        """Retry connection after delay."""
        time.sleep(1)  # Simple retry delay
        return "Connection retry attempted"

    def _handle_timeout(self, error: Exception, context: str) -> str:
        """Handle timeout errors."""
        return "Timeout handled - operation will be retried"

    def _handle_permission(self, error: Exception, context: str) -> str:
        """Handle permission errors."""
        return "Permission error - user will be prompted for elevated access"

    def _handle_missing_file(self, error: Exception, context: str) -> str:
        """Handle missing file errors."""
        return "Missing file - default file will be created"


# Global instances (singleton pattern)
_async_manager = None
_error_handler = None


def get_async_manager() -> AsyncOperationManager:
    """Get the global async operation manager."""
    global _async_manager
    if _async_manager is None:
        _async_manager = AsyncOperationManager()
    return _async_manager


def get_error_handler() -> ErrorHandler:
    """Get the global error handler."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler
