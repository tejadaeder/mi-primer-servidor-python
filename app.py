from flask import Flask, jsonify, request
from servicio import UsuarioServicio
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/", methods=["GET"])
def bienvenida():
    """
    Endpoint raíz para verificar que el servidor está vivo
    ---
    responses:
      200:
        description: Mensaje de bienvenida
    """
    return jsonify({
        "estado": "Online",
        "mensaje": "¡API funcionando hasta la ultima actualización - cuarta prueba automatica",
        "documentacion": "/apidocs"
    }), 200

servicio = UsuarioServicio()

@app.route('/api/usuarios/registro', methods=['POST'])
def registrar_usuario():
    """
    Registra un nuevo usuario en la base de datos de forma segura.
    ---
    tags:
      - Autenticación y Usuarios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
              example: "Mateo Tejada"
            correo:
              type: string
              example: "mateo@unsa.edu.pe"
            password:
              type: string
              example: "PasswordSeguro2026*"
    responses:
      201:
        description: Usuario registrado exitosamente
      400:
        description: Error de validación o usuario duplicado
    """
    datos_json = request.get_json()
    if not datos_json:
        return jsonify({"error": "No se proporcionaron datos"}), 400

    respuesta, codigo_http = servicio.registrar_usuario(datos_json)
    return jsonify(respuesta), codigo_http

@app.route('/api/usuarios/login', methods=['POST'])
def login_usuario():
    """
    Inicia sesión validando el Hash con Bcrypt.
    ---
    tags:
      - Autenticación y Usuarios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            correo:
              type: string
              example: "mateo@unsa.edu.pe"
            password:
              type: string
              example: "PasswordSeguro2026*"
    responses:
      200:
        description: Login exitoso
      401:
        description: Credenciales inválidas
    """
    try:
        datos_json = request.get_json()
        if not datos_json:
            return jsonify({"error": "No se proporcionaron datos"}), 400

        correo = datos_json.get("correo")
        password = datos_json.get("password")

        if not correo or not password:
            return jsonify({"error": "Faltan datos requeridos"}), 400

        respuesta, codigo_http = servicio.login_usuario(correo, password)
        return jsonify(respuesta), codigo_http
    
    except Exception as e:
        return jsonify({"error": f"Error al procesar la solicitud: {str(e)}"}), 500

@app.route('/api/usuarios/listar', methods=['GET'])
def listar_usuarios():
    """
    Lista todos los usuarios registrados en la nube (Aiven)
    ---
    tags:
      - Autenticación y Usuarios
    responses:
      200:
        description: Lista de usuarios obtenida exitosamente
    """
    conexion = servicio.repositorio.obtener_conexion()
    if not conexion:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, correo, fecha_registro FROM usuarios_sistema")
    usuarios = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    return jsonify(usuarios), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)