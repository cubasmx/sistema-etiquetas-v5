#!/bin/bash

echo "=== Instalador Sistema de Etiquetas para Fedora ==="

# Verificar que el ejecutable existe
if [ ! -f "dist/SistemaEtiquetas" ]; then
    echo "❌ Error: No se encontró el ejecutable dist/SistemaEtiquetas"
    echo "Ejecute primero: ./build_fedora.sh"
    exit 1
fi

# Crear directorio de instalación
INSTALL_DIR="/opt/sistema-etiquetas"
echo "Instalando en: $INSTALL_DIR"

# Crear directorio si no existe
sudo mkdir -p "$INSTALL_DIR"

# Copiar archivos
echo "Copiando archivos..."
sudo cp dist/SistemaEtiquetas "$INSTALL_DIR/"
sudo cp styles.qss "$INSTALL_DIR/" 2>/dev/null || echo "styles.qss no encontrado, continuando..."
sudo cp odoo_config.py "$INSTALL_DIR/" 2>/dev/null || echo "odoo_config.py no encontrado, continuando..."
sudo cp printer_config.json "$INSTALL_DIR/" 2>/dev/null || echo "printer_config.json no encontrado, continuando..."

# Hacer el ejecutable ejecutable
sudo chmod +x "$INSTALL_DIR/SistemaEtiquetas"

# Crear enlace simbólico en /usr/local/bin
echo "Creando enlace simbólico..."
sudo ln -sf "$INSTALL_DIR/SistemaEtiquetas" /usr/local/bin/sistema-etiquetas

# Crear archivo .desktop para el menú de aplicaciones
DESKTOP_FILE="/usr/share/applications/sistema-etiquetas.desktop"
echo "Creando entrada en el menú de aplicaciones..."

sudo tee "$DESKTOP_FILE" > /dev/null << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sistema de Etiquetas
Comment=Sistema de impresión de etiquetas con integración Odoo
Exec=sistema-etiquetas
Icon=$INSTALL_DIR/icon.ico
Terminal=false
Categories=Office;
EOF

# Copiar icono si existe
if [ -f "src/assets/icon.ico" ]; then
    sudo cp src/assets/icon.ico "$INSTALL_DIR/"
fi

echo "✅ Instalación completada!"
echo ""
echo "La aplicación está disponible como:"
echo "  - Comando: sistema-etiquetas"
echo "  - Menú de aplicaciones: Sistema de Etiquetas"
echo ""
echo "Para desinstalar:"
echo "  sudo rm -rf $INSTALL_DIR"
echo "  sudo rm /usr/local/bin/sistema-etiquetas"
echo "  sudo rm $DESKTOP_FILE" 