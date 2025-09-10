#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
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

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Función para manejar errores
handle_error() {
    print_error "Error en la línea $1"
    exit 1
}

# Configurar trap para manejar errores
trap 'handle_error $LINENO' ERR

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Sistema de Etiquetas - Build Fedora  ${NC}"
echo -e "${GREEN}========================================${NC}"

# Verificar si estamos en Fedora
if ! grep -q "fedora" /etc/os-release; then
    print_warning "Este script está diseñado para Fedora, pero puede funcionar en otras distribuciones basadas en RPM"
fi

# Verificar si estamos ejecutando como root
if [[ $EUID -eq 0 ]]; then
    print_error "No ejecutes este script como root. Usa tu usuario normal."
    exit 1
fi

# Verificar si estamos en el directorio correcto
if [[ ! -f "../SistemaEtiquetas.py" ]]; then
    print_error "No se encontró SistemaEtiquetas.py. Asegúrate de estar en el directorio correcto del proyecto."
    exit 1
fi

print_status "Verificando dependencias del sistema..."

# Verificar e instalar Python3
if ! command_exists python3; then
    print_status "Instalando Python3..."
    sudo dnf install -y python3
else
    print_success "Python3 ya está instalado: $(python3 --version)"
fi

# Verificar e instalar pip3
if ! command_exists pip3; then
    print_status "Instalando pip3..."
    sudo dnf install -y python3-pip
else
    print_success "pip3 ya está instalado: $(pip3 --version)"
fi

# Instalar dependencias del sistema necesarias
print_status "Instalando dependencias del sistema..."
sudo dnf install -y python3-devel gcc gcc-c++ make

# Instalar dependencias de Qt6
print_status "Instalando dependencias de Qt6..."
sudo dnf install -y qt6-qtbase-devel qt6-qtbase-gui

# Crear y activar entorno virtual
print_status "Configurando entorno virtual..."
if [[ ! -d "venv" ]]; then
    print_status "Creando entorno virtual..."
    python3 -m venv venv
fi

print_status "Activando entorno virtual..."
source venv/bin/activate

# Verificar que el entorno virtual esté activado
if [[ -z "$VIRTUAL_ENV" ]]; then
    print_error "No se pudo activar el entorno virtual"
    exit 1
fi

print_success "Entorno virtual activado: $VIRTUAL_ENV"

# Actualizar pip en el entorno virtual
print_status "Actualizando pip..."
pip install --upgrade pip

# Instalar PyInstaller
print_status "Instalando PyInstaller..."
pip install pyinstaller

# Verificar que PyInstaller se instaló correctamente
if ! command_exists pyinstaller; then
    print_error "PyInstaller no se pudo instalar correctamente"
    exit 1
fi

print_success "PyInstaller instalado: $(pyinstaller --version)"

# Instalar dependencias de Python
if [[ -f "requirements.txt" ]]; then
    print_status "Instalando dependencias de Python..."
    pip install -r requirements.txt
else
    print_warning "No se encontró requirements.txt, instalando dependencias básicas..."
    pip install PyQt6 mysql-connector-python odoorpc
fi

# Crear directorio de build si no existe
mkdir -p dist

# Limpiar builds anteriores
print_status "Limpiando builds anteriores..."
rm -rf build dist/SistemaEtiquetas

# Verificar que el archivo .spec existe
if [[ ! -f "../build/sistema_etiquetas_fedora.spec" ]]; then
    print_error "No se encontró ../build/sistema_etiquetas_fedora.spec"
    exit 1
fi

# Construir el ejecutable
print_status "Construyendo ejecutable con PyInstaller..."
cd ../build
pyinstaller --clean sistema_etiquetas_fedora.spec
cd ../scripts

# Verificar que el ejecutable se creó
if [[ -f "../build/dist/SistemaEtiquetas" ]]; then
    print_success "✅ Build exitoso!"
    echo ""
    echo -e "${GREEN}Información del ejecutable:${NC}"
    echo "Ubicación: $(pwd)/../build/dist/SistemaEtiquetas"
    echo "Tamaño: $(du -h ../build/dist/SistemaEtiquetas | cut -f1)"
    echo "Permisos: $(ls -la ../build/dist/SistemaEtiquetas | awk '{print $1}')"
    
    # Hacer el ejecutable ejecutable
    chmod +x ../build/dist/SistemaEtiquetas
    
    echo ""
    echo -e "${GREEN}Para ejecutar la aplicación:${NC}"
    echo "cd ../build/dist && ./SistemaEtiquetas"
    echo ""
    echo -e "${GREEN}O desde cualquier ubicación:${NC}"
    echo "$(pwd)/../build/dist/SistemaEtiquetas"
    
    # Crear un script de ejecución simple
    cat > ../build/dist/ejecutar_sistema_etiquetas.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./SistemaEtiquetas
