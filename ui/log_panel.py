import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QColor

class LogPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(4)

        # Header
        header_layout = QHBoxLayout()
        self.title = QLabel("AGENT ACTIVITY LOG")
        self.title.setStyleSheet("""
            color: #00f2ff;
            font-weight: bold;
            font-size: 9pt;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        # Log Display
        self.log_display = QPlainTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("""
            background-color: #05060a;
            border: 1px solid rgba(0, 242, 255, 0.1);
            border-radius: 8px;
            font-family: 'Cascadia Code', 'Consolas', 'Monaco', monospace;
            font-size: 9pt;
            color: #b4b4b4;
        """)
        self.layout.addWidget(self.log_display)

    def append_log(self, etype: str, content: str):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Color based on event type
        color = "#b4b4b4" # Default
        if etype == "thought":
            color = "#8a2be2" # Purple
            prefix = "THOUGHT"
        elif etype == "action":
            color = "#00f2ff" # Cyan
            prefix = "ACTION"
        elif etype == "observation":
            color = "#3fb950" # Green
            prefix = "OBSERVE"
        elif etype == "error":
            color = "#f85149" # Red
            prefix = "ERROR"
        else:
            prefix = etype.upper()

        log_entry = f"[{timestamp}] <span style='color: {color}; font-weight: bold;'>{prefix}:</span> {content}"
        
        self.log_display.appendHtml(log_entry)
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)
