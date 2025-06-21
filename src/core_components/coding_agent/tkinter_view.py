"""
Coding Agent View for Tkinter - Modern GUI for the Coding Agent
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import Dict, Any, List, Optional
import json
import threading


class CodingAgentView(ttk.Frame):
    """Modern coding agent interface for tkinter."""
    
    def __init__(self, parent, agent_manager=None):
        super().__init__(parent)
        self.agent_manager = agent_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create tabs
        self.chat_tab = self._create_chat_tab()
        self.notebook.add(self.chat_tab, text="💬 Chat")
        
        self.memory_tab = self._create_memory_tab()
        self.notebook.add(self.memory_tab, text="🧠 Memory")
        
        self.skills_tab = self._create_skills_tab()
        self.notebook.add(self.skills_tab, text="⚡ Skills")
        
        self.knowledge_tab = self._create_knowledge_tab()
        self.notebook.add(self.knowledge_tab, text="📚 Knowledge")
        
        self.tools_tab = self._create_tools_tab()
        self.notebook.add(self.tools_tab, text="🔧 Tools")
        
        self.analytics_tab = self._create_analytics_tab()
        self.notebook.add(self.analytics_tab, text="📊 Analytics")
        
        self.mcp_tab = self._create_mcp_tab()
        self.notebook.add(self.mcp_tab, text="🔌 MCP Services")
        
        self.settings_tab = self._create_settings_tab()
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill='x', side='bottom', padx=5, pady=2)
        
        self.status_label = ttk.Label(self.status_frame, text="🔴 Agent: Not Initialized")
        self.status_label.pack(side='left', padx=5)
        
        # Initialize button
        self.init_button = ttk.Button(self.status_frame, text="Initialize Agent", 
                                     command=self.initialize_agent)
        self.init_button.pack(side='right', padx=5)
        
    def _create_chat_tab(self) -> ttk.Frame:
        """Create the chat interface tab."""
        tab = ttk.Frame(self.notebook)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=20)
        self.chat_display.pack(fill='both', expand=True, padx=5, pady=5)
        self.chat_display.config(state='disabled')
        
        # Input frame
        input_frame = ttk.Frame(tab)
        input_frame.pack(fill='x', padx=5, pady=5)
        
        # Input field
        self.chat_input = ttk.Entry(input_frame)
        self.chat_input.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.chat_input.bind('<Return>', lambda e: self.send_message())
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side='right')
        
        # Options frame
        options_frame = ttk.Frame(tab)
        options_frame.pack(fill='x', padx=5, pady=5)
        
        # Model selection
        ttk.Label(options_frame, text="Model:").pack(side='left', padx=5)
        self.model_var = tk.StringVar(value="deepseek-coder:latest")
        self.model_combo = ttk.Combobox(options_frame, textvariable=self.model_var, 
                                       values=["deepseek-coder:latest", "codellama:latest", 
                                              "gpt-4", "claude-3"], width=20)
        self.model_combo.pack(side='left', padx=5)
        
        # Temperature
        ttk.Label(options_frame, text="Temperature:").pack(side='left', padx=5)
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_scale = ttk.Scale(options_frame, from_=0.0, to=1.0, 
                                   variable=self.temp_var, orient='horizontal', length=100)
        self.temp_scale.pack(side='left', padx=5)
        
        self.temp_label = ttk.Label(options_frame, text="0.7")
        self.temp_label.pack(side='left', padx=5)
        
        # Update temperature label
        def update_temp_label(value):
            self.temp_label.config(text=f"{float(value):.1f}")
        self.temp_scale.config(command=update_temp_label)
        
        # Checkboxes
        self.use_memory_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Use Memory", 
                       variable=self.use_memory_var).pack(side='left', padx=5)
        
        self.use_skills_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Track Skills", 
                       variable=self.use_skills_var).pack(side='left', padx=5)
        
        return tab
    
    def _create_memory_tab(self) -> ttk.Frame:
        """Create the memory management tab."""
        tab = ttk.Frame(self.notebook)
        
        # Controls frame
        controls_frame = ttk.Frame(tab)
        controls_frame.pack(fill='x', padx=5, pady=5)
        
        # Memory type selector
        ttk.Label(controls_frame, text="Memory Type:").pack(side='left', padx=5)
        self.memory_type_var = tk.StringVar(value="All Memories")
        self.memory_type_combo = ttk.Combobox(controls_frame, textvariable=self.memory_type_var,
                                             values=["All Memories", "Short-term Memory", 
                                                    "Long-term Memory", "Critical Memory"],
                                             width=20)
        self.memory_type_combo.pack(side='left', padx=5)
        self.memory_type_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_memory_list())
        
        # Search
        ttk.Label(controls_frame, text="Search:").pack(side='left', padx=5)
        self.memory_search_var = tk.StringVar()
        self.memory_search = ttk.Entry(controls_frame, textvariable=self.memory_search_var)
        self.memory_search.pack(side='left', fill='x', expand=True, padx=5)
        self.memory_search.bind('<KeyRelease>', lambda e: self.search_memories())
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh", 
                  command=self.refresh_memory_list).pack(side='left', padx=5)
        
        # Memory treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create treeview with scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')
        
        self.memory_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, 
                                       columns=('Type', 'Content', 'Created', 'Importance'),
                                       show='headings')
        tree_scroll.config(command=self.memory_tree.yview)
        
        # Configure columns
        self.memory_tree.heading('Type', text='Type')
        self.memory_tree.heading('Content', text='Content')
        self.memory_tree.heading('Created', text='Created')
        self.memory_tree.heading('Importance', text='Importance')
        
        self.memory_tree.column('Type', width=100)
        self.memory_tree.column('Content', width=400)
        self.memory_tree.column('Created', width=150)
        self.memory_tree.column('Importance', width=100)
        
        self.memory_tree.pack(fill='both', expand=True)
        
        # Action buttons
        action_frame = ttk.Frame(tab)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text="Add Memory", 
                  command=self.add_memory).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                  command=self.delete_memory).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Export Memories", 
                  command=self.export_memories).pack(side='left', padx=5)
        
        # Memory stats
        self.memory_stats_label = ttk.Label(action_frame, 
                                           text="Total: 0 | Short: 0 | Long: 0 | Critical: 0")
        self.memory_stats_label.pack(side='right', padx=5)
        
        return tab
    
    def _create_skills_tab(self) -> ttk.Frame:
        """Create the skills and achievements tab."""
        tab = ttk.Frame(self.notebook)
        
        # Main paned window
        paned = ttk.PanedWindow(tab, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left side - Skills
        skills_frame = ttk.LabelFrame(paned, text="Skills", padding=10)
        
        # Skills treeview
        skills_scroll = ttk.Scrollbar(skills_frame)
        skills_scroll.pack(side='right', fill='y')
        
        self.skills_tree = ttk.Treeview(skills_frame, yscrollcommand=skills_scroll.set,
                                       columns=('Level', 'XP', 'Progress'),
                                       show='tree headings')
        skills_scroll.config(command=self.skills_tree.yview)
        
        self.skills_tree.heading('#0', text='Skill')
        self.skills_tree.heading('Level', text='Level')
        self.skills_tree.heading('XP', text='XP')
        self.skills_tree.heading('Progress', text='Progress')
        
        self.skills_tree.column('#0', width=150)
        self.skills_tree.column('Level', width=60)
        self.skills_tree.column('XP', width=100)
        self.skills_tree.column('Progress', width=150)
        
        self.skills_tree.pack(fill='both', expand=True)
        paned.add(skills_frame, weight=2)
        
        # Right side - Achievements and Stats
        right_frame = ttk.Frame(paned)
        
        # Achievements
        achievements_frame = ttk.LabelFrame(right_frame, text="🏆 Achievements", padding=10)
        achievements_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.achievements_list = tk.Listbox(achievements_frame)
        self.achievements_list.pack(fill='both', expand=True)
        
        # Stats
        stats_frame = ttk.LabelFrame(right_frame, text="📊 Statistics", padding=10)
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        self.stats_labels = {}
        stats = [
            ("Total XP", "0"),
            ("Queries Processed", "0"),
            ("Skills Unlocked", "0/6"),
            ("Time Active", "0h 0m")
        ]
        
        for stat_name, default_value in stats:
            stat_row = ttk.Frame(stats_frame)
            stat_row.pack(fill='x', pady=2)
            
            ttk.Label(stat_row, text=f"{stat_name}:", 
                     font=('Arial', 10, 'bold')).pack(side='left')
            
            value_label = ttk.Label(stat_row, text=default_value)
            value_label.pack(side='right')
            self.stats_labels[stat_name] = value_label
        
        paned.add(right_frame, weight=1)
        
        return tab
    
    def _create_knowledge_tab(self) -> ttk.Frame:
        """Create the knowledge base management tab."""
        tab = ttk.Frame(self.notebook)
        
        # Search and filter frame
        filter_frame = ttk.Frame(tab)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        # Search
        ttk.Label(filter_frame, text="Search:").pack(side='left', padx=5)
        self.knowledge_search_var = tk.StringVar()
        self.knowledge_search = ttk.Entry(filter_frame, textvariable=self.knowledge_search_var)
        self.knowledge_search.pack(side='left', fill='x', expand=True, padx=5)
        
        # Category filter
        ttk.Label(filter_frame, text="Category:").pack(side='left', padx=5)
        self.category_filter_var = tk.StringVar(value="All Categories")
        self.category_filter = ttk.Combobox(filter_frame, textvariable=self.category_filter_var,
                                           values=["All Categories", "Code Patterns", 
                                                  "Best Practices", "Documentation",
                                                  "Troubleshooting", "Custom"],
                                           width=20)
        self.category_filter.pack(side='left', padx=5)
        
        # Add knowledge button
        ttk.Button(filter_frame, text="Add Knowledge", 
                  command=self.add_knowledge).pack(side='left', padx=5)
        
        # Knowledge treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')
        
        self.knowledge_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set,
                                          columns=('Category', 'Tags', 'Created'),
                                          show='tree headings')
        tree_scroll.config(command=self.knowledge_tree.yview)
        
        self.knowledge_tree.heading('#0', text='Title')
        self.knowledge_tree.heading('Category', text='Category')
        self.knowledge_tree.heading('Tags', text='Tags')
        self.knowledge_tree.heading('Created', text='Created')
        
        self.knowledge_tree.column('#0', width=300)
        self.knowledge_tree.column('Category', width=150)
        self.knowledge_tree.column('Tags', width=200)
        self.knowledge_tree.column('Created', width=150)
        
        self.knowledge_tree.pack(fill='both', expand=True)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(tab, text="Preview", padding=10)
        preview_frame.pack(fill='x', padx=5, pady=5)
        
        self.knowledge_preview = scrolledtext.ScrolledText(preview_frame, height=5, wrap=tk.WORD)
        self.knowledge_preview.pack(fill='both', expand=True)
        self.knowledge_preview.config(state='disabled')
        
        return tab
    
    def _create_tools_tab(self) -> ttk.Frame:
        """Create the tools management tab."""
        tab = ttk.Frame(self.notebook)
        
        # Tools label
        tools_label = ttk.Label(tab, text="🔧 Available Tools", 
                               font=('Arial', 14, 'bold'))
        tools_label.pack(pady=10)
        
        # Tools frame with scrollbar
        tools_canvas = tk.Canvas(tab)
        tools_scroll = ttk.Scrollbar(tab, orient='vertical', command=tools_canvas.yview)
        tools_scroll.pack(side='right', fill='y')
        tools_canvas.pack(side='left', fill='both', expand=True)
        tools_canvas.configure(yscrollcommand=tools_scroll.set)
        
        # Frame inside canvas
        tools_frame = ttk.Frame(tools_canvas)
        tools_canvas.create_window((0, 0), window=tools_frame, anchor='nw')
        
        # Tool cards
        tools = [
            {
                "name": "Code Generator",
                "icon": "⚡",
                "description": "Generate code from natural language",
                "action": self.open_code_generator
            },
            {
                "name": "Code Analyzer",
                "icon": "🔍",
                "description": "Analyze code quality and suggest improvements",
                "action": self.open_code_analyzer
            },
            {
                "name": "Refactoring Assistant",
                "icon": "🔄",
                "description": "Automated code refactoring suggestions",
                "action": self.open_refactoring_tool
            },
            {
                "name": "Documentation Generator",
                "icon": "📝",
                "description": "Generate documentation from code",
                "action": self.open_doc_generator
            },
            {
                "name": "Test Generator",
                "icon": "🧪",
                "description": "Generate unit tests for your code",
                "action": self.open_test_generator
            },
            {
                "name": "Dependency Analyzer",
                "icon": "🔗",
                "description": "Analyze project dependencies",
                "action": self.open_dependency_analyzer
            }
        ]
        
        # Create tool cards
        for i, tool in enumerate(tools):
            card = self._create_tool_card(tools_frame, tool)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')
        
        # Configure grid weights
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        # Update scroll region
        tools_frame.update_idletasks()
        tools_canvas.configure(scrollregion=tools_canvas.bbox('all'))
        
        return tab
    
    def _create_tool_card(self, parent, tool: Dict[str, Any]) -> ttk.Frame:
        """Create a tool card widget."""
        card = ttk.LabelFrame(parent, text="", padding=15)
        
        # Icon and name
        header_frame = ttk.Frame(card)
        header_frame.pack(fill='x', pady=(0, 10))
        
        icon_label = ttk.Label(header_frame, text=tool["icon"], 
                              font=('Arial', 24))
        icon_label.pack(side='left', padx=(0, 10))
        
        name_label = ttk.Label(header_frame, text=tool["name"], 
                              font=('Arial', 12, 'bold'))
        name_label.pack(side='left')
        
        # Description
        desc_label = ttk.Label(card, text=tool["description"], 
                              wraplength=250)
        desc_label.pack(fill='x', pady=(0, 10))
        
        # Launch button
        launch_btn = ttk.Button(card, text="Launch", command=tool["action"])
        launch_btn.pack()
        
        return card
    
    def _create_analytics_tab(self) -> ttk.Frame:
        """Create the analytics and insights tab."""
        tab = ttk.Frame(self.notebook)
        
        # Title
        title = ttk.Label(tab, text="📊 Agent Analytics & Insights", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=10)
        
        # Metrics frame
        metrics_frame = ttk.Frame(tab)
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        # Create metric cards
        metrics = [
            ("Total Queries", "0", "#00D4FF"),
            ("Tokens Used", "0", "#FF6B6B"),
            ("Active Skills", "0/6", "#4ECDC4"),
            ("Knowledge Items", "0", "#FFE66D")
        ]
        
        self.metric_labels = {}
        for i, (metric_name, value, color) in enumerate(metrics):
            metric_card = self._create_metric_card(metrics_frame, metric_name, value)
            metric_card.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            metrics_frame.columnconfigure(i, weight=1)
        
        # Charts placeholder
        charts_frame = ttk.LabelFrame(tab, text="Analytics Charts", padding=20)
        charts_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        placeholder = ttk.Label(charts_frame, 
                               text="Analytics charts will be displayed here\n\n" +
                                    "• Usage trends over time\n" +
                                    "• Skills progression\n" +
                                    "• Memory utilization\n" +
                                    "• Query performance metrics",
                               font=('Arial', 12))
        placeholder.pack(expand=True)
        
        return tab
    
    def _create_metric_card(self, parent, name: str, value: str) -> ttk.Frame:
        """Create a metric card widget."""
        card = ttk.LabelFrame(parent, text="", padding=15)
        
        value_label = ttk.Label(card, text=value, font=('Arial', 24, 'bold'))
        value_label.pack()
        
        name_label = ttk.Label(card, text=name, font=('Arial', 10))
        name_label.pack()
        
        # Store label for updates
        self.metric_labels[name] = value_label
        
        return card
    
    def _create_mcp_tab(self) -> ttk.Frame:
        """Create the MCP services management tab."""
        tab = ttk.Frame(self.notebook)
        
        # Status frame
        status_frame = ttk.LabelFrame(tab, text="MCP Service Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        # Control buttons
        controls_frame = ttk.Frame(status_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        self.mcp_start_btn = ttk.Button(controls_frame, text="▶️ Start All Services",
                                       command=self.start_mcp_services)
        self.mcp_start_btn.pack(side='left', padx=5)
        
        self.mcp_stop_btn = ttk.Button(controls_frame, text="⏹️ Stop All Services",
                                      command=self.stop_mcp_services, state='disabled')
        self.mcp_stop_btn.pack(side='left', padx=5)
        
        self.mcp_restart_btn = ttk.Button(controls_frame, text="🔄 Restart Services",
                                         command=self.restart_mcp_services)
        self.mcp_restart_btn.pack(side='left', padx=5)
        
        # Services table
        tree_frame = ttk.Frame(status_frame)
        tree_frame.pack(fill='both', expand=True)
        
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side='right', fill='y')
        
        self.mcp_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set,
                                    columns=('Status', 'Port', 'Actions'),
                                    show='tree headings', height=8)
        tree_scroll.config(command=self.mcp_tree.yview)
        
        self.mcp_tree.heading('#0', text='Service')
        self.mcp_tree.heading('Status', text='Status')
        self.mcp_tree.heading('Port', text='Port')
        self.mcp_tree.heading('Actions', text='Actions')
        
        self.mcp_tree.column('#0', width=200)
        self.mcp_tree.column('Status', width=100)
        self.mcp_tree.column('Port', width=100)
        self.mcp_tree.column('Actions', width=150)
        
        self.mcp_tree.pack(fill='both', expand=True)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(tab, text="MCP Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=10)
        
        self.auto_start_var = tk.BooleanVar()
        ttk.Checkbutton(config_frame, text="Auto-start MCP services on agent initialization",
                       variable=self.auto_start_var).pack(anchor='w', pady=5)
        
        self.mcp_logging_var = tk.BooleanVar()
        ttk.Checkbutton(config_frame, text="Enable detailed MCP logging",
                       variable=self.mcp_logging_var).pack(anchor='w', pady=5)
        
        return tab
    
    def _create_settings_tab(self) -> ttk.Frame:
        """Create the settings tab."""
        tab = ttk.Frame(self.notebook)
        
        # AI Model Settings
        ai_frame = ttk.LabelFrame(tab, text="AI Model Settings", padding=10)
        ai_frame.pack(fill='x', padx=10, pady=10)
        
        # Provider
        provider_frame = ttk.Frame(ai_frame)
        provider_frame.pack(fill='x', pady=5)
        ttk.Label(provider_frame, text="Provider:", width=15).pack(side='left')
        self.provider_var = tk.StringVar(value="Ollama")
        self.provider_combo = ttk.Combobox(provider_frame, textvariable=self.provider_var,
                                          values=["Ollama", "OpenAI", "Anthropic", "Local"],
                                          width=30)
        self.provider_combo.pack(side='left', padx=5)
        
        # Model
        model_frame = ttk.Frame(ai_frame)
        model_frame.pack(fill='x', pady=5)
        ttk.Label(model_frame, text="Model:", width=15).pack(side='left')
        self.settings_model_var = tk.StringVar(value="deepseek-coder:latest")
        self.settings_model_combo = ttk.Combobox(model_frame, textvariable=self.settings_model_var,
                                                values=["deepseek-coder:latest", "codellama:latest",
                                                       "gpt-4", "claude-3"],
                                                width=30)
        self.settings_model_combo.pack(side='left', padx=5)
        
        # API Key
        api_frame = ttk.Frame(ai_frame)
        api_frame.pack(fill='x', pady=5)
        ttk.Label(api_frame, text="API Key:", width=15).pack(side='left')
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show='*', width=30)
        self.api_key_entry.pack(side='left', padx=5)
        
        # Memory Settings
        memory_frame = ttk.LabelFrame(tab, text="Memory Settings", padding=10)
        memory_frame.pack(fill='x', padx=10, pady=10)
        
        # Max memory items
        max_items_frame = ttk.Frame(memory_frame)
        max_items_frame.pack(fill='x', pady=5)
        ttk.Label(max_items_frame, text="Max Memory Items:", width=20).pack(side='left')
        self.max_memory_var = tk.IntVar(value=1000)
        self.max_memory_spin = ttk.Spinbox(max_items_frame, from_=100, to=10000,
                                          textvariable=self.max_memory_var, width=10)
        self.max_memory_spin.pack(side='left', padx=5)
        
        # Auto-backup
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(memory_frame, text="Enable automatic memory backup",
                       variable=self.auto_backup_var).pack(anchor='w', pady=5)
        
        # Backup interval
        backup_frame = ttk.Frame(memory_frame)
        backup_frame.pack(fill='x', pady=5)
        ttk.Label(backup_frame, text="Backup Interval (minutes):", width=20).pack(side='left')
        self.backup_interval_var = tk.IntVar(value=15)
        self.backup_interval_spin = ttk.Spinbox(backup_frame, from_=5, to=60,
                                               textvariable=self.backup_interval_var, width=10)
        self.backup_interval_spin.pack(side='left', padx=5)
        
        # Save button
        save_btn = ttk.Button(tab, text="💾 Save Settings", command=self.save_settings)
        save_btn.pack(pady=20)
        
        return tab
    
    # Action methods
    def initialize_agent(self):
        """Initialize the coding agent."""
        if not self.agent_manager:
            self.add_activity("❌ No agent manager available")
            return
        
        self.add_activity("🚀 Initializing agent...")
        
        # Run initialization in thread
        def init_thread():
            result = self.agent_manager.initialize()
            
            # Update UI in main thread
            self.after(0, lambda: self._handle_init_result(result))
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def _handle_init_result(self, result):
        """Handle initialization result."""
        if result['status'] == 'success':
            self.status_label.config(text="🟢 Agent: Ready")
            self.init_button.config(text="✅ Agent Initialized", state='disabled')
            self.add_activity("✅ Agent initialized successfully")
            self.refresh_all_data()
        else:
            self.add_activity(f"❌ Initialization failed: {result.get('error', 'Unknown error')}")
    
    def send_message(self):
        """Send a message to the agent."""
        message = self.chat_input.get().strip()
        if not message:
            return
        
        if not self.agent_manager or not self.agent_manager.is_initialized:
            self.add_to_chat("System", "Please initialize the agent first!", "error")
            return
        
        # Clear input
        self.chat_input.delete(0, tk.END)
        
        # Add user message to chat
        self.add_to_chat("You", message, "user")
        
        # Process in thread
        def process_thread():
            self.add_activity(f"💬 Processing: {message[:50]}...")
            
            context = {
                'use_memory': self.use_memory_var.get(),
                'use_skills': self.use_skills_var.get(),
                'temperature': self.temp_var.get()
            }
            
            result = self.agent_manager.process_query(message, context)
            
            # Update UI in main thread
            self.after(0, lambda: self._handle_message_result(result))
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def _handle_message_result(self, result):
        """Handle message processing result."""
        if 'error' in result:
            self.add_to_chat("Error", result['error'], "error")
        else:
            response = result.get('response', 'No response')
            self.add_to_chat("Agent", response, "agent")
            
            # Update stats
            if 'stats' in result:
                self.update_stats_display(result['stats'])
    
    def add_to_chat(self, sender: str, message: str, msg_type: str = "normal"):
        """Add a message to the chat display."""
        self.chat_display.config(state='normal')
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format message based on type
        if msg_type == "user":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] You: ", "user_tag")
        elif msg_type == "agent":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] Agent: ", "agent_tag")
        elif msg_type == "error":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] Error: ", "error_tag")
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}: ", "system_tag")
        
        self.chat_display.insert(tk.END, message + "\n")
        
        # Configure tags
        self.chat_display.tag_config("user_tag", foreground="#00D4FF", font=('Arial', 10, 'bold'))
        self.chat_display.tag_config("agent_tag", foreground="#4ECDC4", font=('Arial', 10, 'bold'))
        self.chat_display.tag_config("error_tag", foreground="#FF6B6B", font=('Arial', 10, 'bold'))
        self.chat_display.tag_config("system_tag", foreground="#888888", font=('Arial', 10, 'bold'))
        
        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
    
    def add_activity(self, activity: str):
        """Add an activity to internal log."""
        # This could be implemented to show in a status bar or activity log
        print(f"Activity: {activity}")
    
    def refresh_memory_list(self):
        """Refresh the memory list."""
        if not self.agent_manager:
            return
        
        # Clear current items
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)
        
        # Get memory type
        memory_type = self.memory_type_var.get()
        type_map = {
            "All Memories": "all",
            "Short-term Memory": "short",
            "Long-term Memory": "long",
            "Critical Memory": "critical"
        }
        
        memories = self.agent_manager.get_memory_items(
            type_map.get(memory_type, "all")
        )
        
        # Add to tree
        for memory in memories:
            self.memory_tree.insert('', 'end', values=(
                memory.get('type', ''),
                memory.get('content', '')[:100],
                memory.get('created', ''),
                memory.get('importance', 0)
            ))
        
        # Update stats
        self.update_memory_stats()
    
    def search_memories(self):
        """Search memories based on query."""
        query = self.memory_search_var.get()
        if not query or not self.agent_manager:
            self.refresh_memory_list()
            return
        
        # Clear current items
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)
        
        memories = self.agent_manager.search_memories(query)
        
        # Add search results to tree
        for memory in memories:
            self.memory_tree.insert('', 'end', values=(
                memory.get('type', ''),
                memory.get('content', '')[:100],
                memory.get('created', ''),
                memory.get('importance', 0)
            ))
    
    def add_memory(self):
        """Add a new memory."""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Add Memory")
        dialog.geometry("400x300")
        
        # Content
        ttk.Label(dialog, text="Memory Content:").pack(anchor='w', padx=10, pady=5)
        content_text = scrolledtext.ScrolledText(dialog, height=10, width=50)
        content_text.pack(padx=10, pady=5)
        
        # Type selection
        type_frame = ttk.Frame(dialog)
        type_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(type_frame, text="Type:").pack(side='left', padx=5)
        type_var = tk.StringVar(value="short")
        type_combo = ttk.Combobox(type_frame, textvariable=type_var,
                                 values=["short", "long", "critical"],
                                 width=15)
        type_combo.pack(side='left', padx=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def save_memory():
            content = content_text.get('1.0', tk.END).strip()
            if content and self.agent_manager:
                result = self.agent_manager.add_memory(content, type_var.get())
                if result.get('status') == 'success':
                    self.add_activity("✅ Memory added successfully")
                    self.refresh_memory_list()
                    dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_memory).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def delete_memory(self):
        """Delete selected memory."""
        selected = self.memory_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a memory to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected memory?"):
            # Delete memory (implementation would depend on backend)
            self.add_activity("🗑️ Memory deleted")
            self.refresh_memory_list()
    
    def export_memories(self):
        """Export memories to file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path and self.agent_manager:
            result = self.agent_manager.export_data(file_path)
            if result['status'] == 'success':
                self.add_activity(f"✅ Exported memories to {file_path}")
                messagebox.showinfo("Export Successful", f"Memories exported to {file_path}")
    
    def refresh_skills(self):
        """Refresh the skills display."""
        if not self.agent_manager:
            return
        
        # Clear current items
        for item in self.skills_tree.get_children():
            self.skills_tree.delete(item)
        
        skills = self.agent_manager.get_skills()
        
        total_xp = 0
        for skill_name, skill_data in skills.items():
            # Calculate progress percentage
            progress = (skill_data['xp'] / skill_data['xp_to_next']) * 100
            
            self.skills_tree.insert('', 'end', text=skill_name, values=(
                skill_data['level'],
                f"{skill_data['xp']}/{skill_data['xp_to_next']}",
                f"{progress:.1f}%"
            ))
            
            total_xp += skill_data['xp'] + (skill_data['level'] - 1) * 100
        
        # Update achievements
        achievements = self.agent_manager.get_achievements()
        self.achievements_list.delete(0, tk.END)
        for achievement in achievements:
            self.achievements_list.insert(tk.END, f"🏆 {achievement}")
        
        # Update stats
        self.stats_labels["Total XP"].config(text=str(total_xp))
        self.stats_labels["Skills Unlocked"].config(text=f"{len(skills)}/6")
    
    def add_knowledge(self):
        """Add new knowledge item."""
        # Create dialog
        dialog = tk.Toplevel(self)
        dialog.title("Add Knowledge")
        dialog.geometry("500x400")
        
        # Title
        ttk.Label(dialog, text="Title:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        title_var = tk.StringVar()
        title_entry = ttk.Entry(dialog, textvariable=title_var, width=50)
        title_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Category
        ttk.Label(dialog, text="Category:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        category_var = tk.StringVar(value="Code Patterns")
        category_combo = ttk.Combobox(dialog, textvariable=category_var,
                                     values=["Code Patterns", "Best Practices", 
                                            "Documentation", "Troubleshooting", "Custom"],
                                     width=30)
        category_combo.grid(row=1, column=1, sticky='w', padx=10, pady=5)
        
        # Tags
        ttk.Label(dialog, text="Tags (comma-separated):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        tags_var = tk.StringVar()
        tags_entry = ttk.Entry(dialog, textvariable=tags_var, width=50)
        tags_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # Content
        ttk.Label(dialog, text="Content:").grid(row=3, column=0, sticky='nw', padx=10, pady=5)
        content_text = scrolledtext.ScrolledText(dialog, height=15, width=50)
        content_text.grid(row=3, column=1, padx=10, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        def save_knowledge():
            title = title_var.get().strip()
            content = content_text.get('1.0', tk.END).strip()
            tags = [t.strip() for t in tags_var.get().split(',') if t.strip()]
            
            if title and content and self.agent_manager:
                result = self.agent_manager.add_knowledge(
                    title, content, category_var.get(), tags
                )
                if result.get('status') == 'success':
                    self.add_activity("✅ Knowledge added successfully")
                    self.refresh_knowledge()
                    dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_knowledge).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def refresh_knowledge(self):
        """Refresh knowledge display."""
        if not self.agent_manager:
            return
        
        # Clear current items
        for item in self.knowledge_tree.get_children():
            self.knowledge_tree.delete(item)
        
        items = self.agent_manager.get_knowledge_items()
        
        for item in items:
            self.knowledge_tree.insert('', 'end', text=item.get('title', ''), values=(
                item.get('category', ''),
                ', '.join(item.get('tags', [])),
                item.get('created', '')
            ))
    
    def refresh_tools(self):
        """Refresh available tools."""
        if not self.agent_manager:
            return
        
        tools = self.agent_manager.get_tools()
        # Update tools display if needed
    
    def update_memory_stats(self):
        """Update memory statistics."""
        if not self.agent_manager:
            return
        
        # Get counts by type (simplified for now)
        total = len(self.memory_tree.get_children())
        self.memory_stats_label.config(text=f"Total: {total}")
    
    def update_stats_display(self, stats: Dict[str, Any]):
        """Update statistics display."""
        # Update metric cards
        if "queries_processed" in stats:
            self.metric_labels.get("Total Queries", tk.Label()).config(
                text=str(stats["queries_processed"])
            )
        
        if "tokens_used" in stats:
            self.metric_labels.get("Tokens Used", tk.Label()).config(
                text=f"{stats['tokens_used']:,}"
            )
        
        # Update other stats
        if "memory_items" in stats:
            self.metric_labels.get("Knowledge Items", tk.Label()).config(
                text=str(stats["memory_items"])
            )
    
    def refresh_all_data(self):
        """Refresh all data displays."""
        self.refresh_memory_list()
        self.refresh_skills()
        self.refresh_knowledge()
        self.refresh_tools()
    
    # MCP Methods
    def start_mcp_services(self):
        """Start MCP services."""
        if self.agent_manager:
            result = self.agent_manager.start_mcp()
            if result.get('status') == 'success':
                self.mcp_start_btn.config(state='disabled')
                self.mcp_stop_btn.config(state='normal')
                self.add_activity("✅ MCP services started")
                self.update_mcp_status()
    
    def stop_mcp_services(self):
        """Stop MCP services."""
        if self.agent_manager:
            result = self.agent_manager.stop_mcp()
            if result.get('status') == 'success':
                self.mcp_start_btn.config(state='normal')
                self.mcp_stop_btn.config(state='disabled')
                self.add_activity("⏹️ MCP services stopped")
                self.update_mcp_status()
    
    def restart_mcp_services(self):
        """Restart MCP services."""
        self.stop_mcp_services()
        self.after(1000, self.start_mcp_services)
    
    def update_mcp_status(self):
        """Update MCP status display."""
        if not self.agent_manager:
            return
        
        status = self.agent_manager.get_mcp_status()
        # Update tree with service status
        # This would show each MCP service and its status
    
    # Tool launching methods
    def open_code_generator(self):
        """Open code generator tool."""
        self.add_activity("🚀 Launched Code Generator")
        # Create code generator dialog
        self._create_tool_dialog("Code Generator", self._code_generator_content)
    
    def open_code_analyzer(self):
        """Open code analyzer tool."""
        self.add_activity("🚀 Launched Code Analyzer")
        self._create_tool_dialog("Code Analyzer", self._code_analyzer_content)
    
    def open_refactoring_tool(self):
        """Open refactoring assistant."""
        self.add_activity("🚀 Launched Refactoring Assistant")
        self._create_tool_dialog("Refactoring Assistant", self._refactoring_content)
    
    def open_doc_generator(self):
        """Open documentation generator."""
        self.add_activity("🚀 Launched Documentation Generator")
        self._create_tool_dialog("Documentation Generator", self._doc_generator_content)
    
    def open_test_generator(self):
        """Open test generator."""
        self.add_activity("🚀 Launched Test Generator")
        self._create_tool_dialog("Test Generator", self._test_generator_content)
    
    def open_dependency_analyzer(self):
        """Open dependency analyzer."""
        self.add_activity("🚀 Launched Dependency Analyzer")
        self._create_tool_dialog("Dependency Analyzer", self._dependency_analyzer_content)
    
    def _create_tool_dialog(self, title: str, content_func):
        """Create a tool dialog window."""
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("800x600")
        
        # Create content
        content_func(dialog)
    
    def _code_generator_content(self, parent):
        """Create code generator content."""
        ttk.Label(parent, text="Enter your code description:", 
                 font=('Arial', 12)).pack(anchor='w', padx=10, pady=10)
        
        # Input area
        input_text = scrolledtext.ScrolledText(parent, height=10)
        input_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Language selection
        lang_frame = ttk.Frame(parent)
        lang_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(lang_frame, text="Language:").pack(side='left', padx=5)
        lang_var = tk.StringVar(value="python")
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var,
                                 values=["python", "javascript", "java", "c++", "go"],
                                 width=20)
        lang_combo.pack(side='left', padx=5)
        
        # Generate button
        def generate():
            prompt = input_text.get('1.0', tk.END).strip()
            if prompt and self.agent_manager:
                result = self.agent_manager.generate_code(prompt, lang_var.get())
                if result.get('status') == 'success':
                    # Show result in new window or output area
                    self._show_code_result(result.get('code', ''), lang_var.get())
        
        ttk.Button(parent, text="Generate Code", command=generate).pack(pady=10)
    
    def _code_analyzer_content(self, parent):
        """Create code analyzer content."""
        ttk.Label(parent, text="Select a file to analyze:", 
                 font=('Arial', 12)).pack(anchor='w', padx=10, pady=10)
        
        # File selection
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill='x', padx=10, pady=5)
        
        file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=file_var)
        file_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        def browse_file():
            filename = filedialog.askopenfilename(
                filetypes=[("Python files", "*.py"), ("All files", "*.*")]
            )
            if filename:
                file_var.set(filename)
        
        ttk.Button(file_frame, text="Browse", command=browse_file).pack(side='left')
        
        # Analyze button
        def analyze():
            file_path = file_var.get()
            if file_path and self.agent_manager:
                result = self.agent_manager.analyze_code(file_path)
                if result.get('status') == 'success':
                    # Show analysis results
                    self._show_analysis_result(result.get('analysis', {}))
        
        ttk.Button(parent, text="Analyze Code", command=analyze).pack(pady=10)
        
        # Results area
        results_text = scrolledtext.ScrolledText(parent, height=15)
        results_text.pack(fill='both', expand=True, padx=10, pady=5)
    
    def _refactoring_content(self, parent):
        """Create refactoring assistant content."""
        ttk.Label(parent, text="Paste your code for refactoring suggestions:", 
                 font=('Arial', 12)).pack(anchor='w', padx=10, pady=10)
        
        # Code input
        code_text = scrolledtext.ScrolledText(parent, height=20)
        code_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Refactor button
        ttk.Button(parent, text="Get Refactoring Suggestions").pack(pady=10)
    
    def _doc_generator_content(self, parent):
        """Create documentation generator content."""
        ttk.Label(parent, text="Select code files to generate documentation:", 
                 font=('Arial', 12)).pack(anchor='w', padx=10, pady=10)
        
        # File list
        file_listbox = tk.Listbox(parent, selectmode='multiple')
        file_listbox.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Add files button
        ttk.Button(parent, text="Add Files").pack(pady=5)
        ttk.Button(parent, text="Generate Documentation").pack(pady=5)
    
    def _test_generator_content(self, parent):
        """Create test generator content."""
        ttk.Label(parent, text="Paste your code to generate unit tests:", 
                 font=('Arial', 12)).pack(anchor='w', padx=10, pady=10)
        
        # Code input
        code_text = scrolledtext.ScrolledText(parent, height=15)
        code_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Test framework selection
        framework_frame = ttk.Frame(parent)
        framework_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(framework_frame, text="Test Framework:").pack(side='left', padx=5)
        framework_var = tk.StringVar(value="pytest")
        framework_combo = ttk.Combobox(framework_frame, textvariable=framework_var,
                                      values=["pytest", "unittest", "jest", "mocha"],
                                      width=20)
        framework_combo.pack(side='left', padx=5)
        
        # Generate button
        ttk.Button(parent, text="Generate Tests").pack(pady=10)
    
    def _dependency_analyzer_content(self, parent):
        """Create dependency analyzer content."""
        ttk.Label(parent, text="Select project directory to analyze dependencies:", 
                 font=('Arial', 12)).pack(anchor='w', padx=10, pady=10)
        
        # Directory selection
        dir_frame = ttk.Frame(parent)
        dir_frame.pack(fill='x', padx=10, pady=5)
        
        dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=dir_var)
        dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        def browse_dir():
            dirname = filedialog.askdirectory()
            if dirname:
                dir_var.set(dirname)
        
        ttk.Button(dir_frame, text="Browse", command=browse_dir).pack(side='left')
        
        # Analyze button
        ttk.Button(parent, text="Analyze Dependencies").pack(pady=10)
        
        # Results area
        results_text = scrolledtext.ScrolledText(parent, height=15)
        results_text.pack(fill='both', expand=True, padx=10, pady=5)
    
    def _show_code_result(self, code: str, language: str):
        """Show generated code result."""
        result_dialog = tk.Toplevel(self)
        result_dialog.title(f"Generated {language.title()} Code")
        result_dialog.geometry("800x600")
        
        # Code display
        code_text = scrolledtext.ScrolledText(result_dialog)
        code_text.pack(fill='both', expand=True, padx=10, pady=10)
        code_text.insert('1.0', code)
        
        # Copy button
        def copy_code():
            self.clipboard_clear()
            self.clipboard_append(code)
            messagebox.showinfo("Copied", "Code copied to clipboard!")
        
        ttk.Button(result_dialog, text="Copy to Clipboard", 
                  command=copy_code).pack(pady=5)
    
    def _show_analysis_result(self, analysis: Dict[str, Any]):
        """Show code analysis result."""
        result_dialog = tk.Toplevel(self)
        result_dialog.title("Code Analysis Results")
        result_dialog.geometry("800x600")
        
        # Results display
        results_text = scrolledtext.ScrolledText(result_dialog)
        results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Format and display analysis
        results_text.insert('1.0', json.dumps(analysis, indent=2))
    
    def save_settings(self):
        """Save settings."""
        # Save all settings to agent config
        self.add_activity("💾 Settings saved")
        messagebox.showinfo("Settings", "Settings saved successfully!")
