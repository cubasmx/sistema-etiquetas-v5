#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador gráfico para Sistema de Etiquetas - Windows
Permite instalar y configurar el sistema de forma fácil en Windows
"""

import sys
import os
import subprocess
import json
import shutil
import winreg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QProgressBar, QTextEdit, QMessageBox,
    QFileDialog, QCheckBox, QGroupBox, QLineEdit, QSpinBox,
    QFormLayout, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

class InstallerThread(QThread):
    """Hilo para ejecutar instalaciones sin bloquear la UI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, action, params=None):
        super().__init__()
        self.action = action
        self.params = params or {}
    
    def run(self):
        try:
            if self.action == "create_shortcut":
                self.create_shortcut()
            elif self.action == "copy_files":
                self.copy_files()
            elif self.action == "register_app":
                self.register_app()
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def create_shortcut(self):
        """Crea un acceso directo en el escritorio"""
        self.progress.emit("Creando acceso directo en el escritorio...")
        
        executable_path = self.params.get('executable_path', '')
        if not executable_path or not os.path.exists(executable_path):
            raise Exception("No se encontró el ejecutable")
        
        # Obtener ruta del escritorio
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        shortcut_path = os.path.join(desktop, "Sistema de Etiquetas.lnk")
        
        # Crear acceso directo usando PowerShell
        ps_script = f"""
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{executable_path}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(executable_path)}"
        $Shortcut.Description = "Sistema de Etiquetas"
        $Shortcut.Save()
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Error creando acceso directo: {result.stderr}")
        
        self.progress.emit("¡Acceso directo creado correctamente!")
        self.finished.emit(True, "Acceso directo creado correctamente")
    
    def copy_files(self):
        """Copia archivos a ubicación de instalación"""
        self.progress.emit("Copiando archivos...")
        
        source = self.params.get('source', '')
        destination = self.params.get('destination', '')
        
        if not source or not os.path.exists(source):
            raise Exception("No se encontró el archivo fuente")
        
        os.makedirs(destination, exist_ok=True)
        shutil.copy2(source, destination)
        
        self.progress.emit("¡Archivos copiados correctamente!")
        self.finished.emit(True, "Archivos copiados correctamente")
    
    def register_app(self):
        """Registra la aplicación en Windows"""
        self.progress.emit("Registrando aplicación...")
        
        executable_path = self.params.get('executable_path', '')
        if not executable_path:
            raise Exception("No se especificó la ruta del ejecutable")
        
        # Crear entrada en el registro para que aparezca en "Agregar o quitar programas"
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\SistemaEtiquetas"
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Sistema de Etiquetas")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0")
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "ENSA")
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, executable_path)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, os.path.dirname(executable_path))
        except Exception as e:
            self.progress.emit(f"Advertencia: No se pudo registrar en el sistema: {e}")
        
        self.progress.emit("¡Aplicación registrada correctamente!")
        self.finished.emit(True, "Aplicación registrada correctamente")

class ConfigDialog(QDialog):
    """Diálogo para configurar la instalación"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Instalación")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Grupo de configuración de archivos
        files_group = QGroupBox("Archivos")
        files_layout = QFormLayout()
        
        self.executable_path = QLineEdit()
        self.executable_path.setPlaceholderText("Ruta al ejecutable sistema-etiquetas.exe")
        self.browse_executable_btn = QPushButton("Buscar...")
        self.browse_executable_btn.clicked.connect(self.browse_executable)
        
        exec_layout = QHBoxLayout()
        exec_layout.addWidget(self.executable_path)
        exec_layout.addWidget(self.browse_executable_btn)
        files_layout.addRow("Ejecutable:", exec_layout)
        
        self.install_location = QLineEdit()
        self.install_location.setText("C:\\Program Files\\Sistema de Etiquetas")
        self.browse_location_btn = QPushButton("Buscar...")
        self.browse_location_btn.clicked.connect(self.browse_location)
        
        location_layout = QHBoxLayout()
        location_layout.addWidget(self.install_location)
        location_layout.addWidget(self.browse_location_btn)
        files_layout.addRow("Ubicación de instalación:", location_layout)
        
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)
        
        # Grupo de opciones
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout()
        
        self.create_desktop_shortcut = QCheckBox("Crear acceso directo en el escritorio")
        self.create_desktop_shortcut.setChecked(True)
        options_layout.addWidget(self.create_desktop_shortcut)
        
        self.create_start_menu = QCheckBox("Crear entrada en el menú inicio")
        self.create_start_menu.setChecked(True)
        options_layout.addWidget(self.create_start_menu)
        
        self.register_app = QCheckBox("Registrar en el sistema (requiere permisos de administrador)")
        self.register_app.setChecked(False)
        options_layout.addWidget(self.register_app)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Instalar")
        self.cancel_button = QPushButton("Cancelar")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
    
    def browse_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar ejecutable", "", "Ejecutables (*.exe)"
        )
        if file_path:
            self.executable_path.setText(file_path)
    
    def browse_location(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de instalación"
        )
        if folder_path:
            self.install_location.setText(folder_path)
    
    def get_config(self):
        return {
            'executable_path': self.executable_path.text(),
            'install_location': self.install_location.text(),
            'create_desktop_shortcut': self.create_desktop_shortcut.isChecked(),
            'create_start_menu': self.create_start_menu.isChecked(),
            'register_app': self.register_app.isChecked()
        }

