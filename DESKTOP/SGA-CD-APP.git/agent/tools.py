import requests
from langchain_core.tools import tool

# This configuration would be passed dynamically in a real app
API_BASE_URL = "http://127.0.0.1:5001"
# The API key would also be passed dynamically based on the tenant
TENANT_API_KEY = "inquilino_demo_key"

@tool
def get_attendance_report_tool(query: str) -> str:
    """
    Útil para obtener un informe o listado de asistencia de alumnos.
    Responde con los datos del reporte en formato JSON o un mensaje de error.
    El parámetro 'query' no se usa actualmente pero es requerido por el decorador.
    """
    print("--- Usando la herramienta: get_attendance_report_tool ---")
    headers = {"X-API-KEY": TENANT_API_KEY}
    try:
        response = requests.get(f"{API_BASE_URL}/api/reportes/asistencia", headers=headers)
        response.raise_for_status()
        report_data = response.json()
        if not report_data:
            return "No se encontraron datos de asistencia."
        # Return a summary or the full data as a string
        return f"Se encontraron {len(report_data)} registros de asistencia. Aquí están los primeros: {str(report_data[:3])}"
    except requests.exceptions.RequestException as e:
        return f"Error al llamar a la API: {e}"

# Example of another potential tool
@tool
def find_user_by_name(name: str) -> str:
    """
    Busca un usuario en el sistema por su nombre completo.
    Responde con la información del usuario o un mensaje si no se encuentra.
    """
    # This is a placeholder for a future API endpoint
    print(f"--- Usando la herramienta: find_user_by_name con el nombre: {name} ---")
    # Placeholder logic
    if "demo" in name.lower():
        return f"Se encontró al usuario '{name}' con el rol 'profesor' en el área de 'Deportes'."
    else:
        return f"No se encontró ningún usuario con el nombre '{name}'."

# A list of all available tools for the agent
available_tools = [get_attendance_report_tool, find_user_by_name]
