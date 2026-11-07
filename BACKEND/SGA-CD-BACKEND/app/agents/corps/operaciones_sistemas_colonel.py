from typing import TypedDict, List, Any
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from .units.operaciones_sistemas_captain import get_operaciones_sistemas_captain_graph

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class OperacionesSistemasColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict
    error: str | None

def get_operaciones_sistemas_colonel_graph(llm: Any = None):
    c1_ops = get_operaciones_sistemas_captain_graph(llm)

    def create_tactical_plan(state: OperacionesSistemasColonelState) -> OperacionesSistemasColonelState:
        order = state.get("general_order", "")
        print(f"--- ⚙️ CORONEL Operaciones Sistemas: Trazando despliegue de SEO, Legal y Mantenimiento -> '{order[:40]}...' ---")
        tasks = [
            TacticalTask(task_description=f"Operación Sistemas, Legal y SEO: {order}", responsible_captain="operaciones_sistemas")
        ]
        plan = TacticalPlan(plan=tasks)
        state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    async def execute_task(state: OperacionesSistemasColonelState) -> OperacionesSistemasColonelState:
        if not state["task_queue"]:
            return state
        m = state["task_queue"].pop(0)
        res = await c1_ops.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "OperacionesSistemasCaptain", "report": res.get("final_report", "OK")})
        state["final_report"] = {
            "text": f"Misión de División Operaciones Sistemas, Legal y SEO cumplida:\n- {res.get('final_report', 'OK')}",
            "artifacts": []
        }
        return state

    workflow = StateGraph(OperacionesSistemasColonelState)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("execute_task", execute_task)
    workflow.set_entry_point("create_plan")
    workflow.add_edge("create_plan", "execute_task")
    workflow.add_edge("execute_task", END)

    return workflow.compile()
