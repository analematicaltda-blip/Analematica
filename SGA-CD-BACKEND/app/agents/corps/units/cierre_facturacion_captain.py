from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.matricula_digital_teniente import get_matricula_digital_graph
from .platoons.facturacion_cobranza_teniente import get_facturacion_cobranza_graph
from .platoons.retencion_churn_teniente import get_retencion_churn_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str # 'matricula_digital', 'facturacion_cobranza', 'retencion_churn'

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class CierreFacturacionCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_cierre_facturacion_graph(llm: Any = None):
    t1_agent = get_matricula_digital_graph(llm)
    t2_agent = get_facturacion_cobranza_graph(llm)
    t3_agent = get_retencion_churn_graph(llm)

    def create_platoon_plan(state: CierreFacturacionCaptainState) -> CierreFacturacionCaptainState:
        order = state.get("coronel_order", "")
        print(f"--- 🎖️ CAPITÁN CierreFacturacionCaptain: Creando plan táctico de compañía para -> '{order[:40]}...' ---")
        tasks = [
            PlatoonTask(task_description=f"Fase 1: {order}", responsible_lieutenant="matricula_digital"),
            PlatoonTask(task_description=f"Fase 2: {order}", responsible_lieutenant="facturacion_cobranza"),
            PlatoonTask(task_description=f"Fase 3: {order}", responsible_lieutenant="retencion_churn")
        ]
        plan = PlatoonPlan(plan=tasks)
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: CierreFacturacionCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "matricula_digital": return "t1_node"
        elif nxt == "facturacion_cobranza": return "t2_node"
        return "t3_node"

    async def t1_node(state: CierreFacturacionCaptainState) -> CierreFacturacionCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "MatriculaDigitalLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t2_node(state: CierreFacturacionCaptainState) -> CierreFacturacionCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "FacturacionCobranzaLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t3_node(state: CierreFacturacionCaptainState) -> CierreFacturacionCaptainState:
        m = state["task_queue"].pop(0)
        res = await t3_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "RetencionChurnLieutenant", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: CierreFacturacionCaptainState) -> CierreFacturacionCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte de Compañía CierreFacturacionCaptain:\n{reps}"
        return state

    workflow = StateGraph(CierreFacturacionCaptainState)
    workflow.add_node("create_plan", create_platoon_plan)
    workflow.add_node("t1_node", t1_node)
    workflow.add_node("t2_node", t2_node)
    workflow.add_node("t3_node", t3_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_lieutenant)
    workflow.add_conditional_edges("t1_node", route_to_lieutenant)
    workflow.add_conditional_edges("t2_node", route_to_lieutenant)
    workflow.add_conditional_edges("t3_node", route_to_lieutenant)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
