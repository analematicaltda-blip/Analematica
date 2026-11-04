from typing import TypedDict, List, Any
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from .platoons.ciberdefensa_teniente import get_ciberdefensa_lieutenant_graph
from .platoons.intrusiones_teniente import get_intrusiones_lieutenant_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class CiberdefensaCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_ciberdefensa_captain_graph(llm: Any = None):
    t1_agent = get_ciberdefensa_lieutenant_graph(llm)
    t2_agent = get_intrusiones_lieutenant_graph(llm)

    def create_platoon_plan(state: CiberdefensaCaptainState) -> CiberdefensaCaptainState:
        order = state.get("coronel_order", "")
        plan = PlatoonPlan(plan=[
            PlatoonTask(task_description=f"Mitigación DDoS y WAF: {order}", responsible_lieutenant="ciberdefensa"),
            PlatoonTask(task_description=f"Hardening y Vulnerabilidades: {order}", responsible_lieutenant="intrusiones")
        ])
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: CiberdefensaCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "ciberdefensa":
            return "t1_node"
        return "t2_node"

    async def t1_node(state: CiberdefensaCaptainState) -> CiberdefensaCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Pelotón Ciberdefensa", "report": res.get("final_report", "OK")})
        return state

    async def t2_node(state: CiberdefensaCaptainState) -> CiberdefensaCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Pelotón Hardening", "report": res.get("final_report", "OK")})
        return state

    def compile_report(state: CiberdefensaCaptainState) -> CiberdefensaCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte Compañía Ciberdefensa y Ataques:\n{reps}"
        return state

    workflow = StateGraph(CiberdefensaCaptainState)
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
