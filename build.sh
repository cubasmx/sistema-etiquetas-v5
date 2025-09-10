#!/bin/bash

# Script principal de build para Sistema de Etiquetas
# Genera distribuciones completas para diferentes plataformas

echo "========================================"
echo "  Sistema de Etiquetas - Build Principal"
echo "========================================"

# Verificar que estamos en el directorio correcto
if [[ ! -f "SistemaEtiquetas.py" ]]; then
    echo "[ERROR] No se encontró SistemaEtiquetas.py. Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Mostrar opciones
echo ""
echo "Selecciona la plataforma para compilar:"
echo "1) Fedora/Linux"
echo "2) Windows"
echo "3) Ambas"
echo ""
read -p "Ingresa tu opción (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🔧 Compilando para Fedora/Linux..."
        cd scripts
        ./build_fedora.sh
        ;;
    2)
        echo ""
        echo "🔧 Compilando para Windows..."
        cd scripts
        ./build_windows.sh
        ;;
    3)
        echo ""
        echo "🔧 Compilando para ambas plataformas..."
        cd scripts
        echo "--- Compilando Fedora ---"
        ./build_fedora.sh
        echo ""
        echo "--- Compilando Windows ---"
        ./build_windows.sh
        ;;
    *)
        echo "[ERROR] Opción inválida. Selecciona 1, 2 o 3."
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "  ✅ Build Completado"
echo "========================================"
echo ""
echo "Distribuciones generadas:"
if [[ -d "distribucion_sistema_etiquetas_fedora" ]]; then
    echo "📦 Fedora: distribucion_sistema_etiquetas_fedora/"
fi
if [[ -d "distribucion_sistema_etiquetas_windows" ]]; then
    echo "📦 Windows: distribucion_sistema_etiquetas_windows/"
fi
echo ""
echo "Para instalar:"
echo "• Fedora: cd distribucion_sistema_etiquetas_fedora && ./installers/instalar_fedora.sh"
echo "• Windows: cd distribucion_sistema_etiquetas_windows && INSTALAR.bat"
