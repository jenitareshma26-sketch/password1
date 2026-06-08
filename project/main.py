"""
Advanced Random Password Generator Application
A professional cybersecurity tool with modern UI.

Main application entry point with complete Tkinter GUI.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
from typing import Optional, List, Dict

from password_generator import PasswordGenerator, PasswordAnalysis, get_security_level_description
from database import Database
from settings import SettingsManager, ThemeManager, AppSettings
from utils import (
    copy_to_clipboard, clear_clipboard,
    format_datetime, truncate_password,
    get_all_security_tips, get_strength_color,
    get_keyboard_shortcuts
)
from dashboard import DashboardManager
from reports import ReportExporter


class PasswordGeneratorApp:
    """Main application class for Password Generator."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Advanced Password Generator")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Initialize components
        self.db = Database()
        self.generator = PasswordGenerator()
        self.settings_manager = SettingsManager(self.db)
        self.theme_manager = ThemeManager(self.settings_manager)
        self.dashboard = DashboardManager(self.db, self.theme_manager)
        self.reporter = ReportExporter(self.db)

        # Current state
        self.current_password = ""
        self.current_analysis: Optional[PasswordAnalysis] = None
        self.dark_mode = True

        # Apply theme
        self.apply_theme()

        # Build UI
        self.create_ui()

        # Load settings
        self.load_settings()

        # Keyboard shortcuts
        self.bind_shortcuts()

        # Generate initial password
        self.root.after(100, self.generate_password)

    def apply_theme(self):
        """Apply current theme to root."""
        theme = self.theme_manager.get_theme()
        self.root.configure(bg=theme['bg_primary'])
        self.dark_mode = theme == ThemeManager.DARK_THEME

        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TNotebook', background=theme['bg_primary'])
        style.configure('TNotebook.Tab',
                       background=theme['bg_tertiary'],
                       foreground=theme['text_primary'],
                       padding=[15, 8])
        style.map('TNotebook.Tab',
                 background=[('selected', theme['accent_primary'])])

        style.configure('TFrame', background=theme['bg_primary'])
        style.configure('TLabel', background=theme['bg_primary'],
                       foreground=theme['text_primary'])
        style.configure('TButton',
                       background=theme['accent_primary'],
                       foreground=theme['text_primary'])
        style.map('TButton',
                 background=[('active', theme['accent_secondary'])])

        style.configure('TCheckbutton',
                       background=theme['bg_primary'],
                       foreground=theme['text_primary'])
        style.configure('TRadiobutton',
                       background=theme['bg_primary'],
                       foreground=theme['text_primary'])
        style.configure('TScale',
                       background=theme['bg_primary'],
                       troughcolor=theme['bg_tertiary'])

    def create_ui(self):
        """Create the main user interface."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.theme_manager.get_theme()['bg_primary'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        self.create_header()

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Create tabs
        self.create_generator_tab()
        self.create_history_tab()
        self.create_dashboard_tab()
        self.create_settings_tab()
        self.create_security_tips_tab()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create application header."""
        theme = self.theme_manager.get_theme()

        header_frame = tk.Frame(self.main_frame, bg=theme['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Title
        title_label = tk.Label(
            header_frame,
            text="Advanced Password Generator",
            font=('Segoe UI', 24, 'bold'),
            bg=theme['bg_secondary'],
            fg=theme['accent_primary']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # Theme toggle button
        self.theme_btn = tk.Button(
            header_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            bg=theme['bg_tertiary'],
            fg=theme['text_primary'],
            font=('Segoe UI', 10),
            cursor='hand2'
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=20, pady=15)

    def create_generator_tab(self):
        """Create the password generator tab."""
        theme = self.theme_manager.get_theme()

        gen_frame = tk.Frame(self.notebook, bg=theme['bg_primary'])
        self.notebook.add(gen_frame, text='Generator')

        # Left panel - Generator options
        left_panel = tk.Frame(gen_frame, bg=theme['bg_secondary'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

        # Password length section
        length_frame = tk.LabelFrame(
            left_panel, text="Password Length",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        length_frame.pack(fill=tk.X, padx=10, pady=10)

        self.length_var = tk.IntVar(value=16)
        self.length_scale = tk.Scale(
            length_frame, from_=4, to=128,
            variable=self.length_var, orient=tk.HORIZONTAL,
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            highlightthickness=0, length=350
        )
        self.length_scale.pack(fill=tk.X, padx=10, pady=5)

        self.length_entry = tk.Entry(
            length_frame, textvariable=self.length_var,
            width=10, bg=theme['bg_input'], fg=theme['text_primary'],
            font=('Segoe UI', 11)
        )
        self.length_entry.pack(pady=5)

        # Character options section
        options_frame = tk.LabelFrame(
            left_panel, text="Character Options",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        self.uppercase_var = tk.BooleanVar(value=True)
        self.lowercase_var = tk.BooleanVar(value=True)
        self.numbers_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.spaces_var = tk.BooleanVar(value=False)

        options = [
            ("Uppercase (A-Z)", self.uppercase_var),
            ("Lowercase (a-z)", self.lowercase_var),
            ("Numbers (0-9)", self.numbers_var),
            ("Symbols (!@#$%)", self.symbols_var),
            ("Spaces", self.spaces_var)
        ]

        for text, var in options:
            cb = tk.Checkbutton(
                options_frame, text=text, variable=var,
                bg=theme['bg_secondary'], fg=theme['text_primary'],
                selectcolor=theme['bg_tertiary'],
                activebackground=theme['bg_secondary'],
                font=('Segoe UI', 10)
            )
            cb.pack(anchor=tk.W, padx=20, pady=3)

        # Security levels section
        levels_frame = tk.LabelFrame(
            left_panel, text="Security Levels",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        levels_frame.pack(fill=tk.X, padx=10, pady=10)

        self.level_var = tk.StringVar(value='Strong')

        for level in ['Basic', 'Medium', 'Strong', 'Ultra Secure']:
            desc = get_security_level_description(level)
            rb = tk.Radiobutton(
                levels_frame, text=f"{level} ({desc['length_range'][0]}-{desc['length_range'][1]} chars)",
                variable=self.level_var, value=level,
                bg=theme['bg_secondary'], fg=theme['text_primary'],
                selectcolor=theme['bg_tertiary'],
                activebackground=theme['bg_secondary'],
                font=('Segoe UI', 10),
                command=self.apply_security_level
            )
            rb.pack(anchor=tk.W, padx=20, pady=3)

        # Generate button
        self.generate_btn = tk.Button(
            left_panel, text="Generate Password",
            command=self.generate_password,
            bg=theme['accent_primary'],
            fg='white',
            font=('Segoe UI', 12, 'bold'),
            cursor='hand2',
            width=20, height=2
        )
        self.generate_btn.pack(pady=15)

        # Right panel - Result and analysis
        right_panel = tk.Frame(gen_frame, bg=theme['bg_secondary'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        # Password display
        pwd_frame = tk.LabelFrame(
            right_panel, text="Generated Password",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        pwd_frame.pack(fill=tk.X, padx=10, pady=10)

        self.password_display = tk.Entry(
            pwd_frame,
            font=('Consolas', 14),
            bg=theme['bg_card'], fg=theme['accent_primary'],
            width=35
        )
        self.password_display.pack(padx=10, pady=10, fill=tk.X)

        # Password visibility toggle
        self.show_password_var = tk.BooleanVar(value=True)
        self.visibility_cb = tk.Checkbutton(
            pwd_frame, text="Show Password", variable=self.show_password_var,
            command=self.toggle_password_visibility,
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 10)
        )
        self.visibility_cb.pack(pady=5)

        # Action buttons
        btn_frame = tk.Frame(pwd_frame, bg=theme['bg_secondary'])
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.copy_btn = tk.Button(
            btn_frame, text="Copy", command=self.copy_password,
            bg=theme['success'], fg='white',
            font=('Segoe UI', 10), cursor='hand2', width=10
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(
            btn_frame, text="Clear Clipboard", command=self.clear_clipboard,
            bg=theme['warning'], fg='white',
            font=('Segoe UI', 10), cursor='hand2', width=12
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.regen_btn = tk.Button(
            btn_frame, text="Regenerate", command=self.generate_password,
            bg=theme['accent_secondary'], fg='white',
            font=('Segoe UI', 10), cursor='hand2', width=10
        )
        self.regen_btn.pack(side=tk.LEFT, padx=5)

        # Strength indicator
        strength_frame = tk.LabelFrame(
            right_panel, text="Strength Analysis",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        strength_frame.pack(fill=tk.X, padx=10, pady=10)

        # Progress bar for strength
        self.strength_var = tk.DoubleVar(value=0)
        self.strength_bar = ttk.Progressbar(
            strength_frame, variable=self.strength_var,
            length=300, mode='determinate'
        )
        self.strength_bar.pack(padx=10, pady=5)

        self.strength_label = tk.Label(
            strength_frame, text="Strength: --",
            font=('Segoe UI', 12, 'bold'),
            bg=theme['bg_secondary'], fg=theme['text_primary']
        )
        self.strength_label.pack(pady=5)

        # Analysis details
        self.analysis_text = scrolledtext.ScrolledText(
            strength_frame, width=40, height=12,
            bg=theme['bg_card'], fg=theme['text_primary'],
            font=('Consolas', 10)
        )
        self.analysis_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def create_history_tab(self):
        """Create the password history tab."""
        theme = self.theme_manager.get_theme()

        history_frame = tk.Frame(self.notebook, bg=theme['bg_primary'])
        self.notebook.add(history_frame, text='History')

        # Controls frame
        controls_frame = tk.Frame(history_frame, bg=theme['bg_secondary'])
        controls_frame.pack(fill=tk.X, pady=5)

        # Search
        tk.Label(
            controls_frame, text="Search:",
            bg=theme['bg_secondary'], fg=theme['text_primary']
        ).pack(side=tk.LEFT, padx=10)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            controls_frame, textvariable=self.search_var,
            width=25, bg=theme['bg_input'], fg=theme['text_primary']
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame, text="Search",
            command=self.search_history,
            bg=theme['accent_primary'], fg='white'
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls_frame, text="Show All",
            command=self.load_history,
            bg=theme['bg_tertiary'], fg=theme['text_primary']
        ).pack(side=tk.LEFT, padx=5)

        # Action buttons
        tk.Button(
            controls_frame, text="Export History",
            command=self.export_history,
            bg=theme['success'], fg='white'
        ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            controls_frame, text="Clear All",
            command=self.clear_all_history,
            bg=theme['error'], fg='white'
        ).pack(side=tk.RIGHT, padx=5)

        # History treeview
        columns = ('id', 'password', 'strength', 'length', 'created')
        self.history_tree = ttk.Treeview(
            history_frame, columns=columns, show='headings', height=20
        )

        self.history_tree.heading('id', text='ID')
        self.history_tree.heading('password', text='Password')
        self.history_tree.heading('strength', text='Strength')
        self.history_tree.heading('length', text='Length')
        self.history_tree.heading('created', text='Created')

        self.history_tree.column('id', width=50)
        self.history_tree.column('password', width=300)
        self.history_tree.column('strength', width=120)
        self.history_tree.column('length', width=80)
        self.history_tree.column('created', width=150)

        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL,
                                  command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Context menu
        self.history_menu = tk.Menu(history_frame, tearoff=0)
        self.history_menu.add_command(label="Copy Password", command=self.copy_selected_password)
        self.history_menu.add_command(label="Delete Entry", command=self.delete_selected_password)

        self.history_tree.bind('<Button-3>', self.show_history_menu)

        # Load history
        self.load_history()

    def create_dashboard_tab(self):
        """Create the dashboard/analytics tab."""
        theme = self.theme_manager.get_theme()

        dash_frame = tk.Frame(self.notebook, bg=theme['bg_primary'])
        self.notebook.add(dash_frame, text='Dashboard')

        # Stats cards
        stats_frame = tk.Frame(dash_frame, bg=theme['bg_secondary'])
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self.stat_labels = {}
        stats = [
            ('Total Generated', 'total', 0),
            ('Avg Length', 'avg_len', '0'),
            ('Avg Entropy', 'avg_ent', '0'),
            ('Strong %', 'strong_pct', '0%')
        ]

        for i, (title, key, default) in enumerate(stats):
            card = tk.Frame(
                stats_frame,
                bg=theme['bg_tertiary'],
                bd=2, relief=tk.RIDGE
            )
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)

            tk.Label(
                card, text=title,
                bg=theme['bg_tertiary'], fg=theme['text_secondary'],
                font=('Segoe UI', 10)
            ).pack(pady=(10, 0))

            label = tk.Label(
                card, text=str(default),
                bg=theme['bg_tertiary'], fg=theme['accent_primary'],
                font=('Segoe UI', 20, 'bold')
            )
            label.pack(pady=(0, 10))
            self.stat_labels[key] = label

        # Charts frame (uses matplotlib)
        self.charts_frame = tk.Frame(dash_frame, bg=theme['bg_primary'])
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Refresh button
        tk.Button(
            dash_frame, text="Refresh Dashboard",
            command=self.refresh_dashboard,
            bg=theme['accent_primary'], fg='white',
            font=('Segoe UI', 10)
        ).pack(pady=10)

    def create_settings_tab(self):
        """Create the settings tab."""
        theme = self.theme_manager.get_theme()

        settings_frame = tk.Frame(self.notebook, bg=theme['bg_primary'])
        self.notebook.add(settings_frame, text='Settings')

        # Main settings container
        main_settings = tk.Frame(settings_frame, bg=theme['bg_secondary'])
        main_settings.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Default values section
        defaults_frame = tk.LabelFrame(
            main_settings, text="Default Values",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        defaults_frame.pack(fill=tk.X, padx=10, pady=10)

        # Default length
        tk.Label(
            defaults_frame, text="Default Password Length:",
            bg=theme['bg_secondary'], fg=theme['text_primary']
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.default_length_var = tk.IntVar(value=16)
        tk.Scale(
            defaults_frame, from_=8, to=64,
            variable=self.default_length_var, orient=tk.HORIZONTAL,
            bg=theme['bg_secondary'], fg=theme['text_primary']
        ).grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        # Default security level
        tk.Label(
            defaults_frame, text="Default Security Level:",
            bg=theme['bg_secondary'], fg=theme['text_primary']
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.default_level_var = tk.StringVar(value='Strong')
        ttk.Combobox(
            defaults_frame, textvariable=self.default_level_var,
            values=['Basic', 'Medium', 'Strong', 'Ultra Secure'],
            width=20, state='readonly'
        ).grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # Auto-copy option
        self.auto_copy_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            defaults_frame, text="Auto-copy generated passwords",
            variable=self.auto_copy_var,
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            selectcolor=theme['bg_tertiary']
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=10, pady=5)

        # Advanced options
        advanced_frame = tk.LabelFrame(
            main_settings, text="Advanced Options",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)

        self.exclude_similar_var = tk.BooleanVar(value=False)
        self.exclude_ambiguous_var = tk.BooleanVar(value=False)
        self.prevent_repeated_var = tk.BooleanVar(value=False)
        self.prevent_sequential_var = tk.BooleanVar(value=False)

        adv_options = [
            ("Exclude similar characters (0/O, 1/l/I, 5/S, 8/B)", self.exclude_similar_var),
            ("Exclude ambiguous symbols ({[]})", self.exclude_ambiguous_var),
            ("Prevent repeated characters", self.prevent_repeated_var),
            ("Prevent sequential characters", self.prevent_sequential_var)
        ]

        for i, (text, var) in enumerate(adv_options):
            tk.Checkbutton(
                advanced_frame, text=text, variable=var,
                bg=theme['bg_secondary'], fg=theme['text_primary'],
                selectcolor=theme['bg_tertiary']
            ).grid(row=i, column=0, sticky=tk.W, padx=10, pady=3)

        # Minimum requirements
        min_frame = tk.LabelFrame(
            main_settings, text="Minimum Character Requirements",
            bg=theme['bg_secondary'], fg=theme['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        min_frame.pack(fill=tk.X, padx=10, pady=10)

        self.min_upper_var = tk.IntVar(value=0)
        self.min_lower_var = tk.IntVar(value=0)
        self.min_number_var = tk.IntVar(value=0)
        self.min_symbol_var = tk.IntVar(value=0)

        min_options = [
            ("Minimum Uppercase:", self.min_upper_var),
            ("Minimum Lowercase:", self.min_lower_var),
            ("Minimum Numbers:", self.min_number_var),
            ("Minimum Symbols:", self.min_symbol_var)
        ]

        for i, (text, var) in enumerate(min_options):
            tk.Label(
                min_frame, text=text,
                bg=theme['bg_secondary'], fg=theme['text_primary']
            ).grid(row=i, column=0, sticky=tk.W, padx=10, pady=3)
            tk.Spinbox(
                min_frame, from_=0, to=10, textvariable=var, width=5,
                bg=theme['bg_input'], fg=theme['text_primary']
            ).grid(row=i, column=1, sticky=tk.W, padx=5, pady=3)

        # Save button
        tk.Button(
            main_settings, text="Save Settings",
            command=self.save_settings,
            bg=theme['success'], fg='white',
            font=('Segoe UI', 11, 'bold'),
            width=15, height=2
        ).pack(pady=20)

        tk.Button(
            main_settings, text="Reset to Defaults",
            command=self.reset_settings,
            bg=theme['warning'], fg='white',
            font=('Segoe UI', 10)
        ).pack(pady=5)

    def create_security_tips_tab(self):
        """Create the security tips tab."""
        theme = self.theme_manager.get_theme()

        tips_frame = tk.Frame(self.notebook, bg=theme['bg_primary'])
        self.notebook.add(tips_frame, text='Security Tips')

        # Tips display
        self.tips_text = scrolledtext.ScrolledText(
            tips_frame, width=80, height=30,
            bg=theme['bg_card'], fg=theme['text_primary'],
            font=('Segoe UI', 11), wrap=tk.WORD
        )
        self.tips_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.load_security_tips()

    def create_status_bar(self):
        """Create the status bar."""
        theme = self.theme_manager.get_theme()

        status_frame = tk.Frame(self.root, bg=theme['bg_tertiary'])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            status_frame, text="Ready",
            bg=theme['bg_tertiary'], fg=theme['text_secondary'],
            font=('Segoe UI', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.count_label = tk.Label(
            status_frame, text="Passwords Generated: 0",
            bg=theme['bg_tertiary'], fg=theme['text_secondary'],
            font=('Segoe UI', 9)
        )
        self.count_label.pack(side=tk.RIGHT, padx=10, pady=5)

    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Control-g>', lambda e: self.generate_password())
        self.root.bind('<Control-c>', lambda e: self.copy_password())
        self.root.bind('<Control-r>', lambda e: self.generate_password())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<Escape>', lambda e: self.root.quit())

    # ==================== Core Functionality ====================

    def generate_password(self):
        """Generate a new password based on current settings."""
        try:
            length = self.length_var.get()
            use_upper = self.uppercase_var.get()
            use_lower = self.lowercase_var.get()
            use_numbers = self.numbers_var.get()
            use_symbols = self.symbols_var.get()
            use_spaces = self.spaces_var.get()

            # Apply advanced settings
            self.generator.exclude_similar = self.exclude_similar_var.get()
            self.generator.exclude_ambiguous = self.exclude_ambiguous_var.get()
            self.generator.prevent_repeated = self.prevent_repeated_var.get()
            self.generator.prevent_sequential = self.prevent_sequential_var.get()
            self.generator.min_uppercase = self.min_upper_var.get()
            self.generator.min_lowercase = self.min_lower_var.get()
            self.generator.min_numbers = self.min_number_var.get()
            self.generator.min_symbols = self.min_symbol_var.get()

            # Generate
            self.current_password = self.generator.generate(
                length=length,
                use_uppercase=use_upper,
                use_lowercase=use_lower,
                use_numbers=use_numbers,
                use_symbols=use_symbols,
                use_spaces=use_spaces
            )

            # Update display
            self.password_display.delete(0, tk.END)
            self.password_display.insert(0, self.current_password)

            # Analyze password
            self.current_analysis = self.generator.analyze(self.current_password)
            self.update_strength_display()

            # Save to history
            self.db.add_password(
                self.current_password,
                self.current_analysis.strength,
                self.current_analysis.length,
                self.current_analysis.entropy
            )

            # Auto-copy if enabled
            if self.auto_copy_var.get():
                self.copy_password()

            self.update_status("Password generated successfully")
            self.update_count_label()

        except ValueError as e:
            messagebox.showerror("Generation Error", str(e), parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}", parent=self.root)

    def update_strength_display(self):
        """Update the strength indicator and analysis display."""
        if not self.current_analysis:
            return

        analysis = self.current_analysis
        theme = self.theme_manager.get_theme()

        # Update progress bar
        self.strength_var.set(analysis.strength_score)
        self.strength_bar.update()

        # Update strength label with color
        strength_color = get_strength_color(analysis.strength, self.dark_mode)
        self.strength_label.configure(
            text=f"Strength: {analysis.strength}",
            fg=strength_color
        )

        # Update analysis text
        self.analysis_text.delete(1.0, tk.END)

        details = f"""
Password Analysis
{'='*40}

Length: {analysis.length} characters
Entropy: {analysis.entropy:.2f} bits
Strength: {analysis.strength} ({analysis.strength_score}/100)

Estimated Crack Time: {analysis.crack_time}

Character Types:
  Uppercase: {'Yes' if analysis.has_uppercase else 'No'}
  Lowercase: {'Yes' if analysis.has_lowercase else 'No'}
  Numbers: {'Yes' if analysis.has_numbers else 'No'}
  Symbols: {'Yes' if analysis.has_symbols else 'No'}

Security Suggestions:
"""

        for suggestion in analysis.suggestions:
            details += f"  - {suggestion}\n"

        if not analysis.suggestions:
            details += "  - Password meets all security criteria.\n"

        self.analysis_text.insert(tk.END, details)

    def apply_security_level(self):
        """Apply settings for selected security level."""
        level = self.level_var.get()
        config = get_security_level_description(level)

        # Set recommended length (middle of range)
        min_len, max_len = config['length_range']
        recommended = (min_len + max_len) // 2
        self.length_var.set(recommended)

        # Set character types based on level
        if level == 'Basic':
            self.symbols_var.set(False)
        elif level == 'Medium':
            self.symbols_var.set(False)
        else:
            self.symbols_var.set(True)

        self.update_status(f"Applied {level} security level")

    def copy_password(self):
        """Copy current password to clipboard."""
        if self.current_password:
            if copy_to_clipboard(self.current_password):
                self.update_status("Password copied to clipboard")
            else:
                messagebox.showerror("Clipboard Error", "Failed to copy to clipboard", parent=self.root)
        else:
            messagebox.showwarning("No Password", "Generate a password first", parent=self.root)

    def clear_clipboard(self):
        """Clear the clipboard."""
        if clear_clipboard():
            self.update_status("Clipboard cleared")
        else:
            messagebox.showerror("Clipboard Error", "Failed to clear clipboard", parent=self.root)

    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_display.configure(show='')
        else:
            self.password_display.configure(show='*')

    def toggle_theme(self):
        """Toggle between dark and light theme."""
        self.theme_manager.toggle_theme()
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.update_status(f"Theme changed to {'dark' if self.dark_mode else 'light'} mode")

        # Recreate UI
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.create_ui()

    # ==================== History Management ====================

    def load_history(self):
        """Load password history into treeview."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        passwords = self.db.get_all_passwords()
        for p in passwords:
            self.history_tree.insert('', tk.END, values=(
                p['id'],
                truncate_password(p['password']),
                p['strength'],
                p['length'],
                format_datetime(p['created_at']) if p['created_at'] else ''
            ))

    def search_history(self):
        """Search password history."""
        search_term = self.search_var.get()
        if not search_term:
            self.load_history()
            return

        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        passwords = self.db.search_passwords(search_term)
        for p in passwords:
            self.history_tree.insert('', tk.END, values=(
                p['id'],
                truncate_password(p['password']),
                p['strength'],
                p['length'],
                format_datetime(p['created_at']) if p['created_at'] else ''
            ))

    def show_history_menu(self, event):
        """Show context menu for history."""
        item = self.history_tree.identify_row(event.y)
        if item:
            self.history_tree.selection_set(item)
            self.history_menu.post(event.x_root, event.y_root)

    def copy_selected_password(self):
        """Copy password from selected history entry."""
        selection = self.history_tree.selection()
        if selection:
            item = self.history_tree.item(selection[0])
            password_id = item['values'][0]

            # Get full password from database
            for p in self.db.get_all_passwords():
                if p['id'] == password_id:
                    copy_to_clipboard(p['password'])
                    self.update_status("Password copied from history")
                    break

    def delete_selected_password(self):
        """Delete selected history entry."""
        selection = self.history_tree.selection()
        if selection:
            if messagebox.askyesno("Delete Entry", "Delete this password entry?", parent=self.root):
                item = self.history_tree.item(selection[0])
                password_id = item['values'][0]
                self.db.delete_password(password_id)
                self.load_history()
                self.update_status("Entry deleted")

    def clear_all_history(self):
        """Clear all password history."""
        if messagebox.askyesno("Clear All History", "Are you sure you want to delete all password history?", parent=self.root):
            count = self.db.clear_history()
            self.load_history()
            self.update_status(f"Cleared {count} entries from history")

    def export_history(self):
        """Export password history."""
        export_window = tk.Toplevel(self.root)
        export_window.title("Export History")
        export_window.geometry("300x200")
        export_window.transient(self.root)

        theme = self.theme_manager.get_theme()
        export_window.configure(bg=theme['bg_primary'])

        tk.Label(
            export_window, text="Select Export Format:",
            bg=theme['bg_primary'], fg=theme['text_primary'],
            font=('Segoe UI', 11)
        ).pack(pady=20)

        format_var = tk.StringVar(value='txt')
        formats = [('Text (.txt)', 'txt'), ('CSV (.csv)', 'csv'),
                   ('Excel (.xlsx)', 'xlsx'), ('PDF (.pdf)', 'pdf')]

        for text, value in formats:
            tk.Radiobutton(
                export_window, text=text, value=value, variable=format_var,
                bg=theme['bg_primary'], fg=theme['text_primary']
            ).pack(anchor=tk.W, padx=40)

        def do_export():
            try:
                filepath = self.reporter.export_history(format_var.get())
                messagebox.showinfo("Export Complete", f"Exported to:\n{filepath}", parent=export_window)
                export_window.destroy()
            except Exception as e:
                messagebox.showerror("Export Error", str(e), parent=export_window)

        tk.Button(
            export_window, text="Export", command=do_export,
            bg=theme['success'], fg='white', width=15
        ).pack(pady=20)

    # ==================== Dashboard ====================

    def refresh_dashboard(self):
        """Refresh dashboard statistics and charts."""
        stats = self.dashboard.get_summary_stats()

        # Update stat cards
        self.stat_labels['total'].configure(text=str(stats['total_passwords']))
        self.stat_labels['avg_len'].configure(text=f"{stats['average_length']:.1f}")
        self.stat_labels['avg_ent'].configure(text=f"{stats['average_entropy']:.1f}")
        self.stat_labels['strong_pct'].configure(text=f"{stats['strong_password_percentage']}%")

        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # Create charts in grid
        chart_canvas = self.dashboard.create_strength_pie_chart(self.charts_frame)
        chart_canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

        bar_canvas = self.dashboard.create_length_bar_chart(self.charts_frame)
        bar_canvas.get_tk_widget().grid(row=0, column=1, padx=5, pady=5)

        self.update_status("Dashboard refreshed")

    # ==================== Settings ====================

    def load_settings(self):
        """Load settings from database."""
        settings = self.settings_manager.get_settings()

        self.default_length_var.set(settings.default_length)
        self.default_level_var.set(settings.default_security_level)
        self.auto_copy_var.set(settings.auto_copy)
        self.exclude_similar_var.set(settings.exclude_similar)
        self.exclude_ambiguous_var.set(settings.exclude_ambiguous)
        self.prevent_repeated_var.set(settings.prevent_repeated)
        self.prevent_sequential_var.set(settings.prevent_sequential)
        self.min_upper_var.set(settings.min_uppercase)
        self.min_lower_var.set(settings.min_lowercase)
        self.min_number_var.set(settings.min_numbers)
        self.min_symbol_var.set(settings.min_symbols)

        # Apply to generator
        self.generator.min_uppercase = settings.min_uppercase
        self.generator.min_lowercase = settings.min_lowercase
        self.generator.min_numbers = settings.min_numbers
        self.generator.min_symbols = settings.min_symbols

    def save_settings(self):
        """Save current settings to database."""
        settings = AppSettings(
            default_length=self.default_length_var.get(),
            default_security_level=self.default_level_var.get(),
            auto_copy=self.auto_copy_var.get(),
            theme='dark' if self.dark_mode else 'light',
            exclude_similar=self.exclude_similar_var.get(),
            exclude_ambiguous=self.exclude_ambiguous_var.get(),
            prevent_repeated=self.prevent_repeated_var.get(),
            prevent_sequential=self.prevent_sequential_var.get(),
            min_uppercase=self.min_upper_var.get(),
            min_lowercase=self.min_lower_var.get(),
            min_numbers=self.min_number_var.get(),
            min_symbols=self.min_symbol_var.get()
        )

        if self.settings_manager.save_settings(settings):
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully", parent=self.root)
        else:
            messagebox.showerror("Save Error", "Failed to save settings", parent=self.root)

    def reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?", parent=self.root):
            settings = self.settings_manager.reset_to_defaults()
            self.load_settings()
            self.update_status("Settings reset to defaults")

    def load_security_tips(self):
        """Load security tips into the display."""
        tips = get_all_security_tips()
        theme = self.theme_manager.get_theme()

        self.tips_text.delete(1.0, tk.END)

        self.tips_text.insert(tk.END, "Password Security Tips\n")
        self.tips_text.insert(tk.END, "=" * 50 + "\n\n")

        for tip in tips:
            self.tips_text.insert(tk.END, f"{tip['title']}\n")
            self.tips_text.insert(tk.END, f"Category: {tip['category']}\n")
            self.tips_text.insert(tk.END, f"{tip['content']}\n\n")
            self.tips_text.insert(tk.END, "-" * 50 + "\n\n")

    # ==================== Utilities ====================

    def update_status(self, message: str):
        """Update status bar message."""
        self.status_label.configure(text=message)

    def update_count_label(self):
        """Update password generation count."""
        stats = self.db.get_statistics()
        self.count_label.configure(text=f"Passwords Generated: {stats['total_generated']}")

    def show_help(self):
        """Show help dialog."""
        help_text = """
Keyboard Shortcuts:
Ctrl+G - Generate new password
Ctrl+C - Copy current password
Ctrl+R - Regenerate password
Ctrl+T - Toggle theme
F1 - Show this help
Escape - Exit application

Security Tips:
- Use unique passwords for each account
- Longer passwords are more secure
- Include symbols for added security
"""
        messagebox.showinfo("Help", help_text, parent=self.root)


def main():
    """Main entry point."""
    root = tk.Tk()

    # Configure DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = PasswordGeneratorApp(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == '__main__':
    main()
