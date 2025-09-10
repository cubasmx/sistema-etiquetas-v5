import pymysql
import socket
import json
import os


class MysqlClient:
    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        # Cargar configuración desde archivo si no se proporcionan parámetros
        if host is None:
            config = self._load_config()
            self.host = config.get('host', '10.10.1.8')
            self.user = config.get('user', 'master')
            self.password = config.get('password', 'Ensa2025.')
            self.database = config.get('database', 'etiquetas')
            self.port = config.get('port', 3306)
        else:
            self.host = host
            self.user = user
            self.password = password
            self.database = database
            self.port = port
        self.connection = None

    def _load_config(self):
        """Carga la configuración de MySQL desde mysql_config.json"""
        try:
            if os.path.exists('mysql_config.json'):
                with open('mysql_config.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f'[WARNING] Error al cargar configuración MySQL: {e}')
        
        # Valores por defecto si no existe el archivo
        return {
            'host': '10.10.1.8',
            'user': 'master',
            'password': 'Ensa2025.',
            'database': 'etiquetas',
            'port': 3306
        }

    def _is_server_reachable(self):
        """Verificación rápida de conectividad al servidor MySQL"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)  # Timeout aún más corto para verificación súper rápida
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except:
            return False

    def connect(self):
        # Verificación rápida de conectividad primero
        if not self._is_server_reachable():
            print(f'[WARNING] Servidor MySQL no alcanzable: {self.host}:{self.port}')
            self.connection = None
            return False
            
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=1,  # Timeout de 1 segundo (más rápido)
                read_timeout=1,
                write_timeout=1
            )
            print('Conexión a MySQL exitosa')
            return True
        except Exception as e:
            print(f'[WARNING] No se pudo conectar a MySQL: {e}')
            print(f'[INFO] Servidor: {self.host}:{self.port}, Base de datos: {self.database}')
            self.connection = None
            return False

    def select_impresiones(self, ID=None, order_desc=True):
        if self.connection is None:
            print('[LOG] Conexión no activa, reconectando para SELECT...')
            self.connect()

        order = 'DESC' if order_desc else 'ASC'
        try:
            cursor = self.connection.cursor()
            if ID:
                query = f"""
                SELECT ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion
                FROM Impresiones
                WHERE ID = %s ORDER BY fecha_operacion {order}
                """
                print(f'[LOG] Ejecutando SELECT con filtro ID: {ID}')
                cursor.execute(query, (ID,))
            else:
                query = f"""
                SELECT ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion
                FROM Impresiones
                ORDER BY fecha_operacion {order}
                """
                print(f'[LOG] Ejecutando SELECT de todas las impresiones ordenadas por {order}')
                cursor.execute(query)
            results = cursor.fetchall()
            print(f'[LOG] Resultados obtenidos: {results}')
            cursor.close()
            return results
        except Exception as e:
            print(f'[ERROR] Error al ejecutar SELECT en Impresiones: {e}')
            return None

    def insert_impresion(self, ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion=None):
        if self.connection is None:
            print('[LOG] Conexión no activa, intentando reconectar para INSERT...')
            if not self.connect():
                print('[ERROR] No se pudo establecer conexión a MySQL para INSERT')
                return False

        try:
            cursor = self.connection.cursor()
            if fecha_operacion:
                query = """
                    INSERT INTO Impresiones
                    (ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                print(f'[LOG] Ejecutando INSERT con fecha_operacion: {fecha_operacion}')
                cursor.execute(query, (ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion))
            else:
                query = """
                    INSERT INTO Impresiones
                    (ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                print(f'[LOG] Ejecutando INSERT sin fecha_operacion: ({ID}, {user}, {nombre}, {op}, {versionsgc}, {cantidad}, {totallote}, {numinicio})')
                cursor.execute(query, (ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio))

            self.connection.commit()
            print(f'[LOG] Insert realizado, filas afectadas: {cursor.rowcount}')
            cursor.close()
            return cursor.rowcount == 1
        except Exception as e:
            print(f'[ERROR] Error al ejecutar INSERT en Impresiones: {e}')
            print('[INFO] El historial no se guardará, pero la aplicación continuará funcionando')
            return False

    def close(self):
        if self.connection:
            self.connection.close()
            print('Conexión a MySQL cerrada')
