"""Loopback web preview: no financial login or local cache access."""
import flet as ft
from sgacd_wallet_ui import run
if __name__=='__main__':ft.app(target=lambda page:run(page,'web'),view=ft.AppView.WEB_BROWSER,host='127.0.0.1',port=8555)
