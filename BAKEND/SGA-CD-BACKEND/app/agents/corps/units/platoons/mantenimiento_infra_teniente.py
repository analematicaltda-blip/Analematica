from typing import TypedDict, Any
from langgraph.graph import StateGraph, END
from .squads.mantenimiento_infra_sargento import get_mantenimiento_infra_sargento_graph

class MantenimientoInfraLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

def get_mantenimiento_infra_lieutenant_graph(llm: Any = None):
    sq_builder = get_mantenimiento_infra_sargento_graph(llm)

    async def execute_platoon(state: MantenimientoInfraLieutenantState) -> MantenimientoInfraLieutenantState:
        order = state.get("captain_order", "Misión de Mantenimiento de BD y Caché")
        try:
            s1 = sq_builder(state)
            r1 = await s1.ainvoke({"teniente_order": order, "app_context": state.get("app_context")})
            rep1 = r1.get("final_report", {}).get("text", "Misión Mantenimiento OK.") if isinstance(r1.get("final_report"), dict) else str(r1.get("final_report", "OK"))
            state["final_report"] = f"Pelotón Mantenimiento e Infraestructura:\n  - {rep1}"
        except Exception as e:
            state["error"] = str(e)
            state["final_report"] = f"Fallo en Pelotón Mantenimiento: {e}"
        return state

    workflow = StateGraph(MantenimientoInfraLieutenantState)
    workflow.add_node("execute_platoon", execute_platoon)
    workflow.set_entry_point("execute_platoon")
    workflow.add_edge("execute_platoon", END)
    return workflow.compile()
