"""
Comprehensive Modern Workspace Tracker View
Full integration of ALL workspace tracker features with modern UI design
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, font
import threading
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

class ComprehensiveWorkspaceTrackerView:
    """Complete workspace tracker view with all features and modern design."""
    
    def __init__(self, parent: tk.Frame, tracker_manager: Any):
        """Initialize the comprehensive workspace tracker view."""
        self.parent = parent
        self.tracker_manager = tracker_manager
        
        # State management
        self.current_view = "dashboard"
        self.selected_items = {
            'project': None,
            'task': None,
            'module': None,
            'research': None,
            'note': None,
            'file': None
        }
        
        # Create custom fonts
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=20, weight="bold"),
            'heading': font.Font(family="Segoe UI", size=14, weight="bold"),
            'subheading': font.Font(family="Segoe UI", size=12, weight="bold"),
            'body': font.Font(family="Segoe UI", size=10),
            'small': font.Font(family="Segoe UI", size=9)
        }
        
        # Color scheme (Modern dark theme)
        self.colors = {
            'bg': '#1e1e1e',
            'bg_secondary': '#252526',
            'bg_tertiary': '#2d2d30',
            'bg_selected': '#094771',
            'fg': '#cccccc',
            'fg_secondary': '#969696',
            'accent': '#007acc',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f44747',
            'border': '#464647'
        }
        
        # Configure styles
        self._configure_modern_styles()
        
        # Create the main layout
        self._create_main_layout()
        
        # Initialize data
        self._initialize_data()
    
    def _configure_modern_styles(self):
        """Configure modern ttk styles for all widgets."""
        style = ttk.Style()
        
        # Configure notebook
        style.configure('Modern.TNotebook', 
                       background=self.colors['bg'],
                       borderwidth=0,
                       tabposition='wn')  # West-North (left side tabs)
        
        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['fg'],
                       padding=[15, 10],
                       borderwidth=0,
                       font=self.fonts['body'])
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['bg_selected'])],
                 foreground=[('selected', 'white')])
        
        # Configure frames
        style.configure('Card.TFrame',
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)
        
        # Configure buttons
        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       padding=[15, 8],
                       font=self.fonts['body'])
        
        style.configure('Secondary.TButton',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['fg'],
                       borderwidth=1,
                       padding=[15, 8])
    
    def _create_main_layout(self):
        """Create the main layout with all components."""
        # Main container
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create top toolbar
        self._create_toolbar()
        
        # Create main content area with sidebar
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar for navigation
        self._create_sidebar(content_frame)
        
        # Main content area
        self.content_area = ttk.Frame(content_frame, style='Card.TFrame')
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create status bar
        self._create_status_bar()
        
        # Show dashboard by default
        self._show_dashboard()
    
    def _create_toolbar(self):
        """Create the top toolbar with project selector and actions."""
        toolbar = ttk.Frame(self.main_container, style='Card.TFrame')
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Project selector
        project_frame = ttk.Frame(toolbar)
        project_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(project_frame, text="Project:", font=self.fonts['body']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.project_var = tk.StringVar()
        self.project_combo = ttk.Combobox(project_frame, textvariable=self.project_var, 
                                         width=30, state='readonly')
        self.project_combo.pack(side=tk.LEFT)
        self.project_combo.bind('<<ComboboxSelected>>', self._on_project_selected)
        
        # Quick actions
        actions_frame = ttk.Frame(toolbar)
        actions_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(actions_frame, text="➕ New Project", style='Modern.TButton',
                  command=self._new_project_dialog).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(actions_frame, text="🔄 Refresh", style='Secondary.TButton',
                  command=self._refresh_all_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(actions_frame, text="⚙️ Settings", style='Secondary.TButton',
                  command=self._show_settings).pack(side=tk.LEFT, padx=2)
