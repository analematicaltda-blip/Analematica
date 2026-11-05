from langchain_core.messages import FunctionMessage

class SimpleToolExecutor:
    """
    Reemplazo directo de ToolExecutor para LangGraph moderno.
    Se encarga de ejecutar un conjunto de tools registrados.
    """

    def __init__(self, tools: dict):
        """
        tools: diccionario {tool_name: callable}
        """
        self.tools = tools

    def batch(self, calls: list[tuple[str, dict]]):
        """
        Ejecuta múltiples llamadas a herramientas.
        calls: lista de tuplas (tool_name, args_dict)
        """
        results = []
        for name, args in calls:
            tool = self.tools.get(name)
            if tool is None:
                results.append(f"Error: Tool '{name}' not found")
                continue

            try:
                # Si la tool es async
                if callable(getattr(tool, "__call__", None)) and hasattr(tool, "__call__") and getattr(tool, "__call__").__class__.__name__ == "coroutine":
                    # ⚠️ Si usas asyncio deberías hacer await aquí, pero para mantener compatibilidad:
                    results.append("Error: Async tools need explicit await handling")
                else:
                    results.append(tool(**args) if args else tool())
            except Exception as e:
                results.append(f"Error ejecutando {name}: {str(e)}")
        return results
