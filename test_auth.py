# -*- coding: utf-8 -*-
import xmlrpc.client

# Configuración de prueba (usa las mismas de tu odoo_config.py)
url = "https://tuercasyabrazaderasensa.odoo.com"
db = "tuercasyabrazaderasensa"
username = "adgronesensa.com"  # prueba con algo que sepas que es incorrecto
password = "12345678"          # prueba con algo que sepas que es incorrecto

print(f"[DEBUG] Probando conexión a Odoo en {url} con usuario {username}")

# Crear proxy XML-RPC
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

try:
    uid = common.authenticate(db, username, password, {})
    print("[RESULT] authenticate() devolvió:", repr(uid), "type:", type(uid))

    if not uid:
        print("[INFO] Autenticación fallida, credenciales incorrectas.")
    else:
        print("[INFO] Autenticación exitosa. UID obtenido:", uid)
        # opcional: ver versión del servidor
        try:
            version_info = common.version()
            print("[INFO] Versión del servidor Odoo:", version_info)
        except Exception as e:
            print("[WARN] No se pudo obtener versión del servidor:", e)

except Exception as e:
    print("[ERROR] Excepción durante authenticate():", e)
