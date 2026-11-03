import flet as ft
import sqlite3
import os

# --- App-specific Imports ---
from utils.theme import create_light_theme, create_dark_theme
from utils.i18n_service import Translator
from agent.llm_service import initialize_llm, get_llm_status
from utils.database_manager import initialize_local_database
# --- View Imports ---
from views.selection_view import selection_view
from views.setup_online_mode_view import setup_online_mode_view
from views.setup_api_key_view import setup_api_key_view
from views.setup_local_model_view import setup_local_model_view
from views.login import login_view
from views.shared.dashboard_view import dashboard_view
from views.jefe_area.jefe_area_principal import jefe_area_principal_view
from views.profesor_principal import profesor_principal
from views.admin_principal import admin_principal
# ... etc.

def main(page: ft.Page):
    # --- Inicialización de Servicios Críticos ---
    initialize_local_database(page)

    # La inicialización del LLM se moverá a después de que el usuario haga su selección.

    page.title = "SGA-CD: Sistema de Gestión Académica (Desktop)"

    # --- Theme Setup ---
    page.theme = create_light_theme()
    page.dark_theme = create_dark_theme()
    page.theme_mode = page.session.get("theme_mode") or ft.ThemeMode.LIGHT

    def toggle_theme(e):
        page.theme_mode = (
            ft.ThemeMode.DARK
            if page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        page.session.set("theme_mode", page.theme_mode)
        page.update()

    theme_switcher_button = ft.IconButton(
        icon=ft.icons.BRIGHTNESS_4_OUTLINED,
        tooltip="Cambiar tema",
        on_click=toggle_theme,
    )

    # --- Internationalization Service ---
    user_lang = page.session.get("user_lang") or "es"
    translator = Translator(initial_lang=user_lang)
    page.translator = translator

    # --- Main Router Logic ---
    def route_change(route):
        page.views.clear()

        # Primero, comprobar si el modo ha sido seleccionado.
        mode_selected = page.session.get("mode_selected")
        if not mode_selected:
            page.views.append(selection_view(page))
            if page.route != "/selection":
                page.go("/selection")
            page.update()
            return

        # Si el modo ya está seleccionado, proceder con la lógica normal.
        user_id = page.session.get("user_id")

        # Rutas de configuración que no requieren login
        if page.route == "/setup/online_mode":
            page.views.append(setup_online_mode_view(page))
        elif page.route == "/setup/api_key":
            page.views.append(setup_api_key_view(page))
        elif page.route == "/setup/local_model":
            page.views.append(setup_local_model_view(page))
        elif page.route == "/login":
            page.views.append(login_view(page, None, None))
        elif user_id is None:
            # Si no hay usuario y no es una ruta de setup/login, ir a login
            page.go("/login")
        else:
            # Lógica de enrutamiento para usuarios autenticados
            user_role = page.session.get("user_role")
            tenant_id = page.session.get("tenant_id")

            def add_view(view_function, **kwargs):
                view = view_function(page=page, user_id=user_id, tenant_id=tenant_id, **kwargs)
                if hasattr(view, 'appbar') and view.appbar:
                    if not hasattr(view.appbar, 'actions'):
                        view.appbar.actions = []
                    if not any(isinstance(c, ft.IconButton) and c.tooltip == "Cambiar tema" for c in view.appbar.actions):
                        view.appbar.actions.append(theme_switcher_button)
                page.views.append(view)

            routing_table = {
                "/dashboard": (dashboard_view, ["alumno", "profesor", "admin_empresa", "jefe_area"]),
                "/admin_home": (admin_principal, ["admin_empresa"]),
                "/jefe_area/home": (jefe_area_principal_view, ["jefe_area"]),
                "/profesor_home": (profesor_principal, ["profesor"])
            }

            route_found = False
            for route_path, (view_func, allowed_roles) in routing_table.items():
                if page.route == route_path:
                    if user_role in allowed_roles:
                        add_view(view_func)
                        route_found = True
                        break
            if not route_found:
                page.go('/dashboard')
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Iniciar la aplicación en la ruta de selección.
    page.go("/selection")

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
