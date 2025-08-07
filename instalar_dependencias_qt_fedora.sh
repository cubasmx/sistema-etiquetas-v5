#!/bin/bash

echo "Instalando dependencias de Qt y PyQt6 para Fedora..."

sudo dnf install -y \
  libxcb \
  libxkbcommon-x11 \
  libX11-xcb \
  libXrender \
  libXext \
  libXi \
  libGL \
  qt6-qtbase-gui \
  qt6-qtbase \
  qt6-qtwayland \
  qt6-qtimageformats \
  qt6-qt5compat

echo "\n¡Dependencias instaladas!"

# Da permisos de ejecución al ejecutable y al icono si existen en Descargas
APP_EXEC="$HOME/Descargas/sistema-etiquetas"
ICON_JPG="$HOME/Descargas/icon.jpg"
ICON_PNG="$HOME/Descargas/icon.png"

if [ -f "$APP_EXEC" ]; then
  chmod +x "$APP_EXEC"
  echo "Permiso de ejecución otorgado a $APP_EXEC"
fi
if [ -f "$ICON_JPG" ]; then
  chmod +x "$ICON_JPG"
  echo "Permiso de ejecución otorgado a $ICON_JPG (opcional, solo si lo requiere el entorno)"
fi
if [ -f "$ICON_PNG" ]; then
  chmod +x "$ICON_PNG"
  echo "Permiso de ejecución otorgado a $ICON_PNG (opcional, solo si lo requiere el entorno)"
fi

echo "\n¡Listo! Ahora puedes ejecutar sistema-etiquetas desde Descargas." 