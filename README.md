# Sistema de Etiquetas

Sistema de impresión de etiquetas con configuración dinámica y tolerancia a fallos de MySQL.

## Estructura del Proyecto

```
sistema-etiquetas-v5/
├── SistemaEtiquetas.py          # Aplicación principal
├── main.py                      # Punto de entrada alternativo
├── odoo_client.py              # Cliente Odoo (legacy)
├── build.sh                    # Script principal de build
├── .gitignore                  # Archivos ignorados por Git
│
├── assets/                     # Recursos de la aplicación
│   └── styles.qss             # Estilos de la interfaz
│
├── build/                      # Archivos de configuración PyInstaller
│   ├── sistema_etiquetas_fedora.spec
│   └── PythonApplication1.spec
│
├── config/                     # Archivos de configuración
│   ├── config.json            # Configuración general (legacy)
│   ├── mysql_config.json      # Configuración MySQL
│   ├── odoo_config.py         # Configuración Odoo
│   └── printer_config.json    # Configuración impresora
│
├── dist/                      # Ejecutables compilados (generado)
│
├── docs/                      # Documentación
│   ├── README.md             # Este archivo
│   └── requirements.txt      # Dependencias Python
│
├── scripts/                   # Scripts de utilidad
│   └── build_fedora.sh       # Script de compilación Fedora
│
└── src/                       # Código fuente modular
    ├── assets/               # Iconos y recursos
    ├── export/               # Exportadores (Excel, etc.)
    ├── odoo/                 # Módulos de conexión Odoo
    ├── ui/                   # Interfaz de usuario
    └── utils/                # Utilidades (MySQL, config, etc.)
```

## Características

### ✅ Configuración Dinámica
- **Pestañas separadas**: Configuración Odoo y Base de Datos Historial
- **Campos editables**: Todos los parámetros son configurables
- **Guardado automático**: Configuración se guarda en archivos separados

### ✅ Tolerancia a Fallos MySQL
- **Verificación rápida**: Detección de servidor en 0.3 segundos
- **Sin bloqueos**: Aplicación continúa funcionando si MySQL falla
- **Mensajes informativos**: Warnings en lugar de errores críticos

### ✅ Interfaz Mejorada
- **Mejor espaciado**: Elementos organizados visualmente
- **Grupos de configuración**: Campos agrupados por funcionalidad
- **Información contextual**: Ayuda integrada en la interfaz

## Instalación y Uso

### Compilar la aplicación
```bash
./build.sh
```

### Ejecutar desde código fuente
```bash
python3 SistemaEtiquetas.py
```

### Configurar la aplicación
1. Ejecutar la aplicación
2. Hacer clic en "⚙️ Configuración"
3. Cambiar entre pestañas "Configuración Odoo" y "Base de Datos Historial"
4. Modificar los valores según tu configuración
5. Hacer clic en "Guardar Configuración"
6. Reiniciar la aplicación para aplicar cambios

## Archivos de Configuración

- **`config/mysql_config.json`**: Configuración de base de datos del historial
- **`config/odoo_config.py`**: Configuración de conexión Odoo
- **`config/printer_config.json`**: Configuración de impresora
- **`config/config.json`**: Configuración general (legacy)

## Dependencias

Ver `docs/requirements.txt` para la lista completa de dependencias Python.

## Desarrollo

El proyecto está organizado en módulos:
- **`src/ui/`**: Interfaz de usuario (diálogos, ventanas)
- **`src/utils/`**: Utilidades (MySQL, configuración)
- **`src/odoo/`**: Conexión y cliente Odoo
- **`src/export/`**: Exportadores de datos

## Solución de Problemas

- Si MySQL no está disponible, la aplicación funcionará sin guardar historial
- Los mensajes de advertencia son normales y no afectan la funcionalidad
- Reinicia la aplicación después de cambiar la configuración
