#!/usr/bin/env python3
"""
Fixed Qt6 GUI Test
==================

Minimal test with proper error handling and fixed imports.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """Test all imports individually."""
    print("🔍 Testing individual imports...")
    try:
        import PyQt6.QtWidgets  # noqa: F401
        print("✅ PyQt6.QtWidgets imported")
    except Exception as e:
        print(f"❌ PyQt6.QtWidgets failed: {e}")
        return False

    try:
        from src.qt_gui.utils.config_manager import ConfigManager  # noqa: F401
        print("✅ ConfigManager imported")
    except Exception as e:
        print(f"❌ ConfigManager failed: {e}")
        return False

    try:
        from src.qt_gui.themes.theme_manager import ThemeManager  # noqa: F401
        print("✅ ThemeManager imported")
    except Exception as e:
        print(f"❌ ThemeManager failed: {e}")
        return False

    return True


def test_basic_functionality():
    """Test basic Qt6 functionality."""
    print("\n🧪 Testing basic Qt6 functionality...")
    try:
        from PyQt6.QtWidgets import QApplication
        from src.qt_gui.utils.config_manager import ConfigManager
        from src.qt_gui.themes.theme_manager import ThemeManager

        # Create QApplication first
        app = QApplication(sys.argv)
        print("✅ QApplication created")

        # Test ConfigManager
        config = ConfigManager()
        config.set('test', 'value')
        result = config.get('test', 'default')
        print(f"✅ ConfigManager working: {result}")

        # Test ThemeManager (with app instance)
        theme_manager = ThemeManager(app)
        current_theme = theme_manager.get_current_theme()
        print(f"✅ ThemeManager working: {current_theme}")

        print("🎉 All basic tests passed!")
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Fixed Qt6 GUI Test")
    print("=" * 30)

    if not test_imports():
        print("\n❌ Import tests failed")
        sys.exit(1)

    if not test_basic_functionality():
        print("\n❌ Functionality tests failed")
        sys.exit(1)

    print("\n✅ All tests passed! Qt6 GUI framework is working correctly.")
