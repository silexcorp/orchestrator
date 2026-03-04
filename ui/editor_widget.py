import os
import re
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QKeySequence, QShortcut, QFontDatabase, QTextFormat, QPainter
from PyQt6.QtCore import Qt, QRect, QSize

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

class EditorWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        
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
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.update_line_number_area_width(0)

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_file)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo)

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

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#21262d")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def open_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.setPlainText(f.read())
            self.current_file = path
        except Exception as e:
            print(f"Error opening file: {e}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.toPlainText())
            except Exception as e:
                print(f"Error saving file: {e}")

    def get_content(self):
        return self.toPlainText()

    def set_content(self, text):
        self.setPlainText(text)
