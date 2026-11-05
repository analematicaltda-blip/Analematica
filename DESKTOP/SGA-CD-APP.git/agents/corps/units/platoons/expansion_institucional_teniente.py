from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from .squads.institucional_sargento import get_institucional_sargento_graph

class ExpansionLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

async def delegate_to_sargento(state: ExpansionLieutenantState, institucional_sargento_builder: callable) -> ExpansionLieutenantState:
    """Delega la misión de gestión institucional completa a su Sargento especialista."""
    order = state['captain_order']
    print(f"--- 🫡 TENIENTE DE EXPANSIÓN: Recibida orden. Delegando misión al Sargento -> '{order}' ---")
    try:
        sargento_agent = institucional_sargento_builder(state)
        result = await sargento_agent.ainvoke({
            "teniente_order": order,
            "app_context": state['app_context']
        })
        report_from_sargento = result.get("final_report", "El Sargento completó la misión sin reporte.")
        state["final_report"] = report_from_sargento
        print(f"--- ✔️ TENIENTE DE EXPANSIÓN: Sargento reporta misión cumplida. ---")
    except Exception as e:
        error_message = f"Misión de Expansión fallida. El Sargento reporta un error: {e}"
        print(f"--- ❌ TENIENTE DE EXPANSIÓN: {error_message} ---")
        state["error"] = error_message
    return state

async def compile_report(state: ExpansionLieutenantState) -> ExpansionLieutenantState:
    """Prepara el informe final para el Capitán."""
    if state.get("error"):
        state["final_report"] = state["error"]
    print("--- 📄 TENIENTE DE EXPANSIÓN: Informe para el Capitán de Estrategia listo. ---")
    return state

def get_expansion_institucional_lieutenant_graph(llm: Any):
    """Construye el agente LangGraph para el Teniente de Expansión Institucional."""
    institucional_sargento_builder = get_institucional_sargento_graph(llm)

    delegate_node = lambda state: delegate_to_sargento(state, institucional_sargento_builder)

    workflow = StateGraph(ExpansionLieutenantState)
    workflow.add_node("delegate_mission_to_sargento", delegate_node)
    workflow.add_node("compile_final_report", compile_report)
    workflow.set_entry_point("delegate_mission_to_sargento")
    workflow.add_edge("delegate_mission_to_sargento", "compile_final_report")
    workflow.add_edge("compile_final_report", END)
    return workflow.compile().with_types(input_type=ExpansionLieutenantState)
