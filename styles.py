"""Global stylesheet for Orchestrator AI Code Editor."""

STYLESHEET = """
/* ── Base ───────────────────────────────────────────────────────────────── */
QMainWindow, QWidget, QDialog {
    background-color: #05060a;
    color: #e0e6ed;
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 10.5pt;
}

/* ── Toolbar ─────────────────────────────────────────────────────────────── */
QToolBar {
    background-color: #0a0b10;
    border-bottom: 1px solid rgba(0, 242, 255, 0.15);
    spacing: 12px;
    padding: 10px;
}

QToolBar QLabel {
    color: #00f2ff;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 9pt;
    letter-spacing: 1px;
}

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #1a1c24;
}

/* ── Inputs & Combos ──────────────────────────────────────────────────────── */
QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {
    background-color: #0f111a;
    border: 1px solid #1a1c24;
    border-radius: 14px;
    color: #f0f4f8;
    padding: 10px 14px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #00f2ff;
    background-color: #151722;
}

QComboBox {
    min-width: 170px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

/* ── Buttons ──────────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #151722;
    border: 1px solid #1a1c24;
    border-radius: 20px;
    color: #e0e6ed;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1a1c24;
    border-color: #00f2ff;
}

#sendBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f2ff, stop:1 #8a2be2);
    color: #ffffff;
    border: none;
    font-size: 14pt;
}

#sendBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #33f5ff, stop:1 #a155ea);
}

#stopBtn {
    background-color: transparent;
    border: 1px solid #ff4b4b;
    color: #ff4b4b;
}

/* ── Scrollbars ───────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(0, 242, 255, 0.2);
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 242, 255, 0.4);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
