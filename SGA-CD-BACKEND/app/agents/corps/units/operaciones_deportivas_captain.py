from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.deportivo_teniente import get_deportivo_lieutenant_graph
from .platoons.comunicacion_experiencia_teniente import get_comunicacion_experiencia_lieutenant_graph
from .platoons.gamificacion_teniente import get_gamificacion_lieutenant_graph

class PlatoonTask(BaseModel):
    task_description: str = Field(description="La descripción detallada de la misión para el Teniente.")
    responsible_lieutenant: str = Field(
        description="El Teniente especialista. Debe ser: 'Deportivo', 'ComunicacionExperiencia', 'Gamificacion'."
    )

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask] = Field(description="La lista de misiones para los Tenientes.")

class OperacionesDeportivasCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

async def create_platoon_plan(state: OperacionesDeportivasCaptainState, llm: Any) -> OperacionesDeportivasCaptainState:
    print("--- 🧠 CAP. OPERACIONES DEPORTIVAS: Creando Plan de Pelotón... ---")
    structured_llm = llm.with_structured_output(PlatoonPlan)
    prompt = f"""
    Eres un Capitán de Operaciones Deportivas. Tu Coronel te ha dado una orden.
    Descompónla en un plan detallado, asignando cada misión a tu Teniente especialista.
    Tenientes bajo tu mando:
    - 'Deportivo': Comanda entrenamientos, inscripciones, asistencia, reservas y entrenadores.
    - 'ComunicacionExperiencia': Dirige notificaciones, mensajería, traducciones y UX.
    - 'Gamificacion': Orquesta el sistema de puntos, medallas y rankings.
    Analiza la orden y genera el plan en formato JSON: "{state['coronel_order']}"
    """
    try:
        plan = await structured_llm.ainvoke(prompt)
        print(f"--- 📝 CAP. OPERACIONES DEPORTIVAS: Plan de Pelotón Generado. Pasos: {len(plan.plan)} ---")
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    except Exception as e:
        state["error"] = f"No se pudo crear un plan de pelotón: {e}"
    return state

def route_to_lieutenant(state: OperacionesDeportivasCaptainState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    next_task = state["task_queue"][0]
    lieutenant_unit = next_task.responsible_lieutenant
    if lieutenant_unit == 'Deportivo':
        return "deportivo_lieutenant"
    if lieutenant_unit == 'ComunicacionExperiencia':
        return "comunicacion_lieutenant"
    if lieutenant_unit == 'Gamificacion':
        return "gamificacion_lieutenant"
    state["task_queue"].pop(0)
    return "route_to_lieutenant"


async def compile_final_report(state: OperacionesDeportivasCaptainState) -> OperacionesDeportivasCaptainState:
    print("--- 📄 CAP. OPERACIONES DEPORTIVAS: Compilando Informe Táctico para el Coronel... ---")
    if state.get("error"):
        report_body = f"Misión fallida. Razón: {state['error']}"
    else:
        report_body = "\n".join([f"- Reporte del Tte. de {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Misión de Operaciones Deportivas completada. Resumen:\n{report_body}"
    return state

def get_operaciones_deportivas_captain_graph(llm: Any):
    deportivo_agent = get_deportivo_lieutenant_graph(llm)
    comunicacion_agent = get_comunicacion_experiencia_lieutenant_graph(llm)
    gamificacion_agent = get_gamificacion_lieutenant_graph(llm)

    async def deportivo_node(state: OperacionesDeportivasCaptainState) -> OperacionesDeportivasCaptainState:
        mission = state["task_queue"].pop(0)
        print(f"--- 🔽 CAPITÁN: Delegando a TTE. DEPORTIVO -> '{mission.task_description}' ---")
        result = await deportivo_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Deportivo", "report": result.get("final_report", "Sin reporte.")})
        return state

    async def comunicacion_node(state: OperacionesDeportivasCaptainState) -> OperacionesDeportivasCaptainState:
        mission = state["task_queue"].pop(0)
        print(f"--- 🔽 CAPITÁN: Delegando a TTE. COMUNICACIÓN -> '{mission.task_description}' ---")
        result = await comunicacion_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Comunicación y Exp.", "report": result.get("final_report", "Sin reporte.")})
        return state

    async def gamificacion_node(state: OperacionesDeportivasCaptainState) -> OperacionesDeportivasCaptainState:
        mission = state["task_queue"].pop(0)
        print(f"--- 🔽 CAPITÁN: Delegando a TTE. GAMIFICACIÓN -> '{mission.task_description}' ---")
        result = await gamificacion_agent.ainvoke({"captain_order": mission.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Gamificación", "report": result.get("final_report", "Sin reporte.")})
        return state

    workflow = StateGraph(OperacionesDeportivasCaptainState)

    planner_node = lambda state: create_platoon_plan(state, llm)

    workflow.add_node("planner", planner_node)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("deportivo_lieutenant", deportivo_node)
    workflow.add_node("comunicacion_lieutenant", comunicacion_node)
    workflow.add_node("gamificacion_lieutenant", gamificacion_node)
    workflow.add_node("compiler", compile_final_report)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router",
        route_to_lieutenant,
        {
            "deportivo_lieutenant": "deportivo_lieutenant",
            "comunicacion_lieutenant": "comunicacion_lieutenant",
            "gamificacion_lieutenant": "gamificacion_lieutenant",
            "compile_report": "compiler",
            "route_to_lieutenant": "router"
        }
    )
    workflow.add_edge("deportivo_lieutenant", "router")
    workflow.add_edge("comunicacion_lieutenant", "router")
    workflow.add_edge("gamificacion_lieutenant", "router")
    workflow.add_edge("compiler", END)
    return workflow.compile().with_types(input_type=OperacionesDeportivasCaptainState)
