"""
chat_view.py — Main chat panel with message bubbles and streaming input.
"""
from __future__ import annotations

import threading
import time
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QScrollArea, QLabel, QSizePolicy,
    QFrame,
)

try:
    import markdown as _md
    _HAS_MD = True
except ImportError:
    _HAS_MD = False


def _to_html(text: str) -> str:
    if _HAS_MD:
        return _md.markdown(
            text,
            extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
        )
    return text.replace("\n", "<br>")


class _Signals(QObject):
    token_received = pyqtSignal(str)
    stream_done = pyqtSignal()
    stream_error = pyqtSignal(str)


class MessageBubble(QWidget):
    """A single chat message widget."""

    def __init__(self, text: str, role: str = "user", parent=None):
        super().__init__(parent)
        self._role = role
        self._raw_text = text
        self._build(text)

    def _build(self, text: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8 if self._role != "user" else 4, 16, 4)
        layout.setSpacing(4)

        # Antigravity Minimal Role label
        role_label = QLabel("YOU" if self._role == "user" else "ANTIGRAVITY")
        role_label.setStyleSheet(f"font-weight: bold; color: {'#00f2ff' if self._role != 'user' else '#8a2be2'}; font-size: 10px; letter-spacing: 2px;")
        if self._role == "user":
            role_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(role_label)

        # Bubble
        self.bubble = QLabel()
        if self._role == "user":
            self.bubble.setStyleSheet("""
                background-color: rgba(138, 43, 226, 0.1);
                color: #e0e6ed;
                border-radius: 20px;
                padding: 12px 18px;
                border: 1px solid rgba(138, 43, 226, 0.3);
            """)
        else:
            self.bubble.setStyleSheet("""
                background-color: transparent;
                color: #f0f4f8;
                padding: 10px 4px;
            """)
        
        self.bubble.setWordWrap(True)
        self.bubble.setTextFormat(Qt.TextFormat.RichText)
        self.bubble.setOpenExternalLinks(True)
        self.bubble.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.bubble.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.set_text(text)

        row = QHBoxLayout()
        row.setSpacing(0)
        if self._role == "user":
            row.addStretch(1)
            row.addWidget(self.bubble, 8) # Increased stretch for bubble
        else:
            row.addWidget(self.bubble, 10) # Increased stretch for bubble
            row.addStretch(1)
        layout.addLayout(row)

    def set_text(self, text: str) -> None:
        self._raw_text = text
        html = _to_html(text) if text else ""
        self.bubble.setText(html)

    def append_text(self, fragment: str) -> None:
        self._raw_text += fragment
        self.set_text(self._raw_text)


