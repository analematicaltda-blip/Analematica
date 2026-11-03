import sqlite3
import json
from datetime import datetime

def log_action(tenant_id: int, actor_user_id: int, action: str, details: dict):
    """
    Logs a critical action to the audit_log table.

    Args:
        tenant_id: The ID of the tenant where the action occurred.
        actor_user_id: The ID of the user who performed the action.
        action: A string code for the action (e.g., 'CREAR_USUARIO').
        details: A dictionary with relevant data about the action.
    """
    try:
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # Convert details dict to a JSON string for storage
        details_json = json.dumps(details)
        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO audit_log (inquilino_id, usuario_id_actor, accion, detalles, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (tenant_id, actor_user_id, action, details_json, timestamp))

        conn.commit()
        conn.close()
        print(f"AUDIT: Action '{action}' logged for user '{actor_user_id}' in tenant '{tenant_id}'.")
    except Exception as e:
        # In a real application, audit log failures are critical and should be handled robustly.
        print(f"CRITICAL: Failed to write to audit log. Action: {action}, Error: {e}")

# Example usage (for testing purposes)
if __name__ == '__main__':
    # This assumes tenant 1 and user 1 exist from dummy data
    log_action(
        tenant_id=1,
        actor_user_id=1,
        action="INICIAR_SESION",
        details={"ip_address": "127.0.0.1", "user_agent": "Test Script"}
    )
    log_action(
        tenant_id=1,
        actor_user_id=1,
        action="CREAR_USUARIO",
        details={"nuevo_usuario_id": 10, "rol_asignado": "profesor"}
    )
