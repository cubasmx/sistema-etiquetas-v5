#!/usr/bin/env python3
"""
Script principal para ejecutar el exportador de BOM
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Forzar uso de certificados incluidos
os.environ['SSL_CERT_FILE'] = resource_path('src/assets/cacert.pem')

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