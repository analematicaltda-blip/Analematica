from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.alcance_metricas_teniente import get_alcance_metricas_graph
from .platoons.escucha_sentimiento_teniente import get_escucha_sentimiento_graph
from .platoons.informes_export_teniente import get_informes_export_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str # 'alcance_metricas', 'escucha_sentimiento', 'informes_export'

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class AnaliticaSocialCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_analitica_social_graph(llm: Any = None):
    t1_agent = get_alcance_metricas_graph(llm)
    t2_agent = get_escucha_sentimiento_graph(llm)
    t3_agent = get_informes_export_graph(llm)

    def create_platoon_plan(state: AnaliticaSocialCaptainState) -> AnaliticaSocialCaptainState:
        order = state.get("coronel_order", "")
        print(f"--- 🎖️ CAPITÁN AnaliticaSocialCaptain: Creando plan táctico de compañía para -> '{order[:40]}...' ---")
        tasks = [
            PlatoonTask(task_description=f"Fase 1: {order}", responsible_lieutenant="alcance_metricas"),
            PlatoonTask(task_description=f"Fase 2: {order}", responsible_lieutenant="escucha_sentimiento"),
            PlatoonTask(task_description=f"Fase 3: {order}", responsible_lieutenant="informes_export")
        ]
        plan = PlatoonPlan(plan=tasks)
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: AnaliticaSocialCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "alcance_metricas": return "t1_node"
        elif nxt == "escucha_sentimiento": return "t2_node"
        return "t3_node"

    async def t1_node(state: AnaliticaSocialCaptainState) -> AnaliticaSocialCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "AlcanceMetricasLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t2_node(state: AnaliticaSocialCaptainState) -> AnaliticaSocialCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "EscuchaSentimientoLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t3_node(state: AnaliticaSocialCaptainState) -> AnaliticaSocialCaptainState:
        m = state["task_queue"].pop(0)
        res = await t3_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "InformesExportLieutenant", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: AnaliticaSocialCaptainState) -> AnaliticaSocialCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte de Compañía AnaliticaSocialCaptain:\n{reps}"
        return state

    workflow = StateGraph(AnaliticaSocialCaptainState)
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
