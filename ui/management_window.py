"""
management_window.py — Multi-tab management window (⌘ Shift M equivalent).
Tabs: Agents | Providers | Models | Memory | Insights | Server
"""
from __future__ import annotations

import threading
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QTextEdit, QLineEdit, QFormLayout, QComboBox, QCheckBox,
    QScrollArea, QSplitter, QFrame, QProgressBar, QMessageBox,
    QGroupBox, QSpinBox, QDoubleSpinBox, QSizePolicy,
)

from core.agent_store import agent_store, provider_store
from core.insights_service import insights
from core.model_service import router as model_router, OllamaService
from models.agent import Agent
from models.provider import RemoteProvider, PROVIDER_PRESETS


# ══════════════════════════════════════════════════════════════════════════════
# Agents Tab
# ══════════════════════════════════════════════════════════════════════════════

class AgentsTab(QWidget):
    agents_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current: Optional[Agent] = None
        self._build()
        self._refresh_list()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left list
        left = QWidget()
        left.setFixedWidth(220)
        left.setObjectName("mgmtLeft")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.setSpacing(6)

        title = QLabel("Agents")
        title.setObjectName("mgmtSectionTitle")
        ll.addWidget(title)

        self.agent_list = QListWidget()
        self.agent_list.currentRowChanged.connect(self._on_select)
        ll.addWidget(self.agent_list, 1)

        new_btn = QPushButton("＋ New Agent")
        new_btn.setObjectName("newChatBtn")
        new_btn.clicked.connect(self._new_agent)
        ll.addWidget(new_btn)

        root.addWidget(left)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setObjectName("sidebarSep")
        root.addWidget(sep)

        # Right editor
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 16, 20, 16)
        rl.setSpacing(12)

        self.form = QFormLayout()
        self.form.setSpacing(10)

        self.name_edit = QLineEdit()
        self.emoji_edit = QLineEdit()
        self.emoji_edit.setFixedWidth(60)
        self.color_edit = QLineEdit()
        self.color_edit.setPlaceholderText("#7c3aed")
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Leave blank to use global default")
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.05)
        self.temp_spin.setValue(0.7)
        self.desc_edit = QLineEdit()

        self.form.addRow("Name:", self.name_edit)
        self.form.addRow("Emoji:", self.emoji_edit)
        self.form.addRow("Color:", self.color_edit)
        self.form.addRow("Default Model:", self.model_edit)
        self.form.addRow("Temperature:", self.temp_spin)
        self.form.addRow("Description:", self.desc_edit)

        rl.addLayout(self.form)

        prompt_label = QLabel("System Prompt:")
        prompt_label.setObjectName("sectionLabel")
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setObjectName("inputField")
        self.prompt_edit.setPlaceholderText("You are a helpful assistant…")
        self.prompt_edit.setMinimumHeight(120)
        rl.addWidget(prompt_label)
        rl.addWidget(self.prompt_edit, 1)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("sendBtn")
        save_btn.clicked.connect(self._save)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("stopBtn")
        self.delete_btn.clicked.connect(self._delete)
        btn_row.addStretch()
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(save_btn)
        rl.addLayout(btn_row)

        root.addWidget(right, 1)

    def _refresh_list(self) -> None:
        self.agent_list.blockSignals(True)
        self.agent_list.clear()
        for a in agent_store.all():
            self.agent_list.addItem(f"{a.avatar_emoji} {a.name}")
        self.agent_list.blockSignals(False)

    def _on_select(self, row: int) -> None:
        agents = agent_store.all()
        if 0 <= row < len(agents):
            self._current = agents[row]
            self._populate_form(self._current)

    def _populate_form(self, a: Agent) -> None:
        self.name_edit.setText(a.name)
        self.emoji_edit.setText(a.avatar_emoji)
        self.color_edit.setText(a.theme_color)
        self.model_edit.setText(a.model or "")
        self.temp_spin.setValue(a.temperature or 0.7)
        self.desc_edit.setText(a.description)
        self.prompt_edit.setPlainText(a.system_prompt)
        self.delete_btn.setEnabled(not a.is_default)

    def _new_agent(self) -> None:
        a = Agent(name="New Agent")
        agent_store.save(a)
        self._refresh_list()
        self.agent_list.setCurrentRow(self.agent_list.count() - 1)
        self.agents_changed.emit()

    def _save(self) -> None:
        if not self._current:
            return
        self._current.name = self.name_edit.text().strip() or "Agent"
        self._current.avatar_emoji = self.emoji_edit.text().strip() or "🤖"
        self._current.theme_color = self.color_edit.text().strip() or "#7c3aed"
        self._current.model = self.model_edit.text().strip() or None
        self._current.temperature = self.temp_spin.value()
        self._current.description = self.desc_edit.text().strip()
        self._current.system_prompt = self.prompt_edit.toPlainText()
        agent_store.save(self._current)
        self._refresh_list()
        self.agents_changed.emit()

    def _delete(self) -> None:
        if self._current and agent_store.delete(self._current.id):
            self._current = None
            self._refresh_list()
            self.agents_changed.emit()


