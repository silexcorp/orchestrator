"""
skills_view.py — UI for managing AI skills.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QTextEdit, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from core.skill_store import skill_store
from models.schedule import Skill

class SkillsView(QWidget):
    skills_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        
        # Left side: List
        left = QVBoxLayout()
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_select)
        left.addWidget(QLabel("Skills"))
        left.addWidget(self.list)
        
        btn_row = QHBoxLayout()
        import_btn = QPushButton("Import...")
        import_btn.clicked.connect(self._import)
        btn_row.addWidget(import_btn)
        left.addLayout(btn_row)
        
        layout.addLayout(left, 1)
        
        # Right side: Editor
        right = QVBoxLayout()
        self.editor = QTextEdit()
        right.addWidget(QLabel("Skill Content (Markdown)"))
        right.addWidget(self.editor)
        
        save_btn = QPushButton("Save Skill")
        save_btn.clicked.connect(self._save)
        right.addWidget(save_btn)
        
        layout.addLayout(right, 2)

    def _refresh_list(self) -> None:
        self.list.clear()
        for s in skill_store.all():
            self.list.addItem(s.name)

    def _on_select(self, row: int) -> None:
        skills = skill_store.all()
        if 0 <= row < len(skills):
            self.editor.setPlainText(skills[row].content)

    def _save(self) -> None:
        row = self.list.currentRow()
        skills = skill_store.all()
        if 0 <= row < len(skills):
            skill = skills[row]
            skill.content = self.editor.toPlainText()
            skill_store.save(skill)
            self.skills_changed.emit()

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Import Skill", "", "Markdown Files (*.md)")
        if path:
            from pathlib import Path
            skill_store.import_from_file(Path(path))
            self._refresh_list()
            self.skills_changed.emit()
