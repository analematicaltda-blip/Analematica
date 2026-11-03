from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from .squads.gamificacion_sargento import get_gamificacion_sargento_graph

class GamificacionLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

async def delegate_to_sargento(state: GamificacionLieutenantState, gamificacion_sargento_builder: callable) -> GamificacionLieutenantState:
    """Delega la misión completa al Sargento especialista en gamificación."""
    order = state['captain_order']
    print(f"--- 🫡 TENIENTE DE GAMIFICACIÓN: Recibida orden. Delegando misión al Sargento -> '{order}' ---")
    try:
        sargento_agent = gamificacion_sargento_builder(state)
        result = await sargento_agent.ainvoke({
            "teniente_order": order,
            "app_context": state['app_context']
        })
        report_from_sargento = result.get("final_report", "El Sargento completó la misión sin un reporte detallado.")
        state["final_report"] = report_from_sargento
        print(f"--- ✔️ TENIENTE DE GAMIFICACIÓN: El Sargento reporta misión cumplida. ---")
    except Exception as e:
        error_message = f"Misión fallida bajo el mando del Sargento de Gamificación. Razón: {e}"
        print(f"--- ❌ TENIENTE DE GAMIFICACIÓN: El Sargento reportó un error crítico: {error_message} ---")
        state["error"] = error_message
    return state

async def compile_report(state: GamificacionLieutenantState) -> GamificacionLieutenantState:
    """Prepara el informe final para el Capitán."""
    if state.get("error"):
        state["final_report"] = state["error"]
    print("--- 📄 TENIENTE DE GAMIFICACIÓN: Informe para el Capitán de Operaciones Académicas listo. ---")
    return state

def get_gamificacion_lieutenant_graph(llm: Any):
    """Construye el agente LangGraph para el Teniente de Gamificación."""
    gamificacion_sargento_builder = get_gamificacion_sargento_graph(llm)

    # Curry the builder into the node function
    delegate_node = lambda state: delegate_to_sargento(state, gamificacion_sargento_builder)

    workflow = StateGraph(GamificacionLieutenantState)
    workflow.add_node("delegate_mission_to_sargento", delegate_node)
    workflow.add_node("compile_final_report", compile_report)
    workflow.set_entry_point("delegate_mission_to_sargento")
    workflow.add_edge("delegate_mission_to_sargento", "compile_final_report")
    workflow.add_edge("compile_final_report", END)
    return workflow.compile().with_types(input_type=GamificacionLieutenantState)
