from langchain_core.tools import tool

@tool
def tool_crear_lead_crm(nombre: str, correo: str, telefono: str, interes: str) -> str:
    """Registra un nuevo prospecto interesado en cursos deportivos o culturales en el CRM."""
    return f"Prospecto '{nombre}' registrado en el embudo comercial del CRM. Interes: {interes}."

@tool
def tool_consultar_pipeline_ventas(area: str) -> str:
    """Consulta el estado del embudo comercial, cotizaciones activas y oportunidades abiertas."""
    return f"Pipeline comercial para el area '{area}': 12 prospectos en seguimiento, 4 cotizaciones emitidas, tasa de cierre: 35%."