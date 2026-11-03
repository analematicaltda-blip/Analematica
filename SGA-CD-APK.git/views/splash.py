import flet as ft
import time

LOGO_PATH = "assets/logo.png"

def splash_view(page: ft.Page):

    def navigate_to_login(e=None):
        # This function will be called after the splash screen duration
        page.go("/login")

    # This is a simple way to do it. A more advanced way would use threads
    # to avoid blocking the UI, but for a splash screen, this is often acceptable.
    # We can also use Flet's page.run_task() for non-blocking waits.
    # Let's use a simple client-side redirection with a timer control.

    # This approach is better as it doesn't block the main thread.
    # However, Flet does not have a built-in timer control that is simple to use
    # in this context. A common pattern is to use a thread.

    import threading
    def timed_navigation():
        time.sleep(3) # Wait for 3 seconds
        page.go("/login")

    # Run the navigation in a separate thread so it doesn't block the UI
    threading.Thread(target=timed_navigation, daemon=True).start()

    return ft.View(
        "/", # This is the root route
        [
            ft.Column(
                [
                    ft.Image(src=LOGO_PATH, width=200, height=200),
                    ft.ProgressRing(),
                    ft.Text("Cargando...", size=16)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                expand=True
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
