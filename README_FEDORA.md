# Sistema de Etiquetas - Fedora

Este documento contiene las instrucciones para compilar y ejecutar el Sistema de Etiquetas en Fedora.

## Requisitos Previos

- Fedora 35 o superior
- Python 3.8 o superior
- Acceso a internet para descargar dependencias

## Instalación y Compilación

### 1. Clonar o descargar el proyecto

```bash
git clone <url-del-repositorio>
cd sistema-etiquetas-v4
```

### 2. Ejecutar el script de build automático

```bash
./build_fedora.sh
```

Este script automáticamente:
- Instala las dependencias del sistema necesarias
- Instala las dependencias de Python
- Compila la aplicación en un solo archivo ejecutable

### 3. Ejecutar la aplicación

```bash
./dist/SistemaEtiquetas
```

## Instalación Manual (Alternativa)

Si prefieres instalar las dependencias manualmente:

### 1. Instalar dependencias del sistema

```bash
sudo dnf install -y python3-pip python3-devel gcc gcc-c++ make
sudo dnf install -y qt6-qtbase-devel qt6-qtbase-gui qt6-qtbase-widgets
```

### 2. Instalar dependencias de Python

```bash
pip3 install --user -r requirements.txt
pip3 install --user pyinstaller
```

### 3. Compilar la aplicación

```bash
pyinstaller --clean sistema_etiquetas_fedora.spec
```

## Configuración

### Configuración de Odoo

La aplicación requiere un archivo `odoo_config.py` con la configuración de conexión a Odoo:

```python
# -*- coding: utf-8 -*-

# Configuración de conexión a Odoo
ODOO_CONFIG = {
    "url": "https://tu-servidor-odoo.com",
    "db": "nombre_base_datos",
    "username": "usuario",
    "password": "contraseña",
    "port": 443
}
```

### Configuración de Impresora

La aplicación usa un archivo `printer_config.json` para la configuración de la impresora:

```json
{
    "printer_ip": "10.10.2.46",
    "printer_port": 6101
}
```

## Características del Ejecutable

- **Archivo único**: Toda la aplicación se empaqueta en un solo archivo ejecutable
- **Sin dependencias externas**: No requiere Python ni librerías adicionales en el sistema destino
- **Interfaz gráfica**: Aplicación de escritorio con PyQt6
- **Conexión a Odoo**: Integración con sistemas Odoo para búsqueda de productos
- **Impresión de etiquetas**: Generación y envío de etiquetas ZPL a impresoras de red
- **Base de datos**: Registro de impresiones en MySQL

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
Verificar que el archivo `src/assets/cacert.pem` esté presente en el proyecto.

### Error de conexión a MySQL
Verificar que el servidor MySQL esté accesible en la IP configurada (10.10.1.8 por defecto).

## Estructura del Proyecto

```
sistema-etiquetas-v4/
├── PythonApplication1.py      # Archivo principal de la aplicación
├── odoo_client.py            # Cliente para conexión con Odoo
├── src/utils/mysql_client.py # Cliente para conexión con MySQL
├── styles.qss                # Estilos de la interfaz
├── sistema_etiquetas_fedora.spec  # Configuración de PyInstaller
├── build_fedora.sh           # Script de build para Fedora
└── dist/SistemaEtiquetas     # Ejecutable final
```

## Soporte

Para reportar problemas o solicitar ayuda, contactar al equipo de desarrollo. 