import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Any, TypedDict, List
from pydantic import BaseModel, Field

from .units.operaciones_deportivas_captain import get_operaciones_deportivas_captain_graph
from .units.estrategia_plataforma_captain import get_estrategia_plataforma_captain_graph

class TacticalTask(BaseModel):
    task_description: str = Field(description="La descripción específica de la misión para el Capitán.")
    responsible_captain: str = Field(
        description="El Capitán especialista. Debe ser: 'OperacionesDeportivas', 'EstrategiaPlataforma'."
    )
class TacticalPlan(BaseModel):
    plan: List[TacticalTask] = Field(description="La lista de misiones tácticas para cumplir la orden.")
class FormacionDeportivaColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: str
    error: str | None
async def create_tactical_plan(state: FormacionDeportivaColonelState, llm: Any) -> FormacionDeportivaColonelState:
    structured_llm = llm.with_structured_output(TacticalPlan)
    prompt = f"""
    Eres un Coronel del Cuerpo de Formación Deportiva. Tu General te ha dado una orden.
    Descompónla en un plan táctico, asignando cada misión a tu Capitán.
    Capitanes bajo tu mando:
    - 'OperacionesDeportivas': Responsable de la ejecución del día a día (entrenamientos, inscripciones, eventos deportivos).
    - 'EstrategiaPlataforma': Responsable de la infraestructura y crecimiento (sedes, seguridad, analítica).
    Analiza la siguiente orden y genera el plan táctico JSON: "{state['general_order']}"
    """
    try:
        plan = await structured_llm.ainvoke(prompt)
        state.update({
            "tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None
        })
    except Exception as e:
        state["error"] = "No se pudo interpretar la orden para crear un plan táctico."
    return state

def route_to_captain(state: FormacionDeportivaColonelState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    next_mission = state["task_queue"][0]
    captain_unit = next_mission.responsible_captain
    if captain_unit == 'OperacionesDeportivas':
        return "operaciones_deportivas_captain"
    elif captain_unit == 'EstrategiaPlataforma':
        return "estrategia_plataforma_captain"
    else:
        state["error"] = f"Planificación defectuosa: Capitán desconocido '{captain_unit}'."
        state["task_queue"].pop(0)
        return "route_to_captain"

async def operaciones_deportivas_node(state: FormacionDeportivaColonelState) -> FormacionDeportivaColonelState:
    mission = state["task_queue"].pop(0)
    result = await operaciones_deportivas_agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({
        "captain": "Operaciones Deportivas", "mission": mission.task_description, "report": result.get("final_report", "Sin reporte.")
    })
    return state

async def estrategia_plataforma_node(state: FormacionDeportivaColonelState) -> FormacionDeportivaColonelState:
    mission = state["task_queue"].pop(0)
    result = await estrategia_plataforma_agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
    state["completed_missions"].append({
        "captain": "Estrategia y Plataforma", "mission": mission.task_description, "report": result.get("final_report", "Sin reporte.")
    })
    return state

async def compile_final_report(state: FormacionDeportivaColonelState) -> FormacionDeportivaColonelState:
    if state.get("error"):
        state["final_report"] = f"Misión de la División fallida. Razón: {state['error']}"
    else:
        report_body = "\n".join(
            [f"- Reporte del Capitán de {m['captain']}:\n  Misión: '{m['mission']}'\n  Resultado: {m['report']}" for m in state["completed_missions"]]
        )
        state["final_report"] = f"Misión de la División de Formación Deportiva completada.\nResumen de Operaciones:\n{report_body}"
    return state

def get_formacion_deportiva_colonel_graph(db_path: str, llm: Any):
    operaciones_deportivas_agent = get_operaciones_deportivas_captain_graph(llm)
    estrategia_plataforma_agent = get_estrategia_plataforma_captain_graph(llm)

    async def operaciones_deportivas_node(state: FormacionDeportivaColonelState) -> FormacionDeportivaColonelState:
        mission = state["task_queue"].pop(0)
        result = await operaciones_deportivas_agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({
            "captain": "Operaciones Deportivas", "mission": mission.task_description, "report": result.get("final_report", "Sin reporte.")
        })
        return state

    async def estrategia_plataforma_node(state: FormacionDeportivaColonelState) -> FormacionDeportivaColonelState:
        mission = state["task_queue"].pop(0)
        result = await estrategia_plataforma_agent.ainvoke({"coronel_order": mission.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({
            "captain": "Estrategia y Plataforma", "mission": mission.task_description, "report": result.get("final_report", "Sin reporte.")
        })
        return state

    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    workflow = StateGraph(FormacionDeportivaColonelState)

    planner_node = lambda state: create_tactical_plan(state, llm)

    workflow.add_node("planner", planner_node)
    workflow.add_node("router", lambda state: state)
    workflow.add_node("operaciones_deportivas_captain", operaciones_deportivas_node)
    workflow.add_node("estrategia_plataforma_captain", estrategia_plataforma_node)
    workflow.add_node("compiler", compile_final_report)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router", route_to_captain,
        {
            "operaciones_deportivas_captain": "operaciones_deportivas_captain",
            "estrategia_plataforma_captain": "estrategia_plataforma_captain",
            "compile_report": "compiler", "route_to_captain": "router"
        }
    )
    workflow.add_edge("operaciones_deportivas_captain", "router")
    workflow.add_edge("estrategia_plataforma_captain", "router")
    workflow.add_edge("compiler", END)
    return workflow.compile(checkpointer=memory).with_types(input_type=FormacionDeportivaColonelState)
