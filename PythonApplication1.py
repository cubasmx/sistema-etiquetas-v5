# -*- coding: utf-8 -*-
import sys
from datetime import datetime
import os
import json
import socket
import ast

from PyQt6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
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
from PyQt6.QtCore import Qt

# === Dependencias externas del proyecto ===
from odoo_client import OdooClient
from src.utils.mysql_client import MysqlClient


# --------------------------
# Utilidades de recursos/SSL
# --------------------------
def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con PyInstaller y desarrollo."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Forzar uso de certificados incluidos
os.environ['SSL_CERT_FILE'] = resource_path('src/assets/cacert.pem')


# ----------------------
# Diálogo de Config Odoo
# ----------------------
class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configuración de Odoo')
        self.resize(450, 400)
        self.setMinimumSize(450, 400)
        self.setModal(True)

        layout = QFormLayout()

        self.url_input = QLineEdit()
        self.db_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)

        layout.addRow('URL:', self.url_input)
        layout.addRow('Base de datos:', self.db_input)
        layout.addRow('Usuario:', self.username_input)
        layout.addRow('Contraseña:', self.password_input)
        layout.addRow('Puerto:', self.port_input)

        button_layout = QHBoxLayout()
        save_button = QPushButton('Guardar')
        cancel_button = QPushButton('Cancelar')
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.load_current_config()

    def load_current_config(self):
        """Carga ODOO_CONFIG desde odoo_config.py sin usar eval."""
        try:
            with open('odoo_config.py', 'r', encoding='utf-8') as f:
                content = f.read()
                start = content.find('{')
                end = content.rfind('}') + 1
                if start > -1 and end > 0:
                    config_dict = ast.literal_eval(content[start:end])
                    self.url_input.setText(config_dict.get('url', ''))
                    self.db_input.setText(config_dict.get('db', ''))
                    self.username_input.setText(config_dict.get('username', ''))
                    self.password_input.setText(config_dict.get('password', ''))
                    self.port_input.setValue(int(config_dict.get('port', 443)))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error al cargar la configuración: {str(e)}")

    def get_config(self):
        return {
            'url': self.url_input.text().strip(),
            'db': self.db_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text(),
            'port': self.port_input.value()
        }


