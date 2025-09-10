#!/bin/bash

# Desinstalador de Sistema de Etiquetas para Fedora
# Elimina completamente la instalación del sistema

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
echo "  Sistema de Etiquetas - Desinstalador Fedora"
echo "========================================"
echo ""

# Directorio de instalación
INSTALL_DIR="/opt/sistema-etiquetas"

print_status "Iniciando desinstalación del Sistema de Etiquetas..."

# Verificar si el sistema está instalado
if [[ ! -d "$INSTALL_DIR" ]]; then
    print_warning "El Sistema de Etiquetas no parece estar instalado en $INSTALL_DIR"
    print_status "Verificando otros componentes..."
else
    print_status "Sistema de Etiquetas encontrado en $INSTALL_DIR"
fi

# Eliminar enlaces simbólicos globales
print_status "Eliminando enlaces simbólicos globales..."
if [[ -L "/usr/local/bin/sistema-etiquetas" ]]; then
    rm -f "/usr/local/bin/sistema-etiquetas"
    print_success "Enlace simbólico /usr/local/bin/sistema-etiquetas eliminado"
else
    print_warning "Enlace simbólico /usr/local/bin/sistema-etiquetas no encontrado"
fi

if [[ -L "/usr/local/bin/sistema-etiquetas-config" ]]; then
    rm -f "/usr/local/bin/sistema-etiquetas-config"
    print_success "Enlace simbólico /usr/local/bin/sistema-etiquetas-config eliminado"
else
    print_warning "Enlace simbólico /usr/local/bin/sistema-etiquetas-config no encontrado"
fi

# Eliminar archivo .desktop del escritorio
print_status "Eliminando acceso directo del escritorio..."
if [[ -n "$SUDO_USER" ]]; then
    DESKTOP_FILE="/home/$SUDO_USER/Desktop/sistema-etiquetas.desktop"
    if [[ -f "$DESKTOP_FILE" ]]; then
        rm -f "$DESKTOP_FILE"
        print_success "Archivo .desktop eliminado: $DESKTOP_FILE"
    else
        print_warning "Archivo .desktop no encontrado: $DESKTOP_FILE"
    fi
else
    print_warning "No se pudo determinar el usuario para eliminar el archivo .desktop"
fi

# Buscar y eliminar archivos .desktop en otros directorios comunes
print_status "Buscando otros archivos .desktop..."
for desktop_dir in /usr/share/applications /usr/local/share/applications; do
    if [[ -d "$desktop_dir" ]]; then
        desktop_file="$desktop_dir/sistema-etiquetas.desktop"
        if [[ -f "$desktop_file" ]]; then
            rm -f "$desktop_file"
            print_success "Archivo .desktop eliminado: $desktop_file"
        fi
    fi
done

# Eliminar directorio de instalación
if [[ -d "$INSTALL_DIR" ]]; then
    print_status "Eliminando directorio de instalación: $INSTALL_DIR"
    rm -rf "$INSTALL_DIR"
    print_success "Directorio de instalación eliminado"
else
    print_warning "Directorio de instalación no encontrado: $INSTALL_DIR"
fi

# Buscar otros directorios posibles de instalación
print_status "Buscando otras instalaciones posibles..."
for possible_dir in "/usr/local/sistema-etiquetas" "/opt/sistema-etiquetas" "/home/*/sistema-etiquetas"; do
    if [[ -d $possible_dir ]]; then
        print_warning "Encontrado directorio adicional: $possible_dir"
        read -p "¿Deseas eliminar este directorio también? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$possible_dir"
            print_success "Directorio eliminado: $possible_dir"
        fi
    fi
done

# Verificar procesos en ejecución
print_status "Verificando procesos en ejecución..."
if pgrep -f "SistemaEtiquetas" > /dev/null; then
    print_warning "Se encontraron procesos del Sistema de Etiquetas en ejecución"
    print_status "Procesos encontrados:"
    pgrep -f "SistemaEtiquetas" | while read pid; do
        ps -p $pid -o pid,cmd --no-headers
    done
    echo ""
    read -p "¿Deseas terminar estos procesos? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "SistemaEtiquetas"
        print_success "Procesos terminados"
    else
        print_warning "Los procesos siguen ejecutándose. Puedes terminarlos manualmente con: pkill -f SistemaEtiquetas"
    fi
else
    print_success "No se encontraron procesos del Sistema de Etiquetas en ejecución"
fi

# Limpiar caché de aplicaciones (opcional)
print_status "Limpiando caché de aplicaciones..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications 2>/dev/null || true
    print_success "Caché de aplicaciones actualizado"
fi

# Verificar desinstalación completa
print_status "Verificando desinstalación..."
remaining_files=0

if [[ -d "$INSTALL_DIR" ]]; then
    print_error "El directorio de instalación aún existe: $INSTALL_DIR"
    remaining_files=$((remaining_files + 1))
fi

if [[ -L "/usr/local/bin/sistema-etiquetas" ]] || [[ -L "/usr/local/bin/sistema-etiquetas-config" ]]; then
    print_error "Aún existen enlaces simbólicos"
    remaining_files=$((remaining_files + 1))
fi

if [[ -f "/home/$SUDO_USER/Desktop/sistema-etiquetas.desktop" ]]; then
    print_error "El archivo .desktop aún existe"
    remaining_files=$((remaining_files + 1))
fi

if [[ $remaining_files -eq 0 ]]; then
    print_success "¡Desinstalación completada exitosamente!"
    echo ""
    print_status "El Sistema de Etiquetas ha sido completamente eliminado de tu sistema."
    print_status "Ahora puedes instalar la nueva distribución sin problemas."
else
    print_warning "La desinstalación se completó con algunas advertencias."
    print_warning "Revisa los mensajes anteriores para más detalles."
fi

echo ""
echo "========================================"
echo "  Desinstalación completada"
echo "========================================"
