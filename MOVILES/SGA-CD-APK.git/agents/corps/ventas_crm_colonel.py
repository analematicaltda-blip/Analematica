from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .units.prospeccion_leads_captain import get_prospeccion_leads_graph
from .units.negociacion_pipeline_captain import get_negociacion_pipeline_graph
from .units.cierre_facturacion_captain import get_cierre_facturacion_graph

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str # 'prospeccion_leads', 'negociacion_pipeline', 'cierre_facturacion'

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

def get_ventas_crm_colonel_graph(llm: Any = None):
    c1_agent = get_prospeccion_leads_graph(llm)
    c2_agent = get_negociacion_pipeline_graph(llm)
    c3_agent = get_cierre_facturacion_graph(llm)

    def create_tactical_plan(state: VentasCrmColonelState) -> VentasCrmColonelState:
        order = state.get("general_order", "")
        print(f"--- ⚔️ CORONEL VentasCrmColonel: Desplegando plan táctico de división -> '{order[:40]}...' ---")
        tasks = [
            TacticalTask(task_description=f"Operación Fase A: {order}", responsible_captain="prospeccion_leads"),
            TacticalTask(task_description=f"Operación Fase B: {order}", responsible_captain="negociacion_pipeline"),
            TacticalTask(task_description=f"Operación Fase C: {order}", responsible_captain="cierre_facturacion")
        ]
        plan = TacticalPlan(plan=tasks)
        state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_captain(state: VentasCrmColonelState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_captain
        if nxt == "prospeccion_leads": return "c1_node"
        elif nxt == "negociacion_pipeline": return "c2_node"
        return "c3_node"

    async def c1_node(state: VentasCrmColonelState) -> VentasCrmColonelState:
        m = state["task_queue"].pop(0)
        res = await c1_agent.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "ProspeccionLeadsCaptain", "report": res.get("final_report", "Completado")})
        return state

    async def c2_node(state: VentasCrmColonelState) -> VentasCrmColonelState:
        m = state["task_queue"].pop(0)
        res = await c2_agent.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "NegociacionPipelineCaptain", "report": res.get("final_report", "Completado")})
        return state

    async def c3_node(state: VentasCrmColonelState) -> VentasCrmColonelState:
        m = state["task_queue"].pop(0)
        res = await c3_agent.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "CierreFacturacionCaptain", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: VentasCrmColonelState) -> VentasCrmColonelState:
        reps = "\n".join([f"- {m['captain']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = {
            "text": f"Misión de División VentasCrmColonel cumplida exitosamente con mando segregado:\n{reps}",
            "artifacts": []
        }
        return state

    workflow = StateGraph(VentasCrmColonelState)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("c1_node", c1_node)
    workflow.add_node("c2_node", c2_node)
    workflow.add_node("c3_node", c3_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_captain)
    workflow.add_conditional_edges("c1_node", route_to_captain)
    workflow.add_conditional_edges("c2_node", route_to_captain)
    workflow.add_conditional_edges("c3_node", route_to_captain)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
