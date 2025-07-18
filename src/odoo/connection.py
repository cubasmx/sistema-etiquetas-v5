import xmlrpc.client
from odoo_config import ODOO_CONFIG  # <-- Agregado
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

class OdooConnection:
    def __init__(self):
        self.client = None
        self.uid = None
        self.models = None
        self.config = ODOO_CONFIG  # <-- Usar ODOO_CONFIG directamente
        
    def _format_url(self, url: str) -> str:
        """
        Formatea la URL para asegurar que sea válida para XML-RPC
        Args:
            url: URL del servidor Odoo
        Returns:
            str: URL formateada
        """
        # Asegurar que la URL comienza con https://
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Remover la barra final si existe
        url = url.rstrip('/')
        
        # Validar la URL
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError("URL inválida")
            
        return url
        
    def connect(self) -> Tuple[bool, str]:
        """
        Establece la conexión con Odoo usando la configuración de odoo_config.py
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Usar configuración de odoo_config.py
            # Validar configuración
            required_fields = ['url', 'db', 'username', 'password']
            if not all(field in self.config for field in required_fields):
                return False, "Configuración incompleta"
            
            # Formatear URL
            try:
                base_url = self._format_url(self.config['url'])
            except ValueError as e:
                return False, f"URL inválida: {str(e)}"
            
            # Crear conexión
            common_url = f"{base_url}/xmlrpc/2/common"
            print(f"Conectando a: {common_url}")  # Debug
            common = xmlrpc.client.ServerProxy(common_url)
            
            # Autenticar
            try:
                self.uid = common.authenticate(
                    self.config['db'],  # <-- Cambiado de 'database' a 'db'
                    self.config['username'],
                    self.config['password'],
                    {}
                )
            except Exception as e:
                return False, f"Error de autenticación: {str(e)}"
            
            if not self.uid:
                return False, "Error de autenticación: credenciales inválidas"
            
            # Crear cliente
            self.models = xmlrpc.client.ServerProxy(f"{base_url}/xmlrpc/2/object")
            
            return True, "Conexión exitosa"
            
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def get_bom_products(self) -> List[Dict[str, Any]]:
        """
        Obtiene los productos que tienen lista de materiales
        Returns:
            List[Dict]: Lista de productos con sus IDs y nombres
        """
        if not self.models or not self.uid:
            raise ConnectionError("No hay conexión activa con Odoo")
        
        try:
            # Buscar productos con BOM
            bom_products = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'mrp.bom',
                'search_read',
                [[['active', '=', True]]],
                {
                    'fields': ['product_tmpl_id'],
                    'context': {'active_test': True}
                }
            )
            
            if not bom_products:
                return []
            
            # Obtener IDs únicos de productos
            product_ids = list(set(
                bom['product_tmpl_id'][0]
                for bom in bom_products
                if isinstance(bom.get('product_tmpl_id'), list) and len(bom.get('product_tmpl_id')) > 0
            ))
            
            # Obtener detalles de los productos
            products = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'product.template',
                'read',
                [product_ids] if product_ids else [[]],
                {'fields': ['id', 'name', 'default_code']}
            )
            
            return products
            
        except Exception as e:
            raise ConnectionError(f"Error al obtener productos: {str(e)}")
    
    def get_bom_data(self, product_id: int, level: int = 0) -> Dict[str, Any]:
        """
        Obtiene los datos de la lista de materiales para un producto, incluyendo sub-BOMs
        Args:
            product_id: ID del producto
            level: Nivel de profundidad actual (para BOMs anidadas)
        Returns:
            Dict: Datos de la BOM
        """
        if not self.models or not self.uid:
            raise ConnectionError("No hay conexión activa con Odoo")
        
        try:
            # Buscar BOM activa para el producto
            bom = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'mrp.bom',
                'search_read',
                [[
                    ['product_tmpl_id', '=', product_id],
                    ['active', '=', True]
                ]],
                {
                    'fields': [
                        'product_qty',
                        'code',
                        'product_uom_id',
                        'bom_line_ids',
                        'product_tmpl_id',
                        'routing_id'
                    ],
                    'limit': 1
                }
            )
            
            if not bom:
                raise ValueError(f"No se encontró BOM para el producto {product_id}")
            
            bom = bom[0]
            # Validar que product_tmpl_id sea lista
            product_tmpl_id = bom['product_tmpl_id'][0] if isinstance(bom.get('product_tmpl_id'), list) and len(bom.get('product_tmpl_id')) > 0 else None
            
            # Obtener información del producto
            product_info = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'product.template',
                'read',
                [product_tmpl_id] if product_tmpl_id is not None else [],
                {
                    'fields': [
                        'standard_price',  # Costo del producto
                        'route_ids'        # Rutas de fabricación
                    ]
                }
            )
            product_info = product_info[0] if product_info else {}
            
            # Obtener operaciones de fabricación
            operations = []
            if bom.get('routing_id'):
                # Obtener las operaciones de la ruta de fabricación
                routing = self.models.execute_kw(
                    self.config['db'],
                    self.uid,
                    self.config['password'],
                    'mrp.routing',
                    'read',
                    [bom['routing_id'][0]] if isinstance(bom['routing_id'], list) and len(bom['routing_id']) > 0 else [],
                    {
                        'fields': ['operation_ids']
                    }
                )
                routing = routing[0] if routing else {}
                
                if routing.get('operation_ids'):
                    operations = self.models.execute_kw(
                        self.config['db'],
                        self.uid,
                        self.config['password'],
                        'mrp.routing.workcenter',
                        'read',
                        [routing['operation_ids']] if isinstance(routing['operation_ids'], list) and len(routing['operation_ids']) > 0 else [],
                        {
                            'fields': [
                                'name',
                                'workcenter_id',
                                'time_cycle_manual',
                                'time_cycle',
                                'sequence',
                                'active'
                            ]
                        }
                    )
                
                # Obtener información adicional de los centros de trabajo
                for op in operations:
                    if op['workcenter_id']:
                        workcenter = self.models.execute_kw(
                            self.config['db'],
                            self.uid,
                            self.config['password'],
                            'mrp.workcenter',
                            'read',
                            [op['workcenter_id'][0]] if isinstance(op['workcenter_id'], list) and len(op['workcenter_id']) > 0 else [],
                            {
                                'fields': [
                                    'costs_hour',
                                    'time_efficiency'
                                ]
                            }
                        )
                        workcenter = workcenter[0] if workcenter else {}
                        
                        # Calcular costo de la operación
                        time_hours = float(op['time_cycle_manual'] or op['time_cycle'] or 0.0) / 60.0  # Convertir minutos a horas
                        op['operation_cost'] = time_hours * float(workcenter.get('costs_hour', 0.0))
                        op['efficiency'] = float(workcenter.get('time_efficiency', 1.0))
                
                # Ordenar operaciones por secuencia
                operations.sort(key=lambda x: x['sequence'])
            
            # Obtener rutas
            routes = []
            if product_info.get('route_ids'):
                routes = self.models.execute_kw(
                    self.config['db'],
                    self.uid,
                    self.config['password'],
                    'stock.route',
                    'read',
                    [product_info['route_ids']] if isinstance(product_info['route_ids'], list) and len(product_info['route_ids']) > 0 else [],
                    {'fields': ['name']}
                )
            
            # Obtener líneas de la BOM con campos adicionales
            lines = self.models.execute_kw(
                self.config['db'],
                self.uid,
                self.config['password'],
                'mrp.bom.line',
                'read',
                [bom['bom_line_ids']] if isinstance(bom['bom_line_ids'], list) and len(bom['bom_line_ids']) > 0 else [],
                {
                    'fields': [
                        'product_id',
                        'product_qty',
                        'product_uom_id',
                        'sequence',
                        'child_bom_id'
                    ]
                }
            )
            
            # Procesar las líneas para asegurar que son serializables
            processed_lines = []
            total_material_cost = 0.0
            
            for line in lines:
                # Obtener costo del componente
                product_id_val = line['product_id'][0] if isinstance(line['product_id'], list) and len(line['product_id']) > 0 else None
                component_info = self.models.execute_kw(
                    self.config['db'],
                    self.uid,
                    self.config['password'],
                    'product.product',
                    'read',
                    [product_id_val] if product_id_val is not None else [],
                    {'fields': ['standard_price', 'product_tmpl_id']}
                )
                component_info = component_info[0] if component_info else {}
                
                product_cost = float(component_info['standard_price'])
                material_cost = 0.0
                
                # Si la línea tiene una BOM hija, obtener su costo de materiales
                if line['child_bom_id']:
                    try:
                        child_product_tmpl_id = component_info['product_tmpl_id'][0]
                        sub_bom = self.get_bom_data(child_product_tmpl_id, level + 1)
                        material_cost = sub_bom.get('total_material_cost', 0.0)
                    except Exception as e:
                        print(f"Error al obtener sub-BOM: {str(e)}")
                
                # Calcular costos totales
                line_product_cost = product_cost * float(line['product_qty'])
                line_material_cost = material_cost * float(line['product_qty'])
                total_material_cost += line_material_cost if line_material_cost > 0 else line_product_cost
                
                processed_line = {
                    'product_id': line['product_id'],
                    'product_qty': float(line['product_qty']),
                    'product_uom_id': line['product_uom_id'],
                    'sequence': line['sequence'],
                    'level': level,
                    'product_cost': line_product_cost,
                    'material_cost': line_material_cost,
                    'sub_bom': None
                }
                
                # Si tiene sub-BOM, incluirla
                if line['child_bom_id']:
                    try:
                        child_product_tmpl_id = component_info['product_tmpl_id'][0]
                        sub_bom = self.get_bom_data(child_product_tmpl_id, level + 1)
                        processed_line['sub_bom'] = sub_bom
                    except Exception as e:
                        print(f"Error al obtener sub-BOM: {str(e)}")
                
                processed_lines.append(processed_line)
            
            # Ordenar las líneas por secuencia
            processed_lines.sort(key=lambda x: x['sequence'])
            
            # Estructurar respuesta asegurando tipos serializables
            return {
                'bom_id': int(bom['id']),
                'product_qty': float(bom['product_qty']),
                'code': str(bom['code']) if bom.get('code') else '',
                'uom': str(bom['product_uom_id'][1]) if isinstance(bom.get('product_uom_id'), list) and len(bom.get('product_uom_id')) > 1 else '',
                'product_name': str(bom['product_tmpl_id'][1]) if isinstance(bom.get('product_tmpl_id'), list) and len(bom.get('product_tmpl_id')) > 1 else '',
                'lines': processed_lines,
                'level': level,
                'operations': operations,
                'routes': [route['name'] for route in routes],
                'total_material_cost': total_material_cost,
                'product_cost': float(product_info.get('standard_price', 0))
            }
            
        except Exception as e:
            raise ConnectionError(f"Error al obtener BOM: {str(e)}") 