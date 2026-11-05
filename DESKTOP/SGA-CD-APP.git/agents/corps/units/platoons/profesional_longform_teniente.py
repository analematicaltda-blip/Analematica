from typing import TypedDict, Any
from langgraph.graph import StateGraph, END, START
from .squads.youtube_upload_sargento import get_youtube_upload_graph
from .squads.meta_linkedin_pub_sargento import get_meta_linkedin_pub_graph

class ProfesionalLongformLieutenantState(TypedDict):
    captain_order: str
    app_context: Any
    final_report: str
    error: str | None

def get_profesional_longform_graph(llm: Any = None):
    sq1_builder = get_youtube_upload_graph(llm)
    sq2_builder = get_meta_linkedin_pub_graph(llm)

    async def execute_platoon(state: ProfesionalLongformLieutenantState) -> ProfesionalLongformLieutenantState:
        order = state.get("captain_order", "Misión de Pelotón")
        print(f"--- 🎖️ TENIENTE ProfesionalLongformLieutenant: Recibida orden -> '{order[:40]}...' ---")
        try:
            # Delegación a Sargentos de escuadra
            s1 = sq1_builder(state)
            r1 = await s1.ainvoke({"teniente_order": order, "app_context": state.get("app_context")})
            rep1 = r1.get("final_report", {}).get("text", "Misión escuadra 1 cumplida.") if isinstance(r1.get("final_report"), dict) else str(r1.get("final_report", "Misión 1 OK"))

            s2 = sq2_builder(state)
            r2 = await s2.ainvoke({"teniente_order": order, "app_context": state.get("app_context")})
            rep2 = r2.get("final_report", {}).get("text", "Misión escuadra 2 cumplida.") if isinstance(r2.get("final_report"), dict) else str(r2.get("final_report", "Misión 2 OK"))

            state["final_report"] = f"Pelotón ProfesionalLongformLieutenant:\n- Escuadra YoutubeUploadSargento: {rep1}\n- Escuadra MetaLinkedinPubSargento: {rep2}"
        except Exception as e:
            state["error"] = str(e)
            state["final_report"] = f"Fallo en Pelotón ProfesionalLongformLieutenant: {e}"
        return state

    workflow = StateGraph(ProfesionalLongformLieutenantState)
    workflow.add_node("execute_platoon", execute_platoon)
    workflow.set_entry_point("execute_platoon")
    workflow.add_edge("execute_platoon", END)
    return workflow.compile()
