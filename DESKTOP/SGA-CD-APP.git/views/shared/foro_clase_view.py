import flet as ft
import sqlite3
from datetime import datetime
from utils.notification_service import create_notification

def get_or_create_foro(clase_id: int, inquilino_id: int, clase_name: str):
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM foros_clases WHERE clase_id = ?", (clase_id,))
    foro = cursor.fetchone()
    if foro:
        conn.close()
        return foro[0]
    else:
        # Create a new forum for this class
        nombre_foro = f"Foro para la clase: {clase_name}"
        cursor.execute(
            "INSERT INTO foros_clases (clase_id, inquilino_id, nombre_foro) VALUES (?, ?, ?)",
            (clase_id, inquilino_id, nombre_foro)
        )
        foro_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return foro_id

def foro_clase_view(page: ft.Page, user_id: int, tenant_id: int, clase_id: int):

    # Fetch initial data
    conn = sqlite3.connect("formacion.db")
    clase_info = conn.execute("SELECT nombre_clase FROM clases WHERE id = ?", (clase_id,)).fetchone()
    conn.close()

    if not clase_info:
        return ft.View(f"/clase/{clase_id}/foro", [ft.AppBar(title=ft.Text("Error")), ft.Text("Clase no encontrada.")])

    clase_name = clase_info[0]
    foro_id = get_or_create_foro(clase_id, tenant_id, clase_name)

    def load_threads():
        threads_list.controls.clear()
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT h.id, h.titulo, u.nombre_completo, h.timestamp
            FROM foros_hilos h
            JOIN usuarios u ON h.creado_por_usuario_id = u.id
            WHERE h.foro_id = ?
            ORDER BY h.timestamp DESC
        """, (foro_id,))
        threads = cursor.fetchall()
        conn.close()

        if not threads:
            threads_list.controls.append(ft.Text("No hay temas de discusión. ¡Crea el primero!"))
        else:
            for thread_id, titulo, autor, ts in threads:
                threads_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(titulo, weight="bold"),
                        subtitle=ft.Text(f"Iniciado por {autor} el {ts}"),
                        on_click=lambda e, t_id=thread_id: view_thread(t_id) # Placeholder
                    )
                )
        page.update()

    # --- UI Controls ---
    threads_list = ft.ListView(expand=True, spacing=10)
    posts_view = ft.Column(visible=False, expand=True, scroll=ft.ScrollMode.AUTO)
    main_content = ft.Stack(
        [
            ft.Column([
                ft.ElevatedButton("Crear Nuevo Hilo", icon=ft.icons.ADD, on_click=lambda e: open_new_thread_dialog()),
                ft.Divider(),
                ft.Text("Temas de Discusión", style=ft.TextThemeStyle.HEADLINE_SMALL),
                threads_list,
            ], expand=True, spacing=10),
            posts_view,
        ],
        expand=True
    )

    # --- New Thread Dialog ---
    new_thread_title = ft.TextField(label="Título del Hilo")
    new_thread_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Crear Nuevo Hilo de Discusión"),
        content=new_thread_title,
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(new_thread_dialog, "open", False) or page.update()),
            ft.FilledButton("Crear", on_click=lambda e: create_new_thread()),
        ]
    )

    def open_new_thread_dialog():
        new_thread_title.value = ""
        page.dialog = new_thread_dialog
        new_thread_dialog.open = True
        page.update()

    def create_new_thread():
        if not new_thread_title.value:
            return
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO foros_hilos (foro_id, titulo, creado_por_usuario_id, timestamp) VALUES (?, ?, ?, ?)",
            (foro_id, new_thread_title.value, user_id, datetime.now().isoformat())
        )
        hilo_id = cursor.lastrowid
        conn.commit()

        # Notify participants
        cursor.execute("SELECT i.alumno_id FROM inscripciones i WHERE i.clase_id = ?", (clase_id,))
        # The result of fetchall is a list of tuples, so we get the first element of each tuple
        participants = [row[0] for row in cursor.fetchall()]

        instructor_id_result = cursor.execute("SELECT instructor_id FROM clases WHERE id = ?", (clase_id,)).fetchone()
        if instructor_id_result:
            instructor_id = instructor_id_result[0]
            if instructor_id not in participants:
                participants.append(instructor_id)

        for p_id in participants:
            if p_id != user_id: # Don't notify the person who created the thread
                create_notification(tenant_id, p_id, f"Nuevo hilo en '{clase_name}': {new_thread_title.value[:30]}...", page.pubsub)

        conn.close()
        new_thread_dialog.open = False
        load_threads() # Refresh the list
        page.update()

    # --- Thread and Posts View Logic ---
    reply_field = ft.TextField(label="Escribir una respuesta...", multiline=True, expand=True)

    def add_reply(thread_id):
        if not reply_field.value:
            return
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO foros_publicaciones (hilo_id, usuario_id, contenido, timestamp) VALUES (?, ?, ?, ?)",
            (thread_id, user_id, reply_field.value, datetime.now().isoformat())
        )
        conn.commit()

        # Notify participants
        hilo_title = cursor.execute("SELECT titulo FROM foros_hilos WHERE id = ?", (thread_id,)).fetchone()[0]
        cursor.execute("SELECT i.alumno_id FROM inscripciones i WHERE i.clase_id = ?", (clase_id,))
        participants = [row[0] for row in cursor.fetchall()]

        instructor_id_result = cursor.execute("SELECT instructor_id FROM clases WHERE id = ?", (clase_id,)).fetchone()
        if instructor_id_result:
            instructor_id = instructor_id_result[0]
            if instructor_id not in participants:
                participants.append(instructor_id)

        for p_id in participants:
            if p_id != user_id:
                create_notification(tenant_id, p_id, f"Nueva respuesta en '{hilo_title[:20]}...'", page.pubsub)

        conn.close()
        reply_field.value = ""
        view_thread(thread_id) # Refresh the thread view
        page.update()

    def view_thread(thread_id):
        posts_view.controls.clear()
        main_content.controls[0].visible = False # Hide thread list

        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.contenido, u.nombre_completo, p.timestamp
            FROM foros_publicaciones p
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.hilo_id = ?
            ORDER BY p.timestamp ASC
        """, (thread_id,))
        posts = cursor.fetchall()

        # Get thread title
        thread_title = cursor.execute("SELECT titulo FROM foros_hilos WHERE id = ?", (thread_id,)).fetchone()[0]
        conn.close()

        post_items = []
        if not posts:
            post_items.append(ft.Text("No hay publicaciones en este hilo. ¡Sé el primero en responder!"))
        else:
            for post_id, contenido, autor, ts in posts:
                post_items.append(
                    ft.Card(
                        content=ft.Container(
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.CHAT_BUBBLE),
                                title=ft.Text(contenido),
                                subtitle=ft.Text(f"Publicado por {autor} el {ts}")
                            ),
                            padding=10
                        )
                    )
                )

        posts_view.controls.extend([
            ft.Row([
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=show_thread_list, tooltip="Volver a la lista de hilos"),
                ft.Text(thread_title, style=ft.TextThemeStyle.HEADLINE_SMALL)
            ]),
            ft.Column(post_items, spacing=10, scroll=ft.ScrollMode.AUTO),
            ft.Divider(),
            ft.Row([reply_field, ft.IconButton(icon=ft.icons.SEND, on_click=lambda e: add_reply(thread_id))])
        ])
        posts_view.visible = True
        page.update()

    def show_thread_list(e):
        posts_view.visible = False
        main_content.controls[0].visible = True
        page.update()

    # Initial load
    load_threads()

    return ft.View(
        f"/clase/{clase_id}/foro",
        [
            ft.AppBar(title=ft.Text(f"Foro: {clase_name}"), bgcolor=ft.colors.SURFACE_VARIANT),
            main_content
        ],
        padding=10
    )
