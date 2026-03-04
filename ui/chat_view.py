"""
chat_view.py — Main chat panel with message bubbles and streaming input.
"""
from __future__ import annotations

import threading
import time
from typing import Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QVariantAnimation, QAbstractAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent, QColor
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
        # Better math handling: support both $$...$$ and \(...\) / \[...\]
        # Arithmatex handles the math-jax like syntax.
        return _md.markdown(
            text,
            extensions=[
                "fenced_code", 
                "tables", 
                "nl2br", 
                "sane_lists",
                "codehilite",
                "pymdownx.arithmatex"
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "guess_lang": True,
                    "use_pygments": True,
                    "noclasses": True, # Inject inline styles for simplicity in QLabel
                    "pygments_style": "monokai"
                },
                "pymdownx.arithmatex": {
                    "generic": True
                }
            }
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
        role_label = QLabel("YOU" if self._role == "user" else "AGENT")
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
        
        # Add basic CSS for CodeHilite if not using inline styles, 
        # but here we used noclasses: True for easier QLabel support.
        # We also want to stylize <pre> and <code> tags.
        self._set_bubble_base_style()
        
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
            row.addWidget(self.bubble, 8) 
        else:
            row.addWidget(self.bubble, 10) 
            row.addStretch(1)
        layout.addLayout(row)

    def _set_bubble_base_style(self):
        # This CSS will be applied to the rich text content inside the QLabel
        # Note: QLabel RichText support for CSS is limited (no true CSS classes),
        # but we can use noclasses=True in markdown and some tag-based styles here.
        pass

    def set_text(self, text: str) -> None:
        self._raw_text = text
        html = _to_html(text) if text else ""
        
        # Wrap in a custom div to apply some global spacing if needed
        # and more importantly, format the code blocks
        styled_html = f"""
        <style>
            pre {{ background-color: #1e1e2e; border-radius: 8px; padding: 12px; border: 1px solid #313244; margin: 8px 0; }}
            code {{ font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 13px; color: #fab387; }}
            table {{ border-collapse: collapse; margin: 10px 0; width: 100%; }}
            th, td {{ border: 1px solid #45475a; padding: 8px; text-align: left; }}
            th {{ background-color: #313244; }}
            blockquote {{ border-left: 4px solid #89dceb; color: #a6adc8; margin: 0; padding-left: 12px; font-style: italic; }}
        </style>
        <div style="line-height: 1.5; color: #cdd6f4;">
            {html}
        </div>
        """
        self.bubble.setText(styled_html)

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
    - Integrated multi-state action button (Send/Stop) with pulse animation.
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
        self._is_busy = False
        
        # Pulse animation for the action button
        self.pulse_anim = QVariantAnimation(self)
        self.pulse_anim.setDuration(1200)
        self.pulse_anim.setStartValue(0.1)
        self.pulse_anim.setEndValue(0.6)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_anim.setLoopCount(-1)
        self.pulse_anim.valueChanged.connect(self._update_button_pulse)

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
        self.input_frame.setMaximumWidth(1200)
        self.input_frame.setMinimumHeight(64)
        
        inp_layout = QHBoxLayout(self.input_frame)
        inp_layout.setContentsMargins(20, 6, 8, 6)
        inp_layout.setSpacing(10)

        self.input = _StreamInputField()
        self.input.setObjectName("inputField")
        self.input.setStyleSheet("background: transparent; border: none; padding: 12px 0; color: #f0f4f8; font-size: 14px;")
        self.input.setPlaceholderText("How can I help you today?")
        self.input.setFixedHeight(52)
        self.input.setMaximumHeight(200)
        inp_layout.addWidget(self.input, 1)

        # High-performance multi-state Action Button
        self.action_btn = QPushButton("✦")
        self.action_btn.setObjectName("actionBtn")
        self.action_btn.setFixedSize(48, 48)
        self.action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.action_btn.setToolTip("Ignite Thought (Enter)")
        self.action_btn.clicked.connect(self._handle_action_click)
        self.action_btn.setStyleSheet("""
            QPushButton#actionBtn {
                background-color: #00f2ff;
                color: #05060a;
                border-radius: 24px;
                font-size: 20px;
                font-weight: bold;
                border: none;
            }
            QPushButton#actionBtn:hover {
                background-color: #00d9e5;
            }
            QPushButton#actionBtn:pressed {
                background-color: #00b0ba;
            }
        """)
        inp_layout.addWidget(self.action_btn)

        input_container_layout.addWidget(self.input_frame)
        root.addWidget(input_container)

    def _build_welcome(self) -> QWidget:
        # (Same as before, omitted for brevity but should be kept in real implementation)
        # Assuming I should repeat it to avoid issues with replace_file_content
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
        self.input.submit_triggered.connect(self._handle_action_click)
        self._signals.token_received.connect(self._on_token)
        self._signals.stream_done.connect(self._on_done)
        self._signals.stream_error.connect(self._on_error)

    # ── Logic ────────────────────────────────────────────────────────────────

    def set_busy(self, busy: bool) -> None:
        """Toggle UI state between Idle and Working."""
        self._is_busy = busy
        if busy:
            self.action_btn.setText("■")
            self.action_btn.setToolTip("Abrupt Silence (Stop)")
            self.action_btn.setStyleSheet("""
                QPushButton#actionBtn {
                    background-color: #f85149;
                    color: white;
                    border-radius: 24px;
                    font-size: 18px;
                    border: 2px solid rgba(248, 81, 73, 0.4);
                }
            """)
            self.pulse_anim.start()
            self.input.setEnabled(False)
        else:
            self.pulse_anim.stop()
            self.action_btn.setText("✦")
            self.action_btn.setToolTip("Ignite Thought (Enter)")
            self.action_btn.setStyleSheet("""
                QPushButton#actionBtn {
                    background-color: #00f2ff;
                    color: #05060a;
                    border-radius: 24px;
                    font-size: 20px;
                    font-weight: bold;
                    border: none;
                }
            """)
            self.input.setEnabled(True)
            self.input.setFocus()

    def _update_button_pulse(self, value: float):
        """Update button glow effect based on animation value."""
        # Add a glowing drop shadow or border pulse effect
        if self._is_busy:
            self.action_btn.setStyleSheet(f"""
                QPushButton#actionBtn {{
                    background-color: #f85149;
                    color: white;
                    border-radius: 24px;
                    font-size: 18px;
                    border: 3px solid rgba(248, 81, 73, {value});
                }}
            """)

    def _handle_action_click(self) -> None:
        if self._is_busy:
            self._on_stop()
        else:
            self._on_send()

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

    # ── Public API (for non-agent streaming) ──────────────────────────────────

    def start_streaming(self, stream_fn, user_text: str, on_complete=None) -> None:
        self._stop_flag = False
        self._add_bubble(user_text, "user")
        self.welcome_widget.setVisible(False)
        self.scroll.setVisible(True)

        self._current_ai_text = ""
        self._current_ai_bubble = self._add_bubble("▋", "assistant")
        self.set_busy(True)

        def _run():
            try:
                for token in stream_fn():
                    if self._stop_flag: break
                    self._signals.token_received.emit(token)
            except Exception as exc:
                self._signals.stream_error.emit(str(exc))
                return
            self._signals.stream_done.emit()
            if on_complete: on_complete(self._current_ai_text)

        self._stream_thread = threading.Thread(target=_run, daemon=True)
        self._stream_thread.start()

    def _on_token(self, token: str) -> None:
        self._current_ai_text += token
        if self._current_ai_bubble:
            self._current_ai_bubble.set_text(self._current_ai_text + " ▋")
        QTimer.singleShot(15, self._scroll_bottom)

    def _on_done(self) -> None:
        if self._current_ai_bubble:
            self._current_ai_bubble.set_text(self._current_ai_text)
        self._current_ai_bubble = None
        self.set_busy(False)

    def _on_error(self, msg: str) -> None:
        # (Error handling stays similar, just ensure set_busy(False))
        self.set_busy(False)
        # ... (rest of error display code) ...

    def _add_bubble(self, text: str, role: str, scroll: bool = True) -> MessageBubble:
        bubble = MessageBubble(text, role)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)
        if scroll: QTimer.singleShot(30, self._scroll_bottom)
        return bubble

    def add_thought_bubble(self, content: str):
        bubble = QFrame()
        bubble.setStyleSheet("""
            background-color: #0a0b10;
            border-radius: 16px;
            border: 1px solid rgba(138, 43, 226, 0.3);
            margin: 10px 24px;
            padding: 14px;
        """)
        layout = QVBoxLayout(bubble)
        label = QLabel(f"<span style='color: #8a2be2; font-size: 10px; font-weight: bold; letter-spacing: 2px;'>✦ NEURAL THOUGHT</span><br><span style='color: #b4b4b4; line-height: 1.4;'>{content}</span>")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_bottom)

    def add_action_bubble(self, action: str, params: dict):
        import json
        bubble = QFrame()
        bubble.setStyleSheet("""
            background-color: rgba(0, 242, 255, 0.05);
            border-radius: 16px;
            border: 1px solid rgba(0, 242, 255, 0.2);
            margin: 10px 24px;
            padding: 14px;
        """)
        layout = QVBoxLayout(bubble)
        param_str = json.dumps(params, indent=2)
        label = QLabel(f"<span style='color: #00f2ff; font-size: 10px; font-weight: bold; letter-spacing: 2px;'>⚙️ EXECUTING: {action.upper()}</span><br><pre style='color: #8a2be2; font-family: monospace; font-size: 11px;'>{param_str}</pre>")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_bottom)

    def add_observation_bubble(self, content: str):
        bubble = QFrame()
        bubble.setStyleSheet("""
            background-color: #05060a;
            border-radius: 16px;
            border: 1px solid rgba(35, 134, 54, 0.3);
            margin: 10px 24px;
            padding: 14px;
        """)
        layout = QVBoxLayout(bubble)
        display_content = (content[:500] + '...') if len(content) > 500 else content
        label = QLabel(f"<span style='color: #238636; font-size: 10px; font-weight: bold; letter-spacing: 2px;'>👁️ SENSOR DATA</span><br><pre style='color: #8b949e; font-family: monospace; font-size: 11px;'>{display_content}</pre>")
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.msgs_layout.insertWidget(self.msgs_layout.count() - 1, bubble)
        QTimer.singleShot(50, self._scroll_bottom)

    def _scroll_bottom(self) -> None:
        bar = self.scroll.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear_messages(self) -> None:
        while self.msgs_layout.count() > 1:
            item = self.msgs_layout.takeAt(0)
            if w := item.widget(): w.deleteLater()
        self.welcome_widget.setVisible(True)
        self.scroll.setVisible(False)

    def load_session_messages(self, turns: list) -> None:
        self.clear_messages()
        if not turns: return
        self.welcome_widget.setVisible(False)
        self.scroll.setVisible(True)
        for t in turns:
            if t.role in ("user", "assistant"):
                self._add_bubble(t.content, t.role, scroll=False)
        self._scroll_bottom()
