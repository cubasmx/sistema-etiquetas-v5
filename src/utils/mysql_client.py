import mysql.connector
from mysql.connector import Error

class MysqlClient:
    def __init__(self, host='10.10.1.8', user='master', password='Ensa2025.', database='etiquetas', port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                print('Conexión a MySQL exitosa')
        except Error as e:
            print(f'Error al conectar a MySQL: {e}')
            self.connection = None

    def select_impresiones(self, ID=None, order_desc=True):
        """
        Trae todas las impresiones, ordenadas por fecha_operacion ASC o DESC.
        """
        if self.connection is None or not self.connection.is_connected():
            print('[LOG] Conexión no activa, reconectando para SELECT...')
            self.connect()

        order = 'DESC' if order_desc else 'ASC'
        try:
            cursor = self.connection.cursor(dictionary=True)
            if ID:
                query = f"SELECT ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion FROM Impresiones WHERE ID = %s ORDER BY fecha_operacion {order}"
                print(f'[LOG] Ejecutando SELECT con filtro ID: {ID}')
                cursor.execute(query, (ID,))
            else:
                query = f"SELECT ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion FROM Impresiones ORDER BY fecha_operacion {order}"
                print(f'[LOG] Ejecutando SELECT de todas las impresiones ordenadas por {order}')
                cursor.execute(query)
            results = cursor.fetchall()
            print(f'[LOG] Resultados obtenidos: {results}')
            cursor.close()
            return results
        except Error as e:
            print(f'[ERROR] Error al ejecutar SELECT en Impresiones: {e}')
            return None


    def insert_impresion(self, ID, user, nombre, op, versionsgc, cantidad, totallote, numinicio, fecha_operacion=None):
        """
        Inserta un nuevo registro en la tabla Impresiones, puede incluir fecha_operacion manual.
        Si no se manda fecha_operacion, MySQL la llenará automáticamente si tiene DEFAULT CURRENT_TIMESTAMP.
        """
        if self.connection is None or not self.connection.is_connected():
            print('[LOG] Conexión no activa, reconectando para INSERT...')
            self.connect()

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
        except Error as e:
            print(f'[ERROR] Error al ejecutar INSERT en Impresiones: {e}')
            return False

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print('Conexión a MySQL cerrada')