# ══════════════════════════════════════════════════════════════════════════════
# Providers Tab
# ══════════════════════════════════════════════════════════════════════════════

class ProvidersTab(QWidget):
    providers_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current: Optional[RemoteProvider] = None
        self._build()
        self._refresh_list()

    def _build(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        left = QWidget()
        left.setFixedWidth(220)
        left.setObjectName("mgmtLeft")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 12, 12, 12)
        ll.setSpacing(6)

        title = QLabel("Remote Providers")
        title.setObjectName("mgmtSectionTitle")
        ll.addWidget(title)

        self.provider_list = QListWidget()
        self.provider_list.currentRowChanged.connect(self._on_select)
        ll.addWidget(self.provider_list, 1)

        new_btn = QPushButton("＋ Add Provider")
        new_btn.setObjectName("newChatBtn")
        new_btn.clicked.connect(self._new_provider)
        ll.addWidget(new_btn)

        root.addWidget(left)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setObjectName("sidebarSep")
        root.addWidget(sep)

        # Right editor
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 16, 20, 16)
        rl.setSpacing(10)

        self.form = QFormLayout()
        self.form.setSpacing(10)

        self.preset_combo = QComboBox()
        for k, v in PROVIDER_PRESETS.items():
            self.preset_combo.addItem(v["name"], userData=k)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)

        self.name_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.key_edit = QLineEdit()
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.model_edit = QLineEdit()
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 600)
        self.timeout_spin.setValue(60)
        self.enabled_cb = QCheckBox("Enabled")
        self.enabled_cb.setChecked(True)

        self.form.addRow("Preset:", self.preset_combo)
        self.form.addRow("Name:", self.name_edit)
        self.form.addRow("Base URL:", self.url_edit)
        self.form.addRow("API Key:", self.key_edit)
        self.form.addRow("Default Model:", self.model_edit)
        self.form.addRow("Timeout (s):", self.timeout_spin)
        self.form.addRow("", self.enabled_cb)

        rl.addLayout(self.form)
        rl.addStretch()

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("sendBtn")
        save_btn.clicked.connect(self._save)
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("stopBtn")
        delete_btn.clicked.connect(self._delete)
        btn_row.addStretch()
        btn_row.addWidget(delete_btn)
        btn_row.addWidget(save_btn)
        rl.addLayout(btn_row)

        root.addWidget(right, 1)

    def _refresh_list(self) -> None:
        self.provider_list.blockSignals(True)
        self.provider_list.clear()
        for p in provider_store.all():
            status = "●" if p.enabled else "○"
            self.provider_list.addItem(f"{status} {p.name}")
        self.provider_list.blockSignals(False)

    def _on_select(self, row: int) -> None:
        providers = provider_store.all()
        if 0 <= row < len(providers):
            self._current = providers[row]
            self._populate_form(self._current)

    def _populate_form(self, p: RemoteProvider) -> None:
        idx = self.preset_combo.findData(p.preset)
        self.preset_combo.blockSignals(True)
        self.preset_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.preset_combo.blockSignals(False)
        self.name_edit.setText(p.name)
        self.url_edit.setText(p.base_url)
        self.key_edit.setText(p.api_key)
        self.model_edit.setText(p.default_model)
        self.timeout_spin.setValue(p.timeout)
        self.enabled_cb.setChecked(p.enabled)

    def _on_preset_changed(self, _: int) -> None:
        preset_key = self.preset_combo.currentData()
        if preset_key and preset_key in PROVIDER_PRESETS:
            p = PROVIDER_PRESETS[preset_key]
            self.name_edit.setText(p["name"])
            self.url_edit.setText(p["base_url"])
            self.model_edit.setText(p["default_model"])

    def _new_provider(self) -> None:
        p = RemoteProvider(name="New Provider")
        provider_store.save(p)
        self._refresh_list()
        self.provider_list.setCurrentRow(self.provider_list.count() - 1)

    def _save(self) -> None:
        if not self._current:
            return
        self._current.preset = self.preset_combo.currentData() or "custom"
        self._current.name = self.name_edit.text().strip() or "Provider"
        self._current.base_url = self.url_edit.text().strip().rstrip("/")
        self._current.api_key = self.key_edit.text().strip()
        self._current.default_model = self.model_edit.text().strip()
        self._current.timeout = self.timeout_spin.value()
        self._current.enabled = self.enabled_cb.isChecked()
        provider_store.save(self._current)
        self._refresh_list()
        self.providers_changed.emit()

    def _delete(self) -> None:
        if self._current and provider_store.delete(self._current.id):
            self._current = None
            self._refresh_list()
            self.providers_changed.emit()


