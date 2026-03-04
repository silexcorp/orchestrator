"""Global stylesheet for Orchestrator."""

STYLESHEET = """
/* ── Base ───────────────────────────────────────────────────────────────── */
QMainWindow, QWidget, QDialog {
    background-color: #0d0d12;
    color: #e8e8f0;
    font-family: 'Inter', 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
#sidebar {
    background-color: #111118;
    border-right: 1px solid #1e1e2e;
}

#sidebarTitle {
    font-size: 17px;
    font-weight: 700;
    color: #a78bfa;
    padding: 18px 16px 8px 16px;
    letter-spacing: 0.3px;
}

#sidebarSep {
    color: #1e1e2e;
    margin: 2px 12px;
}

#sectionLabel {
    font-size: 10px;
    font-weight: 600;
    color: #44446a;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 6px 16px 2px 16px;
}

/* ── New Chat Button ──────────────────────────────────────────────────────── */
#newChatBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 13px;
    font-weight: 600;
    margin: 6px 12px;
    text-align: left;
}
#newChatBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8b5cf6, stop:1 #6366f1);
}
#newChatBtn:pressed { opacity: 0.85; }

/* ── Conversation List ────────────────────────────────────────────────────── */
#convList {
    background: transparent;
    border: none;
    padding: 2px 8px;
}
#convList::item {
    background: transparent;
    border-radius: 8px;
    padding: 8px 10px;
    margin: 1px 0;
    color: #8888aa;
    font-size: 12px;
}
#convList::item:selected {
    background-color: #1e1e32;
    color: #e8e8f0;
}
#convList::item:hover:!selected {
    background-color: #16161f;
    color: #c4c4d4;
}

/* ── Combos ───────────────────────────────────────────────────────────────── */
QComboBox, #agentCombo, #modelCombo {
    background-color: #1a1a28;
    color: #c4c4d4;
    border: 1px solid #2e2e4e;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    margin: 3px 12px;
}
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    background-color: #1a1a28;
    color: #e8e8f0;
    border: 1px solid #2e2e4e;
    selection-background-color: #7c3aed;
}

/* ── Chat Area ────────────────────────────────────────────────────────────── */
#chatArea { background-color: #0d0d12; }

QScrollArea, #chatScroll { border: none; background: transparent; }
QScrollBar:vertical {
    background: #111118;
    width: 5px;
    border-radius: 2px;
}
QScrollBar::handle:vertical {
    background: #2e2e4e;
    border-radius: 2px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Welcome Screen ───────────────────────────────────────────────────────── */
#welcomeContainer { background: transparent; }

#welcomeTitle {
    font-size: 32px;
    font-weight: 700;
    color: #a78bfa;
    padding-bottom: 4px;
}
#welcomeSubtitle {
    font-size: 14px;
    color: #55557a;
    padding-bottom: 20px;
}
#suggestionBtn {
    background-color: #15151e;
    border: 1px solid #252540;
    border-radius: 12px;
    color: #a0a0c0;
    padding: 12px 18px;
    font-size: 13px;
    text-align: left;
    max-width: 520px;
    margin: 3px auto;
}
#suggestionBtn:hover {
    background-color: #1e1e32;
    border-color: #7c3aed;
    color: #e8e8f0;
}

/* ── Message Bubbles ──────────────────────────────────────────────────────── */
#roleName {
    font-size: 10px;
    font-weight: 600;
    color: #44446a;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 0 4px;
}

#userBubble {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    border-radius: 16px 16px 4px 16px;
    color: white;
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.55;
}
#aiBubble {
    background-color: #16161f;
    border: 1px solid #1e1e30;
    border-radius: 16px 16px 16px 4px;
    color: #d8d8ec;
    padding: 12px 16px;
    font-size: 14px;
    line-height: 1.55;
}

/* ── Input Area ───────────────────────────────────────────────────────────── */
#inputArea {
    background-color: #0d0d12;
    border-top: 1px solid #1a1a28;
    padding: 10px;
}

#inputField {
    background-color: #15151e;
    border: 1px solid #252548;
    border-radius: 12px;
    color: #e8e8f0;
    font-size: 14px;
    padding: 12px 16px;
    selection-background-color: #7c3aed;
}
#inputField:focus { border-color: #7c3aed; }

/* ── Buttons ──────────────────────────────────────────────────────────────── */
#sendBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 13px;
    font-weight: 600;
    min-width: 72px;
}
#sendBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #8b5cf6, stop:1 #6366f1);
}
#sendBtn:disabled { background-color: #252540; color: #444466; }

#stopBtn {
    background-color: #1c1020;
    border: 1px solid #5a2e7c;
    color: #c084fc;
    border-radius: 12px;
    padding: 12px 20px;
    font-size: 13px;
    font-weight: 600;
    min-width: 72px;
}
#stopBtn:hover { background-color: #2a1830; border-color: #8b5cf6; }

/* ── Management Window ────────────────────────────────────────────────────── */
#managementWindow { background-color: #0f0f18; }

#mgmtTabs {
    background: transparent;
    border: none;
}
QTabWidget::pane {
    border: none;
    background-color: #0d0d12;
}
QTabBar::tab {
    background: #111118;
    color: #6666aa;
    border: none;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 500;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #a78bfa;
    border-bottom: 2px solid #7c3aed;
    background: #0d0d12;
}
QTabBar::tab:hover:!selected {
    color: #c4c4d4;
    background: #15151e;
}

#mgmtLeft {
    background-color: #0d0d14;
    border-right: 1px solid #1e1e2e;
}

#mgmtSectionTitle {
    font-size: 14px;
    font-weight: 700;
    color: #a78bfa;
    padding: 4px 0;
}

#pullProgress {
    border: none;
    border-radius: 4px;
    background-color: #1a1a28;
    color: #7c3aed;
    text-align: center;
    height: 8px;
}
#pullProgress::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c3aed, stop:1 #4f46e5);
    border-radius: 4px;
}

/* ── Form inputs ──────────────────────────────────────────────────────────── */
QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #1a1a28;
    color: #e8e8f0;
    border: 1px solid #2a2a45;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: #7c3aed;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #7c3aed;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 16px;
}

QListWidget {
    background: transparent;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 4px;
}
QListWidget::item {
    border-radius: 6px;
    padding: 8px 10px;
    color: #a0a0c0;
}
QListWidget::item:selected {
    background-color: #1e1e32;
    color: #e8e8f0;
}
QListWidget::item:hover:!selected {
    background-color: #16161f;
}

QCheckBox { color: #a0a0c0; spacing: 8px; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #2e2e4e;
    background: #1a1a28;
}
QCheckBox::indicator:checked {
    background: #7c3aed;
    border-color: #7c3aed;
}

/* ── Menu bar ─────────────────────────────────────────────────────────────── */
QMenuBar {
    background-color: #0d0d12;
    color: #a0a0c0;
    border-bottom: 1px solid #1a1a28;
}
QMenuBar::item:selected { background-color: #1e1e32; color: #e8e8f0; }
QMenu {
    background-color: #111118;
    color: #e8e8f0;
    border: 1px solid #2a2a45;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item { padding: 8px 24px; border-radius: 6px; }
QMenu::item:selected { background-color: #7c3aed; }
QMenu::separator { height: 1px; background: #2a2a45; margin: 4px 8px; }
"""
