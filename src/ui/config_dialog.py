from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout,
                                 QLineEdit, QPushButton, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt
import json
import os

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Odoo")
        self.setMinimumWidth(400)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Crear campos de entrada
        self.url_input = QLineEdit()
        self.db_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.port_input = QSpinBox()
        
        # Configurar campos
        self.url_input.setPlaceholderText("https://mi-empresa.odoo.com")
        self.db_input.setPlaceholderText("nombre-base-datos")
        self.username_input.setPlaceholderText("usuario@empresa.com")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)
        self.port_input.setToolTip("443 para Odoo SaaS, 8069 para instalaciones locales")
        
        # Añadir campos al formulario
        form_layout.addRow("URL:", self.url_input)
        form_layout.addRow("Base de datos:", self.db_input)
        form_layout.addRow("Usuario:", self.username_input)
        form_layout.addRow("Contraseña:", self.password_input)
        form_layout.addRow("Puerto:", self.port_input)
        
        # Botones
        button_layout = QVBoxLayout()
        save_button = QPushButton("Guardar")
        save_button.setMinimumWidth(100)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setMinimumWidth(100)
        
        # Conectar señales
        save_button.clicked.connect(self.validate_and_save)
        cancel_button.clicked.connect(self.reject)
        
        # Añadir layouts y widgets
        layout.addLayout(form_layout)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addSpacing(20)
        layout.addLayout(button_layout)

    def load_config(self):
        """Carga la configuración existente si existe"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    self.url_input.setText(config.get('url', ''))
                    self.db_input.setText(config.get('database', ''))
                    self.username_input.setText(config.get('username', ''))
                    self.password_input.setText(config.get('password', ''))
                    self.port_input.setValue(int(config.get('port', 443)))
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Error al cargar la configuración: {str(e)}"
            )

    def validate_and_save(self):
        """Valida y guarda la configuración"""
        # Obtener valores
        url = self.url_input.text().strip()
        database = self.db_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        port = self.port_input.value()
        
        # Validar campos requeridos
        if not all([url, database, username, password]):
            QMessageBox.warning(
                self,
                "Campos requeridos",
                "Todos los campos son obligatorios"
            )
            return
        
        # Validar formato de URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Crear configuración
        config = {
            'url': url,
            'database': database,
            'username': username,
            'password': password,
            'port': port
        }
        
        try:
            # Guardar configuración
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar la configuración: {str(e)}"
            ) 