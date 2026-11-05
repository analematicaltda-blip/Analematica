import asyncio
import flet as ft
from utils.database_manager import get_db_path
from agent.llm_service import get_llm_instance

async def invoke_agent_for_area(page: ft.Page, area: str, user_input: str, user_id: int = 13, tenant_id: int = 1) -> str:
    """
    Orquestador Central de Interfaz: Carga bajo demanda (Lazy Loading) al Coronel correspondiente,
    optimizando la memoria del dispositivo y conectando con SQLite local (local_sga.db).
    """
    print(f"--- 📞 Interfaz de Agente: Recibida orden para división '{area}' -> '{user_input[:40]}...' ---")

    llm = get_llm_instance()
    db_path = get_db_path(page)

    area_upper = area.upper()
    agent_graph = None

    # Lazy Loading: solo se importa y compila la división solicitada
    try:
        if "VENTA" in area_upper or "CRM" in area_upper:
            from agents.corps.ventas_crm_colonel import get_ventas_crm_colonel_graph
            agent_graph = get_ventas_crm_colonel_graph(llm)
        elif "MULTI" in area_upper or "VIDEO" in area_upper or "REEL" in area_upper:
            from agents.corps.multimedia_colonel import get_multimedia_colonel_graph
            agent_graph = get_multimedia_colonel_graph(llm)
        elif "RED" in area_upper or "SOCIAL" in area_upper or "PERFIL" in area_upper:
            from agents.corps.redes_sociales_colonel import get_redes_sociales_colonel_graph
            agent_graph = get_redes_sociales_colonel_graph(llm)
        elif "DEPORTE" in area_upper:
            from agents.corps.formacion_deportiva_colonel import get_formacion_deportiva_colonel_graph
            agent_graph = get_formacion_deportiva_colonel_graph(db_path, llm)
        elif "CULTURA" in area_upper:
            from agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph
            agent_graph = get_formacion_cultura_colonel_graph(db_path, llm)
        else:
            return f"Error: División '{area}' no reconocida en el Estado Mayor."
    except Exception as e:
        return f"Error al cargar la división {area}: {e}"

    if not agent_graph:
        return "Error Crítico: No se pudo construir el grafo del Coronel de división."

    try:
        resultado = await agent_graph.ainvoke({
            "general_order": user_input,
            "coronel_order": user_input,
            "app_context": {"db_path": db_path, "user_id": user_id, "tenant_id": tenant_id}
        })
        rep = resultado.get("final_report", "Misión procesada exitosamente.")
        if isinstance(rep, dict):
            return rep.get("text", str(rep))
        return str(rep)
    except Exception as e:
        return f"Reporte de Estado Mayor: Misión ejecutada con observación local: {e}"