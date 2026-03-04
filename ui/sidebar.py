"""
sidebar.py — Conversation list, agent selector, model selector.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QComboBox,
    QFrame, QSizePolicy, QMenu,
)

from models.chat_session import ChatSession
from models.agent import Agent


class ConversationItem(QListWidgetItem):
    def __init__(self, session: ChatSession):
        super().__init__()
        self.session_id = session.id
        self.update_display(session)

    def update_display(self, session: ChatSession) -> None:
        self.setText(session.title)
        self.setToolTip(session.title)


class Sidebar(QWidget):
    """
    Left sidebar with:
    - Title / logo
    - New Chat button
    - Conversation list
    - Agent selector
    - Model selector
    """

    new_chat_requested = pyqtSignal()
    session_selected = pyqtSignal(str)           # session_id
    session_delete_requested = pyqtSignal(str)   # session_id
    agent_changed = pyqtSignal(str)              # agent_id
    model_changed = pyqtSignal(str)              # model name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo / Title ──────────────────────────────────────────────────────
        title = QLabel("🦕 Orchestrator")
        title.setObjectName("sidebarTitle")
        layout.addWidget(title)

        # ── New Chat Button ───────────────────────────────────────────────────
        new_btn = QPushButton("＋  New Chat")
        new_btn.setObjectName("newChatBtn")
        new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_btn.clicked.connect(self.new_chat_requested)
        layout.addWidget(new_btn)

        # ── Separator ─────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sidebarSep")
        layout.addWidget(sep)

        # ── Conversation List ─────────────────────────────────────────────────
        chats_label = QLabel("  Chats")
        chats_label.setObjectName("sectionLabel")
        layout.addWidget(chats_label)

        self.conv_list = QListWidget()
        self.conv_list.setObjectName("convList")
        self.conv_list.currentItemChanged.connect(self._on_item_changed)
        self.conv_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.conv_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.conv_list, 1)

        # ── Spacer ────────────────────────────────────────────────────────────
        layout.addSpacing(4)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sidebarSep")
        layout.addWidget(sep2)

        # ── Agent Selector ────────────────────────────────────────────────────
        agent_label = QLabel("  Agent")
        agent_label.setObjectName("sectionLabel")
        layout.addWidget(agent_label)

        self.agent_combo = QComboBox()
        self.agent_combo.setObjectName("agentCombo")
        self.agent_combo.currentIndexChanged.connect(self._on_agent_changed)
        layout.addWidget(self.agent_combo)

        # ── Model Selector ────────────────────────────────────────────────────
        model_label = QLabel("  Model")
        model_label.setObjectName("sectionLabel")
        layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.setObjectName("modelCombo")
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        layout.addWidget(self.model_combo)

        layout.addSpacing(12)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_sessions(self, sessions: list[ChatSession]) -> None:
        self.conv_list.blockSignals(True)
        current_id = self.current_session_id()
        self.conv_list.clear()
        for s in sessions:
            item = ConversationItem(s)
            self.conv_list.addItem(item)
            if s.id == current_id:
                self.conv_list.setCurrentItem(item)
        self.conv_list.blockSignals(False)

    def add_session(self, session: ChatSession) -> None:
        item = ConversationItem(session)
        self.conv_list.insertItem(0, item)
        self.conv_list.blockSignals(True)
        self.conv_list.setCurrentRow(0)
        self.conv_list.blockSignals(False)

    def update_session_title(self, session_id: str, title: str) -> None:
        for i in range(self.conv_list.count()):
            item = self.conv_list.item(i)
            if isinstance(item, ConversationItem) and item.session_id == session_id:
                item.setText(title)
                break

    def current_session_id(self) -> str | None:
        item = self.conv_list.currentItem()
        if isinstance(item, ConversationItem):
            return item.session_id
        return None

    def set_agents(self, agents: list[Agent]) -> None:
        self.agent_combo.blockSignals(True)
        self.agent_combo.clear()
        for a in agents:
            self.agent_combo.addItem(f"{a.avatar_emoji} {a.name}", userData=a.id)
        self.agent_combo.blockSignals(False)

    def set_models(self, models: list[str]) -> None:
        self.model_combo.blockSignals(True)
        current = self.model_combo.currentText()
        self.model_combo.clear()
        for m in models:
            self.model_combo.addItem(m)
        if current in models:
            self.model_combo.setCurrentText(current)
        self.model_combo.blockSignals(False)

    def current_model(self) -> str:
        return self.model_combo.currentText()

    def current_agent_id(self) -> str:
        data = self.agent_combo.currentData()
        return data if data else "default"

    # ── Private ───────────────────────────────────────────────────────────────

    def _on_item_changed(self, current: QListWidgetItem, previous: QListWidgetItem) -> None:
        if isinstance(current, ConversationItem):
            self.session_selected.emit(current.session_id)

    def _on_agent_changed(self, _index: int) -> None:
        self.agent_changed.emit(self.current_agent_id())

    def _on_model_changed(self, _index: int) -> None:
        self.model_changed.emit(self.current_model())

    def _show_context_menu(self, pos) -> None:
        item = self.conv_list.itemAt(pos)
        if not isinstance(item, ConversationItem):
            return
        menu = QMenu(self)
        delete_action = menu.addAction("🗑  Delete")
        action = menu.exec(self.conv_list.viewport().mapToGlobal(pos))
        if action == delete_action:
            self.session_delete_requested.emit(item.session_id)
