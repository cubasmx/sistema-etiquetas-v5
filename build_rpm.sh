#!/bin/bash

echo "=== Build RPM Package para Fedora ==="

# Verificar que el ejecutable existe
if [ ! -f "dist/SistemaEtiquetas" ]; then
    echo "❌ Error: No se encontró el ejecutable dist/SistemaEtiquetas"
    echo "Ejecute primero: ./build_fedora.sh"
    exit 1
fi

# Instalar herramientas de build de RPM
echo "Instalando herramientas de build de RPM..."
sudo dnf install -y rpm-build rpmdevtools

# Crear estructura de directorios para RPM
echo "Creando estructura de directorios..."
rpmdev-setuptree

# Crear archivo LICENSE si no existe
if [ ! -f "LICENSE" ]; then
    echo "Creando archivo LICENSE..."
    cat > LICENSE << EOF
MIT License

Copyright (c) 2024 Sistema de Etiquetas

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
fi

# Crear tarball del proyecto
echo "Creando tarball del proyecto..."
tar -czf ~/rpmbuild/SOURCES/sistema-etiquetas-4.0.tar.gz \
    --exclude='.git' \
    --exclude='build' \
    --exclude='dist' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    .

# Copiar spec file
cp sistema-etiquetas-rpm.spec ~/rpmbuild/SPECS/

# Construir RPM
echo "Construyendo RPM..."
rpmbuild -ba ~/rpmbuild/SPECS/sistema-etiquetas-rpm.spec

# Verificar que el RPM se creó
if [ -f "~/rpmbuild/RPMS/noarch/sistema-etiquetas-4.0-1.fc42.noarch.rpm" ]; then
    echo "✅ RPM construido exitosamente!"
    echo "RPM ubicado en: ~/rpmbuild/RPMS/noarch/"
    ls -la ~/rpmbuild/RPMS/noarch/sistema-etiquetas-*.rpm
else
    echo "❌ Error al construir RPM"
    exit 1
fi

echo ""
echo "Para instalar el RPM:"
echo "sudo dnf install ~/rpmbuild/RPMS/noarch/sistema-etiquetas-*.rpm" 