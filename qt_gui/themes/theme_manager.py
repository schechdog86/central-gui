"""
Theme Manager for Modern Qt6 UI
===============================

Provides dynamic theming support with dark/light modes and modern styling.
"""

from enum import Enum
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor


class Theme(Enum):
    """Available themes for the application."""
    DARK = "dark"
    LIGHT = "light"
    AUTO = "auto"


class ThemeManager(QObject):
    """
    Manages application theming with modern dark/light mode support.

    Features:
    - Dynamic theme switching
    - Modern color schemes
    - CSS-based styling
    - Automatic system theme detection
    """

    themeChanged = pyqtSignal(str)

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.current_theme = Theme.DARK
        self.themes_dir = Path(__file__).parent / "styles"

        # Modern color schemes
        self.color_schemes = {
            Theme.DARK: {
                'background': '#2b2b2b',
                'surface': '#3c3c3c',
                'primary': '#0078d4',
                'secondary': '#005a9e',
                'accent': '#00bcf2',
                'text': '#ffffff',
                'text_secondary': '#b3b3b3',
                'border': '#555555',
                'success': '#107c10',
                'warning': '#ff8c00',
                'error': '#d13438'
            },
            Theme.LIGHT: {
                'background': '#ffffff',
                'surface': '#f5f5f5',
                'primary': '#0078d4',
                'secondary': '#005a9e',
                'accent': '#00bcf2',
                'text': '#323130',
                'text_secondary': '#605e5c',
                'border': '#e1dfdd',
                'success': '#107c10',
                'warning': '#ff8c00',
                'error': '#d13438'
            }
        }

    def apply_theme(self, theme_name: str):
        """Apply the specified theme to the application."""
        try:
            theme = Theme(theme_name.lower())
        except ValueError:
            theme = Theme.DARK

        self.current_theme = theme

        # Apply palette
        self._apply_palette(theme)

        # Apply stylesheet
        self._apply_stylesheet(theme)

        # Emit signal
        self.themeChanged.emit(theme.value)

    def _apply_palette(self, theme: Theme):
        """Apply color palette for the theme."""
        palette = QPalette()
        colors = self.color_schemes[theme]

        # Set palette colors
        palette.setColor(
            QPalette.ColorRole.Window, QColor(colors['background'])
        )
        palette.setColor(
            QPalette.ColorRole.WindowText, QColor(colors['text'])
        )
        palette.setColor(
            QPalette.ColorRole.Base, QColor(colors['surface'])
        )
        palette.setColor(
            QPalette.ColorRole.AlternateBase, QColor(colors['border'])
        )
        palette.setColor(
            QPalette.ColorRole.ToolTipBase, QColor(colors['surface'])
        )
        palette.setColor(
            QPalette.ColorRole.ToolTipText, QColor(colors['text'])
        )
        palette.setColor(
            QPalette.ColorRole.Text, QColor(colors['text'])
        )
        palette.setColor(
            QPalette.ColorRole.Button, QColor(colors['surface'])
        )
        palette.setColor(
            QPalette.ColorRole.ButtonText, QColor(colors['text'])
        )
        palette.setColor(
            QPalette.ColorRole.BrightText, QColor(colors['accent'])
        )
        palette.setColor(
            QPalette.ColorRole.Link, QColor(colors['primary'])
        )
        palette.setColor(
            QPalette.ColorRole.Highlight, QColor(colors['primary'])
        )
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#ffffff'))

        self.app.setPalette(palette)

    def _apply_stylesheet(self, theme: Theme):
        """Apply CSS stylesheet for the theme."""
        colors = self.color_schemes[theme]

        # Modern stylesheet with Material Design inspiration
        stylesheet = f"""
        /* Main Application Styling */
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}

        /* Sidebar and Navigation */
        QListWidget {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 4px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 12px 16px;
            margin: 2px 0px;
            border-radius: 4px;
            color: {colors['text']};
        }}

        QListWidget::item:hover {{
            background-color: {colors['primary']}20;
        }}

        QListWidget::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
            min-width: 80px;
        }}

        QPushButton:hover {{
            background-color: {colors['secondary']};
        }}

        QPushButton:pressed {{
            background-color: {colors['secondary']};
            transform: translateY(1px);
        }}

        QPushButton:disabled {{
            background-color: {colors['border']};
            color: {colors['text_secondary']};
        }}

        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            border: 2px solid {colors['border']};
            border-radius: 4px;
            padding: 8px 12px;
            color: {colors['text']};
            selection-background-color: {colors['primary']};
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors['primary']};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            background-color: {colors['background']};
        }}

        QTabBar::tab {{
            background-color: {colors['surface']};
            color: {colors['text']};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:hover {{
            background-color: {colors['primary']}20;
        }}

        QTabBar::tab:selected {{
            background-color: {colors['primary']};
            color: white;
        }}

        /* Dock Widgets */
        QDockWidget {{
            titlebar-close-icon: none;
            titlebar-normal-icon: none;
            color: {colors['text']};
        }}

        QDockWidget::title {{
            background-color: {colors['surface']};
            padding: 8px;
            border-bottom: 1px solid {colors['border']};
        }}

        /* Progress Bars */
        QProgressBar {{
            border: 1px solid {colors['border']};
            border-radius: 4px;
            text-align: center;
            background-color: {colors['surface']};
        }}

        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: 3px;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {colors['surface']};
            border-top: 1px solid {colors['border']};
            color: {colors['text']};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border-bottom: 1px solid {colors['border']};
        }}

        QMenuBar::item {{
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenuBar::item:hover {{
            background-color: {colors['primary']}20;
        }}

        QMenu {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 4px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 6px 12px;
            border-radius: 4px;
        }}

        QMenu::item:hover {{
            background-color: {colors['primary']};
            color: white;
        }}

        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {colors['surface']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}

        QScrollBar:horizontal {{
            background-color: {colors['surface']};
            height: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['text_secondary']};
        }}

        /* Splitter */
        QSplitter::handle {{
            background-color: {colors['border']};
        }}

        QSplitter::handle:horizontal {{
            width: 1px;
        }}

        QSplitter::handle:vertical {{
            height: 1px;
        }}
        """

        self.app.setStyleSheet(stylesheet)

    def get_current_theme(self) -> str:
        """Get the name of the current theme."""
        return self.current_theme.value

    def get_color(self, color_name: str) -> str:
        """Get a color value from the current theme."""
        return self.color_schemes[self.current_theme].get(
            color_name, '#000000'
        )

    def is_dark_theme(self) -> bool:
        """Check if the current theme is dark."""
        return self.current_theme == Theme.DARK
