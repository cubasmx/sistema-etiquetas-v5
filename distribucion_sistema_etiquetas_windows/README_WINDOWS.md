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
