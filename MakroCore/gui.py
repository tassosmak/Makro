"""
Makro Kernel GUI - Modern Edition - FIXED TEXT RENDERING
Complete integration with PyTerminal Makro kernel.
"""

import threading
import queue
import sys
import io
import json
import os
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, filedialog
from tkinter import font as tkfont
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Makro / Kernel imports
from Makro.MakroCore import flags
from Makro.MakroCore.UserHandler import loader

try:
    from Makro.MakroCore import commands as cmd_module
    CommandRunner = getattr(cmd_module, "CommandList", None)
except Exception:
    CommandRunner = None

try:
    from Makro.MakroCore.SystemCalls import SystemCalls
except Exception:
    SystemCalls = None

try:
    from Makro.MakroCore.RendererKit import Renderer as RD
except Exception:
    RD = None

try:
    from Makro.MakroCore.credentials import get_credentials, _get_propiatery
except Exception:
    get_credentials = None
    _get_propiatery = None


# ============================================================================
# THEME CONFIGURATION
# ============================================================================

class DarkTheme:
    """Modern dark transparent theme colors."""
    BG_PRIMARY = "#0f1419"
    BG_SECONDARY = "#1a1f2e"
    BG_TERTIARY = "#252d3d"

    TEXT_PRIMARY = "#e8eaed"
    TEXT_SECONDARY = "#9ca3af"

    ACCENT_PRIMARY = "#00d9ff"
    ACCENT_SECONDARY = "#ff1493"
    ACCENT_SUCCESS = "#10b981"
    ACCENT_ERROR = "#ef4444"

    ENTRY_BG = "#1a1f2e"
    BUTTON_BG = "#2563eb"
    BUTTON_HOVER = "#1d4ed8"
    BUTTON_ACCENT = "#00d9ff"
    SCROLLBAR_BG = "#1a1f2e"
    BORDER_COLOR = "#374151"


class KernelLogger:
    """Thread-safe logger."""
    def __init__(self, q: queue.Queue):
        self.q = q
        self.log_file = "makro_gui.log"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def log(self, level: str, msg: str):
        getattr(self.logger, level.lower())(msg)
        self.q.put(("log", level, msg))


# ============================================================================
# WORKER THREAD
# ============================================================================

class MakroKernelWorker(threading.Thread):
    """Deep kernel integration worker."""
    def __init__(self, command: str, q: queue.Queue, logger: KernelLogger):
        super().__init__(daemon=True)
        self.command = command
        self.q = q
        self.logger = logger

    def run(self):
        buf_out = io.StringIO()
        buf_err = io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = buf_out, buf_err

        try:
            self.q.put(("status", f"Running: {self.command}"))
            self.logger.log("INFO", f"Executing: {self.command}")

            if self.command.startswith("mode:"):
                self._handle_mode_change()
            elif self.command.startswith("reload:"):
                self._handle_reload()
            elif self.command.startswith("flag:"):
                self._handle_flag_change()
            elif self.command.startswith("user:"):
                self._handle_user_operation()
            elif self.command.startswith("fs:"):
                self._handle_filesystem()
            elif self.command.startswith("prop:"):
                self._handle_proprietary()
            elif CommandRunner:
                self._run_command_runner()
            elif SystemCalls and getattr(SystemCalls, "run", None):
                self._run_system_calls()
            else:
                print("No Makro command runner available.")

        except Exception as e:
            self.logger.log("ERROR", f"Worker exception: {e}")
            print(f"Worker exception: {e}")
        finally:
            sys.stdout, sys.stderr = old_out, old_err
            out_text = buf_out.getvalue()
            err_text = buf_err.getvalue()
            if out_text:
                self.q.put(("output", out_text))
            if err_text:
                self.q.put(("error", err_text))
            self.q.put(("done", self.command))

    def _handle_mode_change(self):
        new_mode = self.command.split(":", 1)[1].strip()
        flags.MODE = new_mode
        print(f"[KERNEL] MODE changed to {new_mode}")
        self.q.put(("flags_changed", {"MODE": new_mode}))

    def _handle_reload(self):
        target = self.command.split(":", 1)[1].strip()
        if target == "credentials" and get_credentials:
            try:
                get_credentials(print_credentials=True)
                print("[KERNEL] Credentials reloaded")
                self.q.put(("credentials_updated",))
            except Exception as e:
                print(f"Error reloading credentials: {e}")
        elif target == "flags" and _get_propiatery:
            try:
                _get_propiatery(print_credentials=True)
                print("[KERNEL] Proprietary flags reloaded")
                self.q.put(("flags_changed", {}))
            except Exception as e:
                print(f"Error reloading flags: {e}")

    def _handle_flag_change(self):
        parts = self.command.split(":", 1)[1].split("=")
        if len(parts) == 2:
            flag_name, flag_value = parts
            flag_name = flag_name.strip()
            flag_value = flag_value.strip().lower() in ("true", "1", "yes")
            setattr(flags, flag_name, flag_value)
            print(f"[KERNEL] Flag {flag_name} set to {flag_value}")
            self.q.put(("flags_changed", {flag_name: flag_value}))

    def _handle_user_operation(self):
        op = self.command.split(":", 1)[1].strip()
        if op == "login":
            try:
                loader()
                print("[KERNEL] User login completed")
                self.q.put(("user_updated",))
            except Exception as e:
                print(f"Login error: {e}")
        elif op == "status":
            print(f"[KERNEL] Current user: {getattr(flags, 'USERNAME', 'N/A')}")

    def _handle_filesystem(self):
        op = self.command.split(":", 1)[1].strip()
        if op == "get_folder" and SystemCalls:
            try:
                folder = SystemCalls.get_folder()
                print(f"[KERNEL] Selected folder: {folder}")
                self.q.put(("fs_result", folder))
            except Exception as e:
                print(f"Filesystem error: {e}")
        elif op == "list":
            try:
                cwd = os.getcwd()
                items = os.listdir(cwd)
                print(f"[KERNEL] Directory: {cwd}")
                for item in items[:10]:
                    print(f"  - {item}")
            except Exception as e:
                print(f"Listing error: {e}")

    def _handle_proprietary(self):
        action = self.command.split(":", 1)[1].strip()
        if action == "open_dashboard":
            print("[PROPRIETARY] Opening internal dashboard...")
        elif action == "run_diag":
            print("[PROPRIETARY] Running internal diagnostics...")
        elif action == "enable_trace":
            print("[PROPRIETARY] Enabling advanced trace mode...")
            flags.Runtime_Tracer = True
        elif action == "status":
            prop_status = {
                "EnableIntSoft": getattr(flags, "EnableIntSoft", False),
                "EnableAudio": getattr(flags, "EnableAudio", False),
            }
            print(f"[PROPRIETARY] Status: {prop_status}")

    def _run_command_runner(self):
        try:
            CommandRunner(self.command)
        except TypeError:
            try:
                CommandRunner(self.command, None)
            except Exception as e:
                print(f"CommandRunner error: {e}")
                self.logger.log("ERROR", f"CommandRunner: {e}")
        except Exception as e:
            print(f"CommandRunner exception: {e}")
            self.logger.log("ERROR", f"CommandRunner exception: {e}")

    def _run_system_calls(self):
        try:
            SystemCalls.run(self.command)
        except Exception as e:
            print(f"SystemCalls.run exception: {e}")
            self.logger.log("ERROR", f"SystemCalls.run: {e}")


