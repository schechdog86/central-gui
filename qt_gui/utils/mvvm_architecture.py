"""
Enhanced MVVM Architecture for Qt6 GUI
=====================================

Modern PyQt6 MVVM implementation with proper separation of concerns.
Based on PyQt Fluent Widgets patterns and Qt6 best practices.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable
from enum import Enum

from PyQt6.QtCore import (QObject, pyqtSignal, QAbstractItemModel,
                          QModelIndex, Qt)
from PyQt6.QtWidgets import QWidget

from .async_error_handling import (ErrorHandler, AsyncOperationManager,
                                   ConfigurationError)


class ViewModelState(Enum):
    """ViewModel state enumeration."""
    IDLE = "idle"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"


class BaseViewModel(QObject):
    """
    Base ViewModel with common functionality.
    
    Features:
    - State management
    - Property change notifications
    - Command pattern implementation
    - Async operation support
    """
    
    # Common signals
    stateChanged = pyqtSignal(str)  # state
    propertyChanged = pyqtSignal(str, object)  # property_name, new_value
    errorOccurred = pyqtSignal(str)  # error_message
    operationStarted = pyqtSignal(str)  # operation_name
    operationCompleted = pyqtSignal(str, object)  # operation_name, result
    
    def __init__(self, error_handler: ErrorHandler,
                 async_manager: AsyncOperationManager, parent=None):
        super().__init__(parent)
        
        self.error_handler = error_handler
        self.async_manager = async_manager
        self.logger = logging.getLogger(f"SchechterAI.{self.__class__.__name__}")
        
        # State management
        self._state = ViewModelState.IDLE
        self._properties: Dict[str, Any] = {}
        self._commands: Dict[str, Callable] = {}
        
        # Connect async manager signals
        self.async_manager.operationStarted.connect(self._on_operation_started)
        self.async_manager.operationFinished.connect(self._on_operation_finished)
        self.async_manager.operationError.connect(self._on_operation_error)
    
    @property
    def state(self) -> ViewModelState:
        """Get current state."""
        return self._state
    
    @state.setter
    def state(self, value: ViewModelState):
        """Set state with notification."""
        if self._state != value:
            self._state = value
            self.stateChanged.emit(value.value)
            self.logger.debug(f"State changed to: {value.value}")
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Get property value."""
        return self._properties.get(name, default)
    
    def set_property(self, name: str, value: Any, notify: bool = True):
        """Set property with optional notification."""
        old_value = self._properties.get(name)
        if old_value != value:
            self._properties[name] = value
            if notify:
                self.propertyChanged.emit(name, value)
                self.logger.debug(f"Property '{name}' changed: {old_value} -> {value}")
    
    def register_command(self, name: str, command: Callable):
        """Register a command."""
        self._commands[name] = command
        self.logger.debug(f"Command '{name}' registered")
    
    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """Execute a registered command."""
        if name in self._commands:
            try:
                self.logger.debug(f"Executing command: {name}")
                return self._commands[name](*args, **kwargs)
            except Exception as e:
                self.error_handler.handle_error(e, self.__class__.__name__)
                self.errorOccurred.emit(str(e))
        else:
            error_msg = f"Command '{name}' not found"
            self.logger.error(error_msg)
            self.errorOccurred.emit(error_msg)
    
    def start_async_operation(self, operation: Callable, operation_name: str,
                            *args, **kwargs) -> str:
        """Start an async operation."""
        self.state = ViewModelState.LOADING
        return self.async_manager.start_operation(
            operation, operation_name, *args, **kwargs
        )
    
    def _on_operation_started(self, operation_id: str):
        """Handle operation started."""
        self.operationStarted.emit(operation_id)
    
    def _on_operation_finished(self, operation_id: str):
        """Handle operation finished."""
        self.state = ViewModelState.READY
        self.operationCompleted.emit(operation_id, None)
    
    def _on_operation_error(self, operation_id: str, error: Exception):
        """Handle operation error."""
        self.state = ViewModelState.ERROR
        self.error_handler.handle_error(error, self.__class__.__name__)


