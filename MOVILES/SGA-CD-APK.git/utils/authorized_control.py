"""Launch the shared HTTPS control panel; local/offline login grants no remote authority."""
import os
from urllib.parse import urlsplit

STAFF={'admin_general','admin_empresa','jefe_area','coordinador','profesional_area','tecnico_area'}

def panel_url(origin=None):
    value=(origin or os.environ.get('SGACD_CONTROL_ORIGIN','')).rstrip('/')
    parsed=urlsplit(value)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Configura SGACD_CONTROL_ORIGIN con el origen HTTPS del panel, sin rutas ni credenciales.')
    return value+'/control.html'

def open_control(page):
    # This visibility check is not server authorization. Central JWT login is required.
    if page.session.get('user_role') not in STAFF:
        return
    try:
        url=panel_url()
    except ValueError as error:
        import flet as ft
        page.snack_bar=ft.SnackBar(ft.Text(str(error)));page.snack_bar.open=True;page.update();return
    page.launch_url(url)
