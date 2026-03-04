import json
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from .chat_view import ChatView, MessageBubble
from core.agent import Agent

class AgentWorker(QThread):
    event_received = pyqtSignal(dict)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, agent: Agent, user_input: str):
        super().__init__()
        self.agent = agent
        self.user_input = user_input

    def run(self):
        try:
            for event in self.agent.run(self.user_input):
                self.event_received.emit(event)
            self.finished.emit("Done")
        except Exception as e:
            self.error.emit(str(e))

class AgentChatWidget(ChatView):
    file_created = pyqtSignal(str)
    command_run = pyqtSignal(str)

    def __init__(self, workspace_path: str, model_name: str = "qwen2.5-coder:7b", parent=None):
        super().__init__(parent)
        self.workspace_path = workspace_path
        self.agent = Agent(workspace_path, model_name)
        self.worker = None

    def _submit_text(self, text: str) -> None:
        """Override to start the agent instead of normal streaming."""
        self._add_bubble(text, "user")
        self.welcome_widget.setVisible(False)
        self.scroll.setVisible(True)
        
        self.input.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.worker = AgentWorker(self.agent, text)
        self.worker.event_received.connect(self.handle_agent_event)
        self.worker.finished.connect(self.handle_agent_finished)
        self.worker.error.connect(self.handle_agent_error)
        self.worker.start()

    def handle_agent_event(self, event: dict):
        etype = event.get("type")
        content = event.get("content", "")

        if etype == "thought":
            self.add_thought_bubble(content)
        elif etype == "action":
            action = event.get("action")
            params = event.get("params", {})
            self.add_action_bubble(action, params)
            
            # Emit signals for main window integration
            if action == "create_file":
                self.file_created.emit(params.get("path"))
            elif action == "run_command":
                self.command_run.emit(params.get("command"))
                
        elif etype == "observation":
            self.add_observation_bubble(content)
        elif etype == "final":
            self._add_bubble(content, "assistant")
        elif etype == "error":
            self._on_error(content)

    def handle_agent_finished(self):
        self.input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input.setFocus()

    def handle_agent_error(self, err_msg: str):
        self._on_error(err_msg)
        self.handle_agent_finished()

    def add_thought_bubble(self, content):
        bubble = QFrame()
        bubble.setStyleSheet("background-color: #161b22; border-radius: 8px; border: 1px solid #30363d; margin: 4px;")
        layout = QVBoxLayout(bubble)
        label = QLabel(f"🧠 <i>Pensando...</i><br><small>{content}</small>")
        label.setStyleSheet("color: #8b949e;")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)

    def add_action_bubble(self, action, params):
        bubble = QFrame()
        bubble.setStyleSheet("background-color: #d29922; border-radius: 8px; color: #0d1117; margin: 4px;")
        layout = QVBoxLayout(bubble)
        param_str = json.dumps(params, indent=2)
        label = QLabel(f"⚙️ <b>Acción: {action}</b><br><pre>{param_str}</pre>")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)

    def add_observation_bubble(self, content):
        bubble = QFrame()
        bubble.setStyleSheet("background-color: #238636; border-radius: 8px; color: white; margin: 4px;")
        layout = QVBoxLayout(bubble)
        # Truncate long observations
        display_content = (content[:500] + '...') if len(content) > 500 else content
        label = QLabel(f"👁️ <b>Observación:</b><br><pre>{display_content}</pre>")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)
