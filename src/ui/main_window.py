from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QPushButton, QComboBox, QLabel, QMessageBox,
                               QApplication, QLineEdit, QHBoxLayout)
from PySide6.QtCore import Qt, Slot
from src.ui.config_dialog import ConfigDialog
from src.odoo.connection import OdooConnection
from src.export.excel_exporter import ExcelExporter
import sys
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exportador de BOM")
        self.setGeometry(100, 100, 600, 400)
        
        # Inicializar conexión Odoo
        self.odoo = OdooConnection()
        
        # Almacenar productos para búsqueda
        self.all_products = []
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title_label = QLabel("Exportador de Lista de Materiales")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        
        # Estado de conexión
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)
        
        # Búsqueda y selector de productos
        search_label = QLabel("Buscar producto:")
        layout.addWidget(search_label)
        
        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escriba para buscar...")
        self.search_input.textChanged.connect(self.filter_products)
        layout.addWidget(self.search_input)
        
        # Contador de resultados
        self.results_label = QLabel()
        layout.addWidget(self.results_label)
        
        # Selector de productos
        self.product_combo = QComboBox()
        self.product_combo.setPlaceholderText("Seleccione un producto")
        self.product_combo.setMinimumWidth(400)
        layout.addWidget(self.product_combo)
        layout.addSpacing(10)
        
        # Botones
        self.export_button = QPushButton("Exportar BOM")
        self.export_button.setEnabled(False)
        self.export_button.setMinimumWidth(120)
        
        self.config_button = QPushButton("Configuración")
        self.config_button.setMinimumWidth(120)
        
        # Añadir botones al layout
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.config_button)
        layout.addLayout(button_layout)
        
        # Espacio flexible al final
        layout.addStretch()
        
        # Conectar señales
        self.config_button.clicked.connect(self.show_config_dialog)
        self.export_button.clicked.connect(self.export_bom)
        self.product_combo.currentIndexChanged.connect(self.on_product_selected)
        
        # Cargar configuración inicial
        self.check_config()

    def filter_products(self, search_text: str):
        """Filtra los productos basado en el texto de búsqueda"""
        self.product_combo.clear()
        
        if not search_text:
            # Si no hay texto de búsqueda, mostrar todos los productos
            filtered_products = self.all_products
        else:
            # Filtrar por código o nombre, ignorando mayúsculas/minúsculas
            search_text = search_text.lower()
            filtered_products = [
                product for product in self.all_products
                if search_text in product['name'].lower() or
                   (product.get('default_code') and search_text in product['default_code'].lower())
            ]
        
        # Actualizar el combo box con los productos filtrados
        for product in filtered_products:
            display_name = f"[{product['default_code']}] {product['name']}" if product.get('default_code') else product['name']
            self.product_combo.addItem(display_name, product['id'])
        
        # Actualizar contador de resultados
        total = len(self.all_products)
        filtered = len(filtered_products)
        if search_text:
            self.results_label.setText(f"Mostrando {filtered} de {total} productos")
        else:
            self.results_label.setText(f"Total: {total} productos")

    def check_config(self):
        """Verifica si existe configuración y conecta con Odoo"""
        if not os.path.exists('config.json'):
            self.status_label.setText("Sin configuración")
            self.status_label.setStyleSheet("color: orange;")
            QMessageBox.information(
                self,
                "Configuración necesaria",
                "Por favor configure la conexión a Odoo para comenzar."
            )
            self.show_config_dialog()
        else:
            self.connect_to_odoo()

    def connect_to_odoo(self):
        """Intenta conectar con Odoo y cargar productos"""
        try:
            success, message = self.odoo.connect()
            if success:
                self.status_label.setText("Conectado a Odoo")
                self.status_label.setStyleSheet("color: green;")
                self.load_products()
            else:
                self.status_label.setText(f"Error: {message}")
                self.status_label.setStyleSheet("color: red;")
                QMessageBox.warning(self, "Error de conexión", message)
        except Exception as e:
            self.status_label.setText("Error de conexión")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al conectar con Odoo: {str(e)}"
            )

    def load_products(self):
        """Carga los productos con BOM desde Odoo"""
        try:
            self.all_products = self.odoo.get_bom_products()
            
            if not self.all_products:
                QMessageBox.information(
                    self,
                    "Sin productos",
                    "No se encontraron productos con lista de materiales"
                )
                return
            
            # Mostrar todos los productos inicialmente
            self.filter_products("")
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al cargar productos: {str(e)}"
            )

    @Slot()
    def show_config_dialog(self):
        dialog = ConfigDialog(self)
        if dialog.exec():
            self.check_config()

    @Slot()
    def export_bom(self):
        try:
            product_id = self.product_combo.currentData()
            product_name = self.product_combo.currentText()
            if not product_id:
                return
            
            # Obtener datos de la BOM
            bom_data = self.odoo.get_bom_data(product_id)
            
            # Exportar a Excel
            exporter = ExcelExporter()
            filename = exporter.export_bom(bom_data, product_name)
            
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"BOM exportada exitosamente a:\n{filename}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al exportar BOM: {str(e)}"
            )

    @Slot(int)
    def on_product_selected(self, index):
        self.export_button.setEnabled(index >= 0)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())                                                                                                                                                                                                                                                                                                                    