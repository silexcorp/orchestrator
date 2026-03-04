"""
server_view.py — UI for controlling the MCP Server.
"""
from __future__ import annotations

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
)
from core.mcp_server import run_server

class ServerView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._server_thread = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("Orchestrator MCP Server"))
        layout.addWidget(QLabel("Exposes an OpenAI-compatible API at:"))
        
        self.url_label = QLabel("http://127.0.0.1:8080/v1")
        self.url_label.setStyleSheet("font-family: monospace; color: #a78bfa; font-size: 14px;")
        layout.addWidget(self.url_label)
        
        self.port_edit = QLineEdit("8080")
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_edit)
        
        self.start_btn = QPushButton("Start Server")
        self.start_btn.setObjectName("sendBtn")
        self.start_btn.clicked.connect(self._toggle_server)
        layout.addWidget(self.start_btn)
        
        layout.addStretch()

    def _toggle_server(self) -> None:
        if self._server_thread and self._server_thread.is_alive():
            # In a real app, we would kill the uvicorn process
            self.start_btn.setText("Start Server")
            self.url_label.setText("Server Stopped")
        else:
            port = int(self.port_edit.text())
            self._server_thread = threading.Thread(
                target=run_server, 
                args=("127.0.0.1", port), 
                daemon=True
            )
            self._server_thread.start()
            self.start_btn.setText("Stop Server")
            self.url_label.setText(f"Running at http://127.0.0.1:{port}/v1")
