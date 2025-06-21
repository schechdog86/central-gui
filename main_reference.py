"""
Main entry point for the Schechter Customs LLC Platform.
This module initializes and starts the platform.
"""
import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, messagebox

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """
    Check if all required dependencies are installed.
    
    Returns:
        List of missing dependencies
    """
    missing = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.warning(f"Python version {sys.version_info.major}.{sys.version_info.minor} detected. Version 3.8+ is recommended.")
    
    # Check required packages - always include ray to ensure it's installed
    required_packages = {
        "ray": "ray>=2.0.0",
        "pandas": "pandas>=1.3.0",
        "requests": "requests>=2.25.0",
        "bs4": "beautifulsoup4>=4.9.0",
        "matplotlib": "matplotlib>=3.4.0",
        "numpy": "numpy>=1.20.0"
    }
    
    for package, requirement in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(requirement)
    
    return missing

def install_dependencies(dependencies):
    """
    Install missing dependencies.
    
    Args:
        dependencies: List of package names to install
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import subprocess
        print(f"Installing missing dependencies: {', '.join(dependencies)}")
        
        # Force install required dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install", *dependencies])
        return True
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False

def main():
    """Main entry point for the application."""
    # Check if setup has been completed
    setup_config_path = os.path.join("config", "setup_config.json")
    
    if not os.path.exists(setup_config_path):
        print("Setup configuration not found. Running setup wizard...")
        
        # Import and run the setup wizard
        try:
            from setup.setup_wizard import SetupWizard
            
            # Create root window for setup wizard
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            wizard = SetupWizard()
            wizard.run()
            
            # Check if setup was completed
            if not os.path.exists(setup_config_path):
                print("Setup was not completed. Exiting...")
                sys.exit(0)
                
        except ImportError as e:
            logger.error(f"Error importing setup wizard: {e}")
            print("Setup wizard is not available. Running basic dependency check...")
            
            # Fallback to basic dependency check
            missing_deps = check_dependencies()
            if missing_deps:
                print(f"Missing dependencies: {', '.join(missing_deps)}")
                print("Installing required dependencies automatically...")
                if install_dependencies(missing_deps):
                    print("Dependencies installed successfully.")
                else:
                    print("Failed to install dependencies. Please install them manually.")
                    print(f"Run: pip install {' '.join(missing_deps)}")
                    sys.exit(1)
    
    # Create the data directories
    os.makedirs(os.path.join("config"), exist_ok=True)
    os.makedirs(os.path.join("src", "llm", "templates"), exist_ok=True)
    os.makedirs(os.path.join("src", "llm", "custom_models"), exist_ok=True)
    os.makedirs(os.path.join("logs"), exist_ok=True)
    
    # Import the main GUI here to avoid circular imports
    try:
        from main_gui import MainGUI
    except ImportError as e:
        logger.error(f"Error importing MainGUI: {e}")
        print("Failed to import MainGUI. Make sure all dependencies are installed.")
        sys.exit(1)
    
    # Start the GUI
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
def install_ollama():
    """Install Ollama if not already installed."""
    import platform
    import subprocess
    import os
    import shutil
    
    system = platform.system()
    
    try:
        # Check if Ollama is already installed
        ollama_path = shutil.which("ollama")
        if ollama_path:
            print(f"Ollama already installed at: {ollama_path}")
            return True
            
        print("Ollama not found. Installing...")
        
        if system == "Linux":
            # Install Ollama on Linux
            subprocess.check_call(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"])
            return True
        elif system == "Darwin":  # macOS
            # Show instructions for macOS
            print("Ollama needs to be installed manually on macOS:")
            print("1. Download from: https://ollama.ai/download/mac")
            print("2. Open the downloaded file and drag Ollama to your Applications folder")
            return False
        elif system == "Windows":
            # Show instructions for Windows
            print("Ollama needs to be installed manually on Windows:")
            print("1. Download from: https://ollama.ai/download/windows")
            print("2. Run the installer and follow the instructions")
            return False
        else:
            print(f"Unsupported system: {system}")
            return False
            
    except Exception as e:
        print(f"Error installing Ollama: {e}")
        return False