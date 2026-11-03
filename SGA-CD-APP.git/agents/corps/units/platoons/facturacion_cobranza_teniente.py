from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from .squads.emision_facturas_sargento import get_emision_facturas_graph
from .squads.pasarelas_pago_sargento import get_pasarelas_pago_graph

class FacturacionCobranzaLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

def get_facturacion_cobranza_graph(llm: Any = None):
    sq1_builder = get_emision_facturas_graph(llm)
    sq2_builder = get_pasarelas_pago_graph(llm)

    async def execute_platoon(state: FacturacionCobranzaLieutenantState) -> FacturacionCobranzaLieutenantState:
        order = state.get("captain_order", "Misión de Pelotón")
        print(f"--- 🎖️ TENIENTE FacturacionCobranzaLieutenant: Recibida orden -> '{order[:40]}...' ---")
        try:
            # Delegación a Sargentos de escuadra
            s1 = sq1_builder(state)
            r1 = await s1.ainvoke({"teniente_order": order, "app_context": state.get("app_context")})
            rep1 = r1.get("final_report", {}).get("text", "Misión escuadra 1 cumplida.") if isinstance(r1.get("final_report"), dict) else str(r1.get("final_report", "Misión 1 OK"))

            s2 = sq2_builder(state)
            r2 = await s2.ainvoke({"teniente_order": order, "app_context": state.get("app_context")})
            rep2 = r2.get("final_report", {}).get("text", "Misión escuadra 2 cumplida.") if isinstance(r2.get("final_report"), dict) else str(r2.get("final_report", "Misión 2 OK"))

            state["final_report"] = f"Pelotón FacturacionCobranzaLieutenant:\n- Escuadra EmisionFacturasSargento: {rep1}\n- Escuadra PasarelasPagoSargento: {rep2}"
        except Exception as e:
            state["error"] = str(e)
            state["final_report"] = f"Fallo en Pelotón FacturacionCobranzaLieutenant: {e}"
        return state

    workflow = StateGraph(FacturacionCobranzaLieutenantState)
    workflow.add_node("execute_platoon", execute_platoon)
    workflow.set_entry_point("execute_platoon")
    workflow.add_edge("execute_platoon", END)
    return workflow.compile()
