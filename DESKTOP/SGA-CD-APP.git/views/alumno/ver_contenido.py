import flet as ft
import sqlite3

def ver_contenido_view(page: ft.Page, user_id: int, clase_id: int):

    def get_content_for_class():
        conn = sqlite3.connect("formacion.db")
        cursor = conn.cursor()

        # This is a multi-step query: clase -> proceso -> plan -> temas -> contenido
        # 1. Get proceso_id from clase
        cursor.execute("SELECT proceso_id, nombre_clase FROM clases WHERE id = ?", (clase_id,))
        res = cursor.fetchone()
        if not res:
            conn.close()
            return None, None
        proceso_id, clase_name = res

        # 2. Get plan_id from proceso
        # Assuming one plan per proceso for simplicity. A real app might need a clearer link.
        cursor.execute("SELECT id FROM plan_curricular WHERE proceso_id = ?", (proceso_id,))
        res = cursor.fetchone()
        if not res:
            conn.close()
            return clase_name, {} # Return class name but empty curriculum
        plan_id = res[0]

        # 3. Get all topics and their content for that plan
        cursor.execute("""
            SELECT t.id, t.nombre_tema, t.descripcion_tema
            FROM plan_curricular_temas t
            WHERE t.plan_curricular_id = ?
            ORDER BY t.orden
        """, (plan_id,))
        topics = cursor.fetchall()

        curriculum = {}
        for topic_id, topic_name, topic_desc in topics:
            if topic_name not in curriculum:
                curriculum[topic_name] = {'description': topic_desc, 'contents': []}

            # Get content for this specific topic
            cursor.execute("""
                SELECT titulo, tipo_contenido, ruta_archivo_o_url
                FROM contenido_curricular
                WHERE tema_id = ?
            """, (topic_id,))

            for content_title, content_type, content_path in cursor.fetchall():
                 curriculum[topic_name]['contents'].append({
                    'title': content_title,
                    'type': content_type,
                    'path': content_path
                })

        conn.close()
        return clase_name, curriculum

    # --- UI Generation ---
    clase_name, curriculum_data = get_content_for_class()

    view_title = f"Material para: {clase_name}" if clase_name else "Material de Estudio"
    curriculum_controls = []

    if not curriculum_data:
        curriculum_controls.append(ft.Text("No se encontró un plan de estudios o material para esta clase."))
    else:
        for topic_name, data in curriculum_data.items():
            content_list = ft.Column(spacing=5)
            if data['contents']:
                for content in data['contents']:
                    icon = ft.icons.LINK if content['type'] == 'enlace' else ft.icons.PICTURE_AS_PDF if content['type'] == 'pdf' else ft.icons.VIDEOCAM
                    content_list.controls.append(
                        ft.ListTile(
                            title=ft.Text(content['title']),
                            leading=ft.Icon(icon),
                            on_click=lambda e, url=content['path']: page.launch_url(url) if content['type'] == 'enlace' else None,
                            subtitle=ft.Text(f"Archivo: {content['path']}", italic=True) if content['type'] != 'enlace' else ft.Text(content['path'], italic=True),
                            disabled=(content['type'] != 'enlace'),
                            tooltip="Abrir enlace" if content['type'] == 'enlace' else "Descarga de archivos no implementada"
                        )
                    )
            else:
                content_list.controls.append(ft.Text("No hay materiales para este tema.", color=ft.colors.GREY, italic=True))

            topic_card = ft.Card(
                ft.Container(
                    ft.Column([
                        ft.Text(topic_name, style=ft.TextThemeStyle.TITLE_LARGE),
                        ft.Text(data['description'] or "", italic=True, color=ft.colors.GREY_700),
                        ft.Divider(height=10),
                        content_list
                    ]),
                    padding=15
                )
            )
            curriculum_controls.append(topic_card)

    return ft.View(
        f"/alumno/contenido/{clase_id}",
        [
            ft.AppBar(title=ft.Text(view_title), bgcolor=ft.colors.SURFACE_VARIANT),
            ft.ListView(
                controls=curriculum_controls,
                expand=True,
                padding=20,
                spacing=15
            )
        ]
    )
