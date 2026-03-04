"""
main.py — Entry point for Orchestrator AI Code Editor.
"""
import sys
import os
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from styles import STYLESHEET

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Orchestrator AI")
    app.setOrganizationName("We are Okan")

    # Load Fonts if available
    # QFontDatabase.addApplicationFont("path/to/font.ttf")

    # Base UI Font
    app.setFont(QFont("Segoe UI", 10))

    # Apply Theme
    app.setStyleSheet(STYLESHEET)

    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
