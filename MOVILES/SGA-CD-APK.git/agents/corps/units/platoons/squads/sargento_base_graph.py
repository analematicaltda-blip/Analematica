from typing import TypedDict, Any, List, Annotated
import operator
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.tools import BaseTool

import json

class SargentoBaseState(TypedDict):
    """La pizarra táctica estandarizada para todos los Sargentos."""
    teniente_order: str
    app_context: Any
    messages: Annotated[List[BaseMessage], operator.add]
    # El reporte final ahora es un objeto estructurado
    final_report: dict
    error: str | None

class SargentoGraphBuilder:
    """Constructor estandarizado para todos los agentes Sargento."""
    def __init__(self, squad: List[BaseTool], squad_name: str, llm: Any):
        self.squad_executor = ToolNode(squad)
        self.squad_name = squad_name
        self.model = llm.bind_tools(squad)

    def get_sargento_brain(self, state: SargentoBaseState):
        """El cerebro del Sargento. Analiza el estado y decide la siguiente acción para su escuadra."""
        print(f"--- 🤔 SARGENTO ({self.squad_name}): Analizando orden y decidiendo acción... ---")
        return self.model.invoke(state["messages"])

    def route_action(self, state: SargentoBaseState):
        """Revisa la decisión del cerebro y enruta al ejecutor o al informe final."""
        last_message = state["messages"][-1]
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return "compile_report"
        return "squad_executor"

    def compile_report_node(self, state: SargentoBaseState) -> SargentoBaseState:
        """
        Compila el informe final estructurado (texto e imagen) para el Teniente.
        """
        print(f"--- 📄 SARGENTO ({self.squad_name}): Misión completada. Compilando reporte. ---")

        report_text_parts = []
        image_url = None

        tool_messages = [msg for msg in state["messages"] if msg.type == 'tool']

        for msg in tool_messages:
            try:
                # Intenta parsear el contenido como JSON si es un string
                content_data = json.loads(msg.content) if isinstance(msg.content, str) else msg.content

                # Si es un diccionario y tiene image_url, la extraemos
                if isinstance(content_data, dict) and 'image_url' in content_data:
                    image_url = content_data.get('image_url')
                    # Añadimos un mensaje amigable al reporte de texto
                    report_text_parts.append(f"Acción '{msg.name}': {content_data.get('message', 'Gráfico generado.')}")
                else:
                    # Si no, lo tratamos como texto normal
                    report_text_parts.append(f"Acción '{msg.name}': Resultado: {msg.content}")
            except (json.JSONDecodeError, TypeError):
                # Si no es JSON, es un string simple
                report_text_parts.append(f"Acción '{msg.name}': Resultado: {msg.content}")

        if not report_text_parts:
            final_text = "Misión completada sin necesidad de acciones directas de la escuadra."
        else:
            final_text = f"Resumen de acciones de la escuadra de {self.squad_name}:\n- " + "\n- ".join(report_text_parts)

        state["final_report"] = {
            "text": final_text,
            "image_url": image_url
        }
        return state

    def build_graph(self):
        """Construye y compila el grafo LangGraph para el Sargento."""
        workflow = StateGraph(SargentoBaseState)

        def mission_entry_node(state: SargentoBaseState):
            """Nodo de entrada que formatea la orden del Teniente como el primer mensaje."""
            return {"messages": [HumanMessage(content=state["teniente_order"])]}

        workflow.add_node("mission_entry", mission_entry_node)
        workflow.add_node("brain", self.get_sargento_brain)
        workflow.add_node("squad_executor", self.squad_executor)
        workflow.add_node("compiler", self.compile_report_node)

        workflow.add_edge(START, "mission_entry")
        workflow.add_edge("mission_entry", "brain")

        workflow.add_conditional_edges(
            "brain",
            self.route_action,
            {
                "squad_executor": "squad_executor",
                "compiler": "compiler"
            }
        )
        workflow.add_edge("squad_executor", "brain")
        workflow.add_edge("compiler", END)

        return workflow.compile().with_types(input_type=SargentoBaseState)