EOF
    chmod +x ../build/dist/ejecutar_sistema_etiquetas.sh
    
    print_success "Script de ejecución creado: ../build/dist/ejecutar_sistema_etiquetas.sh"
    
else
    print_error "❌ Error en el build - No se generó el ejecutable"
    print_status "Revisando logs de PyInstaller..."
    if [[ -f "build/SistemaEtiquetas/warn-SistemaEtiquetas.txt" ]]; then
        echo "=== WARNINGS ==="
        cat build/SistemaEtiquetas/warn-SistemaEtiquetas.txt
    fi
    exit 1
fi

print_success "🎉 Proceso de build completado exitosamente!"
print_status "Tu aplicación está lista para usar en: ../build/dist/SistemaEtiquetas"

# Crear distribución completa
print_status "Creando distribución completa para Fedora..."
DIST_DIR="../distribucion_sistema_etiquetas_fedora"

# Limpiar distribución anterior
if [[ -d "$DIST_DIR" ]]; then
    rm -rf "$DIST_DIR"
fi

mkdir -p "$DIST_DIR"
mkdir -p "$DIST_DIR/bin"
mkdir -p "$DIST_DIR/config"
mkdir -p "$DIST_DIR/assets"
mkdir -p "$DIST_DIR/installers"

# Copiar ejecutable
print_status "Copiando ejecutable..."
cp ../build/dist/SistemaEtiquetas "$DIST_DIR/bin/"

