#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Centralized AI UI
Tests all components and dependencies
"""
import sys
import os
import subprocess
import importlib
import json
from pathlib import Path
from datetime import datetime
import traceback

class ComprehensiveTestFramework:
    """Complete testing framework for the AI platform"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'platform': sys.platform,
            'python_version': sys.version,
            'tests': {}
        }
        
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("Schechter Customs LLC - Comprehensive Platform Test")
        print("=" * 60)
        
        # Test categories
        self.test_python_dependencies()
        self.test_tkinter_components()
        self.test_component_modules()
        self.test_external_dependencies()
        self.test_file_structure()
        self.test_async_operations()
        self.test_ui_components()
        
        # Generate report
        self.generate_report()
        
    def test_python_dependencies(self):
        """Test Python package dependencies"""
        print("\n🔍 Testing Python Dependencies...")
        
        packages = {
            'core': ['os', 'sys', 'pathlib', 'subprocess', 'json', 'threading'],
            'ui': ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.scrolledtext'],
            'web': ['urllib.request', 'urllib.parse', 'http.server'],
            'optional': ['requests', 'aiohttp', 'asyncio', 'ray', 'ollama', 'bs4']
        }
        
        results = {}
        
        for category, modules in packages.items():
            print(f"\n  {category.upper()} Packages:")
            results[category] = {}
            
            for module in modules:
                try:
                    if '.' in module:
                        # Handle submodules
                        parts = module.split('.')
                        parent = importlib.import_module(parts[0])
                        for part in parts[1:]:
                            parent = getattr(parent, part)
                    else:
                        importlib.import_module(module)
                    
                    results[category][module] = {'status': 'available'}
                    print(f"    ✅ {module}")
                except ImportError as e:
                    results[category][module] = {'status': 'missing', 'error': str(e)}
                    print(f"    ❌ {module} - {e}")
                except Exception as e:
                    results[category][module] = {'status': 'error', 'error': str(e)}
                    print(f"    ⚠️  {module} - Error: {e}")
                    
        self.results['tests']['python_dependencies'] = results
        
    def test_tkinter_components(self):
        """Test Tkinter GUI components"""
        print("\n🖼️  Testing Tkinter Components...")
        
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox, scrolledtext, filedialog
            
            # Create test window
            root = tk.Tk()
            root.withdraw()  # Hide window
            
            components = {
                'Frame': ttk.Frame(root),
                'Label': ttk.Label(root, text="Test"),
                'Button': ttk.Button(root, text="Test"),
                'Entry': ttk.Entry(root),
                'Combobox': ttk.Combobox(root),
                'Notebook': ttk.Notebook(root),
                'Treeview': ttk.Treeview(root),
                'ScrolledText': scrolledtext.ScrolledText(root),
                'Style': ttk.Style()
            }
            
            results = {}
            for name, widget in components.items():
                try:
                    # Test widget creation
                    if hasattr(widget, 'pack'):
                        widget.pack()
                    results[name] = 'working'
                    print(f"    ✅ {name}")
                except Exception as e:
                    results[name] = f'error: {str(e)}'
                    print(f"    ❌ {name} - {e}")
                    
            root.destroy()
            
            self.results['tests']['tkinter_components'] = results
            
        except Exception as e:
            print(f"    ❌ Tkinter not available: {e}")
            self.results['tests']['tkinter_components'] = {'error': str(e)}
            
    def test_component_modules(self):
        """Test platform component modules"""
        print("\n📦 Testing Component Modules...")
        
        components = {
            'anonymous_browser': self.base_dir / 'anonymous_browser',
            'coding_agent': self.base_dir / 'coding-agent',
            'mcp_tool': self.base_dir / 'mcp-integration-tool',
            'workspace_tracker': self.base_dir / 'workspacetracker',
            'web_scraper': self.base_dir / 'src' / 'web_scraper',
            'ollama_integration': self.base_dir / 'src' / 'ollama'
        }
        
        results = {}
        
        for name, path in components.items():
            print(f"\n  Testing {name}:")
            results[name] = {}
            
            # Check if path exists
            if path.exists():
                results[name]['exists'] = True
                print(f"    ✅ Directory exists")
                
                # Check for key files
                key_files = {
                    'anonymous_browser': ['launcher.py', 'demo.py'],
                    'coding_agent': ['src/main.py', 'requirements.txt'],
                    'mcp_tool': ['run.py', 'src/main.py'],
                    'workspace_tracker': ['main.py', '__init__.py'],
                    'web_scraper': ['__init__.py', 'scraper_manager.py'],
                    'ollama_integration': ['__init__.py', 'ollama_manager.py']
                }
                
                if name in key_files:
                    for file in key_files[name]:
                        file_path = path / file
                        if file_path.exists():
                            print(f"    ✅ {file}")
                            results[name][file] = 'exists'
                        else:
                            print(f"    ❌ {file} missing")
                            results[name][file] = 'missing'
            else:
                results[name]['exists'] = False
                print(f"    ❌ Directory not found")
                
        self.results['tests']['component_modules'] = results
        
    def test_external_dependencies(self):
        """Test external dependencies"""
        print("\n🔧 Testing External Dependencies...")
        
        # Test pip packages
        print("\n  Checking pip packages:")
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=json'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                installed_packages = json.loads(result.stdout)
                package_dict = {pkg['name'].lower(): pkg['version'] for pkg in installed_packages}
                
                required_packages = [
                    'requests', 'aiohttp', 'asyncio-mqtt', 'ray', 'ollama',
                    'beautifulsoup4', 'selenium', 'PyQt6', 'PyQt6-WebEngine'
                ]
                
                results = {}
                for pkg in required_packages:
                    if pkg.lower() in package_dict:
                        version = package_dict[pkg.lower()]
                        results[pkg] = {'status': 'installed', 'version': version}
                        print(f"    ✅ {pkg} ({version})")
                    else:
                        results[pkg] = {'status': 'not installed'}
                        print(f"    ❌ {pkg} - Not installed")
                        
                self.results['tests']['pip_packages'] = results
            else:
                print(f"    ❌ Could not get pip list: {result.stderr}")
                self.results['tests']['pip_packages'] = {'error': result.stderr}
                
        except Exception as e:
            print(f"    ❌ Error checking pip: {e}")
            self.results['tests']['pip_packages'] = {'error': str(e)}
            
        # Test system commands
        print("\n  Checking system commands:")
        commands = {
            'git': ['git', '--version'],
            'node': ['node', '--version'],
            'npm': ['npm', '--version'],
            'docker': ['docker', '--version'],
            'ollama': ['ollama', '--version']
        }
        
        cmd_results = {}
        for name, cmd in commands.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    cmd_results[name] = {'status': 'available', 'version': version}
                    print(f"    ✅ {name}: {version}")
                else:
                    cmd_results[name] = {'status': 'not found'}
                    print(f"    ❌ {name} - Not found")
            except FileNotFoundError:
                cmd_results[name] = {'status': 'not found'}
                print(f"    ❌ {name} - Not found")
            except Exception as e:
                cmd_results[name] = {'status': 'error', 'error': str(e)}
                print(f"    ⚠️  {name} - Error: {e}")
                
        self.results['tests']['system_commands'] = cmd_results
        
    def test_file_structure(self):
        """Test file structure integrity"""
        print("\n📁 Testing File Structure...")
        
        required_dirs = [
            'src', 'src/ui', 'src/llm', 'src/setup', 'src/utils',
            'config', 'docs', 'tests', 'static', 'templates'
        ]
        
        required_files = [
            'requirements.txt', 'README.md', 'launch.py',
            'src/main.py', 'src/main_gui.py'
        ]
        
        results = {'directories': {}, 'files': {}}
        
        print("\n  Required directories:")
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            if full_path.exists() and full_path.is_dir():
                results['directories'][dir_path] = 'exists'
                print(f"    ✅ {dir_path}/")
            else:
                results['directories'][dir_path] = 'missing'
                print(f"    ❌ {dir_path}/ - Missing")
                
        print("\n  Required files:")
        for file_path in required_files:
            full_path = self.base_dir / file_path
            if full_path.exists() and full_path.is_file():
                results['files'][file_path] = 'exists'
                print(f"    ✅ {file_path}")
            else:
                results['files'][file_path] = 'missing'
                print(f"    ❌ {file_path} - Missing")
                
        self.results['tests']['file_structure'] = results
        
    def test_async_operations(self):
        """Test async operations module"""
        print("\n⚡ Testing Async Operations...")
        
        try:
            from async_operations import AsyncOperationManager, get_default_manager
            
            manager = get_default_manager()
            
            # Test subprocess operation
            op_id = manager.submit_operation({
                'type': 'subprocess',
                'command': [sys.executable, '-c', 'print("Test")']
            })
            
            result = manager.get_result(op_id, timeout=5)
            
            if result and result['status'] == 'completed':
                print("    ✅ Async subprocess operations working")
                self.results['tests']['async_operations'] = {'status': 'working'}
            else:
                print("    ❌ Async operations failed")
                self.results['tests']['async_operations'] = {'status': 'failed', 'result': result}
                
        except ImportError as e:
            print(f"    ❌ Could not import async_operations: {e}")
            self.results['tests']['async_operations'] = {'status': 'import_error', 'error': str(e)}
        except Exception as e:
            print(f"    ❌ Error testing async operations: {e}")
            self.results['tests']['async_operations'] = {'status': 'error', 'error': str(e)}
            
    def test_ui_components(self):
        """Test UI component imports"""
        print("\n🎨 Testing UI Components...")
        
        ui_modules = [
            'src.ui.complete_anonymous_browser_tab',
            'src.ui.complete_coding_agent_tab',
            'src.ui.complete_mcp_tools_tab',
            'src.ui.complete_workspace_tracker_tab',
            'src.ui.enhanced_ai_components_tab'
        ]
        
        results = {}
        
        for module in ui_modules:
            try:
                importlib.import_module(module)
                results[module] = 'available'
                print(f"    ✅ {module}")
            except ImportError as e:
                results[module] = f'missing: {str(e)}'
                print(f"    ❌ {module} - {e}")
            except Exception as e:
                results[module] = f'error: {str(e)}'
                print(f"    ⚠️  {module} - Error: {e}")
                
        self.results['tests']['ui_components'] = results
        
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT SUMMARY")
        print("=" * 60)
        
        # Count results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, tests in self.results['tests'].items():
            if isinstance(tests, dict) and 'error' not in tests:
                for test, result in tests.items():
                    total_tests += 1
                    if isinstance(result, dict):
                        if result.get('status') in ['available', 'installed', 'working']:
                            passed_tests += 1
                        else:
                            failed_tests += 1
                    elif result in ['exists', 'available', 'working']:
                        passed_tests += 1
                    else:
                        failed_tests += 1
                        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save report
        report_path = self.base_dir / 'test_report.json'
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        print(f"\nDetailed report saved to: {report_path}")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        
        # Check for missing critical dependencies
        if 'pip_packages' in self.results['tests']:
            missing_packages = []
            for pkg, info in self.results['tests']['pip_packages'].items():
                if isinstance(info, dict) and info.get('status') == 'not installed':
                    missing_packages.append(pkg)
                    
            if missing_packages:
                print(f"\n1. Install missing packages:")
                print(f"   pip install {' '.join(missing_packages)}")
                
        # Check for missing components
        if 'component_modules' in self.results['tests']:
            missing_components = []
            for comp, info in self.results['tests']['component_modules'].items():
                if not info.get('exists'):
                    missing_components.append(comp)
                    
            if missing_components:
                print(f"\n2. Missing components: {', '.join(missing_components)}")
                print("   Run setup scripts or clone missing repositories")
                
        print("\n" + "=" * 60)


def main():
    """Run comprehensive tests"""
    framework = ComprehensiveTestFramework()
    
    try:
        framework.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        traceback.print_exc()
        

if __name__ == "__main__":
    main()