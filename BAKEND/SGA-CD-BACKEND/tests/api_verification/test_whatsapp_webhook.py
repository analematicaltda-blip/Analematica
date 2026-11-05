import requests
import json
import time

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000"
# No se necesita token de usuario para llamar al webhook, ya que es una llamada de servidor a servidor.

# --- Payload de Ejemplo ---
# Esta es una simulación de la estructura de un webhook de mensaje de texto de WhatsApp.
SAMPLE_WHATSAPP_PAYLOAD = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "16505551111",
                            "phone_number_id": "YOUR_PHONE_NUMBER_ID"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "John Doe"
                                },
                                "wa_id": "16505552222"
                            }
                        ],
                        "messages": [
                            {
                                "from": "16505552222", # Número del cliente
                                "id": "wamid.HBgLMTY1MDU1NTIyMjIVAgARGBJDNzE4QkY3OTlDODQxRjk5RgA=",
                                "timestamp": str(int(time.time())),
                                "text": {
                                    "body": "Hola, me gustaría saber más sobre sus planes."
                                },
                                "type": "text"
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}


def run_test(name, method, url, **kwargs):
    """Función helper para ejecutar una prueba y mostrar el resultado."""
    print(f"--- Ejecutando Prueba: {name} ---")
    try:
        response = requests.request(method, url, **kwargs)
        print(f"URL: {method} {url}")
        print(f"Status Code: {response.status_code}")

        if response.text:
            try:
                print("Response JSON:")
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                print("Response Text (not JSON):")
                print(response.text)
        else:
            print("Response: No content")

        assert response.ok, f"La respuesta no fue exitosa (código: {response.status_code})"
        print(f"--- PRUEBA '{name}' PASÓ ---")
        return response.json() if response.text else None

    except Exception as e:
        print(f"--- PRUEBA '{name}' FALLÓ ---")
        print(f"Error: {e}")
    print("\\n" + "="*40 + "\\n")
    return None


if __name__ == "__main__":
    print("Iniciando prueba de webhook de WhatsApp...")

    # El endpoint del webhook no requiere autenticación de usuario,
    # ya que es llamado por el servidor de Meta. La seguridad se
    # maneja a través de la firma de la solicitud (no implementado en este test)
    # o la validación del token en la configuración del webhook.

    run_test(
        name="Simular recepción de mensaje de WhatsApp",
        method="POST",
        url=f"{BASE_URL}/api/v1/webhooks/whatsapp",
        headers={"Content-Type": "application/json"},
        data=json.dumps(SAMPLE_WHATSAPP_PAYLOAD)
    )

    print("Prueba de webhook de WhatsApp completada.")
    print("NOTA: Esta prueba solo confirma que el webhook responde con 'ok'.")
    print("La lógica de procesamiento real (llamada al agente de IA y respuesta) se ejecuta en segundo plano.")
    print("Revise los logs del servidor para confirmar que el mensaje fue procesado.")
