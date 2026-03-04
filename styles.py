"""Global stylesheet for Orchestrator AI Code Editor."""

STYLESHEET = """
/* ── Base ───────────────────────────────────────────────────────────────── */
QMainWindow, QWidget, QDialog {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 10pt;
}

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
QToolBar {
    background-color: #161b22;
    border-bottom: 1px solid #30363d;
    spacing: 10px;
    padding: 5px;
}

QToolBar QLabel {
    color: #8b949e;
}

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #30363d;
}

/* ── Inputs & Combos ──────────────────────────────────────────────────────── */
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    padding: 4px;
}

QComboBox {
    background-color: #21262d;
    min-width: 150px;
}

QComboBox::drop-down {
    border: none;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    padding: 5px 12px;
}

QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}

#execBtn {
    background-color: #238636;
    color: white;
}

#stopBtn {
    background-color: #da3633;
    color: white;
}

/* ── Scrollbars ───────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
