import flet as ft

class MessageIcon(ft.IconButton):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.icon = ft.icons.CHAT_BUBBLE_OUTLINE
        self.tooltip = "Ver Mensajes"
        self.on_click = self.go_to_messages

    def go_to_messages(self, e):
        self.page.go("/mensajes")
