"""
watchers_view.py — UI for managing folder watchers.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QLineEdit, QFileDialog, QCheckBox
)
from PyQt6.QtCore import pyqtSignal
from core.watcher_service import watcher_service
from models.schedule import Watcher

class WatchersView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("Folder Watchers (Automations)"))
        
        self.list = QListWidget()
        layout.addWidget(self.list)
        
        form = QVBoxLayout()
        self.path_edit = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)
        
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse_btn)
        form.addLayout(path_row)
        
        self.recursive_cb = QCheckBox("Recursive")
        form.addWidget(self.recursive_cb)
        
        add_btn = QPushButton("Add Watcher")
        add_btn.setObjectName("sendBtn")
        add_btn.clicked.connect(self._add)
        form.addWidget(add_btn)
        
        layout.addLayout(form)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if path:
            self.path_edit.setText(path)

    def _add(self) -> None:
        path = self.path_edit.text()
        if path:
            w = Watcher(folder_path=path, recursive=self.recursive_cb.isChecked())
            self.list.addItem(f"Watching: {path}")
            # In a real app, we'd save this to a store first
            watcher_service.start_watcher(w, lambda wid, p: print(f"Change in {p}"))
            self.path_edit.clear()
