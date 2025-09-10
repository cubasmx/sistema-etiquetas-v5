#!/bin/bash

# Script de build para Windows usando Wine
# Genera distribución completa para Windows

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
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

echo "========================================"
echo "  Sistema de Etiquetas - Build Windows"
echo "========================================"

# Verificar que estamos en el directorio correcto
if [[ ! -f "../SistemaEtiquetas.py" ]]; then
    print_error "No se encontró SistemaEtiquetas.py. Asegúrate de estar en el directorio correcto del proyecto."
    exit 1
fi

# Verificar Wine
if ! command -v wine >/dev/null 2>&1; then
    print_error "Wine no está instalado. Instálalo con: sudo dnf install wine"
    exit 1
fi

print_info "Verificando dependencias del sistema..."

# Instalar dependencias de Wine si es necesario
if ! dnf list installed wine >/dev/null 2>&1; then
    print_info "Instalando Wine..."
    sudo dnf install -y wine
    print_success "Wine instalado"
fi

# Configurar entorno virtual
print_info "Configurando entorno virtual..."
if [[ ! -d "../venv" ]]; then
    print_info "Creando entorno virtual..."
    cd ..
    python3 -m venv venv
    cd scripts
fi

print_info "Activando entorno virtual..."
source ../venv/bin/activate
print_success "Entorno virtual activado: $(which python)"

# Instalar PyInstaller en Wine
print_info "Instalando PyInstaller en Wine..."
wine python -m pip install --upgrade pip
wine python -m pip install pyinstaller

# Instalar dependencias Python en Wine
print_info "Instalando dependencias Python en Wine..."
wine python -m pip install -r ../docs/requirements.txt

# Limpiar builds anteriores
print_info "Limpiando builds anteriores..."
rm -rf ../dist_windows
rm -rf ../build_windows

# Construir ejecutable con PyInstaller
print_info "Construyendo ejecutable para Windows..."
cd ../build
wine pyinstaller --clean sistema_etiquetas_windows.spec
cd ../scripts

print_success "✅ Build de Windows exitoso!"

# Crear distribución completa
print_info "Creando distribución completa para Windows..."
DIST_DIR="../distribucion_sistema_etiquetas_windows"

# Limpiar distribución anterior
if [[ -d "$DIST_DIR" ]]; then
    rm -rf "$DIST_DIR"
fi

mkdir -p "$DIST_DIR"
mkdir -p "$DIST_DIR/bin"
mkdir -p "$DIST_DIR/config"
mkdir -p "$DIST_DIR/assets"

# Copiar ejecutable
print_info "Copiando ejecutable..."
cp ../build/dist/SistemaEtiquetas.exe "$DIST_DIR/bin/"

# Copiar archivos de configuración
print_info "Copiando archivos de configuración..."
cp ../config/* "$DIST_DIR/config/" 2>/dev/null || true
cp ../assets/* "$DIST_DIR/assets/" 2>/dev/null || true

# Copiar iconos
print_info "Copiando iconos..."
cp ../src/assets/icon.ico "$DIST_DIR/assets/" 2>/dev/null || true
cp ../src/ui/icons/*.png "$DIST_DIR/assets/" 2>/dev/null || true
cp ../src/ui/icons/*.svg "$DIST_DIR/assets/" 2>/dev/null || true

# Crear script de instalación para Windows
print_info "Creando script de instalación..."
cat > "$DIST_DIR/INSTALAR.bat" << 'EOF'
@echo off
echo ========================================
echo   Sistema de Etiquetas - Windows
echo ========================================
echo.
echo Iniciando aplicacion...
echo.
echo Si aparece un mensaje de Windows Defender:
echo - Hacer clic en "Mas informacion"
echo - Hacer clic en "Ejecutar de todas formas"
echo.
pause
echo.
echo Ejecutando Sistema de Etiquetas...
start bin\SistemaEtiquetas.exe
echo.
echo Aplicacion iniciada. Puedes cerrar esta ventana.
pause
EOF

# Crear README para Windows
print_info "Creando documentación..."
cat > "$DIST_DIR/README_WINDOWS.md" << 'EOF'
# Sistema de Etiquetas - Windows

## Instalación

1. Ejecutar el instalador:
   ```cmd
   INSTALAR.bat
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
print_info "Creando archivo de versión..."
cat > "$DIST_DIR/VERSION.txt" << EOF
Sistema de Etiquetas - Windows
Versión: $(date +%Y%m%d)
Build: $(date)

Nuevas características:
- Configuración dinámica con pestañas
- Tolerancia a fallos de MySQL
- Verificación rápida de conectividad
- Campos editables para todas las configuraciones
- Mejor manejo de errores

Archivos incluidos:
- SistemaEtiquetas.exe (ejecutable principal)
- mysql_config.json (configuración MySQL)
- odoo_config.py (configuración Odoo)
- printer_config.json (configuración impresora)
- styles.qss (estilos de interfaz)
- iconos y assets
EOF

print_success "✅ Distribución Windows creada: $DIST_DIR"
print_info "Para instalar: cd $DIST_DIR && INSTALAR.bat"