class BaseView(QWidget):
    """
    Base View with ViewModel integration.
    
    Features:
    - ViewModel binding
    - Automatic property updates
    - Command execution
    - State-based UI updates
    """
    
    def __init__(self, view_model: BaseViewModel, parent=None):
        super().__init__(parent)
        
        self.view_model = view_model
        self.logger = logging.getLogger(f"SchechterAI.{self.__class__.__name__}")
        
        # Property bindings
        self._property_bindings: Dict[str, Callable] = {}
        
        # Connect ViewModel signals
        self.view_model.stateChanged.connect(self._on_state_changed)
        self.view_model.propertyChanged.connect(self._on_property_changed)
        self.view_model.errorOccurred.connect(self._on_error_occurred)
        
        # Initialize UI
        self.setup_ui()
        self.bind_properties()
        self.connect_commands()
    
    @abstractmethod
    def setup_ui(self):
        """Setup the UI components. Must be implemented by subclasses."""
        pass
    
    def bind_properties(self):
        """
        Bind ViewModel properties to UI elements.
        Override in subclasses to define specific bindings.
        """
        pass
    
    def connect_commands(self):
        """
        Connect UI elements to ViewModel commands.
        Override in subclasses to define specific connections.
        """
        pass
    
    def bind_property(self, property_name: str, update_callback: Callable):
        """
        Bind a ViewModel property to a UI update callback.
        
        Args:
            property_name: Name of the ViewModel property
            update_callback: Function to call when property changes
        """
        self._property_bindings[property_name] = update_callback
        
        # Initial update
        current_value = self.view_model.get_property(property_name)
        if current_value is not None:
            update_callback(current_value)
    
    def execute_command(self, command_name: str, *args, **kwargs):
        """Execute a ViewModel command."""
        self.view_model.execute_command(command_name, *args, **kwargs)
    
    def _on_state_changed(self, state: str):
        """Handle ViewModel state change."""
        self.logger.debug(f"ViewModel state changed to: {state}")
        self.update_ui_for_state(ViewModelState(state))
    
    def _on_property_changed(self, property_name: str, new_value: Any):
        """Handle ViewModel property change."""
        if property_name in self._property_bindings:
            self._property_bindings[property_name](new_value)
    
    def _on_error_occurred(self, error_message: str):
        """Handle ViewModel error."""
        self.logger.error(f"ViewModel error: {error_message}")
        self.show_error(error_message)
    
    def update_ui_for_state(self, state: ViewModelState):
        """
        Update UI based on ViewModel state.
        Override in subclasses for specific state handling.
        """
        # Default implementation - can be overridden
        if state == ViewModelState.LOADING:
            self.setEnabled(False)
        else:
            self.setEnabled(True)
    
    def show_error(self, message: str):
        """
        Show error message to user.
        Override in subclasses for custom error display.
        """
        self.logger.error(f"Showing error to user: {message}")


class ComponentListModel(QAbstractItemModel):
    """
    Model for displaying AI components in list/tree views.
    
    Features:
    - Dynamic component loading
    - Status updates
    - Hierarchical display support
    """
    
    def __init__(self, components: List[Dict], parent=None):
        super().__init__(parent)
        self._components = components
        self._headers = ["Name", "Status", "Description"]
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of rows."""
        if not parent.isValid():
            return len(self._components)
        return 0
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns."""
        return len(self._headers)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Return data for given index and role."""
        if not index.isValid() or index.row() >= len(self._components):
            return None
        
        component = self._components[index.row()]
        column = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return component.get('name', 'Unknown')
            elif column == 1:
                return component.get('status', 'Unknown')
            elif column == 2:
                return component.get('description', 'No description')
        
        elif role == Qt.ItemDataRole.UserRole:
            return component
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                  role: int = Qt.ItemDataRole.DisplayRole):
        """Return header data."""
        if (orientation == Qt.Orientation.Horizontal and 
            role == Qt.ItemDataRole.DisplayRole and 
            section < len(self._headers)):
            return self._headers[section]
        return None
    
    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Create index for given row and column."""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column, None)
    
    def parent(self, index: QModelIndex) -> QModelIndex:
        """Return parent index (flat list, so always invalid)."""
        return QModelIndex()
    
    def update_component_status(self, component_name: str, status: str):
        """Update status of a specific component."""
        for i, component in enumerate(self._components):
            if component.get('name') == component_name:
                component['status'] = status
                # Emit data changed signal
                top_left = self.index(i, 1)
                bottom_right = self.index(i, 1)
                self.dataChanged.emit(top_left, bottom_right)
                break
    
    def add_component(self, component: Dict):
        """Add a new component to the model."""
        row = len(self._components)
        self.beginInsertRows(QModelIndex(), row, row)
        self._components.append(component)
        self.endInsertRows()
    
    def remove_component(self, component_name: str):
        """Remove a component from the model."""
        for i, component in enumerate(self._components):
            if component.get('name') == component_name:
                self.beginRemoveRows(QModelIndex(), i, i)
                del self._components[i]
                self.endRemoveRows()
                break


class ConfigurableComponent(ABC):
    """
    Abstract base for configurable components.
    
    Features:
    - Configuration validation
    - Runtime reconfiguration
    - Configuration persistence
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate component configuration."""
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema for configuration validation."""
        pass
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update configuration with validation."""
        old_config = self.config.copy()
        self.config.update(new_config)
        
        try:
            self._validate_config()
        except Exception as e:
            # Rollback on validation failure
            self.config = old_config
            raise ConfigurationError(
                f"Configuration validation failed: {e}",
                component=self.__class__.__name__
            )
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()


# Factory pattern for creating ViewModels
class ViewModelFactory:
    """
    Factory for creating ViewModels with proper dependencies.
    """
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, view_model_class: type):
        """Register a ViewModel class."""
        cls._registry[name] = view_model_class
    
    @classmethod
    def create(cls, name: str, error_handler: ErrorHandler,
              async_manager: AsyncOperationManager, **kwargs) -> BaseViewModel:
        """Create a ViewModel instance."""
        if name not in cls._registry:
            raise ValueError(f"ViewModel '{name}' not registered")
        
        view_model_class = cls._registry[name]
        return view_model_class(error_handler, async_manager, **kwargs)
    
    @classmethod
    def get_registered(cls) -> List[str]:
        """Get list of registered ViewModel names."""
        return list(cls._registry.keys())
