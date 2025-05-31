# -*- coding: utf-8 -*-
import xmlrpc.client
from odoo_config import ODOO_CONFIG

class OdooClient:
    def __init__(self):
        self.url = ODOO_CONFIG['url']
        self.db = ODOO_CONFIG['db']
        self.username = ODOO_CONFIG['username']
        self.password = ODOO_CONFIG['password']
        
        # Crear conexiones XML-RPC
        self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        
        # Autenticar y obtener uid
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})

    def search_products(self, query):
        """Buscar productos en Odoo"""
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