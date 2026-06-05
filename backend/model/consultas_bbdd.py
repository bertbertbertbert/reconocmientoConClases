from model.conexion_bbdd import conexion_bbdd

class consultas_bbdd:

    def __init__(self):
        self.db = conexion_bbdd()

    def verificar_usuario_password(self, usuario, password):
        try:
            conn = self.db.obtener_conexion()
            cur = conn.cursor()
            cur.execute(
                "SELECT code_usuario FROM usuarios WHERE code_usuario = %s AND password = %s",
                (usuario, password))
            resultado = cur.fetchone()
            cur.close()
            if resultado:
                return {"ok": True, "usuario": usuario}
            return {"ok": False}
        except Exception as e:
            print(f"Error al verificar usuario: {e}")
            return {"ok": False}

    def verificar_registro(self, usuario, password, encoding):
        print("entra en funcion de registro")
        try:
            conn = self.db.obtener_conexion()
            cur = conn.cursor()
            cur.execute(
                "SELECT code_usuario FROM usuarios WHERE code_usuario = %s;", (usuario,))
            if cur.fetchone():
                conn.commit()
                cur.close()
                return {"ok":False, "msj":"El usuario ya existe"}
            else:
                cur.execute(
                    "INSERT INTO usuarios (code_usuario, password, vector_128) VALUES (%s, %s, %s);",
                    (usuario, password, encoding))
            conn.commit()
            cur.close()
            print("usuario registrado")
            return {"ok": True, "usuario": usuario}
        except Exception as e:
            print(f"Error en consulta de base de datos: {e}")
            return {"ok": False, "msj": "Error ejecutando la query"}
        
    def guardar_encoding(self, usuario, encoding):
        try:
            conn = self.db.obtener_conexion()
            cur = conn.cursor()
            cur.execute(
                "UPDATE usuarios SET vector_128 = %s WHERE code_usuario = %s;",
                (encoding, usuario))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error guardando encoding: {e}")
            return False
            
    def borrar_usuario(self, usuario):
        try:
            conn = self.db.obtener_conexion()
            cur = conn.cursor()
            cur.execute("DELETE FROM usuarios WHERE code_usuario = %s;", (usuario,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error borrando usuario: {e}")
            return False

    def registrar_video_login(self, nombre_encontrado, fecha_bd, nombre_archivo):
        try:
            conn = self.db.obtener_conexion()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO videos (code_usuario, fecha_video, ruta_video) VALUES (%s, %s, %s);",
                (nombre_encontrado, fecha_bd, nombre_archivo))
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"Error en consulta de base de datos: {e}")

    def buscar_usuario_asincrono(self, encoding, usuario):
        try:
            conn = self.db.obtener_conexion()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT code_usuario, vector_128 <-> %s AS distancia 
                    FROM usuarios 
                    WHERE vector_128 <-> %s < 0.55 AND code_usuario = %s
                    ORDER BY distancia ASC 
                    LIMIT 1;
                """, (encoding, encoding, usuario))
                return cur.fetchone()
        except Exception as e:
            print(f"Error asíncrono en DB: {e}")
            return None