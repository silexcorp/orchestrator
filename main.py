"""
main.py — Entry point for Orchestrator Linux.
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from styles import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Orchestrator")
    app.setOrganizationName("OrchestratorAI")

    # Typography
    app.setFont(QFont("Inter", 11))

    # Dark stylesheet
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
