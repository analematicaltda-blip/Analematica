import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Any, TypedDict, List
from pydantic import BaseModel, Field

from .units.operaciones_academicas_captain import get_operaciones_academicas_captain_graph
from .units.estrategia_plataforma_captain import get_estrategia_plataforma_captain_graph

class TacticalTask(BaseModel):
    task_description: str = Field(description="La descripción específica y detallada de la misión para el Capitán.")
    responsible_captain: str = Field(
        description="El Capitán especialista. Debe ser: 'OperacionesAcademicas', 'EstrategiaPlataforma'."
    )
class TacticalPlan(BaseModel):
    plan: List[TacticalTask] = Field(description="La lista de misiones tácticas para cumplir la orden del General.")
class FormacionCulturaColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict # El reporte ahora es un objeto estructurado
    error: str | None
async def create_tactical_plan(state: FormacionCulturaColonelState, llm: Any) -> FormacionCulturaColonelState:
    print("--- 🧠 CORONEL FORMACIÓN Y CULTURA: Creando Plan Táctico... ---")
    structured_llm = llm.with_structured_output(TacticalPlan)
    prompt = f"""
    Eres un Coronel del Cuerpo de Formación y Cultura. Tu General te ha dado una orden.
    Tu deber es descomponerla en un plan táctico, asignando cada misión a tu Capitán.
    Capitanes bajo tu mando:
    - 'OperacionesAcademicas': Responsable de la ejecución del día a día (clases, inscripciones, eventos).
    - 'EstrategiaPlataforma': Responsable de la infraestructura y crecimiento (sedes, seguridad, analítica).
    Analiza la siguiente orden y genera el plan táctico JSON: "{state['general_order']}"
    """
    try:
        plan = await structured_llm.ainvoke(prompt)
        state.update({
            "tactical_plan": plan,
            "task_queue": plan.plan.copy(),
            "completed_missions": [],
            "error": None
        })
    except Exception as e:
        state["error"] = "No se pudo interpretar la orden para crear un plan táctico."
    return state

def route_to_captain(state: FormacionCulturaColonelState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    next_mission = state["task_queue"][0]
    captain_unit = next_mission.responsible_captain
    if captain_unit == 'OperacionesAcademicas':
        return "operaciones_academicas_captain"
    elif captain_unit == 'EstrategiaPlataforma':
        return "estrategia_plataforma_captain"
    else:
        state["error"] = f"Planificación defectuosa: Capitán desconocido '{captain_unit}'."
        state["task_queue"].pop(0)
        return "route_to_captain"

async def compile_final_report(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
    """Compila el reporte final de la división para el General (la API)."""
    if state.get("error"):
        state["final_report"] = {"text": f"Misión de la División fallida. Razón: {state['error']}", "image_url": None}
    else:
        final_text = "Misión de la División de Formación y Cultura completada.\nResumen de Operaciones:\n"
        final_image_url = None
        for mission_report in state["completed_missions"]:
            report_content = mission_report.get("report", {})
            final_text += f"- Reporte del Capitán de {mission_report['captain']} (Misión: '{mission_report['mission']}'):\n  {report_content.get('text', 'Sin reporte de texto.')}\n"
            if report_content.get('image_url'):
                final_image_url = report_content['image_url']

        state["final_report"] = {
            "text": final_text,
            "image_url": final_image_url
        }
    return state

# The following node definitions are redefined inside get_formacion_cultura_colonel_graph
# to properly close over the initialized subordinate agents.
# This is a pattern to ensure agents are not globally shared.
async def operaciones_academicas_node(state: FormacionCulturaColonelState, agent) -> FormacionCulturaColonelState:
    mission = state["task_queue"].pop(0)
    result = await agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({
        "captain": "Operaciones Academicas", "mission": mission.task_description, "report": result.get('final_report', {"text": "Sin reporte.", "image_url": None})
    })
    return state

async def estrategia_plataforma_node(state: FormacionCulturaColonelState, agent) -> FormacionCulturaColonelState:
    mission = state["task_queue"].pop(0)
    result = await agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({
        "captain": "Estrategia y Plataforma", "mission": mission.task_description, "report": result.get('final_report', {"text": "Sin reporte.", "image_url": None})
    })
    return state

def get_formacion_cultura_colonel_graph(db_path: str, llm: Any):
    # Initialize subordinate agents inside the graph-building function, passing the llm down.
    operaciones_academicas_agent = get_operaciones_academicas_captain_graph(llm)
    estrategia_plataforma_agent = get_estrategia_plataforma_captain_graph(llm)

    # Define nodes here to close over the initialized agents
    async def operaciones_academicas_node_wrapper(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
        return await operaciones_academicas_node(state, operaciones_academicas_agent)

    async def estrategia_plataforma_node_wrapper(state: FormacionCulturaColonelState) -> FormacionCulturaColonelState:
        return await estrategia_plataforma_node(state, estrategia_plataforma_agent)

    memory = MemorySaver()
    workflow = StateGraph(FormacionCulturaColonelState)

    async def planner_node(state):
        return await create_tactical_plan(state, llm)

    workflow.add_node("planner", planner_node)
    workflow.add_node("router", lambda state: state)
    workflow.add_node("operaciones_academicas_captain", operaciones_academicas_node_wrapper)
    workflow.add_node("estrategia_plataforma_captain", estrategia_plataforma_node_wrapper)
    workflow.add_node("compiler", compile_final_report)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router", route_to_captain,
        {
            "operaciones_academicas_captain": "operaciones_academicas_captain",
            "estrategia_plataforma_captain": "estrategia_plataforma_captain",
            "compile_report": "compiler", "route_to_captain": "router"
        }
    )
    workflow.add_edge("operaciones_academicas_captain", "router")
    workflow.add_edge("estrategia_plataforma_captain", "router")
    workflow.add_edge("compiler", END)
    return workflow.compile(checkpointer=memory).with_types(input_type=FormacionCulturaColonelState)
