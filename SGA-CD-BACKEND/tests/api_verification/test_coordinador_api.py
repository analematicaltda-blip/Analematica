import requests
import json

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000"
COORDINADOR_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjb29yZGluYWRvcl9kZW1vIiwiZXhwIjoxNzU2Mzg5OTg3fQ.placeholder_token" # Reemplazar con un token JWT válido para un usuario Coordinador

HEADERS = {
    "Authorization": f"Bearer {COORDINADOR_TOKEN}",
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
        # Devolvemos el contenido por si se necesita para otra prueba
        return response.json() if response.text else None

    except Exception as e:
        print(f"--- PRUEBA '{name}' FALLÓ ---")
        print(f"Error: {e}")
    print("\\n" + "="*40 + "\\n")
    return None


if __name__ == "__main__":
    print("Iniciando pruebas de API para el rol de Coordinador...")

    # Prueba 1: Obtener la programación
    run_test(
        name="Obtener Programación de Actividades",
        method="GET",
        url=f"{BASE_URL}/api/v1/coordinador/programacion",
        headers=HEADERS
    )

    # Prueba 2: Crear una nueva misión de gamificación
    nueva_mision = {
        "nombre": "Misión de Prueba desde API",
        "descripcion": "Completar la prueba de API.",
        "puntos_recompensa": 50,
        "es_grupal": False,
        "inquilino_id": 1 # ID del inquilino/empresa, puede necesitar ajuste
    }
    run_test(
        name="Crear Nueva Misión de Gamificación",
        method="POST",
        url=f"{BASE_URL}/api/v1/gamificacion/misiones",
        headers=HEADERS,
        data=json.dumps(nueva_mision)
    )

    # Prueba 3: Obtener la lista de aprobaciones pendientes
    aprobaciones = run_test(
        name="Obtener Aprobaciones Pendientes",
        method="GET",
        url=f"{BASE_URL}/api/v1/coordinador/aprobaciones",
        headers=HEADERS
    )

    # Prueba 4 y 5: Aprobar y Rechazar una solicitud (si hay alguna)
    if aprobaciones and len(aprobaciones) > 0:
        # Tomamos la primera solicitud para la prueba
        id_aprobacion_a_aprobar = aprobaciones[0]['id']
        run_test(
            name="Aprobar Solicitud",
            method="POST",
            url=f"{BASE_URL}/api/v1/coordinador/aprobaciones/{id_aprobacion_a_aprobar}/approve",
            headers=HEADERS
        )

        # Si hay otra, la rechazamos. Si no, informamos.
        if len(aprobaciones) > 1:
            id_aprobacion_a_rechazar = aprobaciones[1]['id']
            run_test(
                name="Rechazar Solicitud",
                method="POST",
                url=f"{BASE_URL}/api/v1/coordinador/aprobaciones/{id_aprobacion_a_rechazar}/reject",
                headers=HEADERS
            )
        else:
            print("--- INFO: No hay una segunda solicitud para probar la acción de rechazar. ---")

    else:
        print("--- INFO: No hay solicitudes pendientes para probar las acciones de aprobar/rechazar. ---")

    print("Pruebas de API para Coordinador completadas.")
