import flet as ft
import sqlite3
import requests # To call our own API for the portal link

def gestion_suscripcion_view(page: ft.Page, tenant_id: int):

    def get_subscription_details():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT plan, estado, fecha_fin, stripe_customer_id FROM suscripciones WHERE inquilino_id = ?",
            (tenant_id,)
        )
        sub_data = cursor.fetchone()
        conn.close()
        return sub_data

    def get_invoices():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fecha_emision, monto, estado, pdf_url FROM facturas WHERE inquilino_id = ? ORDER BY fecha_emision DESC",
            (tenant_id,)
        )
        invoices = cursor.fetchall()
        conn.close()
        return invoices

    # --- UI Components ---
    plan_name = ft.Text(weight="bold")
    plan_status = ft.Text()
    end_date = ft.Text()
    status_badge = ft.Container(padding=5, border_radius=5)

    invoice_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha Emisión")),
            ft.DataColumn(ft.Text("Monto")),
            ft.DataColumn(ft.Text("Estado")),
            ft.DataColumn(ft.Text("Factura")),
        ],
        rows=[]
    )

    def populate_view():
        sub_details = get_subscription_details()
        if sub_details:
            plan_name.value = f"Plan Actual: {sub_details[0].upper()}"
            plan_status.value = sub_details[1].capitalize()
            end_date.value = f"Válido hasta: {sub_details[2]}"

            status_colors = {
                "activa": ft.colors.GREEN,
                "en_prueba": ft.colors.BLUE,
                "vencida": ft.colors.RED,
                "cancelada": ft.colors.GREY,
            }
            status_badge.bgcolor = status_colors.get(sub_details[1], ft.colors.GREY)
            status_badge.content = ft.Text(sub_details[1].upper(), color="white", weight="bold")
        else:
            plan_name.value = "No se encontró una suscripción."

        invoices = get_invoices()
        invoice_table.rows.clear()
        if not invoices:
            invoice_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("No hay facturas disponibles."), colspan=4)]))
        else:
            for inv in invoices:
                invoice_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(inv[0])),
                        ft.DataCell(ft.Text(f"${inv[1]:.2f}")),
                        ft.DataCell(ft.Text(inv[2].capitalize())),
                        ft.DataCell(ft.IconButton(icon=ft.icons.PICTURE_AS_PDF, url=inv[3], tooltip="Ver Factura en PDF") if inv[3] else ft.Text("-")),
                    ])
                )
        page.update()

    def open_customer_portal(e):
        try:
            # We need the tenant's API key to make an authenticated request
            conn = sqlite3.connect("formacion.db")
            api_key = conn.execute("SELECT api_key FROM inquilinos WHERE id = ?", (tenant_id,)).fetchone()[0]
            conn.close()

            # The API server runs on a different port, so we need the full URL
            # In a real deployment, this URL should come from a config file.
            api_url = "http://127.0.0.1:5001/api/create_customer_portal_session"

            headers = {'X-API-KEY': api_key}
            response = requests.post(api_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                page.launch_url(data['portal_url'])
            else:
                error_data = response.json()
                page.snack_bar = ft.SnackBar(ft.Text(f"Error al crear portal: {error_data.get('error', 'Desconocido')}"), bgcolor="red")
                page.snack_bar.open = True
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error de conexión: {ex}"), bgcolor="red")
            page.snack_bar.open = True

        page.update()

    manage_button = ft.ElevatedButton(
        "Gestionar mi Suscripción y Pagos",
        icon=ft.icons.PAYMENT,
        on_click=open_customer_portal,
        tooltip="Cambiar de plan, actualizar método de pago o cancelar."
    )

    populate_view()

    return ft.View(
        "/admin/suscripcion",
        [
            ft.AppBar(title=ft.Text("Gestión de Suscripción"), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        ft.Text("Estado de la Suscripción", style=ft.TextThemeStyle.HEADLINE_SMALL),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Row([plan_name, status_badge], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    end_date
                                ]),
                                padding=15
                            )
                        ),
                        manage_button,
                        ft.Divider(height=30),
                        ft.Text("Historial de Facturas", style=ft.TextThemeStyle.HEADLINE_SMALL),
                        invoice_table,
                    ],
                    spacing=15
                )
            )
        ]
    )
