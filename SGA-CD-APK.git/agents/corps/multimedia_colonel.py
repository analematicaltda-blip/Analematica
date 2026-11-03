from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .units.produccion_video_captain import get_produccion_video_graph
from .units.diseno_visual_captain import get_diseno_visual_graph
from .units.almacen_assets_captain import get_almacen_assets_graph

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str # 'produccion_video', 'diseno_visual', 'almacen_assets'

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class MultimediaColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict
    error: str | None

def get_multimedia_colonel_graph(llm: Any = None):
    c1_agent = get_produccion_video_graph(llm)
    c2_agent = get_diseno_visual_graph(llm)
    c3_agent = get_almacen_assets_graph(llm)

    def create_tactical_plan(state: MultimediaColonelState) -> MultimediaColonelState:
        order = state.get("general_order", "")
        print(f"--- ⚔️ CORONEL MultimediaColonel: Desplegando plan táctico de división -> '{order[:40]}...' ---")
        tasks = [
            TacticalTask(task_description=f"Operación Fase A: {order}", responsible_captain="produccion_video"),
            TacticalTask(task_description=f"Operación Fase B: {order}", responsible_captain="diseno_visual"),
            TacticalTask(task_description=f"Operación Fase C: {order}", responsible_captain="almacen_assets")
        ]
        plan = TacticalPlan(plan=tasks)
        state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_captain(state: MultimediaColonelState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_captain
        if nxt == "produccion_video": return "c1_node"
        elif nxt == "diseno_visual": return "c2_node"
        return "c3_node"

    async def c1_node(state: MultimediaColonelState) -> MultimediaColonelState:
        m = state["task_queue"].pop(0)
        res = await c1_agent.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "ProduccionVideoCaptain", "report": res.get("final_report", "Completado")})
        return state

    async def c2_node(state: MultimediaColonelState) -> MultimediaColonelState:
        m = state["task_queue"].pop(0)
        res = await c2_agent.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "DisenoVisualCaptain", "report": res.get("final_report", "Completado")})
        return state

    async def c3_node(state: MultimediaColonelState) -> MultimediaColonelState:
        m = state["task_queue"].pop(0)
        res = await c3_agent.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "AlmacenAssetsCaptain", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: MultimediaColonelState) -> MultimediaColonelState:
        reps = "\n".join([f"- {m['captain']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = {
            "text": f"Misión de División MultimediaColonel cumplida exitosamente con mando segregado:\n{reps}",
            "artifacts": []
        }
        return state

    workflow = StateGraph(MultimediaColonelState)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("c1_node", c1_node)
    workflow.add_node("c2_node", c2_node)
    workflow.add_node("c3_node", c3_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_captain)
    workflow.add_conditional_edges("c1_node", route_to_captain)
    workflow.add_conditional_edges("c2_node", route_to_captain)
    workflow.add_conditional_edges("c3_node", route_to_captain)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
