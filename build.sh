#!/bin/bash

# Activar entorno virtual
source venv/bin/activate

# Ejecutar PyInstaller con todos los recursos y dependencias
pyinstaller --noconfirm --windowed --onefile PythonApplication1.py \
  --name sistema-etiquetas \
  --icon=src/assets/icon.ico \
  --add-data "styles.qss:." \
  --add-data "odoo_config.py:." \
  --add-data "config.json:." \
  --add-data "printer_config.json:." \
  --add-data "src:src" \
  --add-data "src/ui/icons:src/ui/icons" \
  --add-data "src/assets:src/assets" \
  --hidden-import mysql.connector \
  --hidden-import mysql \
  --hidden-import odoorpc \
  --hidden-import odoo_client

echo "\nBuild completo. El ejecutable está en dist/sistema-etiquetas" 