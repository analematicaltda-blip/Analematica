import sqlite3
from datetime import datetime
import json

DATABASE_PATH = "formacion.db" # Assuming this runs from the root directory

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_or_create_conversation(user1_id: int, user2_id: int, tenant_id: int):
    """
    Finds an existing 1-on-1 conversation or creates a new one.
    Returns the conversation_id.
    """
    if user1_id == user2_id:
        return None # Cannot have a conversation with oneself

    conn = get_db_connection()
    cursor = conn.cursor()

    # Find a conversation that has EXACTLY these two participants.
    # This is a bit tricky in SQL.
    cursor.execute("""
        SELECT c.id FROM chat_conversaciones c
        JOIN chat_participantes p1 ON c.id = p1.conversacion_id AND p1.usuario_id = ?
        JOIN chat_participantes p2 ON c.id = p2.conversacion_id AND p2.usuario_id = ?
        WHERE c.id IN (
            SELECT conversacion_id FROM chat_participantes
            GROUP BY conversacion_id
            HAVING COUNT(usuario_id) = 2
        )
    """, (user1_id, user2_id))

    conversation = cursor.fetchone()

    if conversation:
        conn.close()
        return conversation['id']
    else:
        # Create a new conversation
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO chat_conversaciones (inquilino_id, fecha_creacion) VALUES (?, ?)",
            (tenant_id, now)
        )
        conversation_id = cursor.lastrowid

        # Add both participants
        cursor.execute("INSERT INTO chat_participantes (conversacion_id, usuario_id) VALUES (?, ?)", (conversation_id, user1_id))
        cursor.execute("INSERT INTO chat_participantes (conversacion_id, usuario_id) VALUES (?, ?)", (conversation_id, user2_id))

        conn.commit()
        conn.close()
        return conversation_id

def send_message(remitente_id: int, conversacion_id: int, contenido: str, pubsub_handler):
    """Saves a message to the DB and publishes it via the provided pubsub handler."""
    conn = get_db_connection()
    cursor = conn.cursor()

    now = datetime.now().isoformat()

    try:
        # Save message to DB
        cursor.execute(
            "INSERT INTO chat_mensajes (conversacion_id, remitente_usuario_id, contenido, timestamp) VALUES (?, ?, ?, ?)",
            (conversacion_id, remitente_id, contenido, now)
        )
        # Update the last message timestamp for the conversation
        cursor.execute(
            "UPDATE chat_conversaciones SET ultimo_mensaje_timestamp = ? WHERE id = ?",
            (now, conversacion_id)
        )
        conn.commit()

        # Find the other participant(s) to send the notification to
        cursor.execute("SELECT usuario_id FROM chat_participantes WHERE conversacion_id = ? AND usuario_id != ?", (conversacion_id, remitente_id))
        recipients = cursor.fetchall()

        # Get sender's name
        sender_name = cursor.execute("SELECT nombre_completo FROM usuarios WHERE id = ?", (remitente_id,)).fetchone()[0]

        # Publish the message
        for recipient in recipients:
            recipient_id = recipient['usuario_id']
            message_data = {
                "type": "new_message",
                "conversacion_id": conversacion_id,
                "remitente_id": remitente_id,
                "remitente_nombre": sender_name,
                "contenido": contenido,
                "timestamp": now,
            }
            # Flet's pubsub requires the message to be a string
            pubsub_handler.send_all_on_topic(f"chat_{recipient_id}", json.dumps(message_data))

        return {"status": "success"}

    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()
