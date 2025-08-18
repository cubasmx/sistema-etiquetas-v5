#!/bin/bash

echo "=== Sistema de Etiquetas - Build para Fedora ==="

# Verificar si estamos en Fedora
if ! grep -q "fedora" /etc/os-release; then
    echo "Advertencia: Este script está diseñado para Fedora"
fi

# Instalar dependencias del sistema
echo "Instalando dependencias del sistema..."
sudo dnf install -y python3-pip python3-devel gcc gcc-c++ make

# Instalar dependencias de Qt
echo "Instalando dependencias de Qt..."
sudo dnf install -y qt6-qtbase-devel qt6-qtbase-gui qt6-qtbase-widgets

# Instalar PyInstaller si no está instalado
echo "Verificando PyInstaller..."
pip3 install --user pyinstaller

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
pip3 install --user -r requirements.txt

# Crear directorio de build si no existe
mkdir -p dist

# Limpiar builds anteriores
echo "Limpiando builds anteriores..."
rm -rf build dist/SistemaEtiquetas

# Construir el ejecutable
echo "Construyendo ejecutable..."
pyinstaller --clean sistema_etiquetas_fedora.spec

# Verificar que el ejecutable se creó
if [ -f "dist/SistemaEtiquetas" ]; then
    echo "✅ Build exitoso!"
    echo "El ejecutable está en: dist/SistemaEtiquetas"
    echo "Tamaño del archivo: $(du -h dist/SistemaEtiquetas | cut -f1)"
    
    # Hacer el ejecutable ejecutable
    chmod +x dist/SistemaEtiquetas
    
    echo ""
    echo "Para ejecutar la aplicación:"
    echo "./dist/SistemaEtiquetas"
else
    echo "❌ Error en el build"
    exit 1
fi 