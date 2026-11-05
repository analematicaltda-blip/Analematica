from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from app.agents.corps.units.difusion_multicanal_captain import get_difusion_multicanal_graph
from app.agents.corps.units.atencion_whatsapp_captain import get_atencion_whatsapp_graph
from app.agents.corps.units.analitica_social_captain import get_analitica_social_graph
from app.agents.corps.units.perfil_branding_captain import get_perfil_branding_captain_graph

class TacticalTask(BaseModel):
    task_description: str
    responsible_captain: str # 'Difusion', 'Atencion', 'Analitica', 'PerfilBranding'

class TacticalPlan(BaseModel):
    plan: List[TacticalTask]

class RedesSocialesColonelState(TypedDict):
    general_order: str
    app_context: Any
    tactical_plan: TacticalPlan | None
    task_queue: List[TacticalTask]
    completed_missions: list
    final_report: dict
    error: str | None

def get_redes_sociales_colonel_graph(llm: Any = None):
    c1_difusion = get_difusion_multicanal_graph(llm)
    c2_atencion = get_atencion_whatsapp_graph(llm)
    c3_analitica = get_analitica_social_graph(llm)
    c4_perfil = get_perfil_branding_captain_graph(llm)

    def create_tactical_plan(state: RedesSocialesColonelState) -> RedesSocialesColonelState:
        order = state.get("general_order", "").lower()
        print(f"--- 📡 CORONEL REDES SOCIALES: Evaluando orden y blindando fronteras de operacion... ---")
        tasks = []

        # 1. Detección estricta de Perfil y Branding Corporativo (Cero datos personales)
        if any(w in order for w in ["perfil", "bio", "foto de perfil", "avatar", "portada", "direccion", "datos de empresa"]):
            tasks.append(TacticalTask(task_description=f"Actualizar identidad, logo corporativo y datos de empresa: {state['general_order']}", responsible_captain="PerfilBranding"))

        # 2. Detección de Atención al Cliente / WhatsApp
        if any(w in order for w in ["mensaje", "whatsapp", "responder", "chat", "duda", "pregunta"]):
            tasks.append(TacticalTask(task_description=f"Atender consultas de usuarios y acudientes: {state['general_order']}", responsible_captain="Atencion"))

        # 3. Detección de Publicación Orgánica de Video / Reels / Imágenes (Cero gasto de Ads)
        if any(w in order for w in ["publicar", "difundir", "subir", "reel", "video", "post"]) or not tasks:
            tasks.append(TacticalTask(task_description=f"Difusion organica multicanal sin costo publicitario: {state['general_order']}", responsible_captain="Difusion"))

        # 4. Auditoría y Analítica
        if any(w in order for w in ["metrica", "analitica", "informe", "estadistica"]):
            tasks.append(TacticalTask(task_description=f"Auditar metricas de engagement y audiencia: {state['general_order']}", responsible_captain="Analitica"))

        plan = TacticalPlan(plan=tasks)
        state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_captain(state: RedesSocialesColonelState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_captain
        if nxt == "PerfilBranding": return "perfil_node"
        elif nxt == "Atencion": return "atencion_node"
        elif nxt == "Analitica": return "analitica_node"
        return "difusion_node"

    async def perfil_node(state: RedesSocialesColonelState) -> RedesSocialesColonelState:
        m = state["task_queue"].pop(0)
        res = await c4_perfil.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "Capitan de Identidad y Perfil", "report": res.get("final_report", "Perfil actualizado")})
        return state

    async def difusion_node(state: RedesSocialesColonelState) -> RedesSocialesColonelState:
        m = state["task_queue"].pop(0)
        res = await c1_difusion.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "Capitan de Difusion Organica (Cero costo Ads)", "report": res.get("final_report", "Difundido")})
        return state

    async def atencion_node(state: RedesSocialesColonelState) -> RedesSocialesColonelState:
        m = state["task_queue"].pop(0)
        res = await c2_atencion.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "Capitan de Atencion WhatsApp / Chat", "report": res.get("final_report", "Atendido")})
        return state

    async def analitica_node(state: RedesSocialesColonelState) -> RedesSocialesColonelState:
        m = state["task_queue"].pop(0)
        res = await c3_analitica.ainvoke({"coronel_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"captain": "Capitan de Analitica Social", "report": res.get("final_report", "Auditado")})
        return state

    def compile_report(state: RedesSocialesColonelState) -> RedesSocialesColonelState:
        reps = "\n".join([f"- {m['captain']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = {
            "text": f"Mision de la Division de Redes Sociales completada con estricta segregacion de funciones:\n{reps}",
            "artifacts": []
        }
        return state

    workflow = StateGraph(RedesSocialesColonelState)
    workflow.add_node("create_plan", create_tactical_plan)
    workflow.add_node("perfil_node", perfil_node)
    workflow.add_node("difusion_node", difusion_node)
    workflow.add_node("atencion_node", atencion_node)
    workflow.add_node("analitica_node", analitica_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_captain)
    workflow.add_conditional_edges("perfil_node", route_to_captain)
    workflow.add_conditional_edges("difusion_node", route_to_captain)
    workflow.add_conditional_edges("atencion_node", route_to_captain)
    workflow.add_conditional_edges("analitica_node", route_to_captain)
    workflow.add_edge("compile_report", END)

    return workflow.compile()