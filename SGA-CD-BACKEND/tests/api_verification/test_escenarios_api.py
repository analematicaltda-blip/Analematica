import requests
import json
from datetime import datetime, timedelta

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000"
JEFE_ESCENARIOS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqZWZlX2VzY2VuYXJpb3NfZGVtbyIsImV4cCI6MTc1NjM4OTk4N30.placeholder_token"

HEADERS = {
    "Authorization": f"Bearer {JEFE_ESCENARIOS_TOKEN}",
    "Content-Type": "application/json"
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
    print("Iniciando pruebas de API para el rol de Jefe de Escenarios...")

    # Prueba 1: Obtener todos los escenarios
    escenarios = run_test(
        name="Obtener todos los escenarios",
        method="GET",
        url=f"{BASE_URL}/api/v1/escenarios",
        headers=HEADERS
    )

    # Prueba 2: Asignar un espacio
    if escenarios and len(escenarios) > 0:
        escenario_id_para_asignar = escenarios[0]['id']

        # Datos para una nueva asignación en el futuro
        fecha_asignacion = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        asignacion_payload = {
            "escenario_id": escenario_id_para_asignar,
            "nombre_evento": "Evento de Prueba API",
            "fecha": fecha_asignacion,
            "hora_inicio": "10:00",
            "hora_fin": "12:00"
        }
        run_test(
            name="Asignar un Escenario a un Evento",
            method="POST",
            url=f"{BASE_URL}/api/v1/escenarios/asignar",
            headers=HEADERS,
            data=json.dumps(asignacion_payload)
        )
    else:
        print("--- INFO: No hay escenarios para probar la asignación de espacios. ---")

    # Prueba 3: Obtener el historial de mantenimiento
    run_test(
        name="Obtener historial de mantenimiento",
        method="GET",
        url=f"{BASE_URL}/api/v1/escenarios/mantenimiento",
        headers=HEADERS
    )

    print("Pruebas de API para Jefe de Escenarios completadas.")
