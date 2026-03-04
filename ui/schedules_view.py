"""
schedules_view.py — UI for managing scheduled agent tasks.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
    QPushButton, QLabel, QLineEdit, QComboBox
)
from core.schedule_service import schedule_service
from models.schedule import Schedule

class SchedulesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("Scheduled Tasks (CRON)"))
        
        self.list = QListWidget()
        layout.addWidget(self.list)
        
        form = QVBoxLayout()
        self.cron_edit = QLineEdit("0 * * * *")
        layout.addWidget(QLabel("Cron Expression (m h dom mon dow):"))
        layout.addWidget(self.cron_edit)
        
        self.prompt_edit = QLineEdit()
        layout.addWidget(QLabel("Prompt to trigger:"))
        layout.addWidget(self.prompt_edit)
        
        add_btn = QPushButton("Add Schedule")
        add_btn.setObjectName("sendBtn")
        add_btn.clicked.connect(self._add)
        form.addWidget(add_btn)
        
        layout.addLayout(form)

    def _add(self) -> None:
        cron = self.cron_edit.text()
        prompt = self.prompt_edit.text()
        if cron and prompt:
            s = Schedule(cron_expression=cron, frequency="cron")
            self.list.addItem(f"[{cron}] {prompt}")
            # Simplified: just registering with current callback
            schedule_service.add_schedule(s, lambda sched: print(f"Triggering: {prompt}"))
            self.prompt_edit.clear()
