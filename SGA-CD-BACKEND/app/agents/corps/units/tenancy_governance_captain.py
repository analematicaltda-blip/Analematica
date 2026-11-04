from typing import TypedDict, List, Any
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from .platoons.tenancy_teniente import get_tenancy_lieutenant_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class TenancyCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_tenancy_governance_captain_graph(llm: Any = None):
    t_agent = get_tenancy_lieutenant_graph(llm)

    def create_platoon_plan(state: TenancyCaptainState) -> TenancyCaptainState:
        order = state.get("coronel_order", "")
        plan = PlatoonPlan(plan=[
            PlatoonTask(task_description=f"Gobernanza inquilinos y roles: {order}", responsible_lieutenant="tenancy")
        ])
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    async def execute_task(state: TenancyCaptainState) -> TenancyCaptainState:
        if not state["task_queue"]:
            return state
        m = state["task_queue"].pop(0)
        res = await t_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "Pelotón Tenancy", "report": res.get("final_report", "OK")})
        state["final_report"] = f"Compañía Gobernanza Inquilinos: {res.get('final_report', 'OK')}"
        return state

    workflow = StateGraph(TenancyCaptainState)
    workflow.add_node("create_plan", create_platoon_plan)
    workflow.add_node("execute_task", execute_task)
    workflow.set_entry_point("create_plan")
    workflow.add_edge("create_plan", "execute_task")
    workflow.add_edge("execute_task", END)
    return workflow.compile()
