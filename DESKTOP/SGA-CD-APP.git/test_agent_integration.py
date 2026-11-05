import asyncio
import os
from agent.llm_service import _load_config
from agents.corps.formacion_cultura_colonel import get_formacion_cultura_colonel_graph

async def run_test():
    """
    Script de prueba de integración para el sistema de agentes.
    Carga la configuración, inicializa el agente Coronel y ejecuta una orden de prueba.
    """
    try:
        config = _load_config()
        provider = config.get('llm_provider')
        print(f"--- 🚀 INICIANDO PRUEBA DE INTEGRACIÓN CON LLM PROVIDER: {provider} ---")
    except FileNotFoundError:
        print("--- 🛑 ERROR: No se encontró el archivo config.json. ---")
        return

    if provider in ['openai', 'google']:
        api_key = config.get('providers', {}).get(provider, {}).get('api_key', '')
        if f"YOUR-{provider.upper()}-API-KEY-HERE" in api_key or not api_key:
            print(f"--- 🛑 ERROR: La clave de API de '{provider}' no está configurada en config.json. ---")
            return

    colonel_agent = get_formacion_cultura_colonel_graph()

    general_order = "Quiero un informe sobre el estado de las inscripciones para el curso 'Introducción a la IA' y, además, necesito que se analice la seguridad de nuestra sede principal y se me dé un reporte de vulnerabilidades."
    print(f"\n--- 🗣️ ORDEN DEL GENERAL: \"{general_order}\" ---")

    # Since memory is disabled, we do not pass the 'config' argument with a thread_id.
    final_state = await colonel_agent.ainvoke(
        {"general_order": general_order, "app_context": None}
    )

    print("\n--- 🏁 MISIÓN COMPLETADA ---")
    print("--- 📝 INFORME FINAL DEL CORONEL ---")
    print(final_state.get("final_report", "No se generó ningún informe."))
    print("--- ✅ PRUEBA FINALIZADA ---")


if __name__ == "__main__":
    asyncio.run(run_test())
