#!/bin/bash

echo "=== Build para Windows desde Fedora ==="

# Verificar que Wine esté instalado
if ! command -v wine &> /dev/null; then
    echo "❌ Wine no está instalado. Instalando..."
    sudo dnf install -y wine
fi

# Verificar que Python esté disponible en Wine
if ! wine python --version &> /dev/null; then
    echo "❌ Python no está instalado en Wine. Instalando..."
    # Descargar e instalar Python para Windows
    wget https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe
    wine python-3.11.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
    rm python-3.11.8-amd64.exe
fi

# Instalar PyInstaller en Wine
echo "📦 Instalando PyInstaller en Wine..."
wine python -m pip install pyinstaller

# Instalar dependencias en Wine
echo "📦 Instalando dependencias en Wine..."
wine python -m pip install PyQt6 mysql-connector-python odoorpc PyMySQL

# Crear el ejecutable para Windows
echo "🔨 Compilando ejecutable para Windows..."
wine pyinstaller --noconfirm --windowed --onefile PythonApplication1.py \
  --name sistema-etiquetas \
  --icon=src/assets/icon.ico \
  --add-data "styles.qss;." \
  --add-data "odoo_config.py;." \
  --add-data "config.json;." \
  --add-data "printer_config.json;." \
  --add-data "src;src" \
  --add-data "src/ui/icons;src/ui/icons" \
  --add-data "src/assets;src/assets" \
  --hidden-import mysql.connector \
  --hidden-import mysql \
  --hidden-import odoorpc \
  --hidden-import odoo_client \
  --hidden-import PyQt6 \
  --hidden-import PyQt6.QtCore \
  --hidden-import PyQt6.QtWidgets \
  --hidden-import PyQt6.QtGui

echo "✅ Build completado. El ejecutable está en dist/sistema-etiquetas.exe"
echo "📁 Puedes copiar dist/sistema-etiquetas.exe a tu sistema Windows" 