class InstallerWindow(QMainWindow):
    """Ventana principal del instalador"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instalador - Sistema de Etiquetas")
        self.setGeometry(100, 100, 600, 500)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Título
        title = QLabel("Instalador del Sistema de Etiquetas")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Descripción
        desc = QLabel("Este instalador te ayudará a configurar el Sistema de Etiquetas en Windows.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        # Botón de configuración
        self.config_btn = QPushButton("⚙️ Configurar Instalación")
        self.config_btn.clicked.connect(self.show_config)
        layout.addWidget(self.config_btn)
        
        # Botón de instalación rápida
        self.quick_install_btn = QPushButton("🚀 Instalación Rápida")
        self.quick_install_btn.clicked.connect(self.quick_install)
        layout.addWidget(self.quick_install_btn)
        
        # Área de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setMaximumHeight(200)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # Botón de salir
        self.exit_btn = QPushButton("Salir")
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn)
        
        # Configuración por defecto
        self.config = {
            'executable_path': '',
            'install_location': 'C:\\Program Files\\Sistema de Etiquetas',
            'create_desktop_shortcut': True,
            'create_start_menu': True,
            'register_app': False
        }
    
    def show_config(self):
        """Muestra el diálogo de configuración"""
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            QMessageBox.information(self, "Configuración", "Configuración guardada. Ahora puedes proceder con la instalación.")
    
    def quick_install(self):
        """Instalación rápida con configuración por defecto"""
        # Buscar el ejecutable automáticamente
        possible_paths = [
            "dist/sistema-etiquetas.exe",
            "sistema-etiquetas.exe",
            os.path.expanduser("~/Desktop/sistema-etiquetas.exe"),
            os.path.expanduser("~/Downloads/sistema-etiquetas.exe")
        ]
        
        executable_found = False
        for path in possible_paths:
            if os.path.exists(path):
                self.config['executable_path'] = os.path.abspath(path)
                executable_found = True
                break
        
        if not executable_found:
            QMessageBox.warning(self, "Error", "No se encontró el ejecutable. Por favor, usa 'Configurar Instalación' para especificar la ruta.")
            return
        
        self.start_installation()
    
    def start_installation(self):
        """Inicia el proceso de instalación"""
        if not self.config['executable_path']:
            QMessageBox.warning(self, "Error", "Por favor, especifica la ruta del ejecutable.")
            return
        
        self.progress_bar.setVisible(True)
        self.log_area.clear()
        
        # Ejecutar instalación en hilo separado
        self.install_thread = InstallerThread("create_shortcut", self.config)
        self.install_thread.progress.connect(self.update_log)
        self.install_thread.finished.connect(self.on_install_finished)
        self.install_thread.start()
    
    def update_log(self, message):
        """Actualiza el área de log"""
        self.log_area.append(message)
        self.log_area.ensureCursorVisible()
    
    def on_install_finished(self, success, message):
        """Maneja el fin de la instalación"""
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Éxito", f"Instalación completada: {message}")
            self.log_area.append("✅ " + message)
        else:
            QMessageBox.critical(self, "Error", f"Error en la instalación: {message}")
            self.log_area.append("❌ " + message)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Instalador Sistema de Etiquetas")
    
    window = InstallerWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 