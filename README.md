# Central GUI - PyQt6 AI Platform Interface

A modern, centralized GUI framework for AI-powered business intelligence and automation tools built with PyQt6.

## 🚀 Features

- **Modern PyQt6 Architecture**: Clean MVVM design pattern with proper separation of concerns
- **Component-Based Design**: Modular components for different AI tools and services
- **Async Operations**: Non-blocking UI with proper async/await patterns
- **Theme Support**: Light/dark mode with dynamic theming
- **Error Handling**: Comprehensive error handling and logging
- **Testing Framework**: Full test coverage with pytest and pytest-qt

## 📋 Core Components

### GUI Framework (`qt_gui/`)
- **Main Application**: Entry point and application lifecycle management
- **Views**: User interface components and layouts
- **View Models**: Business logic and data management
- **Themes**: Dynamic theming system
- **Utils**: Configuration, logging, and async operations

### Integrated Tools (`src/core_components/`)
- **Web Scraper**: Advanced data extraction capabilities
- **Anonymous Browser**: Secure business intelligence gathering
- **Coding Agent**: AI-powered code generation and analysis
- **Workspace Tracker**: Project management and tracking
- **MCP Integration**: Model Context Protocol support

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- PyQt6
- Git

### Quick Start
```bash
# Clone the repository
git clone https://github.com/schechdog86/central-gui.git
cd central-gui

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-qt black flake8 mypy

# Run tests
python -m pytest tests/

# Run the application in development mode
python main.py --debug
```

## 🏗️ Architecture

### MVVM Pattern
```
Views (UI) ↔ ViewModels (Business Logic) ↔ Models (Data)
```

### Component Structure
```
central-gui/
├── main.py                 # Application entry point
├── qt_gui/                 # Core GUI framework
│   ├── main_application.py # Main application class
│   ├── views/              # UI components
│   ├── view_models/        # Business logic
│   ├── themes/             # Theming system
│   └── utils/              # Utilities and helpers
├── src/core_components/    # Integrated AI tools
│   ├── web_scraper/        # Web scraping component
│   ├── anonymous_browser/  # Browser automation
│   ├── coding_agent/       # AI coding assistant
│   ├── workspace_tracker/  # Project management
│   └── mcp_integration/    # MCP protocol support
└── tests/                  # Test suite
```

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python tests/fixed_qt_test.py
python tests/comprehensive_test_framework.py

# Run with coverage
python -m pytest tests/ --cov=qt_gui --cov-report=html
```

## 🎨 Theming

The application supports dynamic theming:

```python
from qt_gui.themes.theme_manager import ThemeManager

# Switch themes
theme_manager.set_theme('dark')
theme_manager.set_theme('light')
```

## 🔧 Configuration

Configuration is managed through the `ConfigManager`:

```python
from qt_gui.utils.config_manager import ConfigManager

config = ConfigManager()
config.set('app.theme', 'dark')
config.set('web_scraper.timeout', 30)
```

## 📚 Documentation

- **Architecture Guide**: [docs/architecture.md](docs/architecture.md)
- **Component Development**: [docs/components.md](docs/components.md)
- **API Reference**: [docs/api.md](docs/api.md)
- **Testing Guide**: [docs/testing.md](docs/testing.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document all public APIs
- Use type hints throughout
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Plugin system for external components
- [ ] WebSocket support for real-time updates
- [ ] REST API for headless operation
- [ ] Docker containerization
- [ ] CI/CD pipeline integration
- [ ] Performance monitoring and analytics

## 🏢 About Schechter Customs LLC

Central GUI is developed by Schechter Customs LLC as part of our AI-powered business intelligence platform suite.

---

**Repository**: https://github.com/schechdog86/central-gui
**Issues**: https://github.com/schechdog86/central-gui/issues
**Discussions**: https://github.com/schechdog86/central-gui/discussions