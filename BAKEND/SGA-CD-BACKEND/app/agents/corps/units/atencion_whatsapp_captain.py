from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.whatsapp_core_teniente import get_whatsapp_core_graph
from .platoons.meta_dms_teniente import get_meta_dms_graph
from .platoons.faq_escalacion_teniente import get_faq_escalacion_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str # 'whatsapp_core', 'meta_dms', 'faq_escalacion'

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class AtencionWhatsappCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_atencion_whatsapp_graph(llm: Any = None):
    t1_agent = get_whatsapp_core_graph(llm)
    t2_agent = get_meta_dms_graph(llm)
    t3_agent = get_faq_escalacion_graph(llm)

    def create_platoon_plan(state: AtencionWhatsappCaptainState) -> AtencionWhatsappCaptainState:
        order = state.get("coronel_order", "")
        print(f"--- 🎖️ CAPITÁN AtencionWhatsappCaptain: Creando plan táctico de compañía para -> '{order[:40]}...' ---")
        tasks = [
            PlatoonTask(task_description=f"Fase 1: {order}", responsible_lieutenant="whatsapp_core"),
            PlatoonTask(task_description=f"Fase 2: {order}", responsible_lieutenant="meta_dms"),
            PlatoonTask(task_description=f"Fase 3: {order}", responsible_lieutenant="faq_escalacion")
        ]
        plan = PlatoonPlan(plan=tasks)
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: AtencionWhatsappCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "whatsapp_core": return "t1_node"
        elif nxt == "meta_dms": return "t2_node"
        return "t3_node"

    async def t1_node(state: AtencionWhatsappCaptainState) -> AtencionWhatsappCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "WhatsappCoreLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t2_node(state: AtencionWhatsappCaptainState) -> AtencionWhatsappCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "MetaDmsLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t3_node(state: AtencionWhatsappCaptainState) -> AtencionWhatsappCaptainState:
        m = state["task_queue"].pop(0)
        res = await t3_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "FaqEscalacionLieutenant", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: AtencionWhatsappCaptainState) -> AtencionWhatsappCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte de Compañía AtencionWhatsappCaptain:\n{reps}"
        return state

    workflow = StateGraph(AtencionWhatsappCaptainState)
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
