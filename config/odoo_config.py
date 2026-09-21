# -*- coding: utf-8 -*-
# Configuración de conexión a Odoo.
# Los valores reales se toman de variables de entorno (.env); los de abajo son solo ejemplo.
import os

ODOO_CONFIG = {
    "url": os.getenv("ODOO_URL", "https://tu-empresa.odoo.com"),
    "db": os.getenv("ODOO_DB", "tu-base-de-datos"),
    "username": os.getenv("ODOO_USERNAME", "tu-usuario@email.com"),
    "password": os.getenv("ODOO_PASSWORD", ""),
    "port": int(os.getenv("ODOO_PORT", 443)),
}
