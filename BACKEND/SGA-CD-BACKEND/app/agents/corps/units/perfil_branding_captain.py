from typing import TypedDict, List, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from app.tools.herramientas_perfil_redes import (
    tool_perfil_redactar_bio_institucional,
    tool_perfil_actualizar_bio_redes,
    tool_perfil_actualizar_telefono_corporativo,
    tool_perfil_actualizar_direccion_sede,
    tool_perfil_formatear_avatar_circular,
    tool_perfil_generar_banner_portada,
    tool_perfil_auditar_proteccion_datos
)

class PerfilTask(BaseModel):
    task_description: str
    responsible_lieutenant: str

class PerfilPlan(BaseModel):
    plan: List[PerfilTask]

class PerfilCaptainState(TypedDict):
    coronel_order: str
    app_context: Any
    tactical_plan: PerfilPlan | None
    task_queue: List[PerfilTask]
    completed_missions: list
    final_report: str
    error: str | None

def create_platoon_plan(state: PerfilCaptainState) -> PerfilCaptainState:
    order = state.get("coronel_order", "")
    print("--- 🏛️ CAPITÁN IDENTIDAD Y PERFIL: Desplegando plan de marca institucional ---")
    tasks = [
        PerfilTask(task_description=f"Actualizar biografia corporativa: {order}", responsible_lieutenant="MetadatosBio"),
        PerfilTask(task_description=f"Sincronizar datos de empresa (Habeas Data): {order}", responsible_lieutenant="DatosEmpresa"),
        PerfilTask(task_description=f"Formatear avatar y portada corporativa: {order}", responsible_lieutenant="BrandingGrafico")
    ]
    plan = PerfilPlan(plan=tasks)
    state.update({"tactical_plan": plan, "task_queue": plan.plan.copy(), "completed_missions": [], "error": None})
    return state

def route_to_lieutenant(state: PerfilCaptainState):
    if state.get("error") or not state["task_queue"]:
        return "compile_report"
    nxt = state["task_queue"][0].responsible_lieutenant
    if nxt == "MetadatosBio": return "bio_node"
    elif nxt == "DatosEmpresa": return "empresa_node"
    return "branding_node"

def bio_node(state: PerfilCaptainState) -> PerfilCaptainState:
    m = state["task_queue"].pop(0)
    tool_perfil_redactar_bio_institucional.invoke({"eslogan": "Líderes en Formación Deportiva y Cultural", "propuesta_valor": "Plataforma Integral SGA-CD"})
    res = tool_perfil_actualizar_bio_redes.invoke({"plataforma": "Meta y LinkedIn", "bio_texto": state["coronel_order"]})
    state["completed_missions"].append({"lieutenant": "Metadatos y Bio", "report": res})
    return state

def empresa_node(state: PerfilCaptainState) -> PerfilCaptainState:
    m = state["task_queue"].pop(0)
    tool_perfil_auditar_proteccion_datos.invoke({"texto": state["coronel_order"]})
    tool_perfil_actualizar_telefono_corporativo.invoke({"plataforma": "WhatsApp y Meta", "telefono_pbx": "+57 300 123 4567"})
    res = tool_perfil_actualizar_direccion_sede.invoke({"plataforma": "Meta y Google", "direccion": "Sede Central Deportiva", "ciudad": "Bogotá"})
    state["completed_missions"].append({"lieutenant": "Datos Empresa (Habeas Data Blindado)", "report": res})
    return state

def branding_node(state: PerfilCaptainState) -> PerfilCaptainState:
    m = state["task_queue"].pop(0)
    tool_perfil_formatear_avatar_circular.invoke({"ruta_logo_original": "assets/images/logo.png"})
    res = tool_perfil_generar_banner_portada.invoke({"titulo_campana": "Temporada de Matrículas", "dimensiones": "1920x1080"})
    state["completed_missions"].append({"lieutenant": "Branding Gráfico y Portadas", "report": res})
    return state

def compile_report(state: PerfilCaptainState) -> PerfilCaptainState:
    reps = "\n".join([f"- {m['lieutenant']}: {m['report']}" for m in state["completed_missions"]])
    state["final_report"] = f"Reporte del Capitán de Identidad y Perfil:\n{reps}"
    return state

def get_perfil_branding_captain_graph(llm: Any = None):
    workflow = StateGraph(PerfilCaptainState)
    workflow.add_node("create_plan", create_platoon_plan)
    workflow.add_node("bio_node", bio_node)
    workflow.add_node("empresa_node", empresa_node)
    workflow.add_node("branding_node", branding_node)
    workflow.add_node("compile_report", compile_report)

    workflow.set_entry_point("create_plan")
    workflow.add_conditional_edges("create_plan", route_to_lieutenant)
    workflow.add_conditional_edges("bio_node", route_to_lieutenant)
    workflow.add_conditional_edges("empresa_node", route_to_lieutenant)
    workflow.add_conditional_edges("branding_node", route_to_lieutenant)
    workflow.add_edge("compile_report", END)

    return workflow.compile()