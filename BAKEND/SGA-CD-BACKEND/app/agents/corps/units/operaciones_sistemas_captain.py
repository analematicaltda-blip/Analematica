from typing import TypedDict, List, Any
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from .platoons.seo_legal_teniente import get_seo_legal_lieutenant_graph
from .platoons.mantenimiento_infra_teniente import get_mantenimiento_infra_lieutenant_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class OperacionesSistemasCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_operaciones_sistemas_captain_graph(llm: Any = None):
    t1_agent = get_seo_legal_lieutenant_graph(llm)
    t2_agent = get_mantenimiento_infra_lieutenant_graph(llm)

    def create_platoon_plan(state: OperacionesSistemasCaptainState) -> OperacionesSistemasCaptainState:
        order = state.get("coronel_order", "")
        plan = PlatoonPlan(plan=[
            PlatoonTask(task_description=f"Auditoría SEO y Legaltech: {order}", responsible_lieutenant="seo_legal"),
            PlatoonTask(task_description=f"Mantenimiento Infraestructura: {order}", responsible_lieutenant="mantenimiento")
        ])
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: OperacionesSistemasCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "seo_legal":
            return "t1_node"
        return "t2_node"

    async def t1_node(state: OperacionesSistemasCaptainState) -> OperacionesSistemasCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Pelotón SEO y Legal", "report": res.get("final_report", "OK")})
        return state

    async def t2_node(state: OperacionesSistemasCaptainState) -> OperacionesSistemasCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Pelotón Mantenimiento", "report": res.get("final_report", "OK")})
        return state

    def compile_report(state: OperacionesSistemasCaptainState) -> OperacionesSistemasCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte Compañía Operaciones Sistemas, Legal y SEO:\n{reps}"
        return state

    workflow = StateGraph(OperacionesSistemasCaptainState)
    workflow.add_node("create_plan", create_platoon_plan)
    workflow.add_node("t1_node", t1_node)
    workflow.add_node("t2_node", t2_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_lieutenant)
    workflow.add_conditional_edges("t1_node", route_to_lieutenant)
    workflow.add_conditional_edges("t2_node", route_to_lieutenant)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
