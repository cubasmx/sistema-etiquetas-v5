import xmlrpc.client
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

class OdooConnection:
    def __init__(self):
        self.client = None
        self.uid = None
        self.models = None
        self.config = None
        
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
        Establece la conexión con Odoo usando la configuración guardada
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Cargar configuración
            if not os.path.exists('config.json'):
                return False, "No existe archivo de configuración"
            
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            
            # Validar configuración
            required_fields = ['url', 'database', 'username', 'password']
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
                    self.config['database'],
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
                self.config['database'],
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
            product_ids = list(set(bom['product_tmpl_id'][0] for bom in bom_products))
            
            # Obtener detalles de los productos
            products = self.models.execute_kw(
                self.config['database'],
                self.uid,
                self.config['password'],
                'product.template',
                'read',
                [product_ids],
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
                self.config['database'],
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
            
            # Obtener información del producto
            product_info = self.models.execute_kw(
                self.config['database'],
                self.uid,
                self.config['password'],
                'product.template',
                'read',
                [bom['product_tmpl_id'][0]],
                {
                    'fields': [
                        'standard_price',  # Costo del producto
                        'route_ids'        # Rutas de fabricación
                    ]
                }
            )[0]
            
            # Obtener operaciones de fabricación
            operations = []
            if bom.get('routing_id'):
                # Obtener las operaciones de la ruta de fabricación
                routing = self.models.execute_kw(
                    self.config['database'],
                    self.uid,
                    self.config['password'],
                    'mrp.routing',
                    'read',
                    [bom['routing_id'][0]],
                    {
                        'fields': ['operation_ids']
                    }
                )[0]
                
                if routing.get('operation_ids'):
                    operations = self.models.execute_kw(
                        self.config['database'],
                        self.uid,
                        self.config['password'],
                        'mrp.routing.workcenter',
                        'read',
                        [routing['operation_ids']],
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
                            self.config['database'],
                            self.uid,
                            self.config['password'],
                            'mrp.workcenter',
                            'read',
                            [op['workcenter_id'][0]],
                            {
                                'fields': [
                                    'costs_hour',
                                    'time_efficiency'
                                ]
                            }
                        )[0]
                        
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
                    self.config['database'],
                    self.uid,
                    self.config['password'],
                    'stock.route',
                    'read',
                    [product_info['route_ids']],
                    {'fields': ['name']}
                )
            
            # Obtener líneas de la BOM con campos adicionales
            lines = self.models.execute_kw(
                self.config['database'],
                self.uid,
                self.config['password'],
                'mrp.bom.line',
                'read',
                [bom['bom_line_ids']],
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
                component_info = self.models.execute_kw(
                    self.config['database'],
                    self.uid,
                    self.config['password'],
                    'product.product',
                    'read',
                    [line['product_id'][0]],
                    {'fields': ['standard_price', 'product_tmpl_id']}
                )[0]
                
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
                'code': str(bom['code']) if bom['code'] else '',
                'uom': str(bom['product_uom_id'][1]) if bom['product_uom_id'] else '',
                'product_name': str(bom['product_tmpl_id'][1]),
                'lines': processed_lines,
                'level': level,
                'operations': operations,
                'routes': [route['name'] for route in routes],
                'total_material_cost': total_material_cost,
                'product_cost': float(product_info.get('standard_price', 0))
            }
            
        except Exception as e:
            raise ConnectionError(f"Error al obtener BOM: {str(e)}") 