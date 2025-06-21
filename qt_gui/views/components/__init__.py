"""
Components package for Qt6 GUI
==============================

Contains all component views and management classes.
"""

from .component_manager import ComponentManager
from .welcome_view import WelcomeView

__all__ = [
    'ComponentManager',
    'WelcomeView'
]
