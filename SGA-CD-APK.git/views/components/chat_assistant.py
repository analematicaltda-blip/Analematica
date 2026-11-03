import flet as ft
import asyncio
from agent.agent_interface import invoke_agent_for_area

class ChatAssistant(ft.Stack):
    def __init__(self, page: ft.Page, user_id: int, tenant_id: int, area: str | None):
        super().__init__()
        self.page = page
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.area = area
        self.chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.user_input = ft.TextField(
            label="Escribe tu orden o pregunta...",
            expand=True,
            on_submit=self.send_message_click
        )
        self.send_button = ft.IconButton(
            icon=ft.icons.SEND,
            on_click=self.send_message_click,
            tooltip="Enviar mensaje"
        )
        self.progress_ring = ft.ProgressRing(visible=False)
        self.area_selector = ft.Dropdown(
            label="Seleccionar Área de Contexto",
            options=[ft.dropdown.Option("Cultura"), ft.dropdown.Option("Deportes")],
            visible=(self.area is None)
        )
        dialog_title = "Asistente de IA" if self.area is None else f"Asistente de IA ({self.area})"
        self.chat_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(dialog_title),
            content=ft.Container(
                width=600,
                height=450,
                content=ft.Column([
                    self.area_selector,
                    self.chat_history,
                    ft.Row([self.user_input, self.send_button]),
                    self.progress_ring
                ])
            ),
            actions=[ft.TextButton("Cerrar", on_click=self.close_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def build(self):
        fab = ft.FloatingActionButton(
            icon=ft.icons.ASSISTANT,
            tooltip="Hablar con Asistente de IA",
            on_click=self.open_dialog
        )
        animated_border_container = ft.Container(
            content=fab,
            width=62,
            height=62,
            border_radius=50,
            padding=3,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#00f", "#0ff", "#0f0", "#ff0", "#f00", "#f0f", "#00f"],
            ),
            animate_rotation=ft.animation.Animation(duration=4000, curve=ft.AnimationCurve.LINEAR),
        )
        async def animate_forever(e):
            while True:
                animated_border_container.rotate.angle += 0.1
                await animated_border_container.update_async()
                await asyncio.sleep(0.02)
        self.on_animation_end = animate_forever
        return animated_border_container

    def open_dialog(self, e):
        self.page.dialog = self.chat_dialog
        self.chat_dialog.open = True
        if not self.on_animation_end.is_running():
             self.page.run_task(self.on_animation_end, self)
        self.page.update()

    def close_dialog(self, e):
        self.chat_dialog.open = False
        self.page.update()

    async def send_message_click(self, e):
        user_text = self.user_input.value
        if not user_text:
            return
        self.chat_history.controls.append(ft.Text(f"Tú: {user_text}", text_align=ft.TextAlign.RIGHT))
        self.user_input.value = ""
        self.progress_ring.visible = True
        self.user_input.disabled = True
        self.send_button.disabled = True
        self.update()
        response_text = await self.call_backend_agent(user_text)
        self.chat_history.controls.append(
            ft.Markdown(f"**Asistente:**\n{response_text}", selectable=True, extension_set="git-hub-flavored")
        )
        self.progress_ring.visible = False
        self.user_input.disabled = False
        self.send_button.disabled = False
        self.update()

    async def call_backend_agent(self, text: str) -> str:
        area_to_use = self.area
        if area_to_use is None:
            area_to_use = self.area_selector.value
            if not area_to_use:
                return "Error: Por favor, selecciona un área de contexto (Cultura o Deportes) para continuar."

        # TODO: La clave de API del inquilino debe obtenerse de forma segura.
        tenant_api_key = "inquilino_demo_key"

        response = await invoke_agent_for_area(
            page=self.page,
            area=area_to_use,
            user_input=text,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            tenant_api_key=tenant_api_key
        )
        return response