# Copiar archivos de configuración
print_status "Copiando archivos de configuración..."
cp ../config/* "$DIST_DIR/config/" 2>/dev/null || true
cp ../assets/* "$DIST_DIR/assets/" 2>/dev/null || true

# Copiar iconos
print_status "Copiando iconos..."
cp ../src/assets/icon.ico "$DIST_DIR/assets/" 2>/dev/null || true
cp ../src/ui/icons/*.png "$DIST_DIR/assets/" 2>/dev/null || true
cp ../src/ui/icons/*.svg "$DIST_DIR/assets/" 2>/dev/null || true

# Crear script wrapper
print_status "Creando script wrapper..."
cat > "$DIST_DIR/bin/ejecutar_sistema_etiquetas.sh" << 'EOF'
#!/bin/bash
# Script wrapper para ejecutar Sistema de Etiquetas con la configuración correcta
# Cambiar al directorio donde están los archivos de configuración
cd ~/.local/bin
# Ejecutar la aplicación
./SistemaEtiquetas
EOF
chmod +x "$DIST_DIR/bin/ejecutar_sistema_etiquetas.sh"

# Crear instalador
print_status "Creando instalador..."
cat > "$DIST_DIR/installers/instalar_fedora.sh" << 'EOF'
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
DESKTOP_FILE="$HOME/Desktop/sistema-etiquetas.desktop"
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

chmod +x "$DESKTOP_FILE"
chown "$SUDO_USER:$SUDO_USER" "$DESKTOP_FILE"

# Crear archivo .desktop global para el menú de aplicaciones
print_status "Creando entrada en el menú de aplicaciones..."
GLOBAL_DESKTOP_FILE="/usr/share/applications/sistema-etiquetas.desktop"
cat > "$GLOBAL_DESKTOP_FILE" << EOF
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

# Actualizar base de datos de aplicaciones
print_status "Actualizando base de datos de aplicaciones..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Habilitar iconos en el escritorio (GNOME)
print_status "Configurando escritorio GNOME..."
if command -v gsettings >/dev/null 2>&1; then
    sudo -u "$SUDO_USER" gsettings set org.gnome.desktop.background show-desktop-icons true 2>/dev/null || true
fi

# Crear directorio de configuración del usuario
print_status "Configurando directorio de configuración del usuario..."
USER_CONFIG_DIR="$HOME/.local/bin"
mkdir -p "$USER_CONFIG_DIR"

# Copiar archivos de configuración al directorio del usuario
print_status "Copiando configuración al directorio del usuario..."
cp "$INSTALL_DIR/bin/SistemaEtiquetas" "$USER_CONFIG_DIR/"
cp "$INSTALL_DIR/bin/ejecutar_sistema_etiquetas.sh" "$USER_CONFIG_DIR/"
cp "$INSTALL_DIR/config/"*.py "$USER_CONFIG_DIR/" 2>/dev/null || true
cp "$INSTALL_DIR/config/"*.json "$USER_CONFIG_DIR/" 2>/dev/null || true
cp "$INSTALL_DIR/assets/"* "$USER_CONFIG_DIR/" 2>/dev/null || true

# Establecer permisos del usuario
chown -R "$SUDO_USER:$SUDO_USER" "$USER_CONFIG_DIR"
chmod +x "$USER_CONFIG_DIR/SistemaEtiquetas"
chmod +x "$USER_CONFIG_DIR/ejecutar_sistema_etiquetas.sh"

echo ""
echo "========================================"
echo "  ✅ Instalación Completada"
echo "========================================"
echo ""
print_success "Sistema de Etiquetas instalado correctamente"
echo ""
echo "Ubicación de instalación: $INSTALL_DIR"
echo "Configuración del usuario: $USER_CONFIG_DIR"
echo ""
echo "Formas de ejecutar la aplicación:"
echo "1. Desde el escritorio: Icono 'Sistema de Etiquetas'"
echo "2. Desde el menú de aplicaciones: Buscar 'Sistema de Etiquetas'"
echo "3. Desde terminal: sistema-etiquetas-config"
echo "4. Desde terminal: sistema-etiquetas"
echo ""
echo "Nuevas características incluidas:"
echo "✅ Configuración dinámica con pestañas"
echo "✅ Tolerancia a fallos de MySQL"
echo "✅ Verificación rápida de conectividad"
echo "✅ Campos editables para todas las configuraciones"
echo "✅ Mejor espaciado en la interfaz"
echo ""
echo "Para configurar la aplicación:"
echo "1. Ejecutar la aplicación"
echo "2. Hacer clic en '⚙️ Configuración'"
echo "3. Cambiar entre pestañas 'Configuración Odoo' y 'Base de Datos Historial'"
echo "4. Modificar los valores según tu configuración"
echo "5. Hacer clic en 'Guardar Configuración'"
echo "6. Reiniciar la aplicación para aplicar cambios"
echo ""
print_success "🎉 ¡Instalación completada exitosamente!"
EOF
chmod +x "$DIST_DIR/installers/instalar_fedora.sh"

# Crear README
print_status "Creando documentación..."
cat > "$DIST_DIR/README_INSTALACION.md" << 'EOF'
# Sistema de Etiquetas - Fedora

## Instalación

1. Ejecutar el instalador:
   ```bash
   ./installers/instalar_fedora.sh
   ```

## Nuevas Características

### Configuración Dinámica
- **Pestañas separadas**: Configuración Odoo y Base de Datos Historial
- **Campos editables**: Todos los parámetros de conexión son configurables
- **Guardado automático**: Configuración se guarda en archivos separados

### Tolerancia a Fallos MySQL
- **Verificación rápida**: Detección de servidor en 0.3 segundos
- **Sin bloqueos**: Aplicación continúa funcionando si MySQL falla
- **Mensajes informativos**: Warnings en lugar de errores críticos

### Archivos de Configuración
- `config/odoo_config.py`: Configuración de conexión Odoo
- `config/mysql_config.json`: Configuración de base de datos del historial
- `config/printer_config.json`: Configuración de impresora
- `config/config.json`: Configuración general (legacy)

## Uso

1. **Configurar conexiones**: Usar el botón "⚙️ Configuración"
2. **Cambiar entre pestañas**: "Configuración Odoo" y "Base de Datos Historial"
3. **Guardar cambios**: Hacer clic en "Guardar Configuración"
4. **Reiniciar aplicación**: Para aplicar cambios de configuración

## Solución de Problemas

- Si MySQL no está disponible, la aplicación funcionará sin guardar historial
- Los mensajes de advertencia son normales y no afectan la funcionalidad
- Reinicia la aplicación después de cambiar la configuración
EOF

# Crear archivo de información de versión
print_status "Creando archivo de versión..."
cat > "$DIST_DIR/VERSION.txt" << EOF
Sistema de Etiquetas - Fedora
Versión: $(date +%Y%m%d)
Build: $(date)

Nuevas características:
- Configuración dinámica con pestañas
- Tolerancia a fallos de MySQL
- Verificación rápida de conectividad
- Campos editables para todas las configuraciones
- Mejor manejo de errores

Archivos incluidos:
- SistemaEtiquetas (ejecutable principal)
- mysql_config.json (configuración MySQL)
- odoo_config.py (configuración Odoo)
- printer_config.json (configuración impresora)
- styles.qss (estilos de interfaz)
- iconos y assets
EOF

print_success "✅ Distribución Fedora creada: $DIST_DIR"
print_status "Para instalar: cd $DIST_DIR && ./installers/instalar_fedora.sh" 