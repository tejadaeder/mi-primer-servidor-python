import os
import mysql.connector 
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class UsuarioRepositorio:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        # Agregamos el puerto con valor por defecto 3306 por si no está en el .env
        self.port = int(os.getenv("DB_PORT", 3306))

    def obtener_conexion(self):
        try:
            conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                ssl_disabled=False # Obligatorio para conexiones seguras en la nube (Aiven)
            )
            return conexion
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def registrar_usuario(self, nombre, correo, password_hash):
        conexion = self.obtener_conexion()
        if conexion is None:
            return False

        try:
            cursor = conexion.cursor()
            query = "INSERT INTO usuarios_sistema (nombre, correo, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, correo, password_hash))
            conexion.commit()
            return True
        except Error as e:
            print(f"Error al registrar el usuario: {e}")
            return False
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

    def obtener_usuario_por_correo(self, correo):
        conexion = self.obtener_conexion()
        if conexion is None:
            return None

        try:
            cursor = conexion.cursor(dictionary=True)
            query = "SELECT * FROM usuarios_sistema WHERE correo = %s"
            cursor.execute(query, (correo,))
            usuario = cursor.fetchone()
            return usuario
        except Error as e:
            print(f"Error al obtener el usuario: {e}")
            return None
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()