class _StreamInputField(QTextEdit):
    """QTextEdit that submits on Enter (without Shift)."""
    submit_triggered = pyqtSignal()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if (
            e.key() == Qt.Key.Key_Return
            and not (e.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        ):
            self.submit_triggered.emit()
        else:
            super().keyPressEvent(e)


class ChatView(QWidget):
    """
    Full chat panel:
    - Scrollable message list
    - Input area with Send / Stop buttons
    """

    message_submitted = pyqtSignal(str)   # raw text from user
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("chatArea")
        self._signals = _Signals()
        self._current_ai_bubble: Optional[MessageBubble] = None
        self._current_ai_text = ""
        self._stop_flag = False
        self._stream_thread: Optional[threading.Thread] = None
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Welcome screen (shown when no messages) ────────────────────────
        self.welcome_widget = self._build_welcome()
        root.addWidget(self.welcome_widget)

        # ── Scroll area ────────────────────────────────────────────────────
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setObjectName("chatScroll")
        self.scroll.hide()

        self.msgs_container = QWidget()
        self.msgs_layout = QVBoxLayout(self.msgs_container)
        self.msgs_layout.setContentsMargins(0, 8, 0, 8)
        self.msgs_layout.setSpacing(0)
        self.msgs_layout.addStretch()

        self.scroll.setWidget(self.msgs_container)
        root.addWidget(self.scroll, 1)

        # ── Input area ─────────────────────────────────────────────────────
        # Main input container (centered capsule)
        input_container = QWidget()
        input_container_layout = QHBoxLayout(input_container)
        input_container_layout.setContentsMargins(16, 8, 16, 24)
        input_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input_frame = QFrame()
        self.input_frame.setObjectName("inputArea")
        self.input_frame.setStyleSheet("""
            QFrame#inputArea {
                background-color: #0d0f17;
                border: 1px solid rgba(0, 242, 255, 0.2);
                border-radius: 28px;
            }
            QFrame#inputArea:focus-within {
                border: 1px solid #00f2ff;
                background-color: #11131e;
            }
        """)
        # Remove setFixedWidth to allow expansion to container width
        self.input_frame.setMaximumWidth(1200) # Optional: sanity limit for very wide screens
        self.input_frame.setMinimumHeight(56)
        
        inp_layout = QHBoxLayout(self.input_frame)
        inp_layout.setContentsMargins(20, 4, 8, 4)
        inp_layout.setSpacing(10)

        self.input = _StreamInputField()
        self.input.setObjectName("inputField")
        self.input.setStyleSheet("background: transparent; border: none; padding: 12px 0; color: #f0f4f8;")
        self.input.setPlaceholderText("How can I hellp you today?")
        self.input.setFixedHeight(50)
        self.input.setMaximumHeight(200)
        inp_layout.addWidget(self.input, 1)

        self.send_btn = QPushButton("✦")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setFixedSize(40, 40)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setToolTip("Ignite Thought (Enter)")
        self.send_btn.clicked.connect(self._on_send)
        inp_layout.addWidget(self.send_btn)

        self.stop_btn = QPushButton("■")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setFixedSize(36, 36)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.hide()
        inp_layout.addWidget(self.stop_btn)

        input_container_layout.addWidget(self.input_frame)
        root.addWidget(input_container)

    def _build_welcome(self) -> QWidget:
        w = QWidget()
        w.setObjectName("welcomeContainer")
        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        title = QLabel("🦕 Orchestrator")
        title.setObjectName("welcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("AI runtime for Linux · Powered by Ollama")
        subtitle.setObjectName("welcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(24)

        suggestions = [
            "Explain quantum entanglement simply",
            "Write a Python script to rename files",
            "What are Rust's main advantages over C++?",
            "Suggest a healthy meal plan for the week",
        ]
        for s in suggestions:
            btn = QPushButton(s)
            btn.setObjectName("suggestionBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked, text=s: self._submit_text(text))
            layout.addWidget(btn)

        return w

    def _connect_signals(self) -> None:
        self.input.submit_triggered.connect(self._on_send)
        self._signals.token_received.connect(self._on_token)
        self._signals.stream_done.connect(self._on_done)
        self._signals.stream_error.connect(self._on_error)

    # ── Public API ────────────────────────────────────────────────────────────

    def clear_messages(self) -> None:
        while self.msgs_layout.count() > 1:
            item = self.msgs_layout.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        self.welcome_widget.setVisible(True)
        self.scroll.setVisible(False)

    def load_session_messages(self, turns: list) -> None:
        self.clear_messages()
        if not turns:
            return
        self.welcome_widget.setVisible(False)
        self.scroll.setVisible(True)
        for t in turns:
            if t.role in ("user", "assistant"):
                self._add_bubble(t.content, t.role, scroll=False)
        self._scroll_bottom()

    def start_streaming(
        self,
        stream_fn,              # callable() -> Iterator[str]
        user_text: str,
        on_complete=None,       # callable(full_text: str)
    ) -> None:
        """Begin a streaming response. Call from main thread."""
        self._stop_flag = False
        # User bubble
        self._add_bubble(user_text, "user")
        self.welcome_widget.setVisible(False)
        self.scroll.setVisible(True)

        # AI bubble placeholder
        self._current_ai_text = ""
        self._current_ai_bubble = self._add_bubble("▋", "assistant")

        self.send_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.input.setEnabled(False)

        def _run():
            t_start = time.time()
            try:
                for token in stream_fn():
                    if self._stop_flag:
                        break
                    self._signals.token_received.emit(token)
            except Exception as exc:
                self._signals.stream_error.emit(str(exc))
                return
            self._signals.stream_done.emit()
            if on_complete:
                on_complete(self._current_ai_text)

        self._stream_thread = threading.Thread(target=_run, daemon=True)
        self._stream_thread.start()

    # ── Private ───────────────────────────────────────────────────────────────

    def _add_bubble(self, text: str, role: str, scroll: bool = True) -> MessageBubble:
        bubble = MessageBubble(text, role)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)
        if scroll:
            QTimer.singleShot(30, self._scroll_bottom)
        return bubble

    def _scroll_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _on_send(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.input.clear()
        self._submit_text(text)

    def _submit_text(self, text: str) -> None:
        self.message_submitted.emit(text)

    def _on_stop(self) -> None:
        self._stop_flag = True
        self.stop_requested.emit()

    def _on_token(self, token: str) -> None:
        self._current_ai_text += token
        if self._current_ai_bubble:
            self._current_ai_bubble.set_text(self._current_ai_text + " ▋")
        QTimer.singleShot(15, self._scroll_bottom)

    def _on_done(self) -> None:
        if self._current_ai_bubble:
            self._current_ai_bubble.set_text(self._current_ai_text)
        self._current_ai_bubble = None
        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.input.setEnabled(True)
        self.input.setFocus()

    def _on_error(self, msg: str) -> None:
        error_html = (
            f"<div style='background:#2a1520; border:1px solid #7c2a3a; padding:10px; border-radius:5px;'>"
            f"<span style='color:#ff8888'>⚠ Error: {msg}</span><br><br>"
            "<code>¿Está Ollama corriendo?  →  <b>ollama serve</b></code>"
            f"</div>"
        )
        if self._current_ai_bubble:
            self._current_ai_bubble.bubble.setText(error_html)
        else:
            bubble = self._add_bubble(error_html, "assistant")
            bubble.bubble.setTextFormat(Qt.TextFormat.RichText)
        self._current_ai_bubble = None
        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.input.setEnabled(True)
