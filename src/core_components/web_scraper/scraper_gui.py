"""
Web Scraper GUI Components
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import Optional, Dict, Any
import threading

class WebScraperGUI:
    """GUI for web scraper functionality"""
    
    def __init__(self, parent: tk.Widget, scraper_manager):
        """Initialize the web scraper GUI"""
        self.parent = parent
        self.scraper_manager = scraper_manager
        self.current_task = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ttk.Label(main_frame, text="Web Scraper", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Single URL tab
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text="Single URL")
        self._create_single_url_tab()
        
        # Bulk URLs tab
        self.bulk_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.bulk_tab, text="Bulk URLs")
        self._create_bulk_urls_tab()
        
        # History tab
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="History")
        self._create_history_tab()
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self._create_settings_tab()    
    def _create_single_url_tab(self):
        """Create the single URL scraping tab"""
        # URL input
        url_frame = ttk.Frame(self.single_tab)
        url_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT, padx=(0, 5))
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.scrape_button = ttk.Button(url_frame, text="Scrape", command=self._scrape_single_url)
        self.scrape_button.pack(side=tk.LEFT)
        
        # Selectors frame
        selectors_frame = ttk.LabelFrame(self.single_tab, text="CSS Selectors (Optional)")
        selectors_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Selector inputs
        self.selectors = {}
        selector_fields = ["title", "price", "description", "image", "custom"]
        
        for i, field in enumerate(selector_fields):
            row_frame = ttk.Frame(selectors_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(row_frame, text=f"{field.capitalize()}:", width=12).pack(side=tk.LEFT)
            entry = ttk.Entry(row_frame, width=40)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.selectors[field] = entry
        
        # Results area
        results_frame = ttk.LabelFrame(self.single_tab, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Export button
        export_frame = ttk.Frame(self.single_tab)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export JSON", 
                  command=lambda: self._export_results("json")).pack(side=tk.RIGHT, padx=2)
        ttk.Button(export_frame, text="Export CSV", 
                  command=lambda: self._export_results("csv")).pack(side=tk.RIGHT, padx=2)    
    def _create_bulk_urls_tab(self):
        """Create the bulk URLs scraping tab"""
        # URLs text area
        urls_frame = ttk.LabelFrame(self.bulk_tab, text="URLs (one per line)")
        urls_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.bulk_urls_text = scrolledtext.ScrolledText(urls_frame, height=10, width=60)
        self.bulk_urls_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.bulk_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.bulk_scrape_button = ttk.Button(control_frame, text="Start Bulk Scrape", 
                                           command=self._scrape_bulk_urls)
        self.bulk_scrape_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", state=tk.DISABLED,
                                    command=self._stop_scraping)
        self.stop_button.pack(side=tk.LEFT)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(control_frame, textvariable=self.progress_var)
        self.progress_label.pack(side=tk.LEFT, padx=20)
    
    def _create_history_tab(self):
        """Create the history tab"""
        # History treeview
        columns = ("timestamp", "url", "status", "data_size")
        self.history_tree = ttk.Treeview(self.history_tab, columns=columns, show="tree headings")
        
        # Configure columns
        self.history_tree.heading("#0", text="ID")
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("url", text="URL")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("data_size", text="Data Size")
        
        # Column widths
        self.history_tree.column("#0", width=50)
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("url", width=300)
        self.history_tree.column("status", width=100)
        self.history_tree.column("data_size", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.history_tab, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load history
        self._refresh_history()    
    def _create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # User agent
        ttk.Label(settings_frame, text="User Agent:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_agent_entry = ttk.Entry(settings_frame, width=50)
        self.user_agent_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.user_agent_entry.insert(0, self.scraper_manager.config["user_agent"])
        
        # Timeout
        ttk.Label(settings_frame, text="Timeout (seconds):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.timeout_var = tk.IntVar(value=self.scraper_manager.config["timeout"])
        self.timeout_spin = ttk.Spinbox(settings_frame, from_=5, to=120, width=10,
                                      textvariable=self.timeout_var)
        self.timeout_spin.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Delay between requests
        ttk.Label(settings_frame, text="Delay (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.delay_var = tk.DoubleVar(value=self.scraper_manager.config["delay_between_requests"])
        self.delay_spin = ttk.Spinbox(settings_frame, from_=0.1, to=10.0, increment=0.1, width=10,
                                    textvariable=self.delay_var)
        self.delay_spin.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Save button
        ttk.Button(settings_frame, text="Save Settings", 
                  command=self._save_settings).grid(row=3, column=0, columnspan=2, pady=20)
    
    def _scrape_single_url(self):
        """Handle single URL scraping"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        # Get selectors
        selectors = {}
        for field, entry in self.selectors.items():
            value = entry.get().strip()
            if value:
                selectors[field] = value
        
        # Disable button during scraping
        self.scrape_button.config(state=tk.DISABLED)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scraping...\n")
        
        # Run in thread to avoid blocking GUI
        def scrape_thread():
            try:
                options = {"selectors": selectors} if selectors else None
                result = self.scraper_manager.scrape_url(url, options)
                
                # Update GUI in main thread
                self.parent.after(0, self._display_single_result, result)
            finally:
                self.parent.after(0, lambda: self.scrape_button.config(state=tk.NORMAL))
        
        threading.Thread(target=scrape_thread, daemon=True).start()    
    def _display_single_result(self, result: Dict[str, Any]):
        """Display single scraping result"""
        self.results_text.delete(1.0, tk.END)
        
        if result["success"]:
            self.results_text.insert(tk.END, f"URL: {result['url']}\n")
            self.results_text.insert(tk.END, f"Status: Success\n")
            self.results_text.insert(tk.END, f"Response Time: {result['metadata'].get('response_time', 0):.2f}s\n\n")
            
            # Display data
            self.results_text.insert(tk.END, "Data:\n")
            self.results_text.insert(tk.END, json.dumps(result["data"], indent=2, ensure_ascii=False))
        else:
            self.results_text.insert(tk.END, f"URL: {result['url']}\n")
            self.results_text.insert(tk.END, f"Status: Failed\n")
            self.results_text.insert(tk.END, f"Error: {result['error']}\n")
        
        # Store for export
        self.last_result = result
    
    def _scrape_bulk_urls(self):
        """Handle bulk URL scraping"""
        urls_text = self.bulk_urls_text.get(1.0, tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter URLs")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Disable button and enable stop
        self.bulk_scrape_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(f"Scraping 0/{len(urls)}")
        
        # Run in thread
        def bulk_scrape_thread():
            try:
                for i, url in enumerate(urls):
                    if hasattr(self, '_stop_flag') and self._stop_flag:
                        break
                    
                    self.parent.after(0, lambda i=i: self.progress_var.set(f"Scraping {i+1}/{len(urls)}"))
                    self.scraper_manager.scrape_url(url)
                
                self.parent.after(0, self._bulk_scrape_complete)
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                self.parent.after(0, self._reset_bulk_controls)
        
        self._stop_flag = False
        threading.Thread(target=bulk_scrape_thread, daemon=True).start()
    
    def _bulk_scrape_complete(self):
        """Handle bulk scrape completion"""
        self.progress_var.set("Complete!")
        self._refresh_history()
        messagebox.showinfo("Complete", "Bulk scraping completed!")
    
    def _reset_bulk_controls(self):
        """Reset bulk scraping controls"""
        self.bulk_scrape_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def _stop_scraping(self):
        """Stop bulk scraping"""
        self._stop_flag = True
        self.progress_var.set("Stopping...")
    
    def _refresh_history(self):
        """Refresh the history view"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history items
        history = self.scraper_manager.get_scraping_history()
        for i, item in enumerate(history):
            status = "Success" if item["success"] else "Failed"
            data_size = len(json.dumps(item.get("data", {}))) if item["success"] else 0
            
            self.history_tree.insert("", "end", text=str(i+1),
                                   values=(item["timestamp"], item["url"], 
                                          status, f"{data_size} bytes"))
    
    def _save_settings(self):
        """Save scraper settings"""
        config = {
            "user_agent": self.user_agent_entry.get(),
            "timeout": self.timeout_var.get(),
            "delay_between_requests": self.delay_var.get()
        }
        
        self.scraper_manager.update_config(config)
        messagebox.showinfo("Success", "Settings saved!")
    
    def _export_results(self, format: str):
        """Export results"""
        if not hasattr(self, 'last_result'):
            messagebox.showwarning("Warning", "No results to export")
            return
        
        # Implementation for file dialog and export would go here
        messagebox.showinfo("Export", f"Export to {format} not yet implemented")