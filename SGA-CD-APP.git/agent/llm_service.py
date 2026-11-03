import os
import flet as ft
from typing import Dict, Any, Union, Optional

_llm_instance = None
_llm_status = "not_initialized"
_active_provider = "none"
_active_model_name = "none"

class RulesBasedAssistant:
    def invoke(self, prompt: Any, *args, **kwargs) -> Any:
        class MockResponse:
            def __init__(self, text):
                self.content = text
        return MockResponse("Respuesta fuera de línea generada con motor de reglas locales SGA-CD.")

def initialize_llm(page: ft.Page, config: Dict[str, Any]) -> None:
    global _llm_instance, _llm_status, _active_provider, _active_model_name

    provider = config.get("llm_preference", "local")
    _llm_status = f"initializing_{provider}"
    print(f"--- 🧠 Inicializando LLM con proveedor: '{provider}' ---")

    llm = None
    if provider == "local":
        platform = getattr(page, "platform", "windows")
        if platform in ["android", "ios"]:
            # Móvil: intentar LlamaCpp o fallback seguro
            try:
                from langchain_community.llms import LlamaCpp
                model_path = config.get("local_model_path", "assets/models/phi-3-mini-4k-instruct.Q4_K_M.gguf")
                if os.path.exists(model_path):
                    llm = LlamaCpp(model_path=model_path, n_ctx=2048, n_gpu_layers=0, verbose=False)
                    _active_provider = "Local LlamaCpp Mobile"
                else:
                    llm = RulesBasedAssistant()
                    _active_provider = "Local Rules-Based (Modelo GGUF no descargado aún)"
            except Exception as e:
                print(f"[Aviso Móvil] LlamaCpp nativo no disponible: {e}. Usando asistente local.")
                llm = RulesBasedAssistant()
                _active_provider = "Local Rules-Based Fallback"
        else:
            # Escritorio: Conectar a Ollama local (DeepSeek)
            try:
                from langchain_ollama import ChatOllama
                ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                model_name = config.get("model_name", "deepseek-r1:8b")
                llm = ChatOllama(model=model_name, base_url=ollama_url, temperature=0.1)
                _active_provider = f"Ollama Local ({model_name})"
            except Exception as e:
                print(f"[Aviso Escritorio] Ollama no disponible: {e}")
                llm = RulesBasedAssistant()
                _active_provider = "Local Rules-Based Fallback"

    elif provider == "rules_based":
        llm = RulesBasedAssistant()
        _active_provider = "Rules Based Assistant"

    _llm_instance = llm
    _llm_status = "initialized"
    print(f"--- ✅ LLM inicializado con éxito. Proveedor activo: '{_active_provider}' ---")

def get_llm_instance():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = RulesBasedAssistant()
    return _llm_instance

def get_llm_status():
    global _llm_status
    return _llm_status