from typing import TypedDict, Any, List
from langgraph.graph import StateGraph, END, START
from pydantic import BaseModel, Field

from .squads.comunicaciones_sargento import get_comunicaciones_sargento_graph
from .squads.experiencia_sargento import get_experiencia_sargento_graph

class SargentoMission(BaseModel):
    task_description: str
    responsible_sargento: str = Field(description="Debe ser 'Comunicaciones' o 'Experiencia'.")

class MissionPlan(BaseModel):
    plan: List[SargentoMission]

class CommsExpLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    mission_plan: MissionPlan | None
    task_queue: List[SargentoMission]
    completed_missions: list
    final_report: str
    error: str | None

async def planner_node(state: CommsExpLieutenantState, llm: Any) -> CommsExpLieutenantState:
    """El cerebro del Teniente: decide qué Sargento es necesario para cada parte de la misión."""
    print("--- 🤔 TTE. COMMS/EXP: Creando Plan de Pelotón... ---")
    planner = llm.with_structured_output(MissionPlan)
    prompt = f"""
    Eres un Teniente de Comunicación y Experiencia. Descompón la orden del Capitán en misiones para tus Sargentos.
    Sargentos Disponibles:
    - 'Comunicaciones': Experto en notificaciones, recordatorios y mensajería.
    - 'Experiencia': Experto en traducciones (MILA), accesibilidad y UX.
    Orden: "{state['captain_order']}"
    """
    try:
        plan = await planner.ainvoke(prompt)
        state.update({"mission_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": []})
    except Exception as e:
        state["error"] = f"Error al planificar para el Teniente de Comms/Exp: {e}"
    return state

def router_node(state: CommsExpLieutenantState):
    """Enruta al Sargento correcto o finaliza."""
    if state.get("error") or not state.get("task_queue"):
        return "compiler"
    sargento = state["task_queue"][0].responsible_sargento
    if sargento == "Comunicaciones":
        return "comunicaciones_sargento"
    if sargento == "Experiencia":
        return "experiencia_sargento"
    state["task_queue"].pop(0)
    return "router"


async def compiler_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
    if state.get("error"):
        state["final_report"] = state["error"]
    else:
        state["final_report"] = "Misión completada. Resumen: " + " | ".join(state["completed_missions"])
    return state

def get_comunicacion_experiencia_lieutenant_graph(llm: Any):
    comunicaciones_sargento_builder = get_comunicaciones_sargento_graph(llm)
    experiencia_sargento_builder = get_experiencia_sargento_graph(llm)

    async def comunicaciones_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
        mission = state["task_queue"].pop(0)
        sargento_agent = comunicaciones_sargento_builder(state)
        result = await sargento_agent.ainvoke({"teniente_order": mission.task_description, "app_context": state["app_context"]})
        state["completed_missions"].append(f"Reporte del Sgto. Comunicaciones: {result.get('final_report', 'Sin reporte.')}")
        return state

    async def experiencia_node(state: CommsExpLieutenantState) -> CommsExpLieutenantState:
        mission = state["task_queue"].pop(0)
        sargento_agent = experiencia_sargento_builder(state)
        result = await sargento_agent.ainvoke({"teniente_order": mission.task_description, "app_context": state["app_context"]})
        state["completed_missions"].append(f"Reporte del Sgto. Experiencia: {result.get('final_report', 'Sin reporte.')}")
        return state

    workflow = StateGraph(CommsExpLieutenantState)

    planner_node_with_llm = lambda state: planner_node(state, llm)

    workflow.add_node("planner", planner_node_with_llm)
    workflow.add_node("router", lambda s: s)
    workflow.add_node("comunicaciones_sargento", comunicaciones_node)
    workflow.add_node("experiencia_sargento", experiencia_node)
    workflow.add_node("compiler", compiler_node)
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "router")
    workflow.add_conditional_edges(
        "router",
        router_node,
        {
            "comunicaciones_sargento": "comunicaciones_sargento",
            "experiencia_sargento": "experiencia_sargento",
            "compiler": "compiler",
            "router": "router"
        }
    )
    workflow.add_edge("comunicaciones_sargento", "router")
    workflow.add_edge("experiencia_sargento", "router")
    workflow.add_edge("compiler", END)
    return workflow.compile().with_types(input_type=CommsExpLieutenantState)
