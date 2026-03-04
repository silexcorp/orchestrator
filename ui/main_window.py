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
        self._load_session()
        self._setup_toolbar()

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

        # Vertical Splitter to add Terminal at bottom
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        self.v_splitter.addWidget(self.h_splitter)
        
        self.terminal = TerminalWidget(self.workspace_manager.get_root() or os.getcwd())
        self.v_splitter.addWidget(self.terminal)
        
        main_layout.addWidget(self.v_splitter)

        # Initial sizes: Sidebar 200px, Rest 1000px; Editor/Chat splitting equal; Terminal 20%
        self.h_splitter.setSizes([200, 1000])
        self.editor_chat_splitter.setSizes([600, 400])
        self.v_splitter.setSizes([600, 200])

        # Status Bar
        self.setStatusBar(QStatusBar())

    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # File Actions
        file_menu = self.menuBar().addMenu("&Archivo")
        
        open_folder_act = QAction("Abrir Carpeta...", self)
        open_folder_act.setShortcut("Ctrl+Shift+O")
        open_folder_act.triggered.connect(self._open_folder_dialog)
        file_menu.addAction(open_folder_act)
        toolbar.addAction(open_folder_act)

        save_act = QAction("Guardar", self)
        save_act.setShortcut("Ctrl+S")
        save_act.triggered.connect(self.editor.save_file)
        file_menu.addAction(save_act)
        toolbar.addAction(save_act)
        
        self.recent_menu = file_menu.addMenu("Carpetas Recientes")
        self._update_recent_menu()

        toolbar.addSeparator()

        # Model Selector
        toolbar.addWidget(QLabel(" Modelo: "))
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

    def _open_folder_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
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
            
            # Restore Model
            self.last_model = state.get("last_model")

    def _save_session(self):
        open_files = []
        for i in range(self.editor.count()):
            open_files.append(self.editor.widget(i).file_path)
            
        state = {
            "last_workspace": self.workspace_manager.get_root(),
            "last_model": self.model_combo.currentText(),
            "open_files": open_files,
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
                res = QMessageBox.question(self, "Guardar cambios", 
                                         f"¿Deseas guardar los cambios en {os.path.basename(editor.file_path)}?",
                                         QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
                if res == QMessageBox.StandardButton.Save:
                    self.editor.save_file(i)
                elif res == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
        
        self._save_session()
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

    def _check_ollama_connection(self):
        client = OllamaClient()
        if client.is_connected():
            self.status_indicator.setStyleSheet("color: #3fb950; font-size: 18px; padding-right: 10px;")
        else:
            self.status_indicator.setStyleSheet("color: #f85149; font-size: 18px; padding-right: 10px;")
