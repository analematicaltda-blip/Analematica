import asyncio
import sqlite3
import time
import random
from agent.agent_interface import invoke_agent_for_area

# -----------------------------------------------------------------------------
# !! ADVERTENCIA CRÍTICA DE RECURSOS !!
# -----------------------------------------------------------------------------
# Este script está configurado para generar una carga EXTREMA
# (100,000,000 de solicitudes concurrentes) en el sistema de agentes.
#
# !! NO EJECUTAR BAJO NINGUNA CIRCUNSTANCIA EN MÁQUINAS CONVENCIONALES !!
#
# La ejecución de este script requiere una máquina cliente de alto rendimiento
# con una cantidad masiva de memoria RAM (probablemente > 64GB) y un gran
# número de núcleos de CPU para manejar la creación de 100 millones de
# tareas de asyncio.
#
# El fallo del script es más probable que ocurra por agotamiento de recursos
# en la máquina cliente que por un problema en el servidor.
# Para una prueba de esta magnitud, se recomienda un framework de pruebas
# de carga distribuido (ej. Locust, k6).
# -----------------------------------------------------------------------------


# --- Definición de Órdenes de Prueba por Rol ---
ORDENES_POR_ROL = {
    "jefe_area": [
        "genera un reporte de los 5 profesores con más clases asignadas este mes en mi área",
        "resume el progreso general de los alumnos en el último trimestre",
        "¿cuál es el escenario más utilizado para eventos de mi área?",
        "dame una lista de coordinadores que no han reportado actividades esta semana",
        "propón un plan de mejora para el área basado en la asistencia del último mes",
        "identifica a los 3 alumnos con mayor progreso en gamificación",
        "crea un borrador de notificación para un nuevo evento la próxima semana",
        "¿cuántas clases se cancelaron el mes pasado?",
        "genera una lista de los recursos de inventario más solicitados por los profesores",
        "resume los comentarios del último foro de la clase más popular"
    ],
    "admin_empresa": [
        "genera un reporte de auditoría de las acciones del último jefe de área contratado",
        "dame un resumen de la actividad de la plataforma en los últimos 7 días",
        "¿cuál es el rol con más usuarios activos?",
        "lista todos los usuarios creados en el último mes",
        "verifica el estado de la suscripción actual",
        "genera un reporte demográfico de todos los alumnos",
        "¿cuántas áreas están actualmente sin un jefe de área asignado?",
        "resume el uso de la IA por los diferentes roles",
        "dame una lista de todo el personal y a quién reportan",
        "propón una optimización para la asignación de recursos de la plataforma"
    ],
    "coordinador": [
        "genera un listado de las clases de la próxima semana",
        "resume la asistencia de los alumnos bajo mi coordinación",
        "identifica profesores que necesiten apoyo por baja asistencia de alumnos",
        "crea un borrador de evento para una reunión de padres",
        "lista los próximos 5 eventos programados",
        "¿qué alumnos tienen una asistencia perfecta este mes?",
        "dame un resumen de los recursos de inventario disponibles",
        "propón un horario para una nueva clase de refuerzo los viernes",
        "lista todos los profesores en mi área de coordinación",
        "resume el feedback de los alumnos sobre la clase 'Introducción al Deporte'"
    ],
    "profesor": [
        "resume el progreso de mi alumno 'Juan Pérez'",
        "genera una idea para una actividad de gamificación para mi próxima clase",
        "lista los alumnos con baja asistencia en mi clase de 'Técnicas Avanzadas'",
        "crea un borrador de notificación para recordar una tarea importante",
        "¿cuál es el tema del currículo que más dificultades presenta a los alumnos?",
        "reserva el 'Gimnasio B' para mi clase del próximo lunes a las 10am",
        "solicita 5 balones nuevos del inventario",
        "registra la asistencia de hoy para la clase de 'Teoría del Arte'",
        "dame un resumen de los comentarios en el foro de mi última clase",
        "propón una medalla para el alumno más participativo"
    ],
    "alumno": [
        "¿cuál es mi próxima clase?",
        "muéstrame mi progreso en el curso de 'Guitarra'",
        "¿cuántos puntos de gamificación tengo?",
        "¿cuáles son los próximos eventos de Cultura?",
        "inscríbeme a la clase de 'Teatro Avanzado'",
        "¿cómo puedo ganar la medalla 'Madrugador'?",
        "muéstrame el ranking de mi clase",
        "¿cuál es el material de estudio para el próximo examen?",
        "envía un mensaje a mi profesor preguntando sobre la tarea",
        "dame un resumen de la última clase a la que falté"
    ],
    "almacenista": [
        "genera un reporte de los elementos con bajo stock",
        "¿cuál es el elemento más prestado este mes?",
        "registra la devolución de 3 balones por parte del profesor 'Carlos Ruiz'",
        "dame el historial de préstamos del proyector multimedia",
        "crea una solicitud de compra para 10 nuevos uniformes",
        "¿qué elementos están actualmente prestados y no han sido devueltos a tiempo?",
        "lista todo el inventario del área de 'Deportes'",
        "asigna el código 'EQ-055' a las nuevas colchonetas",
        "da de baja el equipo 'V-002' por daño",
        "genera un resumen de la actividad del almacén para esta semana"
    ],
    "jefe_escenarios": [
        "muéstrame el calendario de reservas para la 'Cancha Principal' la próxima semana",
        "¿cuál es el escenario con mayor tasa de ocupación?",
        "genera un reporte de mantenimiento para todos los escenarios",
        "crea una reserva para un evento especial del 'admin_empresa' el próximo sábado",
        "cancela la reserva #5890 y notifica al usuario",
        "lista todos los escenarios que no tienen reservas para mañana",
        "propón un plan para optimizar el uso de los salones de música",
        "¿quién fue el último usuario en reservar el 'Teatro al Aire Libre'?",
        "genera un informe de todos los eventos realizados este mes",
        "bloquea el 'Salón de Danza' por mantenimiento para todo el día de mañana"
    ]
}
ORDENES_POR_ROL['admin_general'] = ORDENES_POR_ROL['admin_empresa']