# ============================================================================
# MAIN GUI CLASS
# ============================================================================

class MakroKernelGUI:
    """Modern terminal-style GUI with proprietary support."""

    def __init__(self, root: Optional[tk.Tk] = None):
        self.root = root or tk.Tk()
        self.root.title(f"{getattr(flags, 'Default_text', 'Makro')} Kernel GUI")
        self.root.geometry("1300x750")
        self.root.minsize(900, 600)

        # Transparency
        try:
            self.root.attributes('-alpha', 0.96)
        except Exception:
            pass

        self.root.config(bg=DarkTheme.BG_PRIMARY)

        # Enable GUI flags
        flags.Fully_GUI = True
        flags.EnableGUI = True

        # Threading
        self.q = queue.Queue()
        self.logger = KernelLogger(self.q)
        self.logger.log("INFO", "Makro Kernel GUI started")

        # State
        self.history = []
        self.history_index = None
        self.last_command = ""
        self.current_directory = os.getcwd()
        self.credentials: Dict[str, Any] = {}

        # Setup fonts FIRST - BEFORE ttk style
        self._setup_fonts()

        # Then setup ttk style
        self._setup_ttk_style()

        # Load credentials
        self._load_credentials()

        # Build UI
        self._build_menu()
        self._build_layout()
        self._build_context_menus()
        self._setup_keyboard_shortcuts()

        # Queue processor
        self.root.after(100, self._process_queue)

        # Initial messages
        self._append_terminal(f"{getattr(flags, 'Default_text', 'Makro')} Kernel GUI initialized.\n")
        self._append_terminal(f"Current MODE: {getattr(flags, 'MODE', 'N/A')}\n")
        self._append_terminal(f"Working directory: {self.current_directory}\n")
        self._refresh_session_panel()

        if RD:
            try:
                RD.CommandShow(msg="Makro GUI ready").Show('OKGREEN')
            except Exception:
                pass

    # ========================================================================
    # FONT SETUP - MUST BE FIRST
    # ========================================================================

    def _setup_fonts(self):
        """Setup all fonts with proper fallbacks."""
        # System fonts that work cross-platform
        try:
            # Try macOS/system fonts first
            self.font_mono = tkfont.Font(family="Monaco", size=11, name="mono_font")
        except Exception:
            try:
                self.font_mono = tkfont.Font(family="Courier", size=11, name="mono_font")
            except Exception:
                self.font_mono = tkfont.nametofont("TkFixedFont")

        try:
            self.font_text = tkfont.Font(family="Helvetica", size=11, name="text_font")
        except Exception:
            try:
                self.font_text = tkfont.Font(family="Arial", size=11, name="text_font")
            except Exception:
                self.font_text = tkfont.nametofont("TkDefaultFont")

        try:
            self.font_button = tkfont.Font(family="Helvetica", size=11, weight="normal", name="button_font")
        except Exception:
            self.font_button = tkfont.nametofont("TkDefaultFont")

        try:
            self.font_title = tkfont.Font(family="Helvetica", size=11, weight="bold", name="title_font")
        except Exception:
            self.font_title = tkfont.nametofont("TkDefaultFont")

        try:
            self.font_small = tkfont.Font(family="Helvetica", size=9, name="small_font")
        except Exception:
            self.font_small = tkfont.nametofont("TkDefaultFont")

    # ========================================================================
    # TTK STYLE SETUP
    # ========================================================================

    def _setup_ttk_style(self):
        """Configure modern ttk theme."""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure Notebook
        style.configure('TNotebook', background=DarkTheme.BG_PRIMARY, borderwidth=0)
        style.configure(
            'TNotebook.Tab',
            padding=[20, 10],
            background=DarkTheme.BG_TERTIARY,
            foreground=DarkTheme.TEXT_PRIMARY,
            font=self.font_text
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', DarkTheme.BUTTON_BG)]
        )

        # Configure Frames
        style.configure('TFrame', background=DarkTheme.BG_PRIMARY)

        # Configure Modern Button with FIXED font
        style.configure(
            'Modern.TButton',
            font=self.font_button,
            padding=(12, 6),
            foreground=DarkTheme.TEXT_PRIMARY,
            background=DarkTheme.BUTTON_BG,
            borderwidth=0
        )
        style.map(
            'Modern.TButton',
            background=[('active', DarkTheme.BUTTON_HOVER),
                        ('pressed', DarkTheme.BUTTON_ACCENT)],
            foreground=[('active', DarkTheme.TEXT_PRIMARY)]
        )

        # Configure Accent Button
        style.configure(
            'Accent.TButton',
            font=self.font_button,
            padding=(12, 6),
            foreground="#ffffff",
            background=DarkTheme.BUTTON_ACCENT,
            borderwidth=0
        )
        style.map(
            'Accent.TButton',
            background=[('active', '#00b8cc')]
        )

    # ========================================================================
    # CREDENTIALS & STATE MANAGEMENT
    # ========================================================================

    def _load_credentials(self):
        """Load credentials from config."""
        try:
            if get_credentials:
                get_credentials(print_credentials=False)
                self.credentials = {
                    "username": getattr(flags, "USERNAME", "N/A"),
                    "mode": getattr(flags, "MODE", "N/A"),
                }
        except Exception as e:
            self.logger.log("WARNING", f"Could not load credentials: {e}")

    def _refresh_session_panel(self):
        """Update session info display."""
        info = [
            f"User: {getattr(flags, 'USERNAME', 'N/A')}",
            f"MODE: {getattr(flags, 'MODE', 'N/A')}",
            f"Dir: {self.current_directory[-30:]}...",
            f"",
            f"Fully_GUI: {getattr(flags, 'Fully_GUI', False)}",
            f"EnableGUI: {getattr(flags, 'EnableGUI', False)}",
            f"Inside_Thread: {getattr(flags, 'Inside_Thread', False)}",
            f"Create_Graph: {getattr(flags, 'Create_Graph', False)}",
            f"Runtime_Tracer: {getattr(flags, 'Runtime_Tracer', False)}",
            f"EnableIntSoft: {getattr(flags, 'EnableIntSoft', False)}",
            f"EnableAudio: {getattr(flags, 'EnableAudio', False)}",
        ]
        self.session_text.config(state=tk.NORMAL)
        self.session_text.delete(1.0, tk.END)
        self.session_text.insert(tk.END, "\n".join(info))
        self.session_text.config(state=tk.DISABLED)

    # ========================================================================
    # MENU BAR
    # ========================================================================

    def _build_menu(self):
        menubar = tk.Menu(self.root, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY)

        # File menu
        filemenu = tk.Menu(menubar, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY)
        filemenu.add_command(label="Open file", command=self._menu_open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._on_exit)
        menubar.add_cascade(label="File", menu=filemenu)

        # Tools menu
        toolsmenu = tk.Menu(menubar, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY)
        toolsmenu.add_command(label="User login", command=self._menu_user_login)
        toolsmenu.add_command(label="Get folder", command=self._menu_get_folder)
        toolsmenu.add_separator()
        toolsmenu.add_command(label="Reload credentials", command=self._menu_reload_credentials)
        toolsmenu.add_command(label="Reload flags", command=self._menu_reload_flags)
        menubar.add_cascade(label="Tools", menu=toolsmenu)

        # Mode menu
        modemenu = tk.Menu(menubar, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY)
        for mode in ["1", "2", "3", "9"]:
            modemenu.add_command(label=f"MODE {mode}", command=lambda m=mode: self._set_mode(m))
        menubar.add_cascade(label="Mode", menu=modemenu)

        # Proprietary menu
        propmenu = tk.Menu(menubar, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY)
        propmenu.add_command(label="Dashboard", command=lambda: self._on_prop_command("open_dashboard"))
        propmenu.add_command(label="Diagnostics", command=lambda: self._on_prop_command("run_diag"))
        propmenu.add_command(label="Advanced Trace", command=lambda: self._on_prop_command("enable_trace"))
        menubar.add_cascade(label="Proprietary", menu=propmenu)

        # View menu
        viewmenu = tk.Menu(menubar, bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY)
        viewmenu.add_command(label="Clear terminal", command=self.clear_terminal)
        viewmenu.add_command(label="Clear logs", command=self.clear_logs)
        viewmenu.add_separator()
        viewmenu.add_command(label="Command palette (Ctrl+P)", command=self._open_command_palette)
        menubar.add_cascade(label="View", menu=viewmenu)

        self.root.config(menu=menubar)

    def _menu_open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python", "*.py"), ("All", "*.*")])
        if path:
            self._append_terminal(f"Opened: {path}\n")

    def _menu_user_login(self):
        self._append_terminal("> user:login\n")
        worker = MakroKernelWorker("user:login", self.q, self.logger)
        worker.start()

    def _menu_get_folder(self):
        self._append_terminal("> fs:get_folder\n")
        worker = MakroKernelWorker("fs:get_folder", self.q, self.logger)
        worker.start()

    def _menu_reload_credentials(self):
        self._append_terminal("> reload:credentials\n")
        worker = MakroKernelWorker("reload:credentials", self.q, self.logger)
        worker.start()

    def _menu_reload_flags(self):
        self._append_terminal("> reload:flags\n")
        worker = MakroKernelWorker("reload:flags", self.q, self.logger)
        worker.start()

    # ========================================================================
    # LAYOUT
    # ========================================================================

    def _build_layout(self):
        """Build main layout."""
        self.main_pane = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, sashwidth=4,
            bg=DarkTheme.BG_PRIMARY
        )
        self.main_pane.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        left_frame = tk.Frame(self.main_pane, bg=DarkTheme.BG_PRIMARY)
        self.main_pane.add(left_frame, minsize=800)

        right_frame = tk.Frame(self.main_pane, width=300, bg=DarkTheme.BG_SECONDARY)
        self.main_pane.add(right_frame, minsize=300)

        self.notebook = ttk.Notebook(left_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.tab_terminal = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_terminal, text="Terminal")
        # Reinvented terminal tab (OS-like desktop of commands)
        self._build_terminal_tab()

        self.tab_logs = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_logs, text="Logs")
        self._build_logs_tab()

        self.tab_fs = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_fs, text="Filesystem")
        self._build_filesystem_tab()

        self.tab_config = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_config, text="Config")
        self._build_config_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_frame = tk.Frame(left_frame, bg=DarkTheme.BG_TERTIARY, height=24)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_label = tk.Label(
            status_frame, textvariable=self.status_var, anchor="w",
            bg=DarkTheme.BG_TERTIARY, fg=DarkTheme.TEXT_SECONDARY,
            font=self.font_small
        )
        status_label.pack(fill=tk.X, padx=8, pady=4)

        # Session panel
        self._build_session_panel_ui(right_frame)

    def _build_terminal_tab(self):
        """
        Reinvented Terminal tab: OS‑like “desktop” of app buttons.
        Keeps transparent look + terminal log output area.
        """
        # Top area: “desktop” of buttons (apps)
        desktop_frame = tk.Frame(self.tab_terminal, bg=DarkTheme.BG_PRIMARY)
        desktop_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 3))

        # Header bar like an OS panel
        header = tk.Frame(desktop_frame, bg=DarkTheme.BG_SECONDARY)
        header.pack(fill=tk.X, padx=0, pady=(0, 6))

        title_lbl = tk.Label(
            header, text="Makro Desktop",
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_title
        )
        title_lbl.pack(side=tk.LEFT, padx=8, pady=4)

        hint_lbl = tk.Label(
            header, text="Click an app to run a command",
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_SECONDARY,
            font=self.font_small
        )
        hint_lbl.pack(side=tk.RIGHT, padx=8, pady=4)

        # Scrollable area for “apps”
        canvas = tk.Canvas(
            desktop_frame, bd=0, highlightthickness=0,
            bg=DarkTheme.BG_PRIMARY
        )
        apps_scroll = tk.Scrollbar(
            desktop_frame, orient=tk.VERTICAL, command=canvas.yview,
            bg=DarkTheme.SCROLLBAR_BG
        )
        apps_container = tk.Frame(canvas, bg=DarkTheme.BG_PRIMARY)

        canvas.configure(yscrollcommand=apps_scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        apps_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=apps_container, anchor="nw")

        def _on_apps_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        apps_container.bind("<Configure>", _on_apps_config)

        # Define command “apps” – each entry is (label, command, accent)
        command_groups = [
            # Group 1: Modes
            {
                "label": "Modes",
                "apps": [
                    ("MODE 1", "mode:1", True),
                    ("MODE 2", "mode:2", False),
                    ("MODE 3", "mode:3", False),
                    ("MODE 9 (Makro)", "mode:9", True),
                ],
            },
            # Group 2: User
            {
                "label": "User",
                "apps": [
                    ("Login", "user:login", True),
                    ("Status", "user:status", False),
                ],
            },
            # Group 3: Filesystem
            {
                "label": "Filesystem",
                "apps": [
                    ("Get Folder", "fs:get_folder", True),
                    ("List Directory", "fs:list", False),
                ],
            },
            # Group 4: Reload
            {
                "label": "Reload",
                "apps": [
                    ("Reload Credentials", "reload:credentials", True),
                    ("Reload Flags", "reload:flags", False),
                ],
            },
            # Group 5: Proprietary
            {
                "label": "Proprietary",
                "apps": [
                    ("Dashboard", "prop:open_dashboard", True),
                    ("Diagnostics", "prop:run_diag", False),
                    ("Advanced Trace", "prop:enable_trace", True),
                ],
            },
            # Group 6: Misc / Help
            {
                "label": "Misc",
                "apps": [
                    ("Help (Command Palette)", None, False),
                ],
            },
        ]

        # Build grouped “desktop icons”
        for group in command_groups:
            group_frame = tk.LabelFrame(
                apps_container,
                text=group["label"],
                bg=DarkTheme.BG_SECONDARY,
                fg=DarkTheme.TEXT_PRIMARY,
                font=self.font_button,
                labelanchor="nw"
            )
            group_frame.pack(fill=tk.X, padx=6, pady=4)

            inner = tk.Frame(group_frame, bg=DarkTheme.BG_SECONDARY)
            inner.pack(fill=tk.X, padx=4, pady=4)

            # 3 columns layout
            cols = 3
            for idx, (label, cmd, accent) in enumerate(group["apps"]):
                r = idx // cols
                c = idx % cols

                if cmd is None and "Help" in label:
                    btn_cmd = lambda l=label: self._open_command_palette()
                else:
                    btn_cmd = lambda c=cmd: self._run_command_from_button(c)

                style = "Accent.TButton" if accent else "Modern.TButton"
                btn = ttk.Button(
                    inner,
                    text=label,
                    style=style,
                    command=btn_cmd
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

            for c in range(cols):
                inner.columnconfigure(c, weight=1)

        # Middle area: terminal output (logs of executed commands)
        self.terminal_output = scrolledtext.ScrolledText(
            self.tab_terminal, wrap=tk.WORD, state=tk.DISABLED,
            bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.TEXT_PRIMARY,
            insertbackground=DarkTheme.ACCENT_PRIMARY,
            font=self.font_mono,
            selectbackground=DarkTheme.BUTTON_BG,
            selectforeground=DarkTheme.TEXT_PRIMARY
        )
        self.terminal_output.pack(
            fill=tk.BOTH, expand=False, padx=6, pady=(0, 3), ipady=40
        )

        # Bottom: last command bar (readonly, instead of free-typing entry)
        cmd_bar = tk.Frame(self.tab_terminal, bg=DarkTheme.BG_SECONDARY)
        cmd_bar.pack(fill=tk.X, padx=6, pady=(0, 6))

        lbl_last = tk.Label(
            cmd_bar, text="Last Command:",
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_SECONDARY,
            font=self.font_small
        )
        lbl_last.pack(side=tk.LEFT, padx=(4, 4), pady=4)

        self.last_cmd_var = tk.StringVar(value="")
        last_cmd_entry = tk.Entry(
            cmd_bar,
            textvariable=self.last_cmd_var,
            font=self.font_mono,
            bg=DarkTheme.ENTRY_BG,
            fg=DarkTheme.TEXT_PRIMARY,
            state="readonly",
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightcolor=DarkTheme.ACCENT_PRIMARY,
            readonlybackground=DarkTheme.ENTRY_BG
        )
        last_cmd_entry.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), pady=4
        )

        clear_btn = ttk.Button(
            cmd_bar, text="Clear Output",
            style="Modern.TButton",
            command=self.clear_terminal
        )
        clear_btn.pack(side=tk.RIGHT, padx=(3, 0), pady=2)

    # NEW helper for OS-like terminal behavior
    def _run_command_from_button(self, cmd: str):
        """
        Mimics typing a command and pressing Enter,
        but is wired to desktop buttons instead of a free text entry.
        """
        if not cmd:
            return

        self.history.append(cmd)
        self.history_index = None
        self.last_command = cmd

        if hasattr(self, "last_cmd_var"):
            self.last_cmd_var.set(cmd)

        self._append_terminal(f"> {cmd}\n")
        worker = MakroKernelWorker(cmd, self.q, self.logger)
        worker.start()

    def _build_logs_tab(self):
        """Logs tab."""
        self.log_output = scrolledtext.ScrolledText(
            self.tab_logs, wrap=tk.WORD, state=tk.DISABLED,
            bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.TEXT_SECONDARY,
            insertbackground=DarkTheme.ACCENT_PRIMARY,
            font=self.font_mono,
            selectbackground=DarkTheme.BUTTON_BG
        )
        self.log_output.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def _build_filesystem_tab(self):
        """Filesystem tab."""
        fs_header = tk.Frame(self.tab_fs, bg=DarkTheme.BG_SECONDARY)
        fs_header.pack(fill=tk.X, padx=6, pady=6)

        dir_label = tk.Label(
            fs_header, text=f"Directory: {self.current_directory}",
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_text
        )
        dir_label.pack(anchor="w")

        refresh_btn = ttk.Button(
            fs_header, text="Refresh",
            style="Modern.TButton",
            command=self._refresh_fs_listing
        )
        refresh_btn.pack(anchor="w", pady=(4, 0))

        self.fs_listbox = tk.Listbox(
            self.tab_fs, bg=DarkTheme.BG_PRIMARY,
            fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_mono,
            selectmode=tk.SINGLE,
            activestyle='none',
            highlightthickness=0
        )
        self.fs_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
        self.fs_listbox.bind("<Double-Button-1>", self._on_fs_select)

        self._refresh_fs_listing()

    def _build_config_tab(self):
        """Config tab."""
        config_label = tk.Label(
            self.tab_config, text="Makro Configuration",
            font=self.font_title,
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.ACCENT_PRIMARY
        )
        config_label.pack(anchor="w", padx=6, pady=6)

        self.config_text = scrolledtext.ScrolledText(
            self.tab_config, wrap=tk.WORD,
            bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_mono,
            selectbackground=DarkTheme.BUTTON_BG
        )
        self.config_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self._refresh_config_display()

    def _build_session_panel_ui(self, right_frame):
        """Session panel."""
        title = tk.Label(
            right_frame, text="Session Info", font=self.font_title,
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.ACCENT_PRIMARY
        )
        title.pack(anchor="w", padx=8, pady=8)

        self.session_text = tk.Text(
            right_frame, height=13, state=tk.DISABLED, wrap=tk.WORD,
            bg=DarkTheme.BG_TERTIARY, fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_mono, highlightthickness=0
        )
        self.session_text.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Quick Flags
        flags_label = tk.Label(
            right_frame, text="Quick Flags", font=self.font_button,
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY
        )
        flags_label.pack(anchor="w", padx=8)

        self.var_inside_thread = tk.BooleanVar(value=getattr(flags, "Inside_Thread", False))
        self.var_create_graph = tk.BooleanVar(value=getattr(flags, "Create_Graph", False))
        self.var_runtime_tracer = tk.BooleanVar(value=getattr(flags, "Runtime_Tracer", False))

        for var, label_text in [
            (self.var_inside_thread, "Inside Thread"),
            (self.var_create_graph, "Create Graph"),
            (self.var_runtime_tracer, "Runtime Tracer"),
        ]:
            cb = tk.Checkbutton(
                right_frame, text=label_text, variable=var,
                command=self._update_flags_gui,
                bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY,
                activebackground=DarkTheme.BG_TERTIARY,
                activeforeground=DarkTheme.ACCENT_PRIMARY,
                selectcolor=DarkTheme.BG_TERTIARY,
                font=self.font_small
            )
            cb.pack(anchor="w", padx=8)

        # Proprietary Frame
        self.proprietary_frame = tk.LabelFrame(
            right_frame, text="Proprietary",
            bg=DarkTheme.BG_SECONDARY,
            fg=DarkTheme.ACCENT_SECONDARY,
            font=self.font_button,
            labelanchor="nw"
        )
        self.proprietary_frame.pack(fill=tk.X, padx=8, pady=8)
        self.proprietary_frame.pack_forget()

        self.btn_prop_dashboard = ttk.Button(
            self.proprietary_frame, text="Dashboard",
            style="Accent.TButton",
            command=lambda: self._on_prop_command("open_dashboard")
        )
        self.btn_prop_dashboard.pack(fill=tk.X, pady=2)

        self.btn_prop_diag = ttk.Button(
            self.proprietary_frame, text="Diagnostics",
            style="Accent.TButton",
            command=lambda: self._on_prop_command("run_diag")
        )
        self.btn_prop_diag.pack(fill=tk.X, pady=2)

        self.btn_prop_trace = ttk.Button(
            self.proprietary_frame, text="Advanced Trace",
            style="Accent.TButton",
            command=lambda: self._on_prop_command("enable_trace")
        )
        self.btn_prop_trace.pack(fill=tk.X, pady=2)

        # Action buttons
        btn_frame = tk.Frame(right_frame, bg=DarkTheme.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=8, pady=8)

        refresh_btn = ttk.Button(
            btn_frame, text="Refresh Session", style="Modern.TButton",
            command=self._refresh_session_panel
        )
        refresh_btn.pack(fill=tk.X, pady=2)

        palette_btn = ttk.Button(
            btn_frame, text="Cmd Palette (Ctrl+P)", style="Modern.TButton",
            command=self._open_command_palette
        )
        palette_btn.pack(fill=tk.X, pady=2)

    # ========================================================================
    # OUTPUT METHODS
    # ========================================================================

    def _append_terminal(self, text: str):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)

    def _append_log(self, text: str):
        self.log_output.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.insert(tk.END, f"[{timestamp}] {text}\n")
        self.log_output.see(tk.END)
        self.log_output.config(state=tk.DISABLED)

    def clear_terminal(self):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.delete(1.0, tk.END)
        self.terminal_output.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_output.config(state=tk.NORMAL)
        self.log_output.delete(1.0, tk.END)
        self.log_output.config(state=tk.DISABLED)

    # ========================================================================
    # FILESYSTEM TAB
    # ========================================================================

    def _refresh_fs_listing(self):
        """Refresh filesystem listing."""
        self.fs_listbox.delete(0, tk.END)
        try:
            items = os.listdir(self.current_directory)
            for item in sorted(items)[:100]:
                self.fs_listbox.insert(tk.END, item)
        except Exception as e:
            self.fs_listbox.insert(tk.END, f"Error: {e}")

    def _on_fs_select(self, event):
        """Handle filesystem selection."""
        selection = self.fs_listbox.curselection()
        if selection:
            item = self.fs_listbox.get(selection[0])
            path = os.path.join(self.current_directory, item)
            if os.path.isdir(path):
                self.current_directory = path
                self._refresh_fs_listing()

    # ========================================================================
    # CONFIG TAB
    # ========================================================================

    def _refresh_config_display(self):
        """Display current config."""
        config_info = f"""Makro Kernel Configuration
================================

MODE Settings:
  Current MODE: {getattr(flags, 'MODE', 'N/A')}
  Username: {getattr(flags, 'USERNAME', 'N/A')}
  
GUI Settings:
  Fully_GUI: {getattr(flags, 'Fully_GUI', False)}
  EnableGUI: {getattr(flags, 'EnableGUI', False)}
  Inside_Thread: {getattr(flags, 'Inside_Thread', False)}
  Create_Graph: {getattr(flags, 'Create_Graph', False)}
  Runtime_Tracer: {getattr(flags, 'Runtime_Tracer', False)}

Proprietary Settings:
  EnableIntSoft: {getattr(flags, 'EnableIntSoft', False)}
  EnableAudio: {getattr(flags, 'EnableAudio', False)}

Environment:
  Working Directory: {self.current_directory}
  Log File: {self.logger.log_file}
"""
        self.config_text.config(state=tk.NORMAL)
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(tk.END, config_info)
        self.config_text.config(state=tk.DISABLED)

    # ========================================================================
    # COMMAND INPUT & HISTORY (only used via buttons now)
    # ========================================================================

    def _on_enter(self, event=None):
        # Kept for compatibility if you ever re-enable a text entry
        self._on_send()

    def _on_send(self):
        # Not used by the new desktop-style terminal, but left for compatibility
        cmd_text = self.last_command.strip()
        if not cmd_text:
            return
        self.history.append(cmd_text)
        self.history_index = None
        self.last_command = cmd_text
        self._append_terminal(f"> {cmd_text}\n")
        worker = MakroKernelWorker(cmd_text, self.q, self.logger)
        worker.start()

    def _on_history_up(self, event=None):
        if not self.history:
            return "break"
        if self.history_index is None:
            self.history_index = len(self.history) - 1
        else:
            self.history_index = max(0, self.history_index - 1)
        if hasattr(self, "last_cmd_var"):
            self.last_cmd_var.set(self.history[self.history_index])
        return "break"

    def _on_history_down(self, event=None):
        if not self.history or self.history_index is None:
            return "break"
        self.history_index = min(len(self.history) - 1, self.history_index + 1)
        if hasattr(self, "last_cmd_var"):
            self.last_cmd_var.set(self.history[self.history_index])
        return "break"

    # ========================================================================
    # KERNEL OPERATIONS
    # ========================================================================

    def _set_mode(self, mode: str):
        """Change MODE."""
        cmd = f"mode:{mode}"
        self._append_terminal(f"> {cmd}\n")
        worker = MakroKernelWorker(cmd, self.q, self.logger)
        worker.start()

    def _on_prop_command(self, action: str):
        """Handle proprietary commands."""
        if not getattr(flags, "EnableIntSoft", False):
            messagebox.showwarning(
                "Proprietary Disabled",
                "Proprietary features are not enabled."
            )
            return
        cmd = f"prop:{action}"
        self._append_terminal(f"> {cmd}\n")
        worker = MakroKernelWorker(cmd, self.q, self.logger)
        worker.start()

    def _update_flags_gui(self):
        """Sync flags."""
        flags.Inside_Thread = self.var_inside_thread.get()
        flags.Create_Graph = self.var_create_graph.get()
        flags.Runtime_Tracer = self.var_runtime_tracer.get()
        self._refresh_session_panel()
        self._refresh_config_display()
        self.logger.log("INFO", "Flags updated from GUI")

    # ========================================================================
    # CONTEXT MENUS
    # ========================================================================

    def _build_context_menus(self):
        """Build context menus."""
        self.term_menu = tk.Menu(
            self.root, tearoff=0,
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY
        )
        self.term_menu.add_command(
            label="Copy",
            command=lambda: self._ctx_copy(self.terminal_output)
        )
        self.term_menu.add_command(
            label="Paste",
            command=lambda: self._ctx_paste(None)  # no entry now
        )
        self.term_menu.add_separator()
        self.term_menu.add_command(label="Clear All", command=self.clear_terminal)
        self.terminal_output.bind(
            "<Button-3>",
            lambda e: self.term_menu.tk_popup(e.x_root, e.y_root)
        )

        self.log_menu = tk.Menu(
            self.root, tearoff=0,
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY
        )
        self.log_menu.add_command(
            label="Copy",
            command=lambda: self._ctx_copy(self.log_output)
        )
        self.log_menu.add_separator()
        self.log_menu.add_command(label="Clear All", command=self.clear_logs)
        self.log_output.bind(
            "<Button-3>",
            lambda e: self.log_menu.tk_popup(e.x_root, e.y_root)
        )

        self.fs_menu = tk.Menu(
            self.root, tearoff=0,
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY
        )
        self.fs_menu.add_command(label="Open Directory", command=self._ctx_open_fs)
        self.fs_menu.add_command(label="Copy Path", command=self._ctx_copy_fs_path)
        self.fs_menu.add_command(label="Refresh", command=self._refresh_fs_listing)
        self.fs_listbox.bind(
            "<Button-3>",
            lambda e: self.fs_menu.tk_popup(e.x_root, e.y_root)
        )

    def _ctx_copy(self, text_widget):
        """Copy selected text."""
        try:
            selection = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selection)
            self._append_log("Copied to clipboard")
        except tk.TclError:
            messagebox.showinfo("Copy", "No text selected")

    def _ctx_paste(self, _entry_widget):
        """Paste from clipboard (no direct entry in new terminal, so no-op)."""
        try:
            data = self.root.clipboard_get()
            # You could choose to append to last_cmd_var here if you want.
            if hasattr(self, "last_cmd_var"):
                current = self.last_cmd_var.get()
                self.last_cmd_var.set(current + data)
        except tk.TclError:
            messagebox.showwarning("Paste", "Nothing in clipboard")

    def _ctx_open_fs(self):
        """Open filesystem item."""
        selection = self.fs_listbox.curselection()
        if selection:
            item = self.fs_listbox.get(selection[0])
            path = os.path.join(self.current_directory, item)
            if os.path.isdir(path):
                self.current_directory = path
                self._refresh_fs_listing()

    def _ctx_copy_fs_path(self):
        """Copy filesystem path."""
        selection = self.fs_listbox.curselection()
        if selection:
            item = self.fs_listbox.get(selection[0])
            path = os.path.join(self.current_directory, item)
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            self._append_log(f"Copied: {path}")

    # ========================================================================
    # COMMAND PALETTE
    # ========================================================================

    def _open_command_palette(self):
        """Command palette."""
        palette = tk.Toplevel(self.root)
        palette.title("Command Palette")
        palette.geometry("400x350")
        palette.transient(self.root)
        palette.grab_set()
        palette.config(bg=DarkTheme.BG_SECONDARY)
        try:
            palette.attributes('-alpha', 0.96)
        except Exception:
            pass

        label = tk.Label(
            palette, text="Search commands (press Enter to run)",
            bg=DarkTheme.BG_SECONDARY, fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_text
        )
        label.pack(anchor="w", padx=8, pady=(8, 4))

        entry = tk.Entry(
            palette, font=self.font_mono,
            bg=DarkTheme.ENTRY_BG, fg=DarkTheme.TEXT_PRIMARY,
            insertbackground=DarkTheme.ACCENT_PRIMARY,
            relief=tk.FLAT, bd=1
        )
        entry.pack(fill=tk.X, padx=8, pady=(0, 8))

        listbox = tk.Listbox(
            palette, bg=DarkTheme.BG_PRIMARY, fg=DarkTheme.TEXT_PRIMARY,
            font=self.font_mono, activestyle='none',
            highlightthickness=0
        )
        listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        commands = [
            ("help", "Show help"),
            ("mode:1", "Switch to MODE 1"),
            ("mode:2", "Switch to MODE 2"),
            ("mode:3", "Switch to MODE 3"),
            ("mode:9", "Switch to MODE 9 (Makro)"),
            ("user:login", "User login"),
            ("user:status", "Show user status"),
            ("fs:get_folder", "Get folder dialog"),
            ("fs:list", "List current directory"),
            ("reload:credentials", "Reload credentials"),
            ("reload:flags", "Reload flags"),
            ("prop:open_dashboard", "Open proprietary dashboard"),
            ("prop:run_diag", "Run proprietary diagnostics"),
            ("prop:enable_trace", "Enable advanced trace"),
        ]

        for cmd, desc in commands:
            listbox.insert(tk.END, f"{cmd:25} {desc}")

        def run_selected(event=None):
            selection = listbox.curselection()
            if selection:
                item = listbox.get(selection[0])
                cmd = item.split()[0]
                self._run_command_from_button(cmd)
                palette.destroy()

        def on_filter(event=None):
            text = entry.get().strip().lower()
            listbox.delete(0, tk.END)
            for cmd, desc in commands:
                full = f"{cmd} {desc}".lower()
                if text in full:
                    listbox.insert(tk.END, f"{cmd:25} {desc}")

        entry.bind("<KeyRelease>", on_filter)
        listbox.bind("<Double-Button-1>", run_selected)
        listbox.bind("<Return>", run_selected)
        entry.focus_set()

    # ========================================================================
    # KEYBOARD SHORTCUTS
    # ========================================================================

    def _setup_keyboard_shortcuts(self):
        self.root.bind("<Control-l>", lambda e: self.clear_terminal())
        self.root.bind("<Control-L>", lambda e: self.clear_terminal())
        self.root.bind("<Control-p>", lambda e: self._open_command_palette())
        self.root.bind("<Control-P>", lambda e: self._open_command_palette())
        self.root.bind("<F9>", lambda e: self._set_mode("9"))
        self.root.bind("<F1>", lambda e: self._set_mode("1"))

    # ========================================================================
    # QUEUE PROCESSING
    # ========================================================================

    def _process_queue(self):
        """Process worker messages."""
        try:
            while True:
                ev = self.q.get_nowait()
                if not isinstance(ev, tuple) or len(ev) < 2:
                    continue
                etype = ev[0]

                if etype == "output":
                    self._append_terminal(ev[1])
                    self._append_log(ev[1].strip())
                elif etype == "error":
                    msg = f"ERROR: {ev[1]}"
                    self._append_terminal(msg + "\n")
                    self._append_log(msg)
                    if RD:
                        try:
                            RD.CommandShow("Error occurred").Show('FAIL')
                        except Exception:
                            pass
                elif etype == "status":
                    self.status_var.set(ev[1])
                elif etype == "done":
                    self.status_var.set(f"Done: {ev[1]}")
                elif etype == "log":
                    level, msg = ev[1], ev[2]
                    self._append_log(f"{level}: {msg}")
                elif etype == "flags_changed":
                    self._refresh_session_panel()
                    self._refresh_config_display()
                    if getattr(flags, "EnableIntSoft", False):
                        self.proprietary_frame.pack(fill=tk.X, padx=8, pady=8)
                    else:
                        self.proprietary_frame.pack_forget()
                elif etype == "credentials_updated":
                    self._load_credentials()
                    self._refresh_session_panel()
                elif etype == "user_updated":
                    self._load_credentials()
                    self._refresh_session_panel()
                elif etype == "fs_result":
                    self.current_directory = ev[1]
                    self._refresh_fs_listing()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._process_queue)

    # ========================================================================
    # EXIT
    # ========================================================================

    def _on_exit(self):
        if messagebox.askokcancel("Exit", "Quit Makro Kernel GUI?"):
            self.logger.log("INFO", "GUI closing")
            try:
                self.root.quit()
            except Exception:
                pass


# ============================================================================
# ENTRYPOINT
# ============================================================================

def start_makro_gui():
    """Launch the GUI."""
    try:
        if not getattr(flags, "Fully_GUI", False):
            flags.Fully_GUI = True
    except Exception:
        pass

    try:
        root = tk.Tk()
    except Exception as e:
        print(f"Tkinter not available: {e}")
        return

    app = MakroKernelGUI(root)
    root.mainloop()


if __name__ == "__main__":
    start_makro_gui()
