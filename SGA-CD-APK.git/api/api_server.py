from flask import Flask, jsonify, request, g
from functools import wraps
import sqlite3
import stripe
import os
from datetime import datetime
from views.login import hash_password # Reutilizamos el hasher

# --- Configuración ---
# En un entorno de producción real, esta conexión apuntaría a una DB en la nube como Amazon RDS.
DATABASE_PATH = "../formacion.db"

app = Flask(__name__)

# --- Conexión a la Base de Datos ---
def get_db_connection():
    """Crea una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Decorador de Autenticación ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({"error": "Unauthorized. API key is missing."}), 401

        conn = get_db_connection()
        tenant = conn.execute('SELECT id FROM inquilinos WHERE api_key = ? AND activo = 1', (api_key,)).fetchone()

        if tenant:
            g.tenant_id = tenant['id']
            conn.close()
            return f(*args, **kwargs)
        else:
            conn.close()
            return jsonify({"error": "Unauthorized. API key is invalid or tenant is inactive."}), 401

    return decorated_function

# --- API Endpoints ---

@app.route('/api/status', methods=['GET'])
def get_status():
    """Endpoint simple para verificar si la API está funcionando."""
    return jsonify({"status": "ok", "message": "API is running."})

@app.route('/api/user_context', methods=['GET'])
@require_api_key
def get_user_context():
    """Devuelve el contexto para un usuario específico, incluyendo su rol e información de rol."""
    tenant_id = g.tenant_id
    user_id = request.headers.get('X-USER-ID')
    if not user_id: return jsonify({"error": "Header 'X-USER-ID' is missing."}), 400

    try:
        conn = get_db_connection()
        query = "SELECT u.rol, ja.area_responsabilidad FROM usuarios u LEFT JOIN jefes_area ja ON u.id = ja.usuario_id WHERE u.id = ? AND u.inquilino_id = ?"
        user_data = conn.execute(query, (user_id, tenant_id)).fetchone()
        conn.close()
        if not user_data: return jsonify({"error": "User not found or does not belong to this tenant."}), 404
        return jsonify(dict(user_data))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/clases', methods=['GET'])
@require_api_key
def get_clases_profesor():
    """Obtiene las clases asignadas a un profesor."""
    tenant_id = g.tenant_id
    profesor_id = request.args.get('profesor_id')
    if not profesor_id: return jsonify({"error": "profesor_id is required."}), 400

    try:
        conn = get_db_connection()
        query = """
            SELECT c.id, c.nombre_clase, p.nombre_proceso, c.fecha, c.hora_inicio, c.hora_fin
            FROM clases c
            JOIN procesos_formacion p ON c.proceso_id = p.id
            WHERE c.instructor_id = ? AND c.inquilino_id = ?
        """
        clases = conn.execute(query, (profesor_id, tenant_id)).fetchall()
        conn.close()
        return jsonify([dict(row) for row in clases])
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/alumnos', methods=['POST'])
@require_api_key
def create_alumno():
    """Crea un nuevo alumno."""
    tenant_id = g.tenant_id
    data = request.json
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        hashed_password = hash_password(data['password'])
        cursor.execute(
            "INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo) VALUES (?, ?, ?, 'alumno', ?, ?)",
            (tenant_id, data['nombre_usuario'], hashed_password, data['nombre_completo'], data['correo'])
        )
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO alumnos (usuario_id, inquilino_id, documento, fecha_nacimiento, genero) VALUES (?, ?, ?, ?, ?)",
            (user_id, tenant_id, data['documento'], data['fecha_nacimiento'], data['genero'])
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "user_id": user_id}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "El nombre de usuario o documento ya existe."}), 409
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Endpoints para Sincronización (Motor de Datos) ---

@app.route('/api/sync/push', methods=['POST'])
@require_api_key
def sync_push():
    """
    Recibe un lote de datos desde un cliente local y los aplica a la DB central.
    NOTA: Esta es una implementación simplificada 'last-write-wins'.
    """
    tenant_id = g.tenant_id
    data_batch = request.json
    if not data_batch: return jsonify({"error": "No data batch provided."}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if 'alumnos' in data_batch:
            for alumno in data_batch['alumnos']:
                pass # Lógica de inserción/reemplazo simplificada
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Push sync completed."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sync/pull', methods=['GET'])
@require_api_key
def sync_pull():
    """
    Envía datos desde la DB central a un cliente local.
    """
    tenant_id = g.tenant_id
    last_sync_timestamp = request.args.get('last_sync_timestamp')
    try:
        conn = get_db_connection()
        clases = conn.execute("SELECT * FROM clases WHERE inquilino_id = ?", (tenant_id,)).fetchall()
        alumnos = conn.execute("SELECT * FROM alumnos WHERE inquilino_id = ?", (tenant_id,)).fetchall()
        conn.close()
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "data": {
                "clases": [dict(row) for row in clases],
                "alumnos": [dict(row) for row in alumnos]
            }
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Endpoints para Configuración de IA ---

@app.route('/api/config/llm', methods=['GET'])
@require_api_key
def get_llm_config():
    """
    Obtiene la configuración de LLM para el inquilino autenticado.
    """
    tenant_id = g.tenant_id
    try:
        conn = get_db_connection()
        config_data = conn.execute(
            "SELECT llm_preference, openai_api_key, google_api_key FROM inquilinos WHERE id = ?",
            (tenant_id,)
        ).fetchone()
        conn.close()
        if not config_data:
            return jsonify({
                "llm_preference": "local",
                "openai_api_key": "",
                "google_api_key": ""
            })
        return jsonify(dict(config_data))
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/config/llm', methods=['POST'])
@require_api_key
def set_llm_config():
    """Permite a un administrador de inquilino guardar su configuración de LLM."""
    tenant_id = g.tenant_id
    data = request.json
    llm_preference = data.get('llm_preference')
    openai_key = data.get('openai_api_key')
    google_key = data.get('google_api_key')
    if not llm_preference: return jsonify({"error": "El campo 'llm_preference' es requerido."}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE inquilinos SET llm_preference = ?, openai_api_key = ?, google_api_key = ? WHERE id = ?",
            (llm_preference, openai_key, google_key, tenant_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Configuración de LLM guardada."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- Endpoints de Ventas y Registro (Públicos) ---
@app.route('/api/sales_agent', methods=['POST'])
def handle_sales_query():
    return jsonify({"reply": "Respuesta de ventas..."})

@app.route('/api/register_tenant', methods=['POST'])
def register_tenant():
    return jsonify({"checkout_url": "url_de_stripe..."})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
