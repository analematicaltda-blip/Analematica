import flet as ft

def main(page: ft.Page):
    print(hasattr(ft, 'UserControl'))
    page.add(ft.Text("Test"))

if __name__ == "__main__":
    ft.app(target=main)
