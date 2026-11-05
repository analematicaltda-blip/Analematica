import sqlite3
import json
from datetime import datetime

def create_notification(tenant_id: int, user_id: int, message: str, pubsub_instance):
    """
    Creates a notification in the database and sends a real-time alert via Pub/Sub.

    Args:
        tenant_id: The ID of the tenant.
        user_id: The ID of the user who will receive the notification.
        message: The notification message content.
        pubsub_instance: The page.pubsub object to send real-time updates.
    """
    try:
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO notificaciones (inquilino_id, usuario_id, mensaje, fecha_hora, leido)
            VALUES (?, ?, ?, ?, 0)
        """, (tenant_id, user_id, message, timestamp))

        conn.commit()
        conn.close()
        print(f"NOTIFICATION: Created for user '{user_id}': '{message}'")

        # Send a real-time message to the specific user's channel
        if pubsub_instance:
            pubsub_instance.send_all({"topic": f"new_notification_{user_id}", "message": message})
            print(f"NOTIFICATION: PubSub message sent to topic 'new_notification_{user_id}'")

    except Exception as e:
        print(f"CRITICAL: Failed to create notification. User: {user_id}, Error: {e}")

# Example usage
if __name__ == '__main__':
    # This example won't send a pubsub message because it doesn't have the instance.
    # It only tests the database insertion.
    class MockPubSub:
        def send_all(self, msg):
            print(f"MockPubSub sending: {msg}")

    mock_pubsub = MockPubSub()
    create_notification(
        tenant_id=1,
        user_id=1,
        message="Esta es una notificación de prueba.",
        pubsub_instance=mock_pubsub
    )
