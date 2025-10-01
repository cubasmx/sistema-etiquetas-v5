# src/utils/mysql_client.py
import pymysql
import time

class MysqlClient:
    def __init__(self, **cfg):
        self.cfg = dict(
            host="10.10.2.63",      # 👈 tu servidor nuevo
            user="etiquetas",       # 👈 usuario creado en MariaDB
            password="C0ntr@s3ñA.Segura!",  # 👈 tu contraseña
            database="etiquetas",   # 👈 base de datos
            port=3306,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5
        )
        self.cfg.update(cfg)
        self.conn = None

    def connect(self, retries=3, delay=2):
        last = None
        for i in range(retries):
            try:
                self.conn = pymysql.connect(**self.cfg, autocommit=True)
                with self.conn.cursor() as c:
                    c.execute("SELECT 1")
                return True
            except Exception as e:
                last = e
                time.sleep(delay)
        self.conn = None
        print(f"[ERROR] No se pudo conectar: {last}")
        return False

    def ensure_conn(self):
        if self.conn is None:
            return self.connect()
        try:
            self.conn.ping(reconnect=True)
            return True
        except Exception:
            return self.connect()

    def insert_impresion(self, id_producto, user, nombre, op, versionsgc, cantidad, totallote, numinicio):
        if not self.ensure_conn():
            return False
        try:
            with self.conn.cursor() as cur:
                sql = """
                INSERT INTO Impresiones
                    (id_producto, user, nombre, op, versionsgc, cantidad, totallote, numinicio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (id_producto, user, nombre, op, versionsgc, cantidad, totallote, numinicio))
            return True
        except Exception as e:
            print(f"[ERROR] insert_impresion falló: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
