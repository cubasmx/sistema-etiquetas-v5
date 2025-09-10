from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
                                 QLineEdit, QPushButton, QSpinBox, QMessageBox,
                                 QTabWidget, QWidget, QLabel, QGroupBox)
from PySide6.QtCore import Qt
import json
import os

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Sistema")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Crear widget de pestañas
        self.tab_widget = QTabWidget()
        
        # Pestaña 1: Configuración de Odoo
        self.odoo_tab = self.create_odoo_tab()
        self.tab_widget.addTab(self.odoo_tab, "Configuración Odoo")
        
        # Pestaña 2: Configuración de Base de Datos
        self.mysql_tab = self.create_mysql_tab()
        self.tab_widget.addTab(self.mysql_tab, "Base de Datos Historial")
        
        layout.addWidget(self.tab_widget)
        
        # Botones
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar Configuración")
        save_button.setMinimumWidth(150)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setMinimumWidth(100)
        
        # Conectar señales
        save_button.clicked.connect(self.validate_and_save)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        
        layout.addSpacing(20)
        layout.addLayout(button_layout)

    def create_odoo_tab(self):
        """Crear la pestaña de configuración de Odoo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de configuración Odoo
        odoo_group = QGroupBox("Configuración de Conexión Odoo")
        odoo_layout = QFormLayout(odoo_group)
        odoo_layout.setSpacing(10)
        
        # Crear campos de entrada para Odoo
        self.url_input = QLineEdit()
        self.db_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.port_input = QSpinBox()
        
        # Configurar campos Odoo
        self.url_input.setPlaceholderText("https://mi-empresa.odoo.com")
        self.db_input.setPlaceholderText("nombre-base-datos")
        self.username_input.setPlaceholderText("usuario@empresa.com")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)
        self.port_input.setToolTip("443 para Odoo SaaS, 8069 para instalaciones locales")
        
        # Añadir campos al formulario Odoo
        odoo_layout.addRow("URL:", self.url_input)
        odoo_layout.addRow("Base de datos:", self.db_input)
        odoo_layout.addRow("Usuario:", self.username_input)
        odoo_layout.addRow("Contraseña:", self.password_input)
        odoo_layout.addRow("Puerto:", self.port_input)
        
        layout.addWidget(odoo_group)
        layout.addStretch()
        
        return tab

    def create_mysql_tab(self):
        """Crear la pestaña de configuración de MySQL"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo de configuración MySQL
        mysql_group = QGroupBox("Configuración de Base de Datos del Historial")
        mysql_layout = QFormLayout(mysql_group)
        mysql_layout.setSpacing(10)
        
        # Crear campos de entrada para MySQL
        self.mysql_host_input = QLineEdit()
        self.mysql_port_input = QSpinBox()
        self.mysql_user_input = QLineEdit()
        self.mysql_password_input = QLineEdit()
        self.mysql_database_input = QLineEdit()
        
        # Configurar campos MySQL
        self.mysql_host_input.setPlaceholderText("10.10.1.8")
        self.mysql_port_input.setRange(1, 65535)
        self.mysql_port_input.setValue(3306)
        self.mysql_user_input.setPlaceholderText("master")
        self.mysql_password_input.setEchoMode(QLineEdit.Password)
        self.mysql_password_input.setPlaceholderText("Ensa2025.")
        self.mysql_database_input.setPlaceholderText("etiquetas")
        
        # Añadir campos al formulario MySQL
        mysql_layout.addRow("Servidor:", self.mysql_host_input)
        mysql_layout.addRow("Puerto:", self.mysql_port_input)
        mysql_layout.addRow("Usuario:", self.mysql_user_input)
        mysql_layout.addRow("Contraseña:", self.mysql_password_input)
        mysql_layout.addRow("Base de datos:", self.mysql_database_input)
        
        layout.addWidget(mysql_group)
        
        # Información adicional
        info_label = QLabel(
            "Esta configuración se usa para guardar el historial de impresiones.\n"
            "Si el servidor no está disponible, la aplicación continuará funcionando\n"
            "pero no se guardará el historial."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return tab

    def load_config(self):
        """Carga la configuración existente si existe"""
        try:
            # Cargar configuración de Odoo
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    self.url_input.setText(config.get('url', ''))
                    self.db_input.setText(config.get('database', ''))
                    self.username_input.setText(config.get('username', ''))
                    self.password_input.setText(config.get('password', ''))
                    self.port_input.setValue(int(config.get('port', 443)))
            
            # Cargar configuración de MySQL
            if os.path.exists('mysql_config.json'):
                with open('mysql_config.json', 'r') as f:
                    mysql_config = json.load(f)
                    self.mysql_host_input.setText(mysql_config.get('host', '10.10.1.8'))
                    self.mysql_port_input.setValue(int(mysql_config.get('port', 3306)))
                    self.mysql_user_input.setText(mysql_config.get('user', 'master'))
                    self.mysql_password_input.setText(mysql_config.get('password', 'Ensa2025.'))
                    self.mysql_database_input.setText(mysql_config.get('database', 'etiquetas'))
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Error al cargar la configuración: {str(e)}"
            )

    def validate_and_save(self):
        """Valida y guarda la configuración"""
        # Validar configuración de Odoo
        odoo_url = self.url_input.text().strip()
        odoo_database = self.db_input.text().strip()
        odoo_username = self.username_input.text().strip()
        odoo_password = self.password_input.text().strip()
        odoo_port = self.port_input.value()
        
        # Validar campos requeridos de Odoo
        if not all([odoo_url, odoo_database, odoo_username, odoo_password]):
            QMessageBox.warning(
                self,
                "Campos requeridos",
                "Todos los campos de Odoo son obligatorios"
            )
            return
        
        # Validar formato de URL de Odoo
        if not odoo_url.startswith(('http://', 'https://')):
            odoo_url = 'https://' + odoo_url
        
        # Validar configuración de MySQL
        mysql_host = self.mysql_host_input.text().strip()
        mysql_port = self.mysql_port_input.value()
        mysql_user = self.mysql_user_input.text().strip()
        mysql_password = self.mysql_password_input.text().strip()
        mysql_database = self.mysql_database_input.text().strip()
        
        # Validar campos requeridos de MySQL
        if not all([mysql_host, mysql_user, mysql_password, mysql_database]):
            QMessageBox.warning(
                self,
                "Campos requeridos",
                "Todos los campos de MySQL son obligatorios"
            )
            return
        
        try:
            # Guardar configuración de Odoo
            odoo_config = {
                'url': odoo_url,
                'database': odoo_database,
                'username': odoo_username,
                'password': odoo_password,
                'port': odoo_port
            }
            
            with open('config.json', 'w') as f:
                json.dump(odoo_config, f, indent=4)
            
            # Guardar configuración de MySQL
            mysql_config = {
                'host': mysql_host,
                'port': mysql_port,
                'user': mysql_user,
                'password': mysql_password,
                'database': mysql_database
            }
            
            with open('mysql_config.json', 'w') as f:
                json.dump(mysql_config, f, indent=4)
            
            QMessageBox.information(
                self,
                "Configuración guardada",
                "La configuración se ha guardado correctamente.\n"
                "Reinicia la aplicación para aplicar los cambios."
            )
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar la configuración: {str(e)}"
            ) 