# Distribución del Sistema de Etiquetas para Fedora

Este documento describe las diferentes opciones para distribuir el Sistema de Etiquetas en Fedora.

## Opciones de Distribución

### 1. Ejecutable Único (Recomendado)

**Ventajas:**
- Fácil de distribuir (un solo archivo)
- No requiere dependencias externas
- Funciona en cualquier sistema Fedora compatible

**Archivos generados:**
- `dist/SistemaEtiquetas` - Ejecutable único (~65MB)

**Uso:**
```bash
# Construir
./build_fedora.sh

# Ejecutar directamente
./dist/SistemaEtiquetas

# O instalar en el sistema
./install_fedora.sh
```

### 2. Paquete RPM

**Ventajas:**
- Instalación profesional
- Gestión de dependencias automática
- Integración completa con el sistema

**Archivos generados:**
- `~/rpmbuild/RPMS/noarch/sistema-etiquetas-*.rpm`

**Uso:**
```bash
# Construir RPM
./build_rpm.sh

# Instalar RPM
sudo dnf install ~/rpmbuild/RPMS/noarch/sistema-etiquetas-*.rpm
```

### 3. Instalación Manual

**Para usuarios avanzados que prefieren control total:**

```bash
# 1. Instalar dependencias
sudo dnf install -y python3-pip python3-devel gcc gcc-c++ make
sudo dnf install -y qt6-qtbase-devel qt6-qtbase-gui qt6-qtbase-widgets

# 2. Instalar dependencias de Python
pip3 install --user -r requirements.txt
pip3 install --user pyinstaller

# 3. Construir ejecutable
pyinstaller --clean sistema_etiquetas_fedora.spec

# 4. Ejecutar
./dist/SistemaEtiquetas
```

## Estructura de Archivos

```
sistema-etiquetas-v4/
├── PythonApplication1.py              # Aplicación principal
├── odoo_client.py                     # Cliente Odoo
├── src/utils/mysql_client.py          # Cliente MySQL
├── styles.qss                         # Estilos de interfaz
├── src/assets/
│   ├── icon.ico                       # Icono de la aplicación
│   └── cacert.pem                     # Certificados SSL
├── sistema_etiquetas_fedora.spec      # Configuración PyInstaller
├── build_fedora.sh                    # Script de build
├── install_fedora.sh                  # Script de instalación
├── sistema-etiquetas-rpm.spec         # Especificación RPM
├── build_rpm.sh                       # Script de build RPM
├── README_FEDORA.md                   # Documentación
└── DISTRIBUCION_FEDORA.md             # Esta guía
```

## Configuración Requerida

### Configuración de Odoo
Crear archivo `odoo_config.py`:
```python
# -*- coding: utf-8 -*-
ODOO_CONFIG = {
    "url": "https://tu-servidor-odoo.com",
    "db": "nombre_base_datos",
    "username": "usuario",
    "password": "contraseña",
    "port": 443
}
```

### Configuración de Impresora
Crear archivo `printer_config.json`:
```json
{
    "printer_ip": "10.10.2.46",
    "printer_port": 6101
}
```

## Características del Ejecutable

- **Tamaño:** ~65MB (incluye todas las dependencias)
- **Dependencias incluidas:**
  - Python 3.13 runtime
  - PyQt6 (interfaz gráfica)
  - PyMySQL (conexión MySQL)
  - xmlrpc.client (conexión Odoo)
  - Todas las librerías necesarias

- **Funcionalidades:**
  - Búsqueda de productos en Odoo
  - Generación de etiquetas ZPL
  - Impresión directa a impresoras de red
  - Registro en base de datos MySQL
  - Interfaz gráfica moderna
  - Configuración integrada

## Solución de Problemas

### Error de permisos
```bash
chmod +x dist/SistemaEtiquetas
```

### Error de dependencias de Qt
```bash
sudo dnf install -y qt6-qtbase-devel qt6-qtbase-gui qt6-qtbase-widgets
```

### Error de certificados SSL
Verificar que `src/assets/cacert.pem` esté presente.

### Error de conexión a MySQL
Verificar que el servidor MySQL esté accesible en la IP configurada.

### Error de conexión a Odoo
Verificar la configuración en `odoo_config.py`.

## Distribución a Usuarios Finales

### Opción 1: Archivo único
1. Ejecutar `./build_fedora.sh`
2. Distribuir `dist/SistemaEtiquetas`
3. El usuario ejecuta directamente

### Opción 2: Instalador
1. Ejecutar `./build_fedora.sh`
2. Ejecutar `./install_fedora.sh`
3. Distribuir el ejecutable instalado

### Opción 3: Paquete RPM
1. Ejecutar `./build_rpm.sh`
2. Distribuir el archivo `.rpm`
3. El usuario instala con `sudo dnf install`

## Requisitos del Sistema

- **Sistema operativo:** Fedora 35 o superior
- **Arquitectura:** x86_64
- **Memoria:** Mínimo 512MB RAM
- **Espacio en disco:** ~100MB para instalación
- **Red:** Acceso a servidor Odoo y MySQL

## Notas de Seguridad

- El ejecutable incluye todas las dependencias, no requiere permisos especiales
- Las configuraciones de conexión se almacenan en archivos locales
- Se recomienda configurar firewalls apropiados para las conexiones de red
- Los certificados SSL están incluidos para conexiones seguras

## Soporte

Para reportar problemas o solicitar ayuda:
1. Verificar la configuración de red y servidores
2. Revisar los logs de la aplicación
3. Contactar al equipo de desarrollo con detalles del error 