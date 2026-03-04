import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit
from PyQt6.QtCore import QProcess, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor

class TerminalWidget(QWidget):
    def __init__(self, workspace_path: str, parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path
        self.history = []
        self.history_index = -1

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Output Area
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("JetBrains Mono", 10))
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d1117;
                color: #e6edf3;
                border: none;
            }
        """)
        self.layout.addWidget(self.output)

        # Input Area
        self.input = QLineEdit()
        self.input.setFont(QFont("JetBrains Mono", 10))
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #161b22;
                color: #58a6ff;
                border: none;
                padding: 5px;
            }
        """)
        self.input.returnPressed.connect(self.handle_command)
        self.layout.addWidget(self.input)

        # Setup Process
        self.process = QProcess(self)
        self.process.setWorkingDirectory(self.workspace_path)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        self.process.finished.connect(self.process_finished)

        self.append_text("❯ Terminal Ready.\n", "#3fb950")

    def handle_command(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        
        self.history.append(cmd)
        self.history_index = len(self.history)
        self.input.clear()
        
        self.append_text(f"❯ {cmd}\n", "#58a6ff")
        self.run_command(cmd)

    def run_command(self, cmd: str):
        if not cmd or not cmd.strip():
            return
            
        if self.process.state() == QProcess.ProcessState.Running:
            self.append_text("Process already running. Wait or stop it.\n", "#f85149")
            return
        
        # Simple parsing for 'cd' though we target workspace
        if cmd.startswith("cd "):
            path = cmd[3:].strip()
            self.workspace_path = os.path.abspath(os.path.join(self.workspace_path, path))
            self.process.setWorkingDirectory(self.workspace_path)
            self.append_text(f"Working directory changed to {self.workspace_path}\n", "#8b949e")
            return

        self.process.startCommand(cmd)

    def read_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.append_text(data)

    def read_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.append_text(data, "#f85149")

    def process_finished(self):
        self.append_text("\n[Process Finished]\n", "#8b949e")

    def append_text(self, text, color=None):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color:
            fmt = cursor.charFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
        
        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def stop(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.input.setText(self.history[self.history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.input.setText(self.history[self.history_index])
            else:
                self.history_index = len(self.history)
                self.input.clear()
        super().keyPressEvent(event)

