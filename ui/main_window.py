import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QComboBox, QLabel, QFileDialog, QToolBar,
    QStatusBar, QApplication, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon

from ui.editor_widget import EditorWidget
from ui.terminal_widget import TerminalWidget
from ui.chat_widget import AgentChatWidget
from core.ollama_client import OllamaClient

WORKSPACE_PATH = os.path.expanduser("~/nova_workspace")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orchestrator AI Code Editor")
        self.resize(1200, 800)
        
        if not os.path.exists(WORKSPACE_PATH):
            os.makedirs(WORKSPACE_PATH)

        self.ollama_client = OllamaClient()
        
        self._setup_ui()
        self._setup_toolbar()
        self._connect_signals()
        
        # Initial refresh
        QTimer.singleShot(500, self.refresh_models)
        self.check_ollama_status()
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.check_ollama_status)
        self.status_timer.start(5000)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main Vertical Splitter (Editor+Chat vs Terminal)
        self.v_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Horizontal Splitter (Editor vs Chat)
        self.h_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.editor = EditorWidget()
        self.chat = AgentChatWidget(WORKSPACE_PATH)
        
        self.h_splitter.addWidget(self.editor)
        self.h_splitter.addWidget(self.chat)
        self.h_splitter.setSizes([700, 500])
        
        self.terminal = TerminalWidget(WORKSPACE_PATH)
        self.terminal.setMinimumHeight(150)
        
        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.terminal)
        self.v_splitter.setSizes([600, 200])
        
        layout.addWidget(self.v_splitter)

    def _setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # File actions
        open_act = QAction("Abrir", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_act)

        save_act = QAction("Guardar", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self.save_file)
        toolbar.addAction(save_act)

        toolbar.addSeparator()

        # Execute actions
        self.exec_btn = QPushButton("▶ Ejecutar")
        self.exec_btn.setStyleSheet("background-color: #3fb950; color: white; border-radius: 4px; padding: 4px 8px;")
        self.exec_btn.clicked.connect(self.run_current_file)
        toolbar.addWidget(self.exec_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setStyleSheet("background-color: #f85149; color: white; border-radius: 4px; padding: 4px 8px; margin-left: 5px;")
        self.stop_btn.clicked.connect(self.terminal.stop)
        toolbar.addWidget(self.stop_btn)

        toolbar.addSeparator()

        # Model selection
        toolbar.addWidget(QLabel(" Modelo: "))
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        toolbar.addWidget(self.model_combo)

        # Status indicator
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: gray; font-size: 18px; padding-right: 10px;")
        toolbar.addWidget(self.status_indicator)

    def _connect_signals(self):
        self.chat.file_created.connect(self.open_agent_file)
        self.chat.command_run.connect(self.terminal.run_command)

        # Shortcuts
        self.terminal_toggle_act = QAction("Toggle Terminal", self)
        self.terminal_toggle_act.setShortcut(QKeySequence("Ctrl+`"))
        self.terminal_toggle_act.triggered.connect(self.toggle_terminal)
        self.addAction(self.terminal_toggle_act)
        
        self.run_act = QAction("Run Script", self)
        self.run_act.setShortcut(QKeySequence("F5"))
        self.run_act.triggered.connect(self.run_current_file)
        self.addAction(self.run_act)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", WORKSPACE_PATH)
        if path:
            self.editor.open_file(path)

    def save_file(self):
        if not self.editor.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "Save File", WORKSPACE_PATH)
            if path:
                self.editor.current_file = path
                self.editor.save_file()
        else:
            self.editor.save_file()

    def open_agent_file(self, path):
        full_path = os.path.join(WORKSPACE_PATH, path)
        if os.path.exists(full_path):
            self.editor.open_file(full_path)

    def run_current_file(self):
        if self.editor.current_file:
            self.editor.save_file()
            self.terminal.run_command(f"python3 {self.editor.current_file}")
        else:
            QMessageBox.warning(self, "Error", "Guarda el archivo primero")

    def toggle_terminal(self):
        if self.v_splitter.sizes()[1] == 0:
            self.v_splitter.setSizes([600, 200])
        else:
            self.v_splitter.setSizes([800, 0])

    def refresh_models(self):
        models = self.ollama_client.list_models()
        self.model_combo.clear()
        self.model_combo.addItems(models)
        if "qwen2.5-coder:7b" in models:
            self.model_combo.setCurrentText("qwen2.5-coder:7b")

    def on_model_changed(self, model_name):
        self.chat.agent.ollama.set_model(model_name)

    def check_ollama_status(self):
        if self.ollama_client.check_connection():
            self.status_indicator.setStyleSheet("color: #3fb950; font-size: 18px; padding-right: 10px;")
        else:
            self.status_indicator.setStyleSheet("color: #f85149; font-size: 18px; padding-right: 10px;")

