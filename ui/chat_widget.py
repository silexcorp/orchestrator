import json
import os
import re
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
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
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            for event in self.agent.run(self.user_input):
                if not self._is_running:
                    break
                self.event_received.emit(event)
            self.finished.emit("Done")
        except Exception as e:
            self.error.emit(str(e))

from core.session import SessionManager
import uuid
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QListWidget, QListWidgetItem, QPushButton, QSplitter
)

class AgentChatWidget(QWidget): # Changed from ChatView to QWidget to hold sidebar
    file_created = pyqtSignal(str)
    command_run = pyqtSignal(str)
    agent_event = pyqtSignal(str, str)

    def __init__(self, workspace_manager, model_name: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.workspace_manager = workspace_manager
        self.session_manager = SessionManager()
        self.agent = Agent(workspace_manager, model_name)
        self.worker = None
        self.current_chat_id = None
        
        self._setup_ui()
        self._load_chats()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #0d0f17;
                border-right: 1px solid rgba(0, 242, 255, 0.1);
            }
        """)
        
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(8, 16, 8, 16)
        
        new_btn = QPushButton("+ New Chat")
        new_btn.setObjectName("sendBtn")
        new_btn.setFixedHeight(36)
        new_btn.clicked.connect(self._new_chat)
        side_layout.addWidget(new_btn)
        
        side_layout.addWidget(QLabel("Recent Chats"))
        
        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget { background: transparent; border: none; }
            QListWidget::item { color: #f0f4f8; padding: 10px; border-radius: 8px; }
            QListWidget::item:selected { background: rgba(138, 43, 226, 0.2); }
        """)
        self.chat_list.currentRowChanged.connect(self._on_chat_selected)
        side_layout.addWidget(self.chat_list)
        
        delete_btn = QPushButton("Delete Chat")
        delete_btn.setStyleSheet("color: #f85149; background: transparent; border: 1px solid rgba(248,81,73,0.3);")
        delete_btn.clicked.connect(self._delete_current_chat)
        side_layout.addWidget(delete_btn)
        
        # --- Chat Area ---
        self.chat_view = ChatView()
        self.chat_view.message_submitted.connect(self._submit_text)
        self.chat_view.stop_requested.connect(self._on_stop_requested)
        
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.chat_view)
        main_layout.addWidget(self.splitter)

    def _load_chats(self):
        self.chat_list.clear()
        chats = self.session_manager.get_chats()
        for chat in chats:
            item = QListWidgetItem(chat["title"])
            item.setData(Qt.ItemDataRole.UserRole, chat["id"])
            self.chat_list.addItem(item)
            
        # Restore last active chat
        session_state = self.session_manager.load()
        last_id = session_state.get("active_chat_id")
        
        if last_id:
            for i in range(self.chat_list.count()):
                if self.chat_list.item(i).data(Qt.ItemDataRole.UserRole) == last_id:
                    self.chat_list.setCurrentRow(i)
                    return
        
        if self.chat_list.count() == 0:
            self._new_chat()
        else:
            self.chat_list.setCurrentRow(0)

    def _on_chat_selected(self, index):
        if index < 0: return
        item = self.chat_list.currentItem()
        if not item: return
        
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        if chat_id == self.current_chat_id: return
        
        self.current_chat_id = chat_id
        chat_data = self.session_manager.load_chat(chat_id)
        
        if chat_data:
            self.agent.set_history(chat_data.get("history", []))
            self.chat_view.clear_messages()
            self._render_history(chat_data.get("history", []))
            
            # Persist active chat ID
            state = self.session_manager.load()
            state["active_chat_id"] = chat_id
            self.session_manager.save(state)

    def set_sidebar_visible(self, visible: bool):
        self.sidebar.setVisible(visible)

    def _render_history(self, history):
        if not history:
            self.chat_view.welcome_widget.show()
            self.chat_view.scroll.hide()
            return
            
        self.chat_view.welcome_widget.hide()
        self.chat_view.scroll.show()
        
        for turn in history:
            role = turn.get("role")
            content = turn.get("content")
            if role == "user":
                self.chat_view._add_bubble(content, "user")
            elif role == "assistant":
                # Try to parse as agent JSON
                try:
                    import re
                    # Strip <think> if present (though history usually has final JSON)
                    clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                    # Find outermost JSON
                    start = clean_content.find('{')
                    end = clean_content.rfind('}')
                    if start != -1 and end != -1:
                        data = json.loads(clean_content[start:end+1])
                        thought = data.get("thought")
                        action = data.get("action")
                        params = data.get("params", {})
                        
                        if thought: self.chat_view.add_thought_bubble(thought)
                        if action and action != "finish":
                             self.chat_view.add_action_bubble(action, params)
                             # Note: observations are usually separate "user" turns in ReAct
                        
                        # Use finish content or fallback to full text
                        final_text = params.get("content") or content
                        if action == "finish" or not action:
                            self.chat_view._add_bubble(final_text, "assistant")
                    else:
                        self.chat_view._add_bubble(content, "assistant")
                except:
                    self.chat_view._add_bubble(content, "assistant")
            elif role == "observation": # Handle observation role if it exists in history
                self.chat_view.add_observation_bubble(content)

    def _new_chat(self):
        new_id = str(uuid.uuid4())
        self.session_manager.save_chat(new_id, [], "New Chat")
        
        item = QListWidgetItem("New Chat")
        item.setData(Qt.ItemDataRole.UserRole, new_id)
        self.chat_list.addItem(item)
        self.chat_list.setCurrentRow(self.chat_list.count() - 1)

    def clear_session(self):
        """Clear current chat session and memory for a fresh start."""
        self.agent.history = []
        self.chat_view.clear_messages()
        self.chat_view.welcome_widget.show()
        self.chat_view.scroll.hide()
        self._new_chat()

    def _delete_current_chat(self):
        row = self.chat_list.currentRow()
        if row < 0: return
        
        item = self.chat_list.item(row)
        if not item: return
        
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        self.session_manager.delete_chat(chat_id)
        self.chat_list.takeItem(row)
        self.current_chat_id = None
        
        if self.chat_list.count() == 0:
            self._new_chat()
        else:
            new_row = max(0, row - 1)
            self.chat_list.setCurrentRow(new_row)
            # Signal currentRowChanged will handle _on_chat_selected automatically
            # if index changed. If it didn't (e.g. from 0 to 0), we call it manually
            if row == 0:
                self._on_chat_selected(0)

    def _submit_text(self, text: str) -> None:
        self.chat_view._add_bubble(text, "user")
        self.chat_view.welcome_widget.setVisible(False)
        self.chat_view.scroll.setVisible(True)
        self.chat_view.set_busy(True)

        self.worker = AgentWorker(self.agent, text)
        self.worker.event_received.connect(self.handle_agent_event)
        self.worker.finished.connect(self.handle_agent_finished)
        self.worker.error.connect(self.handle_agent_error)
        self.worker.start()

    def _on_stop_requested(self):
        if self.worker:
            self.worker.stop()

    def handle_agent_event(self, event: dict):
        etype = event.get("type")
        content = event.get("content", "")

        if etype == "thought":
            self.chat_view.add_thought_bubble(content)
        elif etype == "action":
            action = event.get("action")
            params = event.get("params", {})
            self.chat_view.add_action_bubble(action, params)
            if action == "create_file": self.file_created.emit(params.get("path"))
            elif action == "run_command": self.command_run.emit(params.get("command"))
        elif etype == "observation":
            self.chat_view.add_observation_bubble(content)
        elif etype == "final":
            self.chat_view._add_bubble(content, "assistant")
        elif etype == "error":
            self.chat_view._on_error(content)
        
        self.agent_event.emit(etype, str(content))

    def handle_agent_finished(self):
        self.chat_view.set_busy(False)
        
        # Auto-update title if it's currently "New Chat" and we have history
        should_refresh_title = False
        if self.current_chat_id:
            chat_data = self.session_manager.load_chat(self.current_chat_id)
            if chat_data and chat_data.get("title") == "New Chat" and len(self.agent.history) >= 1:
                should_refresh_title = True
        
        if should_refresh_title or len(self.agent.history) >= 2:
            self.session_manager.save_chat(self.current_chat_id, self.agent.history)
            
            # Update sidebar item title
            for i in range(self.chat_list.count()):
                item = self.chat_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == self.current_chat_id:
                    # Reload data to get the newly generated title
                    updated_data = self.session_manager.load_chat(self.current_chat_id)
                    if updated_data:
                        item.setText(updated_data.get("title", "Updated Chat"))
                    break

    def handle_agent_error(self, err_msg: str):
        self.chat_view._on_error(err_msg)
        self.handle_agent_finished()

    # Proxy methods expected by main window - moved logic to chat_view
    def add_thought_bubble(self, content): self.chat_view.add_thought_bubble(content)
    def add_action_bubble(self, action, params): self.chat_view.add_action_bubble(action, params)
    def add_observation_bubble(self, content): self.chat_view.add_observation_bubble(content)
