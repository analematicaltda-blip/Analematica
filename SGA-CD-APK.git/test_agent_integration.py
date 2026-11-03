import asyncio
import os
import sqlite3
from agent.llm_service import initialize_llm, get_llm_instance
from agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph

# --- Mock Page Object ---
class MockPage:
    def __init__(self):
        self.platform = "android" # Simulate running on Android for local model tests
        self._session = {}

    def session_get(self, key):
        return self._session.get(key)

    def session_set(self, key, value):
        self._session[key] = value

async def run_test():
    """
    Script de prueba de integración para el sistema de agentes refactorizado.
    Simula el flujo de configuración, inicializa el LLM y el agente, y ejecuta una orden.
    """
    print("--- 🚀 INICIANDO PRUEBA DE INTEGRACIÓN DEL AGENTE REFACTORIZADO ---")

    # 1. Simular el flujo de configuración del usuario (Modo Online)
    mock_page = MockPage()
    # Para esta prueba, usaremos el modo online. Se requiere una clave de API válida.
    # ADVERTENCIA: La prueba fallará si la clave no es válida, pero verificará la estructura.
    api_key = os.environ.get("OPENAI_API_KEY", "TEST_API_KEY")

    if not api_key or api_key == "TEST_API_KEY":
        print("--- ⚠️ ADVERTENCIA: No se encontró OPENAI_API_KEY en las variables de entorno. Usando clave de prueba. ---")
        print("--- La prueba verificará la estructura del agente pero fallará al llamar a la API de OpenAI. ---")

    test_config = {
        "llm_preference": "openai",
        "openai_api_key": api_key
    }
    initialize_llm(mock_page, test_config)
    llm = get_llm_instance()

    if not llm:
        print("--- 🛑 ERROR: La inicialización del LLM falló. ---")
        return

    # 2. Crear una base de datos de prueba para la memoria del agente
    db_path = ":memory:" # Usar una base de datos en memoria para la prueba

    # 3. Inicializar el agente Coronel con el LLM y la DB
    colonel_agent = get_formacion_cultura_colonel_graph(db_path, llm)

    # 4. Ejecutar una orden de prueba
    general_order = "Quiero un informe sobre el estado de las inscripciones para el curso 'Introducción a la IA'."
    print(f"\n--- 🗣️ ORDEN DEL GENERAL: \"{general_order}\" ---")

    try:
        # The checkpointer needs a thread_id to save progress.
        config = {"configurable": {"thread_id": "test-thread-1"}}
        final_state = await colonel_agent.ainvoke(
            {"general_order": general_order, "app_context": None},
            config=config
        )
        print("\n--- 🏁 MISIÓN COMPLETADA ---")
        print("--- 📝 INFORME FINAL DEL CORONEL ---")
        # El informe final puede estar en 'final_report' o en el último mensaje
        report = final_state.get("final_report")
        if not report and final_state.get("messages"):
            report = final_state["messages"][-1].content
        print(report or "No se generó ningún informe.")

    except Exception as e:
        print(f"\n--- ❌ ERROR DURANTE LA EJECUCIÓN DEL AGENTE: {e} ---")
        print("--- Esto puede ser esperado si la clave de API no es válida. ---")

    print("\n--- ✅ PRUEBA FINALIZADA ---")


if __name__ == "__main__":
    # Añadir un event loop si no existe (importante para algunos entornos)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(run_test())
