# -*- coding: utf-8 -*-
import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLabel,
    QProgressBar
)

class TransformadorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Configuración de la ventana principal
        self.setWindowTitle('Transformador Excel a CSV')
        self.setGeometry(100, 100, 600, 200)

        # Crear layouts
        main_layout = QVBoxLayout()
        file_layout = QHBoxLayout()
        
        # Botones para archivo Excel
        self.excel_label = QLabel('Archivo Excel: No seleccionado')
        self.excel_button = QPushButton('Seleccionar Excel')
        self.excel_button.clicked.connect(self.select_excel)
        
        file_layout.addWidget(self.excel_label)
        file_layout.addWidget(self.excel_button)

        # Botón para guardar CSV
        self.save_button = QPushButton('Guardar CSV')
        self.save_button.clicked.connect(self.save_csv)
        self.save_button.setEnabled(False)

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.hide()

        # Status label
        self.status_label = QLabel('')

        # Agregar widgets al layout principal
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.save_button)
        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        
        # Variables para almacenar datos
        self.excel_path = None
        self.df = None

    def select_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos Excel (*.xlsx *.xls);;Todos los archivos (*)"
        )

        if file_path:
            try:
                self.excel_path = file_path
                self.excel_label.setText(f'Archivo Excel: {file_path}')
                
                # Leer el archivo Excel
                self.progress.show()
                self.progress.setValue(20)
                self.df = pd.read_excel(file_path, usecols=[0, 2])  # Leer solo columnas A y C
                self.progress.setValue(100)
                
                # Habilitar botón de guardar
                self.save_button.setEnabled(True)
                self.status_label.setText('Excel cargado correctamente')
                
            except Exception as e:
                self.status_label.setText(f'Error al leer el archivo: {str(e)}')
                self.progress.hide()
            
    def save_csv(self):
        if self.df is not None:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar archivo CSV",
                "",
                "Archivos CSV (*.csv);;Todos los archivos (*)"
            )

            if save_path:
                try:
                    self.progress.show()
                    self.progress.setValue(20)
                    
                    # Crear el nuevo DataFrame con el formato requerido
                    col_names = self.df.columns.tolist()
                    new_df = pd.DataFrame()
                    new_df['id_producto'] = self.df[col_names[0]]  # Primera columna del Excel
                    new_df['code_128'] = self.df[col_names[0]]  # Repetir primera columna
                    new_df['nombre'] = self.df[col_names[1]]  # Tercera columna del Excel
                    
                    self.progress.setValue(60)
                    
                    # Guardar como CSV
                    new_df.to_csv(save_path, index=False, encoding='utf-8')
                    
                    self.progress.setValue(100)
                    self.status_label.setText('Archivo CSV guardado correctamente')
                    
                except Exception as e:
                    self.status_label.setText(f'Error al guardar el archivo: {str(e)}')
                finally:
                    self.progress.hide()

# Solo ejecutar si se llama directamente
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransformadorWindow()
    window.show()
    sys.exit(app.exec())
