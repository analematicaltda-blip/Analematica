import flet as ft
import sqlite3
from views.login import hash_password

def gestion_personal_view(page: ft.Page, tenant_id: int, user_id: int):

    ROLES_DISPONIBLES = [
        'jefe_area', 'coordinador', 'profesor',
        'alumno', 'almacenista', 'jefe_almacen', 'jefe_escenarios'
    ]

    # --- DIALOG FOR CREATING/EDITING USER ---
    def crear_dialogo_usuario(usuario_existente=None):

        is_edit = usuario_existente is not None

        nombre_completo_input = ft.TextField(label="Nombre Completo", value=usuario_existente['nombre_completo'] if is_edit else "")
        nombre_usuario_input = ft.TextField(label="Nombre de Usuario", value=usuario_existente['nombre_usuario'] if is_edit else "")
        password_input = ft.TextField(label="Contraseña (dejar en blanco para no cambiar)", password=True, can_reveal_password=True)
        correo_input = ft.TextField(label="Correo Electrónico", value=usuario_existente['correo'] if is_edit else "")
        rol_dropdown = ft.Dropdown(
            label="Rol",
            options=[ft.dropdown.Option(rol) for rol in ROLES_DISPONIBLES],
            value=usuario_existente['rol'] if is_edit else None
        )
        activo_switch = ft.Switch(label="Activo", value=usuario_existente['activo'] if is_edit else True)

        def guardar_usuario(e):
            # Validation
            if not all([nombre_completo_input.value, nombre_usuario_input.value, correo_input.value, rol_dropdown.value]):
                # show error
                return

            conn = sqlite3.connect("formacion.db")
            cursor = conn.cursor()
            try:
                if is_edit:
                    user_id_to_update = usuario_existente['id']
                    # Update logic
                    base_query = "UPDATE usuarios SET nombre_completo = ?, nombre_usuario = ?, correo = ?, rol = ?, activo = ? "
                    params = [nombre_completo_input.value, nombre_usuario_input.value, correo_input.value, rol_dropdown.value, activo_switch.value]
                    if password_input.value:
                        base_query += ", password_hash = ? "
                        params.append(hash_password(password_input.value))
                    base_query += "WHERE id = ?"
                    params.append(user_id_to_update)
                    cursor.execute(base_query, tuple(params))
                else:
                    # Insert logic
                    cursor.execute("""
                        INSERT INTO usuarios (inquilino_id, nombre_usuario, password_hash, rol, nombre_completo, correo, activo)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tenant_id, nombre_usuario_input.value, hash_password(password_input.value),
                        rol_dropdown.value, nombre_completo_input.value, correo_input.value, activo_switch.value
                    ))
                conn.commit()
                page.dialog.open = False
                cargar_usuarios()
            except Exception as ex:
                print(f"Error saving user: {ex}")
            finally:
                conn.close()
                page.update()

        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Usuario" if is_edit else "Crear Nuevo Usuario"),
            content=ft.Column([
                nombre_completo_input, nombre_usuario_input, password_input, correo_input, rol_dropdown, activo_switch
            ], tight=True, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("Guardar", on_click=guardar_usuario),
            ]
        )

    def handle_open_dialog(e, usuario=None):
        page.dialog = crear_dialogo_usuario(usuario)
        page.dialog.open = True
        page.update()

    # --- MAIN VIEW WIDGETS ---
    tabla_usuarios = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Rol")),
            ft.DataColumn(ft.Text("Activo")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[]
    )

    def cargar_usuarios():
        conn = sqlite3.connect("formacion.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre_completo, rol, activo, correo, nombre_usuario FROM usuarios WHERE inquilino_id = ?", (tenant_id,))
        usuarios = cursor.fetchall()
        conn.close()

        tabla_usuarios.rows = []
        for u in usuarios:
            tabla_usuarios.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(u['id'])),
                    ft.DataCell(ft.Text(u['nombre_completo'])),
                    ft.DataCell(ft.Text(u['rol'])),
                    ft.DataCell(ft.Icon(name=ft.icons.CHECK_CIRCLE if u['activo'] else ft.icons.CANCEL, color="green" if u['activo'] else "red")),
                    ft.DataCell(ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, usr=u: handle_open_dialog(e, usr))),
                ])
            )
        page.update()

    cargar_usuarios()

    return ft.View(
        "/admin/personal",
        [
            ft.AppBar(title=ft.Text("Gestión de Personal")),
            ft.Container(
                padding=20,
                expand=True,
                content=ft.Column([
                    ft.Row([
                        ft.Text("Usuarios de la Empresa", size=22, weight="bold"),
                        ft.ElevatedButton("Crear Usuario", icon=ft.icons.ADD, on_click=handle_open_dialog)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Row([tabla_usuarios], scroll=ft.ScrollMode.ALWAYS, expand=True)
                ], expand=True)
            )
        ]
    )
