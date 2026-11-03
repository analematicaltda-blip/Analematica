import requests
import json

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000"  # Cambiar si el backend corre en otro puerto/host
ALUMNO_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbHVtbm9fZGVtbyIsImV4cCI6MTc1NjM4OTk4N30.placeholder_token" # Reemplazar con un token JWT válido para un usuario Alumno

HEADERS = {
    "Authorization": f"Bearer {ALUMNO_TOKEN}"
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

        # Assertions básicas
        assert response.ok, f"La respuesta no fue exitosa (código: {response.status_code})"
        print(f"--- PRUEBA '{name}' PASÓ ---")

    except Exception as e:
        print(f"--- PRUEBA '{name}' FALLÓ ---")
        print(f"Error: {e}")
    print("\\n" + "="*40 + "\\n")


if __name__ == "__main__":
    print("Iniciando pruebas de API para el rol de Alumno...")

    # Prueba 1: Obtener los cursos del alumno
    run_test(
        name="Obtener Mis Cursos",
        method="GET",
        url=f"{BASE_URL}/api/v1/alumno/cursos",
        headers=HEADERS
    )

    # Prueba 2: Obtener el horario del alumno
    run_test(
        name="Obtener Mi Horario",
        method="GET",
        url=f"{BASE_URL}/api/v1/alumno/horario",
        headers=HEADERS
    )

    # Prueba 3: Obtener las calificaciones del alumno
    run_test(
        name="Obtener Mis Calificaciones",
        method="GET",
        url=f"{BASE_URL}/api/v1/alumno/calificaciones",
        headers=HEADERS
    )

    # Prueba 4: Obtener misiones de gamificación
    run_test(
        name="Obtener Misiones de Gamificación",
        method="GET",
        url=f"{BASE_URL}/api/v1/gamificacion/misiones",
        headers=HEADERS
    )

    # Prueba 5: Obtener artículos del mercado de gamificación
    run_test(
        name="Obtener Artículos del Mercado",
        method="GET",
        url=f"{BASE_URL}/api/v1/gamificacion/mercado/items",
        headers=HEADERS
    )

    print("Pruebas de API para Alumno completadas.")
