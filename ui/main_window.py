"""
main_window.py — Top-level QMainWindow: sidebar + chat view + menu bar.
"""
from __future__ import annotations

import time
from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QFont, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter,
    QApplication, QMessageBox,
)

from ui.sidebar import Sidebar
from ui.chat_view import ChatView
from ui.management_window import ManagementWindow
from core.agent_store import agent_store, provider_store, session_store
from core.model_service import router as model_router, RemoteProviderService, AnthropicService
from core.insights_service import insights
from models.chat_session import ChatSession
from models.agent import DEFAULT_AGENT


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orchestrator")
        self.resize(1200, 780)
        self._current_session: Optional[ChatSession] = None
        self._mgmt_window: Optional[ManagementWindow] = None

        self._setup_ui()
        self._setup_menu()
        self._refresh_providers()
        self._load_sessions()
        self._new_chat()
        QTimer.singleShot(200, self._refresh_models)

    # ── UI Setup ──────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)

        self.sidebar = Sidebar()
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(300)
        splitter.addWidget(self.sidebar)

        self.chat_view = ChatView()
        splitter.addWidget(self.chat_view)

        splitter.setSizes([240, 960])
        root.addWidget(splitter)

        # ── Signal connections ────────────────────────────────────────────────
        self.sidebar.new_chat_requested.connect(self._new_chat)
        self.sidebar.session_selected.connect(self._on_session_selected)
        self.sidebar.session_delete_requested.connect(self._delete_session)
        self.sidebar.agent_changed.connect(self._on_agent_changed)
        self.sidebar.model_changed.connect(self._on_model_changed)

        self.chat_view.message_submitted.connect(self._on_message_submitted)

    def _setup_menu(self) -> None:
        mb = self.menuBar()

        # File menu
        file_menu = mb.addMenu("File")
        new_act = QAction("New Chat", self)
        new_act.setShortcut(QKeySequence("Ctrl+N"))
        new_act.triggered.connect(self._new_chat)
        file_menu.addAction(new_act)

        file_menu.addSeparator()

        quit_act = QAction("Quit", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_act)

        # View menu
        view_menu = mb.addMenu("View")
        mgmt_act = QAction("Management…", self)
        mgmt_act.setShortcut(QKeySequence("Ctrl+Shift+M"))
        mgmt_act.triggered.connect(self._open_management)
        view_menu.addAction(mgmt_act)

    # ── Session management ────────────────────────────────────────────────────

    def _load_sessions(self) -> None:
        sessions = session_store.all()
        self.sidebar.set_sessions(sessions)

    def _new_chat(self) -> None:
        session = ChatSession()
        session_store.save(session)
        self._current_session = session
        self.sidebar.add_session(session)
        self.chat_view.clear_messages()

    def _on_session_selected(self, session_id: str) -> None:
        session = session_store.get(session_id)
        if session:
            self._current_session = session
            self.chat_view.load_session_messages(session.turns)

    def _delete_session(self, session_id: str) -> None:
        session_store.delete(session_id)
        sessions = session_store.all()
        self.sidebar.set_sessions(sessions)
        if self._current_session and self._current_session.id == session_id:
            if sessions:
                self._on_session_selected(sessions[0].id)
            else:
                self._new_chat()

    # ── Chat ──────────────────────────────────────────────────────────────────

    def _on_message_submitted(self, text: str) -> None:
        if not self._current_session:
            self._new_chat()

        model = self.sidebar.current_model()
        agent_id = self.sidebar.current_agent_id()
        agent = agent_store.get(agent_id) or DEFAULT_AGENT

        self._current_session.add_turn("user", text, model=model)

        # Build messages for API
        messages = self._current_session.to_api_messages(
            system_prompt=agent.system_prompt or ""
        )

        t_start = time.time()
        ai_text_holder = [""]

        def stream_fn():
            return model_router.resolve_stream(
                model=model,
                messages=messages,
                temperature=agent.temperature or 0.7,
                max_tokens=agent.max_tokens or 4096,
            )

        def on_complete(full_text: str) -> None:
            ai_text_holder[0] = full_text
            self._current_session.add_turn("assistant", full_text, model=model)
            session_store.save(self._current_session)
            self.sidebar.update_session_title(
                self._current_session.id,
                self._current_session.title,
            )
            # Log inference
            duration_ms = (time.time() - t_start) * 1000
            insights.log(
                model=model,
                input_tokens=sum(len(m.get("content") or "") // 4 for m in messages),
                output_tokens=max(1, len(full_text) // 4),
                duration_ms=duration_ms,
            )

        self.chat_view.start_streaming(stream_fn, text, on_complete=on_complete)

    # ── Model / Agent ─────────────────────────────────────────────────────────

    def _refresh_models(self) -> None:
        models = model_router.all_model_names()
        if not models:
            models = ["(no models — run: ollama pull qwen2.5:7b)"]
        self.sidebar.set_models(models)

    def _refresh_agents(self) -> None:
        self.sidebar.set_agents(agent_store.all())

    def _on_agent_changed(self, agent_id: str) -> None:
        if self._current_session:
            self._current_session.agent_id = agent_id

    def _on_model_changed(self, model: str) -> None:
        if self._current_session:
            self._current_session.model = model

    # ── Providers ─────────────────────────────────────────────────────────────

    def _refresh_providers(self) -> None:
        """Register enabled providers into the model router."""
        for provider in provider_store.enabled():
            if not provider.base_url:
                continue

            if provider.preset == "anthropic":
                svc = AnthropicService(provider.api_key, provider.timeout)
                models = [provider.default_model] if provider.default_model else []
                model_router.register_anthropic(provider.id, svc, models)
            else:
                svc = RemoteProviderService(
                    provider.base_url, provider.get_headers(), provider.timeout
                )
                # Get remote model list or fall back to the configured default
                try:
                    remote_models = svc.list_models()
                except Exception:
                    remote_models = []
                if not remote_models and provider.default_model:
                    remote_models = [provider.default_model]
                model_router.register_remote_provider(provider.id, svc, remote_models)

    # ── Management Window ─────────────────────────────────────────────────────

    def _open_management(self) -> None:
        if not self._mgmt_window:
            self._mgmt_window = ManagementWindow(self)
            self._mgmt_window.agents_changed.connect(self._refresh_agents)
            self._mgmt_window.providers_changed.connect(self._on_providers_changed)
        self._mgmt_window.show()
        self._mgmt_window.raise_()

    def _on_providers_changed(self) -> None:
        self._refresh_providers()
        QTimer.singleShot(300, self._refresh_models)
