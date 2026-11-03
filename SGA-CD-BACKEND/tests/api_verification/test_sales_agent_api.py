import requests
import json

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000"

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
    print("Iniciando prueba del Agente de Ventas...")

    # Este endpoint es público y no requiere autenticación.

    pregunta = {
        "query": "¿Cuáles son los roles disponibles en el sistema?"
    }

    run_test(
        name="Consultar al Agente de Ventas sobre los roles",
        method="POST",
        url=f"{BASE_URL}/api/v1/sales_agent",
        headers={"Content-Type": "application/json"},
        data=json.dumps(pregunta)
    )

    pregunta_2 = {
        "query": "¿Qué planes de precios ofrecen?"
    }

    run_test(
        name="Consultar al Agente de Ventas sobre los planes",
        method="POST",
        url=f"{BASE_URL}/api/v1/sales_agent",
        headers={"Content-Type": "application/json"},
        data=json.dumps(pregunta_2)
    )

    print("Prueba del Agente de Ventas completada.")
    print("NOTA: Si la base de conocimiento (índice FAISS) no ha sido creada,")
    print("el agente responderá que no tiene la información. Esto es esperado.")
    print("Ejecute 'python run_ingest.py' con una clave de OpenAI válida para habilitar el conocimiento completo.")
