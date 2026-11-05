"""
CRM & Marketing View for SGA-CD Mobile Flet Application (Plan Full).
Provides administrative staff with campaign management, AI multimedia generation,
and real HTTP integration with the FastAPI backend.
"""
import flet as ft
from typing import Dict, Any, Optional

FORBIDDEN_CRM_ROLES = [
    "coordinador",
    "jefe_almacen",
    "almacenista",
    "jefe_escenarios",
    "profesor",
    "alumno",
    "padre_acudiente"
]

def crm_marketing_view(page: ft.Page, user_data: Dict[str, Any], api_client: Optional[Any] = None) -> ft.Control:
    user_role = user_data.get("role", "admin_empresa")
    user_plan = user_data.get("plan", "full")

    # Roles forbidden from CRM Suite
    if user_role in FORBIDDEN_CRM_ROLES:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCK, size=64, color=ft.Colors.RED_400),
                ft.Text("Acceso Restringido", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400),
                ft.Text("La suite CRM y Marketing está reservada exclusivamente para la administración principal y líderes de área autorizados.", color=ft.Colors.WHITE70)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )

    # Basic Plan locked
    if user_plan != "full":
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOCK_CLOCK, size=64, color=ft.Colors.AMBER_400),
                ft.Text("Módulo Requiere Plan Full", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                ft.Text("Actualice a Plan Full para desbloquear la suite completa de CRM, Campañas e Inteligencia Artificial.", color=ft.Colors.WHITE70)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )

    # Status / Result Text Controls
    ia_status_text = ft.Text("", size=13, color=ft.Colors.CYAN_300)
    campaign_status_text = ft.Text("", size=13, color=ft.Colors.GREEN_300)

    # Text Fields
    prompt_field = ft.TextField(
        label="Prompt para Open Generative AI / SkyReels",
        hint_text="Ej: Video promocional para escuela de fútbol",
        multiline=True
    )
    copy_field = ft.TextField(
        label="Mensaje o Copy Comercial",
        hint_text="Ej: ¡Inscripciones abiertas temporada 2025!",
        multiline=True
    )

    # Buttons
    btn_generar_ia = ft.ElevatedButton("Generar Contenido IA", icon=ft.Icons.AUTO_AWESOME)
    btn_lanzar_campana = ft.ElevatedButton("Lanzar Campaña Masiva", icon=ft.Icons.SEND)

    # Event Handlers with HTTP Integration
    def handle_generar_ia(e):
        prompt = prompt_field.value.strip() if prompt_field.value else ""
        if not prompt:
            ia_status_text.value = "⚠️ Por favor ingresa un prompt válido."
            ia_status_text.color = ft.Colors.AMBER_400
            page.update()
            return

        # Disable button during processing to prevent double clicks
        btn_generar_ia.disabled = True
        ia_status_text.value = "⏳ Procesando solicitud en el backend..."
        ia_status_text.color = ft.Colors.CYAN_300
        page.update()

        try:
            if api_client:
                endpoint = "/api/v1/crm/generate_predis_media"
                payload = {
                    "prompt": prompt,
                    "media_type": "post_1_1",
                    "aspect_ratio": "1:1"
                }
                res = api_client.post(endpoint, payload)
                if isinstance(res, dict) and res.get("error"):
                    status_code = res.get("status_code", 500)
                    if status_code == 402:
                        ia_status_text.value = "⛔ Plan Básico o cuota agotada. Requiere Plan Full."
                        ia_status_text.color = ft.Colors.RED_400
                    elif status_code == 403:
                        ia_status_text.value = "⛔ Sin permisos para ejecutar esta operación."
                        ia_status_text.color = ft.Colors.RED_400
                    elif status_code == 429:
                        ia_status_text.value = "⚠️ Cuota mensual de IA alcanzada (100/100)."
                        ia_status_text.color = ft.Colors.AMBER_400
                    else:
                        ia_status_text.value = f"⚠️ Error en backend ({res.get('code', 'ERR')})"
                        ia_status_text.color = ft.Colors.RED_400
                else:
                    ia_status_text.value = f"✅ Generación completada con éxito. ID: {res.get('job_id', 'N/A') if isinstance(res, dict) else 'OK'}"
                    ia_status_text.color = ft.Colors.GREEN_400
            else:
                ia_status_text.value = "ℹ️ Modo local activo: Petición formateada correctamente."
                ia_status_text.color = ft.Colors.CYAN_400
        except Exception as ex:
            ia_status_text.value = f"❌ Error de conexión: {str(ex)}"
            ia_status_text.color = ft.Colors.RED_400
        finally:
            btn_generar_ia.disabled = False
            page.update()

    def handle_lanzar_campana(e):
        copy_text = copy_field.value.strip() if copy_field.value else ""
        if not copy_text:
            campaign_status_text.value = "⚠️ Por favor ingresa el copy o mensaje comercial."
            campaign_status_text.color = ft.Colors.AMBER_400
            page.update()
            return

        btn_lanzar_campana.disabled = True
        campaign_status_text.value = "⏳ Publicando campaña en el backend real..."
        campaign_status_text.color = ft.Colors.CYAN_300
        page.update()

        try:
            if api_client:
                endpoint = "/api/v1/video_distribution/publish"
                payload = {
                    "platform": "instagram",
                    "video_path": "assets/generated/promo.mp4",
                    "caption": copy_text
                }
                res = api_client.post(endpoint, payload)
                if isinstance(res, dict) and res.get("error"):
                    status_code = res.get("status_code", 500)
                    if status_code in (402, 429):
                        campaign_status_text.value = "⛔ Cuota mensual de publicaciones agotada (50/50)."
                        campaign_status_text.color = ft.Colors.AMBER_400
                    elif status_code == 403:
                        campaign_status_text.value = "⛔ Rol no autorizado para publicar campañas."
                        campaign_status_text.color = ft.Colors.RED_400
                    else:
                        campaign_status_text.value = f"⚠️ Error en backend ({res.get('code', 'ERR')})"
                        campaign_status_text.color = ft.Colors.RED_400
                else:
                    campaign_status_text.value = f"✅ Campaña distribuida exitosamente. ID: {res.get('publish_id', 'PUB-OK') if isinstance(res, dict) else 'OK'}"
                    campaign_status_text.color = ft.Colors.GREEN_400
            else:
                campaign_status_text.value = "ℹ️ Modo local activo: Solicitud formateada correctamente."
                campaign_status_text.color = ft.Colors.CYAN_400
        except Exception as ex:
            campaign_status_text.value = f"❌ Error de conexión: {str(ex)}"
            campaign_status_text.color = ft.Colors.RED_400
        finally:
            btn_lanzar_campana.disabled = False
            page.update()

    btn_generar_ia.on_click = handle_generar_ia
    btn_lanzar_campana.on_click = handle_lanzar_campana

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CAMPAIGN, color=ft.Colors.CYAN_400, size=32),
                ft.Text("CRM & Marketing de Captación — Plan Full", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
            ]),
            ft.Divider(color=ft.Colors.CYAN_900),
            ft.ResponsiveRow([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Generador de Videos & Multimedia IA", weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                        prompt_field,
                        btn_generar_ia,
                        ia_status_text
                    ]),
                    padding=15,
                    bgcolor="#0D1424",
                    border_radius=10,
                    col={"sm": 12, "md": 6}
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Campañas Masivas (WhatsApp & Redes)", weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                        copy_field,
                        btn_lanzar_campana,
                        campaign_status_text
                    ]),
                    padding=15,
                    bgcolor="#0D1424",
                    border_radius=10,
                    col={"sm": 12, "md": 6}
                )
            ])
        ]),
        padding=20,
        expand=True
    )
