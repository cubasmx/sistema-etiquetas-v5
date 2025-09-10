# Sistema de Impresión de Etiquetas

Sistema para la impresión de etiquetas con códigos de barras, integrado con Odoo.

## Características

- Búsqueda de productos en Odoo
- Generación de etiquetas con códigos de barras
- Impresión en formato ZPL
- Configuración de conexión a Odoo
- Interfaz gráfica intuitiva

## Requisitos

- Python 3.11 o superior
- PyQt6
- Impresora compatible con ZPL
- Acceso a Odoo

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd sistema-etiquetas
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la conexión a Odoo:
   - Copiar `odoo_config.py.example` a `odoo_config.py`
   - Editar `odoo_config.py` con los datos de conexión

## Uso

1. Activar el entorno virtual:
```bash
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

2. Ejecutar la aplicación:
```bash
python PythonApplication1.py
```

## Compilación para Windows

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Compilar con PyInstaller:
```bash
pyinstaller sistema_etiquetas.spec
```

El ejecutable se creará en la carpeta `dist/`. 