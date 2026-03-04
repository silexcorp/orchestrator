import os
import re
from PyQt6.QtWidgets import (
    QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QTabWidget, QTabBar, QMessageBox, QFileDialog
)
from PyQt6.QtGui import (
    QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QKeySequence,
    QShortcut, QFontDatabase, QTextFormat, QPainter
)
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # Formats
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#f97583"))  # Red/Orange
        keyword_format.setFontWeight(QFont.Weight.Bold)

        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#ffab70"))  # Orange

        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#b392f0"))  # Purple

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#9ecbff"))  # Light Blue

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#8b949e"))  # Gray
        comment_format.setFontItalic(True)

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#79c0ff"))  # Blue

        # Rules
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class", "continue",
            "def", "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
            "while", "with", "yield"
        ]
        for word in keywords:
            pattern = rf"\b{word}\b"
            self.highlighting_rules.append((pattern, keyword_format))

        builtins = ["print", "len", "range", "str", "int", "float", "list", "dict", "set", "tuple", "open"]
        for word in builtins:
            pattern = rf"\b{word}\b"
            self.highlighting_rules.append((pattern, builtin_format))

        self.highlighting_rules.append((r"\bdef\s+(\w+)", function_format))
        self.highlighting_rules.append((r'".*?"', string_format))
        self.highlighting_rules.append((r"'.*?'", string_format))
        self.highlighting_rules.append((r"#.*", comment_format))
        self.highlighting_rules.append((r"\b[0-9]+\b", number_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    text_modified = pyqtSignal()

    def __init__(self, file_path=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.dirty = False
        
        # Setup Font
        font = QFont("JetBrains Mono", 12)
        if QFontDatabase.families().count("JetBrains Mono") == 0:
            font = QFont("Consolas", 12)
        self.setFont(font)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)

        # UI Styling
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0d1117;
                color: #e6edf3;
                border: none;
            }
        """)

        self.highlighter = PythonHighlighter(self.document())
        
        # Line Numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        if not self.dirty:
            self.dirty = True
            self.text_modified.emit()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#161b22"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#8b949e"))
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

class EditorWidget(QTabWidget):
    active_file_changed = pyqtSignal(str, str) # path, content

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_tab_changed)
        
        self.setStyleSheet("""
            QTabWidget::pane { border: none; background: #0d1117; }
            QTabBar::tab { background: #161b22; color: #8b949e; padding: 8px 12px; border-right: 1px solid #30363d; }
            QTabBar::tab:selected { background: #0d1117; color: #e6edf3; }
        """)

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_active_tab)
        QShortcut(QKeySequence("Ctrl+Tab"), self, self.next_tab)

    def close_active_tab(self):
        idx = self.currentIndex()
        if idx >= 0: self.close_tab(idx)

    def next_tab(self):
        count = self.count()
        if count <= 1: return
        next_idx = (self.currentIndex() + 1) % count
        self.setCurrentIndex(next_idx)

    def open_file(self, path):
        path = os.path.abspath(path)
        # Check if already open
        for i in range(self.count()):
            if self.widget(i).file_path == path:
                self.setCurrentIndex(i)
                return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            editor = CodeEditor(path)
            editor.setPlainText(content)
            editor.dirty = False
            editor.text_modified.connect(lambda: self._update_tab_title(editor))
            
            index = self.addTab(editor, os.path.basename(path))
            self.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def _update_tab_title(self, editor):
        for i in range(self.count()):
            if self.widget(i) == editor:
                title = os.path.basename(editor.file_path)
                if editor.dirty:
                    title += " ●"
                self.setTabText(i, title)
                break

    def close_tab(self, index):
        editor = self.widget(index)
        if editor.dirty:
            res = QMessageBox.question(self, "Guardar cambios", 
                                     f"¿Deseas guardar los cambios en {os.path.basename(editor.file_path)}?",
                                     QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
            if res == QMessageBox.StandardButton.Save:
                self.save_file(index)
            elif res == QMessageBox.StandardButton.Cancel:
                return
        
        self.removeTab(index)

    def save_file(self, index=None):
        if index is None or isinstance(index, bool):
            index = self.currentIndex()
        
        if index < 0: return
        
        editor = self.widget(index)
        if not editor: return
        
        if not editor.file_path:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar como")
            if path:
                editor.file_path = os.path.abspath(path)
                self.setTabText(index, os.path.basename(path))
            else:
                return
        
        try:
            with open(editor.file_path, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
            editor.dirty = False
            self.setTabText(index, os.path.basename(editor.file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {e}")

    def get_active_file(self):
        idx = self.currentIndex()
        if idx >= 0:
            return self.widget(idx).file_path
        return None

    def _on_tab_changed(self, index):
        if index >= 0:
            editor = self.widget(index)
            self.active_file_changed.emit(editor.file_path, editor.toPlainText())
        else:
            self.active_file_changed.emit("", "")
