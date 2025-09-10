# -*- coding: utf-8 -*-
import xmlrpc.client
import sys
import os
import ssl

# Importar configuración desde el directorio config
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
from odoo_config import ODOO_CONFIG

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Crear contexto SSL que no verifique certificados
def create_ssl_context():
    """Crear contexto SSL que no verifique certificados"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

# Forzar uso de certificados incluidos si se ejecuta directamente
if __name__ == "__main__":
    os.environ['SSL_CERT_FILE'] = resource_path('src/assets/cacert.pem')

class OdooClient:
    def __init__(self):
        self.url = ODOO_CONFIG['url']
        self.db = ODOO_CONFIG['db']
        self.username = ODOO_CONFIG['username']
        self.password = ODOO_CONFIG['password']
        
        # Crear contexto SSL sin verificación
        ssl_context = create_ssl_context()
        
        # Crear conexiones XML-RPC con contexto SSL personalizado
        transport = xmlrpc.client.SafeTransport(context=ssl_context)
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common', transport=transport)
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object', transport=transport)
        
        # Autenticar y obtener uid
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if not self.uid:
                print("⚠️ Advertencia: No se pudo autenticar con Odoo. La aplicación funcionará en modo offline.")
                self.uid = None
        except Exception as e:
            print(f"⚠️ Advertencia: Error de conexión a Odoo: {str(e)}")
            print("La aplicación funcionará en modo offline.")
            self.uid = None

    def search_products(self, query):
        """Buscar productos en Odoo"""
        if not self.uid:
            print("⚠️ Modo offline: No hay conexión a Odoo")
            return []
            
        try:
            # Buscar productos que coincidan con el criterio
            domain = [
                '|',  # OR para los siguientes criterios
                ('default_code', 'ilike', query),  # Código del producto
                ('name', 'ilike', query),          # Nombre del producto
            ]
            
            # Campos que queremos obtener
            fields = ['id', 'name', 'default_code', 'description']
            
            # Realizar la búsqueda
            products = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.template',  # Modelo a consultar
                'search_read',      # Método
                [domain],           # Dominio de búsqueda
                {'fields': fields}  # Campos a retornar
            )
            
            return products
        except Exception as e:
            print(f"Error al buscar productos: {str(e)}")
            return []

    def get_product(self, product_id):
        """Obtener un producto específico por ID"""
        if not self.uid:
            print("⚠️ Modo offline: No hay conexión a Odoo")
            return None
            
        try:
            fields = ['name', 'default_code', 'description']
            products = self.models.execute_kw(
                self.db, self.uid, self.password,
                'product.template',
                'read',
                [product_id],
                {'fields': fields}
            )
            return products[0] if products else None
        except Exception as e:
            print(f"Error al obtener producto: {str(e)}")
            return None 