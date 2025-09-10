# -*- coding: utf-8 -*-
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QListWidget,
    QSpinBox,
    QWidget,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QHBoxLayout,
    QMessageBox,
    QDialog,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QSizePolicy,
    QTabWidget,
    QGroupBox
)
import socket
from odoo_client import OdooClient
import json
import os
from src.utils.mysql_client import MysqlClient
from PyQt6.QtCore import Qt

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller y desarrollo."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Forzar uso de certificados incluidos
os.environ['SSL_CERT_FILE'] = resource_path('src/assets/cacert.pem')

class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Historial de Impresiones')
        self.resize(1000, 500)
        self.setMinimumSize(900, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        # Filtro de orden
        self.order_combo = QComboBox()
        self.order_combo.addItems(['Más reciente primero', 'Más antiguo primero'])
        self.order_combo.currentIndexChanged.connect(self.load_history)
        layout.addWidget(self.order_combo)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels([
            'ID', 'Nombre', 'OP', 'SGC', 'Cantidad', 'Total Lote', 'Inicio', 'Fecha'
        ])
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.table_widget)

        self.load_history()

    def load_history(self):
        order_desc = self.order_combo.currentIndex() == 0 if hasattr(self, 'order_combo') else True
        try:
            client = MysqlClient()
            client.connect()
            resultados = client.select_impresiones(order_desc=order_desc)
            if resultados:
                self.table_widget.setRowCount(len(resultados))
                for row, entry in enumerate(resultados):
                    fecha_raw = entry.get('fecha_operacion', entry.get('FECHA_OPERACION', ''))
                    try:
                        if isinstance(fecha_raw, datetime):
                            fecha_fmt = fecha_raw.strftime("%d/%m/%Y %H:%M")
                        else:
                            fecha_fmt = datetime.strptime(str(fecha_raw), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    except Exception:
                        fecha_fmt = str(fecha_raw)
                    id_ = entry.get('ID', entry.get('id', ''))
                    nombre = entry.get('nombre', entry.get('NOMBRE', ''))
                    op = entry.get('op', entry.get('OP', ''))
                    versionsgc = entry.get('versionsgc', entry.get('VERSIONSGC', ''))
                    cantidad = entry.get('cantidad', entry.get('CANTIDAD', ''))
                    totallote = entry.get('totallote', entry.get('TOTALLOTE', ''))
                    numinicio = entry.get('numinicio', entry.get('NUMINICIO', ''))
                    values = [id_, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_fmt]
                    for col, value in enumerate(values):
                        item = QTableWidgetItem(str(value))
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        if col == 1:  # Columna 'Nombre'
                            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        self.table_widget.setItem(row, col, item)
                self.table_widget.setColumnWidth(1, 200)  # Columna 'Nombre'
                self.table_widget.resizeRowsToContents()
                self.table_widget.setWordWrap(True)
            else:
                self.table_widget.setRowCount(1)
                self.table_widget.setItem(0, 0, QTableWidgetItem('No hay historial disponible.'))
            client.close()
        except Exception as e:
            import traceback
            print("[ERROR] Excepción al cargar historial:", e)
            traceback.print_exc()
            self.table_widget.setRowCount(1)
            self.table_widget.setItem(0, 0, QTableWidgetItem(f"Error al cargar historial: {str(e)}"))

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Sistema")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setModal(True)
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
        layout.setSpacing(15)  # Espaciado vertical entre elementos
        layout.setContentsMargins(10, 10, 10, 10)  # Márgenes del layout
        
        # Grupo de configuración Odoo
        odoo_group = QGroupBox("Configuración de Conexión Odoo")
        odoo_layout = QFormLayout(odoo_group)
        odoo_layout.setSpacing(15)  # Más espaciado entre campos
        odoo_layout.setContentsMargins(15, 20, 15, 15)  # Márgenes internos del grupo
        
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
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
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
        layout.setSpacing(15)  # Espaciado vertical entre elementos
        layout.setContentsMargins(10, 10, 10, 10)  # Márgenes del layout
        
        # Grupo de configuración MySQL
        mysql_group = QGroupBox("Configuración de Base de Datos del Historial")
        mysql_layout = QFormLayout(mysql_group)
        mysql_layout.setSpacing(15)  # Más espaciado entre campos
        mysql_layout.setContentsMargins(15, 20, 15, 15)  # Márgenes internos del grupo
        
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
        self.mysql_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.mysql_password_input.setPlaceholderText("Ensa2025.")
        self.mysql_database_input.setPlaceholderText("etiquetas")
        
        # Añadir campos al formulario MySQL
        mysql_layout.addRow("Servidor:", self.mysql_host_input)
        mysql_layout.addRow("Puerto:", self.mysql_port_input)
        mysql_layout.addRow("Usuario:", self.mysql_user_input)
        mysql_layout.addRow("Contraseña:", self.mysql_password_input)
        mysql_layout.addRow("Base de datos:", self.mysql_database_input)
        
        layout.addWidget(mysql_group)
        
        # Espaciado antes del texto informativo
        layout.addSpacing(20)
        
        # Información adicional
        info_label = QLabel(
            "Esta configuración se usa para guardar el historial de impresiones.\n"
            "Si el servidor no está disponible, la aplicación continuará funcionando\n"
            "pero no se guardará el historial."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return tab

    def load_config(self):
        """Carga la configuración existente si existe"""
        try:
            # Cargar configuración de Odoo
            if os.path.exists('odoo_config.py'):
                with open('odoo_config.py', 'r') as f:
                    content = f.read()
                    # Extraer el diccionario de configuración usando eval
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start > -1 and end > 0:
                        config_dict = eval(content[start:end])
                        self.url_input.setText(config_dict.get('url', ''))
                        self.db_input.setText(config_dict.get('db', ''))
                        self.username_input.setText(config_dict.get('username', ''))
                        self.password_input.setText(config_dict.get('password', ''))
                        self.port_input.setValue(config_dict.get('port', 443))
            
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
                'db': odoo_database,
                'username': odoo_username,
                'password': odoo_password,
                'port': odoo_port
            }
            
            with open('odoo_config.py', 'w') as f:
                f.write(f"# -*- coding: utf-8 -*-\n\n")
                f.write(f"# Configuración de conexión a Odoo\n")
                f.write(f"ODOO_CONFIG = {odoo_config}\n")
            
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

    def get_config(self):
        return {
            'url': self.url_input.text(),
            'db': self.db_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'port': self.port_input.value()
        }

class PrinterConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configuración de Impresora')
        self.resize(400, 200)
        self.setMinimumSize(400, 200)
        self.setModal(True)
        
        # Crear layout
        layout = QFormLayout()
        
        # Campos de configuración de impresora
        self.printer_ip_input = QLineEdit()
        self.printer_ip_input.setText('10.10.2.46')  # IP por defecto
        self.printer_port_input = QSpinBox()
        self.printer_port_input.setRange(1, 65535)
        self.printer_port_input.setValue(6101)  # Puerto por defecto
        
        # Agregar campos al layout
        layout.addRow('IP de la Impresora:', self.printer_ip_input)
        layout.addRow('Puerto de la Impresora:', self.printer_port_input)
        
        # Botones
        button_layout = QHBoxLayout()
        save_button = QPushButton('Guardar')
        cancel_button = QPushButton('Cancelar')
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        # Conectar señales
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
        
        # Cargar configuración actual
        self.load_current_config()
    
    def load_current_config(self):
        try:
            with open('printer_config.json', 'r') as f:
                config = json.load(f)
                self.printer_ip_input.setText(config.get('printer_ip', '10.10.2.46'))
                self.printer_port_input.setValue(config.get('printer_port', 6101))
        except FileNotFoundError:
            # Si no existe el archivo, usar valores por defecto
            pass
        except Exception as e:
            print(f"Error al cargar la configuración de impresora: {str(e)}")
    
    def get_config(self):
        return {
            'printer_ip': self.printer_ip_input.text(),
            'printer_port': self.printer_port_input.value()
        }

class MainWindow(QWidget):
    def __init__(self):
        # Constructor de la ventana principal
        super().__init__()
        self.setWindowTitle('Impresión de Etiquetas')
        self.setGeometry(100, 100, 500, 500)
        self.resize(500, 500)
        self.setMinimumSize(500, 500)

        try:
            # Inicializar cliente de Odoo
            self.odoo_client = OdooClient()
            self.connection_status = True
        except Exception as e:
            self.connection_status = False
            QMessageBox.warning(self, "Error de Conexión", 
                              f"No se pudo conectar a Odoo: {str(e)}\n"
                              "La aplicación funcionará en modo offline.")

        # Botón de configuración
        self.config_button = QPushButton('⚙️ Configuración')
        self.config_button.clicked.connect(self.show_config_dialog)
        # Botón de historial
        self.history_button = QPushButton('📄 Ver Historial')
        self.history_button.clicked.connect(self.show_history_dialog)
        # Botón de configuración de impresora
        self.printer_config_button = QPushButton('🖨️ Config. Impresora')
        self.printer_config_button.clicked.connect(self.show_printer_config_dialog)

        # Layout para los botones superiores
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.addWidget(self.config_button)
        top_buttons_layout.addWidget(self.history_button)
        top_buttons_layout.addWidget(self.printer_config_button)

        # Botones y campos de entrada
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Buscar ID o Nombre de Producto')
        self.search_button = QPushButton('Buscar')
        self.clear_button = QPushButton('Limpiar')

        # Layout de búsqueda horizontal
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_button)

        # Área de resultados
        self.result_label = QLabel('Resultados de la búsqueda:')
        self.results_area = QListWidget()
        self.results_area.itemClicked.connect(self.item_selected)
        self.results_area.setWordWrap(True)

        # Configuración del área de desplazamiento
        self.scroll_inner = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_inner)
        scroll_layout.addWidget(self.results_area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_inner)

        # Campos para la Orden de Producción
        self.op_description_label = QLabel('OP:')
        self.op_description_input = QLineEdit()
        
        # Campo para versión SGC
        self.sgc_version_label = QLabel('Versión SGC:')
        self.sgc_version_input = QLineEdit()
        self.sgc_version_input.setPlaceholderText('Ej: V1.0')

        self.quantity_label = QLabel('Cantidad a Imprimir:')
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setMaximum(1000)
        self.quantity_spinbox.setValue(1)

        # Campo para total de etiquetas en el lote
        self.lote_total_label = QLabel('Total de etiquetas en el lote:')
        self.lote_total_spinbox = QSpinBox()
        self.lote_total_spinbox.setMinimum(1)
        self.lote_total_spinbox.setMaximum(10000)
        self.lote_total_spinbox.setValue(1)

        # Campo para número de inicio
        self.start_number_label = QLabel('Número de inicio:')
        self.start_number_spinbox = QSpinBox()
        self.start_number_spinbox.setMinimum(1)
        self.start_number_spinbox.setMaximum(10000)
        self.start_number_spinbox.setValue(1)

        # Layouts para OP, cantidad, lote y número de inicio
        op_layout = QHBoxLayout()
        op_layout.addWidget(self.op_description_label)
        op_layout.addWidget(self.op_description_input)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(self.quantity_spinbox)

        # Layout para versión SGC
        sgc_layout = QHBoxLayout()
        sgc_layout.addWidget(self.sgc_version_label)
        sgc_layout.addWidget(self.sgc_version_input)

        # Layouts para lote y número de inicio
        lote_layout = QHBoxLayout()
        lote_layout.addWidget(self.lote_total_label)
        lote_layout.addWidget(self.lote_total_spinbox)

        start_layout = QHBoxLayout()
        start_layout.addWidget(self.start_number_label)
        start_layout.addWidget(self.start_number_spinbox)

        # Botón de impresión
        self.print_button = QPushButton('Imprimir')

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_buttons_layout)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.result_label)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(op_layout)
        main_layout.addLayout(sgc_layout)
        main_layout.addLayout(quantity_layout)
        main_layout.addLayout(lote_layout)
        main_layout.addLayout(start_layout)
        main_layout.addWidget(self.print_button)

        # Conexiones de señales
        self.search_button.clicked.connect(self.perform_search)
        self.clear_button.clicked.connect(self.clear_search_and_results)
        self.search_input.returnPressed.connect(self.perform_search)
        self.print_button.clicked.connect(self.handle_print)

        # Variables de datos
        self.selected_product = None

    def perform_search(self):
        """Realiza búsqueda en Odoo"""
        if not self.connection_status:
            QMessageBox.warning(self, "Error", "No hay conexión con Odoo")
            return

        query = self.search_input.text()
        if not query:
            return

        try:
            products = self.odoo_client.search_products(query)
            
            self.results_area.clear()
            if products:
                for product in products:
                    item_text = f"ID: {product['default_code'] or 'N/A'}, "
                    item_text += f"Nombre: {product['name']}"
                    self.results_area.addItem(item_text)
            else:
                self.results_area.addItem(f'No se encontraron coincidencias para: "{query}"')
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al buscar productos: {str(e)}")

    def item_selected(self, item):
        """Procesa el elemento seleccionado de la lista"""
        texto_item = item.text()
        partes = texto_item.split(', ')
        seleccion = {}
        
        for parte in partes:
            clave_valor = parte.split(': ')
            if len(clave_valor) == 2:
                seleccion[clave_valor[0].strip()] = clave_valor[1].strip()

        if 'ID' in seleccion:
            self.selected_product = {
                'id_producto': seleccion['ID'],
                'nombre': seleccion['Nombre']
            }
            print(f"Producto seleccionado: {self.selected_product}")
        else:
            self.selected_product = None

    def handle_print(self):
        """Maneja la impresión de etiquetas"""
        if self.selected_product:
            op_description = self.op_description_input.text()
            sgc_version = self.sgc_version_input.text()
            quantity = self.quantity_spinbox.value()
            id_producto = self.selected_product.get('id_producto', 'N/A')
            nombre_producto = self.selected_product.get('nombre', 'N/A')
            lote_total = self.lote_total_spinbox.value()
            start_number = self.start_number_spinbox.value()

            # Validación
            if start_number + quantity - 1 > lote_total:
                QMessageBox.warning(self, "Error", "El rango de etiquetas a imprimir excede el total del lote.")
                return

            # Intentar guardar en la base de datos del historial (opcional)
            try:
                client = MysqlClient()
                client.connect()
                user = None
                insert_ok = client.insert_impresion(
                    ID=id_producto,
                    user=user,
                    nombre=nombre_producto,
                    op=op_description,
                    versionsgc=sgc_version,
                    cantidad=quantity,
                    totallote=lote_total,
                    numinicio=start_number
                )
                print(f'[LOG] Resultado de insert_impresion: {insert_ok}')
                client.close()
                if not insert_ok:
                    print('[WARNING] No se guardó la impresión en la base de datos del historial')
            except Exception as e:
                print(f'[WARNING] No se pudo conectar a la base de datos del historial: {e}')
                print('[INFO] La aplicación continuará funcionando sin guardar el historial')
                # No mostrar mensaje de error al usuario, solo continuar

            print("--- Generando etiquetas ZPL ---")
            try:
                # Cargar configuración de impresora
                printer_ip = "10.10.2.46"  # IP por defecto
                printer_port = 6101  # Puerto por defecto
                
                try:
                    with open('printer_config.json', 'r') as f:
                        printer_config = json.load(f)
                        printer_ip = printer_config.get('printer_ip', printer_ip)
                        printer_port = printer_config.get('printer_port', printer_port)
                except FileNotFoundError:
                    # Si no existe el archivo de configuración, usar valores por defecto
                    pass
                except Exception as e:
                    print(f"Error al cargar configuración de impresora: {e}")

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((printer_ip, printer_port))
                    for i in range(start_number, start_number + quantity):
                        # Convertir a Latin-1 para la impresora
                        nombre_producto_print = nombre_producto.encode('latin1', errors='replace').decode('latin1')
                        op_description_print = op_description.encode('latin1', errors='replace').decode('latin1')
                        sgc_version_print = sgc_version.encode('latin1', errors='replace').decode('latin1')

                        zpl_label = f"""^XA
                        ^FO20,5^A0N,18,18^FD{nombre_producto_print}^FS
                        ^FO80,37^BCN,75,Y,N,N^FD{id_producto}^FS
                        ^FO20,145^A0N,20,20^FD{op_description_print}^FS
                        ^FO20,170^A0N,18,18^FD{i}/{lote_total}^FS
                        ^FO200,170^A0N,18,18^FD{sgc_version_print}^FS
                        ^FO200,145^A0N,18,18^FD{datetime.now().strftime('%d/%m/%Y')}^FS
                        ^PQ1,1,1,Y^XZ"""

                        print(f"--- Enviando etiqueta {i}/{lote_total} ---")
                        print(zpl_label)
                        sock.sendall(zpl_label.encode('latin1'))
                    print(f"Se enviaron {quantity} etiquetas a la impresora!")

            except ConnectionRefusedError:
                QMessageBox.warning(self, "Error", 
                    f"No se pudo conectar a la impresora en {printer_ip}:{printer_port}.\n"
                    "Asegúrate de que la impresora está encendida y conectada a la red.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al enviar a la impresora: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Por favor, busca y selecciona un producto primero.")

    def clear_search_and_results(self):
        """Limpia el campo de búsqueda y resultados"""
        self.search_input.clear()
        self.results_area.clear()
        self.selected_product = None

    def show_config_dialog(self):
        """Muestra el diálogo de configuración"""
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            try:
                # Guardar la configuración
                config_content = f"""# -*- coding: utf-8 -*-

# Configuración de conexión a Odoo
ODOO_CONFIG = {json.dumps(config, indent=4)}"""
                
                with open('odoo_config.py', 'w') as f:
                    f.write(config_content)
                
                # Reiniciar el cliente de Odoo
                try:
                    self.odoo_client = OdooClient()
                    self.connection_status = True
                    QMessageBox.information(self, "Éxito", "Configuración guardada y conexión establecida correctamente.")
                except Exception as e:
                    self.connection_status = False
                    QMessageBox.warning(self, "Error de Conexión", 
                                      f"No se pudo conectar a Odoo con la nueva configuración: {str(e)}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al guardar la configuración: {str(e)}")

    def show_history_dialog(self):
        """Muestra el diálogo de historial"""
        dialog = HistoryDialog(self)
        dialog.exec()

    def show_printer_config_dialog(self):
        """Muestra el diálogo de configuración de impresora"""
        dialog = PrinterConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            try:
                # Guardar la configuración de impresora
                with open('printer_config.json', 'w') as f:
                    json.dump(config, f, indent=4)
                QMessageBox.information(self, "Éxito", "Configuración de impresora guardada correctamente.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al guardar la configuración de impresora: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open(resource_path("assets/styles.qss"), "r") as f:
        qss = f.read()
        app.setStyleSheet(qss)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
