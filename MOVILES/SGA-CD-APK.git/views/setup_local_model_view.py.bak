import flet as ft
import os
from utils.hardware_info import get_device_ram_gb
from utils.downloader import download_file
from agent.llm_service import initialize_llm, get_llm_status

# --- Model Configuration ---
MODELS = {
    "high": {
        "name": "Phi-3-mini-4k-instruct (Recomendado)",
        "size_gb": 2.2,
        "url": "https://huggingface.co/TheBloke/Phi-3-mini-4k-instruct-GGUF/resolve/main/Phi-3-mini-4k-instruct.Q4_K_M.gguf",
        "filename": "phi-3-mini-4k-instruct.Q4_K_M.gguf"
    },
    "medium": {
        "name": "Gemma-2B-IT",
        "size_gb": 1.4,
        "url": "https://huggingface.co/TheBloke/gemma-2b-it-GGUF/resolve/main/gemma-2b-it.Q4_K_M.gguf",
        "filename": "gemma-2b-it.Q4_K_M.gguf"
    }
}

def setup_local_model_view(page: ft.Page):
    """
    View for downloading and managing the local LLM based on device RAM.
    """

    # --- UI Elements ---
    progress_bar = ft.ProgressBar(width=400, visible=False)
    progress_text = ft.Text(visible=False)
    download_button = ft.ElevatedButton()
    back_button = ft.TextButton(
        "Volver",
        icon=ft.icons.ARROW_BACK_ROUNDED,
        on_click=lambda _: page.go("/selection")
    )
    title_text = ft.Text(size=24, weight=ft.FontWeight.BOLD)
    message_text = ft.Text(text_align=ft.TextAlign.CENTER)

    # --- Hardware Detection and Tier Logic ---
    ram_gb = get_device_ram_gb(page)
    tier = "low"
    if ram_gb:
        if ram_gb >= 7.5:
            tier = "high"
        elif ram_gb >= 3.8:
            tier = "medium"

    # --- Core Functions ---
    def start_download(model_config):
        local_path = os.path.join("assets", "models", model_config['filename'])

        def update_progress(downloaded, total):
            if total > 0:
                progress = downloaded / total
                progress_bar.value = progress
                progress_text.value = f"Descargando... {downloaded / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB"
                page.run_threadsafe(page.update)

        def on_download_complete(success, error_message):
            if success:
                progress_text.value = "¡Descarga completada! Inicializando el modelo..."
                page.run_threadsafe(page.update)

                config = {"llm_preference": "local", "local_model_path": local_path}
                initialize_llm(page, config)
                status = get_llm_status()

                if status == "initialized":
                    page.session.set("llm_config", config)
                    page.run_threadsafe(page.go, "/login")
                else:
                    progress_text.value = f"Error al cargar el modelo: {status}"
                    download_button.disabled = False
                    back_button.disabled = False
                    page.run_threadsafe(page.update)
            else:
                progress_text.value = f"Error en la descarga: {error_message}"
                download_button.disabled = False
                back_button.disabled = False
                page.run_threadsafe(page.update)

        print(f"--- 📥 Iniciando descarga de {model_config['name']} desde {model_config['url']} ---")

        download_button.disabled = True
        back_button.disabled = True
        progress_bar.visible = True
        progress_bar.value = 0
        progress_text.value = "Iniciando descarga..."
        progress_text.visible = True
        page.update()

        download_file(
            url=model_config['url'],
            local_path=local_path,
            progress_callback=update_progress,
            completion_callback=on_download_complete
        )

    def setup_rules_based_assistant():
        print("--- 🤖 Configurando asistente basado en reglas ---")
        config = {"llm_preference": "rules_based"}
        initialize_llm(page, config)
        page.session.set("llm_config", config)
        page.go("/login")

    # --- Set UI content based on tier ---
    if tier == "high":
        model = MODELS["high"]
        title_text.value = "Dispositivo de Gama Alta Detectado"
        message_text.value = f"Su dispositivo puede ejecutar nuestro mejor modelo: {model['name']}. Tamaño de descarga: {model['size_gb']} GB."
        download_button.text = f"Descargar Modelo ({model['size_gb']} GB)"
        download_button.on_click = lambda _: start_download(model)
    elif tier == "medium":
        model = MODELS["medium"]
        title_text.value = "Dispositivo de Gama Media Detectado"
        message_text.value = f"Su dispositivo puede ejecutar nuestro modelo estándar: {model['name']}. Tamaño de descarga: {model['size_gb']} GB."
        download_button.text = f"Descargar Modelo ({model['size_gb']} GB)"
        download_button.on_click = lambda _: start_download(model)
    else: # low tier
        title_text.value = "Modo de Asistente Básico"
        message_text.value = "Su dispositivo no puede ejecutar un modelo de IA local. Se activará un modo de asistente basado en reglas, que no requiere descarga."
        download_button.text = "Activar y Continuar"
        download_button.on_click = lambda _: setup_rules_based_assistant()

    # --- View Assembly ---
    view = ft.View(
        "/setup/local_model",
        [
            ft.Column(
                [
                    title_text,
                    message_text,
                    ft.Container(height=20),
                    download_button,
                    progress_bar,
                    progress_text,
                    back_button
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return view
