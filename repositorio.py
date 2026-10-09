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
        # Capturamos el puerto de la variable de entorno, por defecto 3306 si no existe
        self.port = int(os.getenv("DB_PORT", 3306))
        
        # Auto-crear la tabla al iniciar la aplicación para evitar errores en la nube
        self.inicializar_base_datos()

    def obtener_conexion(self):
        try:
            conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                ssl_disabled=False # Obligatorio para conexiones seguras en Aiven y la nube
            )
            return conexion
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def inicializar_base_datos(self):
        """Crea la tabla usuarios_sistema automáticamente si no existe en la nube"""
        conexion = self.obtener_conexion()
        if conexion is None:
            print("No se pudo conectar a la base de datos para inicializar la tabla.")
            return

        try:
            cursor = conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios_sistema (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    correo VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conexion.commit()
            print("Tabla 'usuarios_sistema' verificada o creada exitosamente.")
        except Error as e:
            print(f"Error al crear la tabla automáticamente: {e}")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

    def registrar_usuario(self, nombre, correo, password_hash):
        conexion = self.obtener_conexion()
        if conexion is None:
            return False, "Error de conexión con la base de datos"

        try:
            cursor = conexion.cursor()
            query = "INSERT INTO usuarios_sistema (nombre, correo, password_hash) VALUES (%s, %s, %s)"
            cursor.execute(query, (nombre, correo, password_hash))
            conexion.commit()
            return True, "Usuario registrado con éxito"
        except Error as e:
            # Retornamos el error exacto de MySQL para depurar en Postman
            error_msg = f"Error MySQL: {e.msg}" if hasattr(e, 'msg') else str(e)
            print(error_msg)
            return False, error_msg
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