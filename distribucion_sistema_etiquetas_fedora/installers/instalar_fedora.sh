#!/bin/bash

# Instalador de Sistema de Etiquetas para Fedora
# Versión actualizada con configuración dinámica

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script debe ejecutarse como root (usar sudo)"
   exit 1
fi

echo "========================================"
echo "  Sistema de Etiquetas - Instalador Fedora"
echo "========================================"
echo ""

# Verificar que estamos en el directorio correcto
if [[ ! -f "bin/SistemaEtiquetas" ]]; then
    print_error "No se encontró bin/SistemaEtiquetas. Asegúrate de ejecutar desde el directorio de distribución."
    exit 1
fi

print_status "Verificando dependencias del sistema..."

# Instalar dependencias de Qt6
print_status "Instalando dependencias de Qt6..."
if dnf list installed qt6-qtbase-widgets >/dev/null 2>&1; then
    print_success "qt6-qtbase-widgets ya está instalado"
else
    if dnf list available qt6-qtbase-widgets >/dev/null 2>&1; then
        dnf install -y qt6-qtbase-widgets
        print_success "qt6-qtbase-widgets instalado"
    else
        print_warning "qt6-qtbase-widgets no disponible, instalando qt6-qtbase-gui"
        dnf install -y qt6-qtbase-gui
        print_success "qt6-qtbase-gui instalado"
    fi
fi

# Crear directorio de instalación
INSTALL_DIR="/opt/sistema-etiquetas"
print_status "Creando directorio de instalación: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/bin"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/assets"

# Copiar archivos
print_status "Copiando archivos de la aplicación..."
cp bin/SistemaEtiquetas "$INSTALL_DIR/bin/"
cp bin/ejecutar_sistema_etiquetas.sh "$INSTALL_DIR/bin/"
cp assets/icon.ico "$INSTALL_DIR/assets/" 2>/dev/null || print_warning "icon.ico no encontrado"
cp assets/styles.qss "$INSTALL_DIR/assets/" 2>/dev/null || print_warning "styles.qss no encontrado"

# Copiar archivos de configuración
print_status "Copiando archivos de configuración..."
cp config/odoo_config.py "$INSTALL_DIR/config/" 2>/dev/null || print_warning "odoo_config.py no encontrado"
cp config/printer_config.json "$INSTALL_DIR/config/" 2>/dev/null || print_warning "printer_config.json no encontrado"
cp config/mysql_config.json "$INSTALL_DIR/config/" 2>/dev/null || print_warning "mysql_config.json no encontrado"
cp config/config.json "$INSTALL_DIR/config/" 2>/dev/null || print_warning "config.json no encontrado"

# Establecer permisos
print_status "Estableciendo permisos..."
chmod +x "$INSTALL_DIR/bin/SistemaEtiquetas"
chmod +x "$INSTALL_DIR/bin/ejecutar_sistema_etiquetas.sh"
chown -R root:root "$INSTALL_DIR"

# Crear enlace simbólico global
print_status "Creando enlace simbólico global..."
ln -sf "$INSTALL_DIR/bin/SistemaEtiquetas" /usr/local/bin/sistema-etiquetas
ln -sf "$INSTALL_DIR/bin/ejecutar_sistema_etiquetas.sh" /usr/local/bin/sistema-etiquetas-config

# Crear archivo .desktop para el escritorio
print_status "Creando acceso directo en el escritorio..."
DESKTOP_FILE="/home/$SUDO_USER/Desktop/sistema-etiquetas.desktop"
mkdir -p "/home/$SUDO_USER/Desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sistema de Etiquetas
Comment=Sistema de impresión de etiquetas con configuración dinámica
Exec=sistema-etiquetas-config
Icon=$INSTALL_DIR/assets/icon.ico
Terminal=false
Categories=Office;Printing;
StartupNotify=true
EOF