# ---------------------------
# Diálogo de Config de Impresora (incluye offsets)
# ---------------------------
class PrinterConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Configuración de Impresora')
        self.resize(400, 260)
        self.setMinimumSize(400, 260)
        self.setModal(True)

        layout = QFormLayout()

        self.printer_ip_input = QLineEdit()
        self.printer_ip_input.setText('10.10.2.46')
        self.printer_port_input = QSpinBox()
        self.printer_port_input.setRange(1, 65535)
        self.printer_port_input.setValue(6101)

        # NUEVO: offsets (en dots)
        self.offset_v_input = QSpinBox()
        self.offset_v_input.setRange(-500, 500)
        self.offset_v_input.setValue(0)
        self.offset_h_input = QSpinBox()
        self.offset_h_input.setRange(-500, 500)
        self.offset_h_input.setValue(0)

        layout.addRow('IP de la Impresora:', self.printer_ip_input)
        layout.addRow('Puerto de la Impresora:', self.printer_port_input)
        layout.addRow('Ajuste vertical (dots):', self.offset_v_input)
        layout.addRow('Ajuste horizontal (dots):', self.offset_h_input)

        button_layout = QHBoxLayout()
        save_button = QPushButton('Guardar')
        cancel_button = QPushButton('Cancelar')
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.load_current_config()

    def load_current_config(self):
        try:
            with open('printer_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.printer_ip_input.setText(config.get('printer_ip', '10.10.2.46'))
                self.printer_port_input.setValue(int(config.get('printer_port', 6101)))
                self.offset_v_input.setValue(int(config.get('vertical_offset_dots', 0)))
                self.offset_h_input.setValue(int(config.get('horizontal_offset_dots', 0)))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error al cargar la configuración de impresora: {e}")

    def get_config(self):
        return {
            'printer_ip': self.printer_ip_input.text().strip(),
            'printer_port': self.printer_port_input.value(),
            'vertical_offset_dots': self.offset_v_input.value(),
            'horizontal_offset_dots': self.offset_h_input.value(),
        }


# -----------------
# Ventana principal
# -----------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Impresión de Etiquetas')
        self.setGeometry(100, 100, 500, 560)
        self.resize(500, 560)
        self.setMinimumSize(500, 560)

        # Conexión Odoo
        try:
            self.odoo_client = OdooClient()
            self.connection_status = True
        except Exception as e:
            self.connection_status = False
            QMessageBox.warning(self, "Error de Conexión",
                                f"No se pudo conectar a Odoo: {str(e)}\n"
                                "La aplicación funcionará en modo offline.")

        # Botones configuración
        self.config_button = QPushButton('⚙️ Configuración')
        self.config_button.clicked.connect(self.show_config_dialog)
        self.printer_config_button = QPushButton('🖨️ Config. Impresora')
        self.printer_config_button.clicked.connect(self.show_printer_config_dialog)

        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.addWidget(self.config_button)
        top_buttons_layout.addWidget(self.printer_config_button)

        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Buscar ID o Nombre de Producto')
        self.search_button = QPushButton('Buscar')
        self.clear_button = QPushButton('Limpiar')

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_button)

        # Resultados
        self.result_label = QLabel('Resultados de la búsqueda:')
        self.results_area = QListWidget()
        self.results_area.itemClicked.connect(self.item_selected)
        self.results_area.setWordWrap(True)

        self.scroll_inner = QWidget()
        scroll_layout = QVBoxLayout(self.scroll_inner)
        scroll_layout.addWidget(self.results_area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_inner)

        # Campos OP/SGC/cantidad/lote/número
        self.op_description_label = QLabel('OP:')
        self.op_description_input = QLineEdit()

        self.sgc_version_label = QLabel('Versión SGC:')
        self.sgc_version_input = QLineEdit()
        self.sgc_version_input.setPlaceholderText('Ej: V1.0')

        self.quantity_label = QLabel('Cantidad a Imprimir:')
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setMinimum(1)
        self.quantity_spinbox.setMaximum(1000)
        self.quantity_spinbox.setValue(1)

        self.lote_total_label = QLabel('Total de etiquetas en el lote:')
        self.lote_total_spinbox = QSpinBox()
        self.lote_total_spinbox.setMinimum(1)
        self.lote_total_spinbox.setMaximum(10000)
        self.lote_total_spinbox.setValue(1)

        self.start_number_label = QLabel('Número de inicio:')
        self.start_number_spinbox = QSpinBox()
        self.start_number_spinbox.setMinimum(1)
        self.start_number_spinbox.setMaximum(10000)
        self.start_number_spinbox.setValue(1)

        op_layout = QHBoxLayout()
        op_layout.addWidget(self.op_description_label)
        op_layout.addWidget(self.op_description_input)

        sgc_layout = QHBoxLayout()
        sgc_layout.addWidget(self.sgc_version_label)
        sgc_layout.addWidget(self.sgc_version_input)

        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(self.quantity_label)
        quantity_layout.addWidget(self.quantity_spinbox)

        lote_layout = QHBoxLayout()
        lote_layout.addWidget(self.lote_total_label)
        lote_layout.addWidget(self.lote_total_spinbox)

        start_layout = QHBoxLayout()
        start_layout.addWidget(self.start_number_label)
        start_layout.addWidget(self.start_number_spinbox)

        # Botón imprimir
        self.print_button = QPushButton('Imprimir')

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

        # Señales
        self.search_button.clicked.connect(self.perform_search)
        self.clear_button.clicked.connect(self.clear_search_and_results)
        self.search_input.returnPressed.connect(self.perform_search)
        self.print_button.clicked.connect(self.handle_print)

        # Estado
        self.selected_product = None

    # -----------------------
    # Lógica de búsqueda Odoo
    # -----------------------
    def perform_search(self):
        if not self.connection_status:
            QMessageBox.warning(self, "Error", "No hay conexión con Odoo")
            return

        query = self.search_input.text().strip()
        if not query:
            return

        try:
            products = self.odoo_client.search_products(query)
            self.results_area.clear()
            if products:
                for product in products:
                    code = product.get('default_code') or 'N/A'
                    name = product.get('name') or ''
                    item = QListWidgetItem(f"ID: {code} — {name}")
                    item.setData(Qt.ItemDataRole.UserRole, {
                        'id_producto': code,
                        'nombre': name
                    })
                    self.results_area.addItem(item)
            else:
                self.results_area.addItem(f'No se encontraron coincidencias para: "{query}"')

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al buscar productos: {str(e)}")

    def item_selected(self, item: QListWidgetItem):
        datos = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(datos, dict) and 'id_producto' in datos:
            self.selected_product = datos
            print(f"Producto seleccionado: {self.selected_product}")
        else:
            self.selected_product = None

    # --------------------
    # Lógica de impresión
    # --------------------
    def handle_print(self):
        if not self.selected_product:
            QMessageBox.warning(self, "Error", "Por favor, busca y selecciona un producto primero.")
            return

        op_description = self.op_description_input.text().strip()
        sgc_version = self.sgc_version_input.text().strip()
        quantity = self.quantity_spinbox.value()
        id_producto = self.selected_product.get('id_producto', 'N/A')
        nombre_producto = self.selected_product.get('nombre', 'N/A')
        lote_total = self.lote_total_spinbox.value()
        start_number = self.start_number_spinbox.value()

        # Validación de rango
        if start_number + quantity - 1 > lote_total:
            QMessageBox.warning(self, "Error", "El rango de etiquetas a imprimir excede el total del lote.")
            return

        # 1) Registrar en BD (si no está desactivado) con manejo robusto
        db_logged = False
        if os.getenv('ETIQUETAS_DISABLE_MYSQL', '0') != '1':
            try:
                client = MysqlClient()
                connected = False
                try:
                    connected = client.connect()
                except Exception as ce:
                    print(f"[ERROR] Conectando MySQL: {ce}")
                    connected = False

                if connected:
                    user = None  # TODO: pon aquí el usuario real si lo tienes
                    try:
                        db_logged = client.insert_impresion(
                            ID=id_producto,
                            user=user,
                            nombre=nombre_producto,
                            op=op_description,
                            versionsgc=sgc_version,
                            cantidad=quantity,
                            totallote=lote_total,
                            numinicio=start_number
                        )
                    except Exception as ie:
                        print(f"[ERROR] insert_impresion lanzó excepción: {ie}")
                        db_logged = False
                    finally:
                        try:
                            client.close()
                        except Exception:
                            pass
                else:
                    print("[WARN] MySQL no disponible (connect() False)")

                print(f"[LOG] Resultado de insert_impresion: {db_logged}")

                if not db_logged:
                    resp = QMessageBox.question(
                        self,
                        "Base de datos no disponible",
                        "No se pudo guardar el registro en la base de datos.\n\n"
                        "¿Deseas imprimir de todas formas?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    if resp != QMessageBox.StandardButton.Yes:
                        return
            except Exception as e:
                print(f"[ERROR] Excepción general en bloque MySQL: {e}")
                resp = QMessageBox.question(
                    self,
                    "Error registrando en BD",
                    f"Ocurrió un error registrando en BD:\n{str(e)}\n\n¿Imprimir de todas formas?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return

        # 2) Envío a la impresora Zebra/Argox vía socket
        print("--- Generando etiquetas ZPL ---")
        try:
            # Config impresora (por defecto / json)
            printer_ip = "10.10.2.46"
            printer_port = 6101
            vertical_offset = 0
            horizontal_offset = 0
            try:
                with open('printer_config.json', 'r', encoding='utf-8') as f:
                    printer_config = json.load(f)
                    printer_ip = printer_config.get('printer_ip', printer_ip)
                    printer_port = int(printer_config.get('printer_port', printer_port))
                    vertical_offset = int(printer_config.get('vertical_offset_dots', 0))
                    horizontal_offset = int(printer_config.get('horizontal_offset_dots', 0))
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Error al cargar configuración de impresora: {e}")

            # Helper para aplicar offsets y evitar negativos
            def adj(x, y):
                xx = x + horizontal_offset
                yy = y + vertical_offset
                if xx < 0: xx = 0
                if yy < 0: yy = 0
                return xx, yy

            sent_count = 0
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(int(os.getenv('ETIQUETAS_PRINTER_TIMEOUT', '5')))
                sock.connect((printer_ip, printer_port))

                for i in range(start_number, start_number + quantity):
                    # Convertir a Latin-1 para la impresora
                    nombre_producto_print = nombre_producto.encode('latin1', errors='replace').decode('latin1')
                    op_description_print = op_description.encode('latin1', errors='replace').decode('latin1')
                    sgc_version_print = sgc_version.encode('latin1', errors='replace').decode('latin1')

                    # Posiciones base (en dots) — mismas que ya usabas
                    x1, y1   = adj(20,   5)    # nombre
                    x2, y2   = adj(80,   37)   # barcode
                    x3, y3   = adj(20,   145)  # OP
                    x4, y4   = adj(20,   170)  # i/total
                    x5, y5   = adj(200,  170)  # versión SGC
                    x6, y6   = adj(200,  145)  # fecha

                    zpl_label = (
                        "^XA\n"
                        f"^FO{x1},{y1}^A0N,18,18^FD{nombre_producto_print}^FS\n"
                        f"^FO{x2},{y2}^BCN,75,Y,N,N^FD{id_producto}^FS\n"
                        f"^FO{x3},{y3}^A0N,20,20^FD{op_description_print}^FS\n"
                        f"^FO{x4},{y4}^A0N,18,18^FD{i}/{lote_total}^FS\n"
                        f"^FO{x5},{y5}^A0N,18,18^FD{sgc_version_print}^FS\n"
                        f"^FO{x6},{y6}^A0N,18,18^FD{datetime.now().strftime('%d/%m/%Y')}^FS\n"
                        "^PQ1,1,1,Y^XZ"
                    )

                    try:
                        print(f"--- Enviando etiqueta {i}/{lote_total} (offset H:{horizontal_offset} V:{vertical_offset}) ---")
                        sock.sendall(zpl_label.encode('latin1'))
                        sent_count += 1
                    except Exception as se:
                        print(f"[ERROR] Falló envío de etiqueta {i}: {se}")
                        continue

            print(f"Se enviaron {sent_count} etiquetas a la impresora!")
            if sent_count < quantity:
                QMessageBox.warning(
                    self,
                    "Impresión incompleta",
                    f"Se enviaron {sent_count} de {quantity} etiquetas.\n"
                    "Verifica la conexión de la impresora o reduce los offsets."
                )

        except ConnectionRefusedError:
            QMessageBox.warning(
                self, "Error",
                f"No se pudo conectar a la impresora en {printer_ip}:{printer_port}.\n"
                "Asegúrate de que la impresora está encendida y conectada a la red."
            )
        except socket.timeout:
            QMessageBox.warning(
                self, "Error",
                f"Conexión a la impresora agotó el tiempo ({printer_ip}:{printer_port})."
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al enviar a la impresora: {str(e)}")

    # -------------
    # Utilidades UI
    # -------------
    def clear_search_and_results(self):
        self.search_input.clear()
        self.results_area.clear()
        self.selected_product = None

    def show_config_dialog(self):
        dialog = ConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            try:
                # Guardar como .py (para no romper OdooClient existente)
                config_content = (
                    "# -*- coding: utf-8 -*-\n\n"
                    "# Configuración de conexión a Odoo\n"
                    f"ODOO_CONFIG = {json.dumps(config, indent=4)}"
                )
                with open('odoo_config.py', 'w', encoding='utf-8') as f:
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

    def show_printer_config_dialog(self):
        dialog = PrinterConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            try:
                with open('printer_config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4)
                QMessageBox.information(self, "Éxito", "Configuración de impresora guardada correctamente.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al guardar la configuración de impresora: {str(e)}")


# ---------------------
# Arranque de la app Qt
# ---------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Carga QSS y elimina automáticamente líneas con 'transition' (no soportado por Qt)
    try:
        with open(resource_path("styles.qss"), "r", encoding="utf-8") as f:
            qss = f.read()
        cleaned_lines = []
        for line in qss.splitlines():
            if 'transition' in line.lower():
                continue
            cleaned_lines.append(line)
        app.setStyleSheet("\n".join(cleaned_lines))
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"[WARN] No se pudo aplicar stylesheet: {e}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
