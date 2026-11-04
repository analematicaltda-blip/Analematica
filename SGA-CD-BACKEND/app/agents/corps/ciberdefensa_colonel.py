from typing import TypedDict, List, Any
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from .units.ciberdefensa_captain import get_ciberdefensa_captain_graph
from .units.security_vault_captain import get_security_vault_captain_graph

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class CiberdefensaColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict
    error: str | None

def get_ciberdefensa_colonel_graph(llm: Any = None):
    c1_ciber = get_ciberdefensa_captain_graph(llm)
    c2_vault = get_security_vault_captain_graph(llm)

    def create_tactical_plan(state: CiberdefensaColonelState) -> CiberdefensaColonelState:
        order = state.get("general_order", "")
        print(f"--- 🛡️ CORONEL Ciberdefensa: Trazando despliegue militar de seguridad y mitigación de ataques -> '{order[:40]}...' ---")
        tasks = [
            TacticalTask(task_description=f"Operación Ciberdefensa y Anti-Ataques: {order}", responsible_captain="ciberdefensa"),
            TacticalTask(task_description=f"Operación Bóveda y Auditoría STAR: {order}", responsible_captain="vault")
        ]
        plan = TacticalPlan(plan=tasks)
        state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_captain(state: CiberdefensaColonelState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_captain
        if nxt == "ciberdefensa":
            return "c1_node"
        return "c2_node"

    async def c1_node(state: CiberdefensaColonelState) -> CiberdefensaColonelState:
        m = state["task_queue"].pop(0)
        res = await c1_ciber.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "CiberdefensaCaptain", "report": res.get("final_report", "OK")})
        return state

    async def c2_node(state: CiberdefensaColonelState) -> CiberdefensaColonelState:
        m = state["task_queue"].pop(0)
        res = await c2_vault.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "SecurityVaultCaptain", "report": res.get("final_report", "OK")})
        return state

    def compile_report(state: CiberdefensaColonelState) -> CiberdefensaColonelState:
        reps = "\n".join([f"- {m['captain']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = {
            "text": f"Misión de División Ciberdefensa cumplida exitosamente:\n{reps}",
            "artifacts": []
        }
        return state

    workflow = StateGraph(CiberdefensaColonelState)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("c1_node", c1_node)
    workflow.add_node("c2_node", c2_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_captain)
    workflow.add_conditional_edges("c1_node", route_to_captain)
    workflow.add_conditional_edges("c2_node", route_to_captain)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
