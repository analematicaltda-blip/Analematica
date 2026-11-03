import importlib
import os
from pathlib import Path
import sys
import flet as ft

client = Path(os.environ['SGACD_FLET_CLIENT']).resolve()
sys.path.insert(0, str(client))
app = importlib.import_module('main')
ft.app(target=app.main, view=ft.AppView.WEB_BROWSER, web_renderer=ft.WebRenderer.CANVAS_KIT,
       host=os.getenv('FLET_SERVER_IP', '127.0.0.1'),
       port=int(os.environ['FLET_SERVER_PORT']),
       assets_dir=str(client / 'assets'))
