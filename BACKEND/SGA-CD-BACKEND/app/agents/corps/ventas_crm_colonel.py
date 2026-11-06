from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from app.tools.herramientas_crm_completo import (
    tool_lead_capturar_landing,
    tool_score_interes_deporte,
    tool_pipeline_etapa_propuesta,
    tool_cotizar_plan_mensual
)

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class VentasCrmColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict
    error: str | None

def create_tactical_plan(state: VentasCrmColonelState, llm: Any = None) -> VentasCrmColonelState:
    print("--- [CORONEL VENTAS Y CRM] Desplegando plan directo y selectivo... ---")
    tasks = [
        TacticalTask(task_description="Capturar lead y calificar interes institucional", responsible_captain="Prospeccion"),
        TacticalTask(task_description="Auditar pipeline y generar cotizacion corporativa", responsible_captain="Negociacion")
    ]
    plan = TacticalPlan(plan=tasks)
    state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
    return state

def route_to_captain(state: VentasCrmColonelState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    nxt = state["task_queue"][0].responsible_captain
    if nxt == "Prospeccion":
        return "prospeccion_node"
    return "negociacion_node"

def prospeccion_node(state: VentasCrmColonelState) -> VentasCrmColonelState:
    mission = state["task_queue"].pop(0)
    res1 = tool_lead_capturar_landing.invoke({"instruccion": state["general_order"]})
    res2 = tool_score_interes_deporte.invoke({"instruccion": "Mariana Gomez - Calificacion Alta"})
    state["completed_missions"].append({"captain": "Capitan de Prospeccion", "report": f"{res1} | {res2}"})
    return state

def negociacion_node(state: VentasCrmColonelState) -> VentasCrmColonelState:
    mission = state["task_queue"].pop(0)
    res1 = tool_pipeline_etapa_propuesta.invoke({"instruccion": state["general_order"]})
    res2 = tool_cotizar_plan_mensual.invoke({"instruccion": "Plan Corporativo Institucional SGA-CD"})
    state["completed_missions"].append({"captain": "Capitan de Negociacion", "report": f"{res1} | {res2}"})
    return state

def compile_report(state: VentasCrmColonelState) -> VentasCrmColonelState:
    reps = "\n".join([f"- {m['captain']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = {
        "text": f"Mision de la Division de Ventas y CRM cumplida exitosamente:\n{reps}",
        "artifacts": []
    }
    return state

def get_ventas_crm_colonel_graph(llm: Any = None):
    workflow = StateGraph(VentasCrmColonelState)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("prospeccion_node", prospeccion_node)
    workflow.add_node("negociacion_node", negociacion_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_captain)
    workflow.add_conditional_edges("prospeccion_node", route_to_captain)
    workflow.add_conditional_edges("negociacion_node", route_to_captain)
    workflow.add_edge("compile_report", END)

    return workflow.compile()