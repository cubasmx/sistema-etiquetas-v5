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
    QFormLayout
)
import socket
from odoo_client import OdooClient
import json
import os

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configuración de Odoo')
        self.setModal(True)
        
        # Crear layout
        layout = QFormLayout()
        
        # Campos de configuración
        self.url_input = QLineEdit()
        self.db_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)
        
        # Agregar campos al layout
        layout.addRow('URL:', self.url_input)
        layout.addRow('Base de datos:', self.db_input)
        layout.addRow('Usuario:', self.username_input)
        layout.addRow('Contraseña:', self.password_input)
        layout.addRow('Puerto:', self.port_input)
        
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
        except Exception as e:
            print(f"Error al cargar la configuración: {str(e)}")
    
    def get_config(self):
        return {
            'url': self.url_input.text(),
            'db': self.db_input.text(),
            'username': self.username_input.text(),
            'password': self.password_input.text(),
            'port': self.port_input.value()
        }

class MainWindow(QWidget):
    def __init__(self):
        # Constructor de la ventana principal
        super().__init__()
        self.setWindowTitle('Impresión de Etiquetas')
        self.setGeometry(100, 100, 500, 500)

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

        # Layouts para OP y cantidad
        op_layout = QHBoxLayout()
        op_layout.addWidget(self.op_description_label)
        op_layout.addWidget(self.op_description_input)

        # Layout para versión SGC
        sgc_layout = QHBoxLayout()
        sgc_layout.addWidget(self.sgc_version_label)
        sgc_layout.addWidget(self.sgc_version_input)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(self.quantity_spinbox)

        # Botón de impresión
        self.print_button = QPushButton('Imprimir')

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.config_button)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.result_label)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(op_layout)
        main_layout.addLayout(sgc_layout)
        main_layout.addWidget(self.quantity_label)
        main_layout.addWidget(self.quantity_spinbox)
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

            print("--- Generando etiquetas ZPL ---")
            try:
                printer_ip = "10.10.2.34"
                printer_port = 9100

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((printer_ip, printer_port))
                    for i in range(1, quantity + 1):
                        # Convertir a Latin-1 para la impresora
                        nombre_producto_print = nombre_producto.encode('latin1', errors='replace').decode('latin1')
                        op_description_print = op_description.encode('latin1', errors='replace').decode('latin1')
                        sgc_version_print = sgc_version.encode('latin1', errors='replace').decode('latin1')

                        zpl_label = f"""^XA
                        ^FO50,35^A0N,18,18^FD{nombre_producto_print}^FS
                        ^FO50,60^BCN,75,Y,N,N^FD{id_producto}^FS
                        ^FO50,168^A0N,20,20^FD{op_description_print}^FS
                        ^FO50,188^A0N,18,18^FD{i}/{quantity}^FS
                        ^FO200,188^A0N,18,18^FD{sgc_version_print}^FS
                        ^FO215,168^A0N,18,18^FD{datetime.now().strftime('%d/%m/%Y')}^FS
                        ^PQ1,1,1,Y^XZ"""

                        print(f"--- Enviando etiqueta {i}/{quantity} ---")
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
