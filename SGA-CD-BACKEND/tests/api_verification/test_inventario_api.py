import requests
import json

# --- Configuración ---
BASE_URL = "http://127.0.0.1:8000"
# Usamos el token del Jefe de Almacén ya que tiene los permisos más altos para inventario
JEFE_ALMACEN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqZWZlX2FsbWFjZW5fZGVtbyIsImV4cCI6MTc1NjM4OTk4N30.placeholder_token"

HEADERS = {
    "Authorization": f"Bearer {JEFE_ALMACEN_TOKEN}",
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
    print("Iniciando pruebas de API para los roles de Inventario...")

    # Prueba 1: Obtener todos los items del inventario
    items = run_test(
        name="Obtener todos los items de inventario",
        method="GET",
        url=f"{BASE_URL}/api/v1/inventory/items",
        headers=HEADERS
    )

    # Prueba 2: Registrar un movimiento de ENTRADA
    if items and len(items) > 0:
        item_id_para_entrada = items[0]['id']
        movimiento_entrada = {
            "item_id": item_id_para_entrada,
            "cantidad": 10,
            "tipo": "entrada",
            "justificacion": "Entrada de prueba desde API"
        }
        run_test(
            name="Registrar Movimiento de Entrada",
            method="POST",
            url=f"{BASE_URL}/api/v1/inventory/movimientos",
            headers=HEADERS,
            data=json.dumps(movimiento_entrada)
        )
    else:
        print("--- INFO: No hay items en el inventario para probar el registro de movimientos. ---")

    # Prueba 3: Registrar un movimiento de SALIDA
    if items and len(items) > 0:
        item_id_para_salida = items[0]['id']
        movimiento_salida = {
            "item_id": item_id_para_salida,
            "cantidad": 2,
            "tipo": "salida",
            "justificacion": "Salida de prueba desde API"
        }
        run_test(
            name="Registrar Movimiento de Salida",
            method="POST",
            url=f"{BASE_URL}/api/v1/inventory/movimientos",
            headers=HEADERS,
            data=json.dumps(movimiento_salida)
        )
    else:
        print("--- INFO: No hay items en el inventario para probar el registro de movimientos. ---")

    # Prueba 4: Obtener items con bajo stock (endpoint asumido)
    run_test(
        name="Obtener Items con Bajo Stock",
        method="GET",
        url=f"{BASE_URL}/api/v1/inventory/items?stock_level=low",
        headers=HEADERS
    )

    print("Pruebas de API para Inventario completadas.")
