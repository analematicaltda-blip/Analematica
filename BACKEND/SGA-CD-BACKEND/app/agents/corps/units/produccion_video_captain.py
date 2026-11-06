from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from .platoons.preproduccion_teniente import get_preproduccion_graph
from .platoons.locucion_audio_teniente import get_locucion_audio_graph
from .platoons.postproduccion_ffmpeg_teniente import get_postproduccion_ffmpeg_graph

class PlatoonTask(BaseModel):
    task_description: str
    responsible_lieutenant: str # 'preproduccion', 'locucion_audio', 'postproduccion_ffmpeg'

class PlatoonPlan(BaseModel):
    plan: List[PlatoonTask]

class ProduccionVideoCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    platoon_plan: PlatoonPlan | None
    task_queue: List[PlatoonTask]
    completed_missions: list
    final_report: str
    error: str | None

def get_produccion_video_graph(llm: Any = None):
    t1_agent = get_preproduccion_graph(llm)
    t2_agent = get_locucion_audio_graph(llm)
    t3_agent = get_postproduccion_ffmpeg_graph(llm)

    def create_platoon_plan(state: ProduccionVideoCaptainState) -> ProduccionVideoCaptainState:
        order = state.get("coronel_order", "")
        print(f"--- 🎖️ CAPITÁN ProduccionVideoCaptain: Creando plan táctico de compañía para -> '{order[:40]}...' ---")
        tasks = [
            PlatoonTask(task_description=f"Fase 1: {order}", responsible_lieutenant="preproduccion"),
            PlatoonTask(task_description=f"Fase 2: {order}", responsible_lieutenant="locucion_audio"),
            PlatoonTask(task_description=f"Fase 3: {order}", responsible_lieutenant="postproduccion_ffmpeg")
        ]
        plan = PlatoonPlan(plan=tasks)
        state.update({"platoon_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
        return state

    def route_to_lieutenant(state: ProduccionVideoCaptainState):
        if state.get("error") or not state["task_queue"]:
            return "compile_report"
        nxt = state["task_queue"][0].responsible_lieutenant
        if nxt == "preproduccion": return "t1_node"
        elif nxt == "locucion_audio": return "t2_node"
        return "t3_node"

    async def t1_node(state: ProduccionVideoCaptainState) -> ProduccionVideoCaptainState:
        m = state["task_queue"].pop(0)
        res = await t1_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "PreproduccionLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t2_node(state: ProduccionVideoCaptainState) -> ProduccionVideoCaptainState:
        m = state["task_queue"].pop(0)
        res = await t2_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "LocucionAudioLieutenant", "report": res.get("final_report", "Completado")})
        return state

    async def t3_node(state: ProduccionVideoCaptainState) -> ProduccionVideoCaptainState:
        m = state["task_queue"].pop(0)
        res = await t3_agent.ainvoke({"captain_order": m.task_description, "app_context": state.get("app_context")})
        state["completed_missions"].append({"lieutenant": "PostproduccionFfmpegLieutenant", "report": res.get("final_report", "Completado")})
        return state

    def compile_report(state: ProduccionVideoCaptainState) -> ProduccionVideoCaptainState:
        reps = "\n".join([f"- {m['lieutenant']}:\n  {m['report']}" for m in state["completed_missions"]])
        state["final_report"] = f"Reporte de Compañía ProduccionVideoCaptain:\n{reps}"
        return state

    workflow = StateGraph(ProduccionVideoCaptainState)
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
