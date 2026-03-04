import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QComboBox, QLabel, QFileDialog, QToolBar,
    QStatusBar, QApplication, QMessageBox, QSizePolicy, QMenu
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon

from ui.editor_widget import EditorWidget
from ui.terminal_widget import TerminalWidget
from ui.chat_widget import AgentChatWidget
from ui.file_tree import FileTreeWidget
from ui.log_panel import LogPanel
from ui.settings_dialog import SettingsDialog
from core.ollama_client import OllamaClient
from core.workspace import WorkspaceManager
from core.session import SessionManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orchestrator AI Code Editor")
        self.resize(1200, 800)
        
        self.workspace_manager = WorkspaceManager()
        self.session_manager = SessionManager()
        
        self._setup_ui()
        self._setup_toolbar()
        self._load_session()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Horizontal Splitter for Sidebar | (Editor | Chat)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar (File Tree)
        self.file_tree = FileTreeWidget()
        self.file_tree.file_clicked.connect(self._on_file_selected)
        self.h_splitter.addWidget(self.file_tree)

        # Nested Splitter for Editor | Chat
        self.editor_chat_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.editor = EditorWidget()
        self.editor.active_file_changed.connect(self._on_active_file_changed)
        self.editor_chat_splitter.addWidget(self.editor)

        self.chat = AgentChatWidget(self.workspace_manager)
        self.chat.file_created.connect(lambda p: self.file_tree.refresh())
        self.editor_chat_splitter.addWidget(self.chat)
        
        self.h_splitter.addWidget(self.editor_chat_splitter)

        # Vertical Splitter for top/bottom
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h_splitter)

        # Sub-splitter for Terminal | Log Panel
        self.bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.terminal = TerminalWidget(self.workspace_manager.get_root() or os.getcwd())
        self.bottom_splitter.addWidget(self.terminal)
        
        self.log_panel = LogPanel()
        self.bottom_splitter.addWidget(self.log_panel)
        
        self.v_splitter.addWidget(self.bottom_splitter)
        
        main_layout.addWidget(self.v_splitter)

        # Connect agent events to log panel
        self.chat.agent_event.connect(self.log_panel.append_log)
        
        # Connect agent terminal commands to terminal widget
        self.chat.command_run.connect(self.terminal.run_command)

        # Initial sizes: Sidebar 200px, Rest 1000px; Editor/Chat splitting equal; Terminal/Log 50/50; Bottom 25%
        self.h_splitter.setSizes([200, 1000])
        self.editor_chat_splitter.setSizes([600, 400])
        self.bottom_splitter.setSizes([600, 400])
        self.v_splitter.setSizes([600, 200])

        # Status Bar
        self.setStatusBar(QStatusBar())

    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # File Actions
        file_menu = self.menuBar().addMenu("&File")
        
        open_folder_act = QAction("Open Folder...", self)
        open_folder_act.setShortcut("Ctrl+Shift+O")
        open_folder_act.triggered.connect(self._open_folder_dialog)
        file_menu.addAction(open_folder_act)
        toolbar.addAction(open_folder_act)

        save_act = QAction("Save", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.editor.save_file)
        file_menu.addAction(save_act)
        toolbar.addAction(save_act)
        
        self.recent_menu = file_menu.addMenu("Recent Folders")
        self._update_recent_menu()

        # Edit Actions
        edit_menu = self.menuBar().addMenu("&Edit")
        
        settings_act = QAction("Settings...", self)
        settings_act.setShortcut("Ctrl+,")
        settings_act.triggered.connect(self._show_settings)
        edit_menu.addAction(settings_act)

        # View Actions (Toggle Panels)
        view_menu = self.menuBar().addMenu("&View")
        self.toggle_actions = {}
        
        panels = [
            ("File Explorer", self.file_tree),
            ("Code Editor", self.editor),
            ("Agent Chat", self.chat),
            ("Chat History Sidebar", None),
            ("Terminal", self.terminal),
            ("Log Panel", self.log_panel)
        ]
        
        for name, widget in panels:
            act = QAction(name, self, checkable=True)
            act.setChecked(True)
            act.triggered.connect(lambda checked, w=widget, n=name: self._toggle_panel(n, checked))
            view_menu.addAction(act)
            self.toggle_actions[name] = act

        toolbar.addSeparator()

        # Model Selector
        toolbar.addWidget(QLabel(" Model: "))
        self.model_combo = QComboBox()
        self.model_combo.setFixedWidth(150)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        self._populate_models()
        toolbar.addWidget(self.model_combo)

        # Status indicator
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: gray; font-size: 18px; padding-right: 10px;")
        toolbar.addWidget(self.status_indicator)

        # Connection Timer
        self.conn_timer = QTimer()
        self.conn_timer.timeout.connect(self._check_ollama_connection)
        self.conn_timer.start(5000)

    def _toggle_panel(self, name, visible):
        widget_map = {
            "File Explorer": self.file_tree,
            "Code Editor": self.editor,
            "Agent Chat": self.chat,
            "Chat History Sidebar": None, # Handled specially
            "Terminal": self.terminal,
            "Log Panel": self.log_panel
        }
        
        if name == "Chat History Sidebar":
            self.chat.set_sidebar_visible(visible)
            return

        widget = widget_map.get(name)
        if widget:
            widget.setVisible(visible)
            
            # Special case: If all bottom panels are hidden, hide the bottom splitter
            if name in ["Terminal", "Log Panel"]:
                # Use isHidden() or the 'visible' parameter directly to avoid recursive visibility issues
                has_terminal = visible if name == "Terminal" else not self.terminal.isHidden()
                has_log = visible if name == "Log Panel" else not self.log_panel.isHidden()
                self.bottom_splitter.setVisible(has_terminal or has_log)

    def _open_folder_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self._open_workspace(path)

    def _open_workspace(self, path):
        self.workspace_manager.open_folder(path)
        self.file_tree.set_root(path)
        self.terminal.process.setWorkingDirectory(path)
        self.session_manager.add_recent_workspace(path)
        self._update_recent_menu()
        self.statusBar().showMessage(f"Workspace: {path}")

    def _on_file_selected(self, path):
        self.editor.open_file(path)

    def _on_active_file_changed(self, path, content):
        self.workspace_manager.set_active_file(path, content)
        self.file_tree.highlight_file(path)

    def _update_recent_menu(self):
        if not hasattr(self, 'recent_menu'):
            return
        self.recent_menu.clear()
        recent = self.session_manager.get_recent_workspaces()
        for path in recent:
            act = self.recent_menu.addAction(path)
            act.triggered.connect(lambda checked, p=path: self._open_workspace(p))

    def _load_session(self):
        state = self.session_manager.load()
        if state:
            # Restore Workspace
            last_ws = state.get("last_workspace")
            if last_ws and os.path.exists(last_ws):
                self._open_workspace(last_ws)
            
            # Restore Files
            for f in state.get("open_files", []):
                if os.path.exists(f):
                    self.editor.open_file(f)
            
            # Restore Layout
            if "splitter_sizes" in state:
                h_sizes = state["splitter_sizes"].get("horizontal")
                if h_sizes: self.h_splitter.setSizes(h_sizes)
                v_sizes = state["splitter_sizes"].get("vertical")
                if v_sizes: self.v_splitter.setSizes(v_sizes)
            
            # Restore Panel Visibility
            visibility = state.get("panel_visibility", {})
            for name, is_visible in visibility.items():
                if name in self.toggle_actions:
                    self.toggle_actions[name].setChecked(is_visible)
                    self._toggle_panel(name, is_visible)

            # Restore Model
            self.last_model = state.get("last_model")

    def _save_session(self):
        open_files = []
        for i in range(self.editor.count()):
            open_files.append(self.editor.widget(i).file_path)
            
        visibility = {name: act.isChecked() for name, act in self.toggle_actions.items()}

        state = {
            "last_workspace": self.workspace_manager.get_root(),
            "last_model": self.model_combo.currentText(),
            "open_files": open_files,
            "panel_visibility": visibility,
            "splitter_sizes": {
                "horizontal": self.h_splitter.sizes(),
                "vertical": self.v_splitter.sizes()
            }
        }
        self.session_manager.save(state)

    def closeEvent(self, event):
        # Check for unsaved changes
        for i in range(self.editor.count()):
            editor = self.editor.widget(i)
            if editor.dirty:
                res = QMessageBox.question(self, "Save changes", 
                                         f"Do you want to save changes in {os.path.basename(editor.file_path)}?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
                if res == QMessageBox.StandardButton.Save:
                    self.editor.save_file(i)
                elif res == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
        
        self._save_session()
        
        # Unload model to free memory
        try:
            current_model = self.model_combo.currentText()
            if current_model:
                client = OllamaClient()
                client.unload_model(current_model)
        except Exception as e:
            print(f"Could not unload model on close: {e}")
            
        super().closeEvent(event)

    def _populate_models(self):
        client = OllamaClient()
        models = client.list_models()
        self.model_combo.addItems(models)
        
        # Try to restore last model, else fallback to default
        restored_model = getattr(self, 'last_model', None)
        if restored_model and restored_model in models:
            self.model_combo.setCurrentText(restored_model)
        elif "qwen2.5-coder:7b" in models:
            self.model_combo.setCurrentText("qwen2.5-coder:7b")
        elif models:
            self.model_combo.setCurrentIndex(0)

    def _on_model_changed(self, model_name):
        self.chat.agent.ollama.model = model_name

    def _show_settings(self):
        diag = SettingsDialog(self)
        if diag.exec():
            # Refresh agent if necessary
            self.chat.agent.config_manager.load()
            active_agent = self.chat.agent.config_manager.get_active_agent()
            self.chat.agent.system_prompt = active_agent.get("prompt")
            self.chat.agent.name = active_agent.get("name")

    def _check_ollama_connection(self):
        client = OllamaClient()
        if client.is_connected():
            self.status_indicator.setStyleSheet("color: #3fb950; font-size: 18px; padding-right: 10px;")
        else:
            self.status_indicator.setStyleSheet("color: #f85149; font-size: 18px; padding-right: 10px;")
