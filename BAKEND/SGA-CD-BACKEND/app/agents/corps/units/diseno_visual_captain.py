from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.posts_banners_teniente import get_posts_banners_graph
from .platoons.carruseles_secuencias_teniente import get_carruseles_secuencias_graph
from .platoons.branding_identidad_teniente import get_branding_identidad_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str # 'posts_banners', 'carruseles_secuencias', 'branding_identidad'

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class DisenoVisualCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_diseno_visual_graph(llm: Any = None):
    t1_agent = get_posts_banners_graph(llm)
    t2_agent = get_carruseles_secuencias_graph(llm)
    t3_agent = get_branding_identidad_graph(llm)

    def create_platoon_plan(state: DisenoVisualCaptainState) -> DisenoVisualCaptainState:
        order = state.get("coronel_order", "")
        print(f"--- 🎖️ CAPITÁN DisenoVisualCaptain: Creando plan táctico de compañía para -> '{order[:40]}...' ---")
        tasks = [
            PlatoonTask(task_description=f"Fase 1: {order}", responsible_lieutenant="posts_banners"),
            PlatoonTask(task_description=f"Fase 2: {order}", responsible_lieutenant="carruseles_secuencias"),
            PlatoonTask(task_description=f"Fase 3: {order}", responsible_lieutenant="branding_identidad")
        ]
        plan = PlatoonPlan(plan=tasks)
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: DisenoVisualCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "posts_banners": return "t1_node"
        elif nxt == "carruseles_secuencias": return "t2_node"
        return "t3_node"

    async def t1_node(state: DisenoVisualCaptainState) -> DisenoVisualCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "PostsBannersLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t2_node(state: DisenoVisualCaptainState) -> DisenoVisualCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "CarruselesSecuenciasLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t3_node(state: DisenoVisualCaptainState) -> DisenoVisualCaptainState:
        m = state["task_queue"].pop(0)
        res = await t3_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "BrandingIdentidadLieutenant", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: DisenoVisualCaptainState) -> DisenoVisualCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte de Compañía DisenoVisualCaptain:\n{reps}"
        return state

    workflow = StateGraph(DisenoVisualCaptainState)
    workflow.add_node("create_plan", create_platoon_plan)
    workflow.add_node("t1_node", t1_node)
    workflow.add_node("t2_node", t2_node)
    workflow.add_node("t3_node", t3_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_lieutenant)
    workflow.add_conditional_edges("t1_node", route_to_lieutenant)
    workflow.add_conditional_edges("t2_node", route_to_lieutenant)
    workflow.add_conditional_edges("t3_node", route_to_lieutenant)
    workflow.add_edge("compile_report", END)

    return workflow.compile()
