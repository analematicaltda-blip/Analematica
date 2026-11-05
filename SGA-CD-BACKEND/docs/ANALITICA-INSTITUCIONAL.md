# Modelo institucional y autorización

Las rutas están bajo `/api/v1/workspace/institutional`. La identidad y los permisos se resuelven desde la base de datos, no desde los parámetros de URL. La empresa del usuario delimita todas las consultas. La revisión entre entidades es exclusiva del dueño. El personal administrativo se limita a sus áreas asignadas o heredadas por la cadena de supervisión, con detección de ciclos. Sin área asignada no se inventa acceso global.

## Modelo y medidas

Inscripcion → Alumno → Usuario y Clase → ProcesoFormacion conservan sus tablas originales. `institutional_process_specialties` relaciona procesos con el catálogo; `institutional_enrollment_events` registra de manera acumulativa estados y motivos. No se alteran ni se eliminan inscripciones existentes.

- Estudiantes: personas únicas en el conjunto filtrado. Una persona inscrita en dos clases cuenta una vez.
- Inscripciones: registros de matrícula; una persona puede tener varios.
- Activas: último estado explícito `activa` al cierre del periodo.
- Deserciones: último estado explícito `retirada` con motivo `desercion`. No se deducen de cuentas inactivas.
- Oferta deportiva/cultural: especialidades activas adoptadas, respetando filtros vertical/especialidad.
- Calidad: registros sin estado, sin especialidad o sin fecha; no se reemplazan por ejemplos.

Las fechas de inicio y fin seleccionan la cohorte por fecha de inscripción. El estado corresponde al último evento hasta el cierre inclusivo del día en la zona IANA seleccionada. La tendencia distingue ingresos de eventos de deserción. Las claves de dimensiones ajenas a la entidad no se resuelven ni exponen. Las consultas rechazan relaciones de alumno/clase fuera de la entidad.

## Presentación y captura

Tarjetas KPI, barras por especialidad, distribución de estados, tendencia mensual y tabla detallada. Segmentadores: vertical, especialidad, proceso, profesor, escenario, grupo, género, grupo etario, barrio y estado, además del periodo. Se presentan datos agregados, exportación CSV segura y vista para impresión. La lectura se actualiza cada cinco segundos mientras la página está visible; se informa la última lectura y se conserva ante un error transitorio. No es una integración con Microsoft Power BI ni una conexión push.

La empresa adopta las especialidades y vincula sus procesos. Administración registra estados y motivos con fecha efectiva; no se reclasifica retrospectivamente información desconocida. La creación de equipo valida la autoridad funcional del actor, correo único, contraseña y áreas permitidas. La asignación de supervisor valida entidad y ausencia de ciclos. No se envían correos ni se crean contraseñas predeterminadas.

## Verificación

Pruebas ORM/API en `tests/test_institutional_panels.py`; navegador en `../SGA-CD-WEB.git/tests/institutional.cjs`. Se prueban planes reales, revisiones del dueño, herencia Full, restricciones explícitas, aislamiento, personas frente a inscripciones, deserción explícita, catálogo, equipo y adaptación a pantallas.

Resultado del 4 de noviembre de 2026: 16 pruebas institucionales y 32 regresiones de backend aprobadas; 111 recorridos institucionales en Chromium (11 roles, dos planes, cuatro anchos para revisión, más sesiones reales simuladas), 16 recorridos de campañas, publicador y service worker aprobados. El navegador usa respuestas controladas para la matriz completa. Además se verificó el servicio real con Nginx, JWT y PostgreSQL: 3 estudiantes, 4 inscripciones y 1 deserción con datos señalados de validación. Backend, nodo 6 y scheduler quedaron saludables en el entorno de validación. Los envíos externos permanecieron deshabilitados. Las capturas corresponden al entorno de validación, no a datos de clientes.
