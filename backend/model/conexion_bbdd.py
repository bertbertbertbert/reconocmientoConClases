import psycopg2
from pgvector.psycopg2 import register_vector

class conexion_bbdd:

    DB_CONFIG = {
    "dbname": "faces",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
    }
        
    def __init__(self):
        self.conn = None

    def conectar_db(self):
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(**self.DB_CONFIG)
                register_vector(self.conn)

        except Exception as e:
            print(f"Error al conectar: {e}")    

    def desconectar_db(self):
        try:
            if self.conn and not self.conn.closed:
                self.conn.closed()
        except Exception as e: 
            print(f"Error al desconectar: {e}")

    def obtener_conexion(self):
        self.conectar_db()
        return self.conn