# ══════════════════════════════════════════════════════════════════════════════
# Models Tab  (Ollama pull / delete)
# ══════════════════════════════════════════════════════════════════════════════

class _PullThread(QThread):
    progress = pyqtSignal(str, int)   # status, percent
    finished_ok = pyqtSignal()
    finished_err = pyqtSignal(str)

    def __init__(self, service: OllamaService, name: str):
        super().__init__()
        self._svc = service
        self._name = name

    def run(self) -> None:
        try:
            for event in self._svc.pull_model(self._name):
                status = event.get("status", "")
                completed = event.get("completed", 0)
                total = event.get("total", 0)
                pct = int(completed / total * 100) if total else 0
                self.progress.emit(status, pct)
            self.finished_ok.emit()
        except Exception as e:
            self.finished_err.emit(str(e))


class ModelsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._svc = OllamaService()
        self._pull_thread: Optional[_PullThread] = None
        self._build()
        self._refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        title = QLabel("Local Models  (Ollama)")
        title.setObjectName("mgmtSectionTitle")
        layout.addWidget(title)

        pull_row = QHBoxLayout()
        self.pull_input = QLineEdit()
        self.pull_input.setObjectName("inputField")
        self.pull_input.setPlaceholderText("Model name, e.g. qwen2.5:7b")
        pull_row.addWidget(self.pull_input, 1)
        pull_btn = QPushButton("⬇ Pull")
        pull_btn.setObjectName("sendBtn")
        pull_btn.clicked.connect(self._pull)
        pull_row.addWidget(pull_btn)
        layout.addLayout(pull_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("pullProgress")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setObjectName("sectionLabel")
        layout.addWidget(self.status_label)

        self.model_list = QListWidget()
        layout.addWidget(self.model_list, 1)

        del_btn = QPushButton("🗑 Delete Selected")
        del_btn.setObjectName("stopBtn")
        del_btn.clicked.connect(self._delete)
        layout.addWidget(del_btn)

    def _refresh(self) -> None:
        self.model_list.clear()
        for m in self._svc.list_models():
            size_gb = m.get("size", 0) / 1e9
            item = QListWidgetItem(f"{m['name']}  ({size_gb:.1f} GB)")
            self.model_list.addItem(item)

    def _pull(self) -> None:
        name = self.pull_input.text().strip()
        if not name:
            return
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        self.status_label.setText("Starting download…")
        self._pull_thread = _PullThread(self._svc, name)
        self._pull_thread.progress.connect(self._on_progress)
        self._pull_thread.finished_ok.connect(self._on_pull_done)
        self._pull_thread.finished_err.connect(self._on_pull_error)
        self._pull_thread.start()

    def _on_progress(self, status: str, pct: int) -> None:
        self.status_label.setText(status)
        self.progress_bar.setValue(pct)

    def _on_pull_done(self) -> None:
        self.progress_bar.hide()
        self.status_label.setText("✓ Done")
        self._refresh()

    def _on_pull_error(self, msg: str) -> None:
        self.progress_bar.hide()
        self.status_label.setText(f"⚠ Error: {msg}")

    def _delete(self) -> None:
        item = self.model_list.currentItem()
        if not item:
            return
        name = item.text().split("  ")[0]
        self._svc.delete_model(name)
        self._refresh()


# ══════════════════════════════════════════════════════════════════════════════
# Insights Tab
# ══════════════════════════════════════════════════════════════════════════════

class InsightsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Inference Insights")
        title.setObjectName("mgmtSectionTitle")
        layout.addWidget(title)

        self.stats_label = QLabel()
        self.stats_label.setObjectName("sectionLabel")
        layout.addWidget(self.stats_label)

        self.log_list = QListWidget()
        layout.addWidget(self.log_list, 1)

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.setObjectName("sendBtn")
        refresh_btn.clicked.connect(self._refresh)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("stopBtn")
        clear_btn.clicked.connect(self._clear)
        btn_row.addStretch()
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(refresh_btn)
        layout.addLayout(btn_row)

    def _refresh(self) -> None:
        stats = insights.stats()
        self.stats_label.setText(
            f"Total: {stats['total']}  |  "
            f"Success: {stats['success_rate']*100:.0f}%  |  "
            f"Avg latency: {stats['avg_latency_ms']:.0f}ms  |  "
            f"Avg tok/s: {stats['avg_tps']:.1f}"
        )
        self.log_list.clear()
        for log in insights.all():
            from datetime import datetime
            ts = datetime.fromtimestamp(log.timestamp).strftime("%H:%M:%S")
            self.log_list.addItem(
                f"{ts}  {log.model}  {log.output_tokens}tok  {log.duration_ms:.0f}ms  [{log.finish_reason}]"
            )

    def _clear(self) -> None:
        insights.clear()
        self._refresh()


from ui.skills_view import SkillsView
from ui.watchers_view import WatchersView
from ui.schedules_view import SchedulesView
from ui.server_view import ServerView

# ══════════════════════════════════════════════════════════════════════════════
# Management Window
# ══════════════════════════════════════════════════════════════════════════════

class ManagementWindow(QDialog):
    agents_changed = pyqtSignal()
    providers_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Orchestrator — Management")
        self.resize(860, 600)
        self.setObjectName("managementWindow")
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        tabs = QTabWidget()
        tabs.setObjectName("mgmtTabs")

        self.agents_tab = AgentsTab()
        self.agents_tab.agents_changed.connect(self.agents_changed)
        tabs.addTab(self.agents_tab, "🤖 Agents")

        self.providers_tab = ProvidersTab()
        self.providers_tab.providers_changed.connect(self.providers_changed)
        tabs.addTab(self.providers_tab, "☁️ Providers")

        self.models_tab = ModelsTab()
        tabs.addTab(self.models_tab, "📦 Models")

        self.skills_tab = SkillsView()
        tabs.addTab(self.skills_tab, "📜 Skills")

        self.watchers_tab = WatchersView()
        tabs.addTab(self.watchers_tab, "👁️ Watchers")

        self.schedules_tab = SchedulesView()
        tabs.addTab(self.schedules_tab, "⏰ Schedules")

        self.insights_tab = InsightsTab()
        tabs.addTab(self.insights_tab, "📊 Insights")

        self.server_tab = ServerView()
        tabs.addTab(self.server_tab, "📡 Server")

        layout.addWidget(tabs)
