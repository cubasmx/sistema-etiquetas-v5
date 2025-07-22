#!/usr/bin/env python3
"""
Script principal para ejecutar el exportador de BOM
"""
import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    with open("styles.qss", "r") as f:
        qss = f.read()
        app.setStyleSheet(qss)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    sys.exit(main()) 