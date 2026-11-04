from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from .squads.tenancy_sargento import get_tenancy_sargento_graph

class TenancyLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

def get_tenancy_lieutenant_graph(llm: Any = None):
    sq_builder = get_tenancy_sargento_graph(llm)

    async def execute_platoon(state: TenancyLieutenantState) -> TenancyLieutenantState:
        order = state.get("captain_order", "Misión de Tenencia Multi-Inquilino")
        try:
            s1 = sq_builder(state)
            r1 = await s1.ainvoke({"teniente_order": order, "app_context": state.get("app_context")})
            rep1 = r1.get("final_report", {}).get("text", "Misión Escuadra Tenancy OK.") if isinstance(r1.get("final_report"), dict) else str(r1.get("final_report", "OK"))
            state["final_report"] = f"Pelotón Gobernanza Inquilinos:\n  - {rep1}"
        except Exception as e:
            state["error"] = str(e)
            state["final_report"] = f"Fallo en Pelotón Tenancy: {e}"
        return state

    workflow = StateGraph(TenancyLieutenantState)
    workflow.add_node("execute_platoon", execute_platoon)
    workflow.set_entry_point("execute_platoon")
    workflow.add_edge("execute_platoon", END)
    return workflow.compile()