TARGET_TOTAL_REQUESTS = 100_000_000

async def run_load_test():
    """
    Ejecuta una prueba de carga concurrente contra el sistema de agentes de IA.
    """
    print("--- Iniciando Prueba de Carga Masiva del Sistema de Agentes ---")
    print(f"--- Objetivo: {TARGET_TOTAL_REQUESTS:,} solicitudes concurrentes ---")
    db_path = 'formacion.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT u.id, u.rol, u.inquilino_id, u.nombre_usuario FROM usuarios u JOIN inquilinos i ON u.inquilino_id = i.id WHERE i.nombre_empresa = 'Inquilino de Pruebas'")
        test_users = cursor.fetchall()
        conn.close()

        if not test_users:
            print("\n⚠️  Error Crítico: No se encontraron usuarios de prueba. Asegúrate de ejecutar 'create_test_users.py' primero.")
            return

        users_with_ai_access = [u for u in test_users if u[1] in ORDENES_POR_ROL]
        if not users_with_ai_access:
            print("No se encontraron usuarios de prueba con roles que tengan acceso a la IA.")
            return

        print(f"Se encontraron {len(users_with_ai_access)} perfiles de usuario con acceso a IA para la prueba.")

        requests_per_user = TARGET_TOTAL_REQUESTS // len(users_with_ai_access)
        print(f"Se generarán aproximadamente {requests_per_user:,} solicitudes por usuario.")

        tasks = []
        for user_id, role, tenant_id, username in users_with_ai_access:
            area_context = 'Cultura'
            if 'deportes' in username:
                area_context = 'Deportes'

            for i in range(requests_per_user):
                orden = random.choice(ORDENES_POR_ROL[role])
                task = asyncio.create_task(
                    invoke_agent_for_area(
                        area=area_context,
                        user_input=f"{orden} (req:{i+1})", # Añadir un ID único a la orden
                        user_id=user_id,
                        tenant_id=tenant_id
                    )
                )
                tasks.append(task)

        total_requests = len(tasks)
        if not tasks:
            print("No se generaron tareas para la prueba.")
            return

        print(f"\n🚀 Lanzando {total_requests:,} órdenes concurrentes al sistema de agentes...")
        start_time = time.time()

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        duration = end_time - start_time

        print("\n--- Resultados de la Prueba de Carga ---")
        success_count = 0
        error_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # print(f"  - Tarea {i+1}: ❌ Falló con error: {result}")
                error_count += 1
            else:
                success_count += 1

        if error_count > 0:
            print(f"Se encontraron {error_count:,} errores durante la ejecución. Mostrando el primero:")
            for r in results:
                if isinstance(r, Exception):
                    print(r)
                    break

        print("\n--- Resumen de Rendimiento ---")
        print(f"Tiempo total de ejecución: {duration:.2f} segundos")
        print(f"Total de solicitudes: {total_requests:,}")
        print(f"Solicitudes exitosas: {success_count:,}")
        print(f"Solicitudes fallidas: {error_count:,}")
        if duration > 0:
            rps = total_requests / duration
            print(f"Rendimiento: {rps:.2f} solicitudes por segundo")

    except Exception as e:
        print(f"\nOcurrió un error durante la prueba de carga: {e}")

if __name__ == "__main__":
    asyncio.run(run_load_test())
