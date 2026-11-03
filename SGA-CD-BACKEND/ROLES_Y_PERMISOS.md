# Definición de Roles y Permisos del Sistema SGA-CD

Este documento describe los roles de usuario, sus responsabilidades y jerarquías dentro de la plataforma SGA-CD.

---

### 1. `admin_general` (Super Administrador del Sistema)
- **Descripción:** Rol máximo con control total sobre todas las empresas y funcionalidades del sistema.
- **Funciones Clave:**
    - Acceso total y sin restricciones a todas las empresas (inquilinos).
    - Crear, modificar y eliminar empresas.
    - Gestionar roles y permisos a nivel global.
    - Monitoreo y auditoría completa del sistema (logs, actividad).
    - Gestión del sistema de cobros y suscripciones enlazado a la web.
    - Creación y gestión de promociones y descuentos.
- **Jerarquía:** Nivel más alto, no reporta a nadie.

### 2. `admin_empresa` (Administrador de Empresa/Inquilino)
- **Descripción:** Administra una única empresa o inquilino dentro del sistema.
- **Funciones Clave:**
    - Gestionar usuarios (crear, editar, eliminar) únicamente dentro de su propia empresa.
    - Asignar roles a los usuarios de su empresa (jefe_area, profesional_area, etc.).
    - Crear y gestionar las áreas de la empresa (ej. Cultura, Deportes).
    - Acceder a reportes, estadísticas y paneles de Power BI de su organización.
    - Descargar informes en formato PDF y Excel.
    - Monitoreo y auditoría de la actividad de su empresa.
- **Jerarquía:** Reporta al `admin_general`. Es el rol más alto dentro de una empresa.

### 3. `jefe_area` (Jefe de Área)
- **Descripción:** Responsable de un área específica (ej. Cultura, Deportes) dentro de una empresa.
- **Funciones Clave:**
    - Supervisar todas las actividades y personal de su área.
    - Crear, editar y eliminar eventos, salidas, disciplinas y procesos de inscripción.
    - Aprobar o rechazar solicitudes del personal a su cargo.
    - Dar de alta y gestionar a los `coordinador`, `profesor`, `jefe_escenarios` y `jefe_almacen`.
    - Definir y aprobar las reglas de gamificación para su área.
    - Acceder a reportes y auditoría de su área.
- **Jerarquía:** Reporta al `admin_empresa`. Supervisa a `coordinador`, `profesor`, etc.

### 4. `profesional_area` (Profesional de Área)
- **Descripción:** Asistente principal del `jefe_area`.
- **Funciones Clave:**
    - Crear y editar disciplinas, eventos y salidas (no puede eliminar).
    - Apoyar en la supervisión de actividades del área.
    - Aprobar solicitudes con autorización del `jefe_area`.
    - Crear y editar usuarios (no puede eliminar).
    - Proponer reglas y puntos para la gamificación.
    - Acceder a reportes del área.
- **Jerarquía:** Reporta al `jefe_area`.

### 5. `tecnico_area` (Técnico o Asistente de Área)
- **Descripción:** Brinda soporte operativo al `jefe_area` y al `profesional_area`.
- **Funciones Clave:**
    - Crear y editar disciplinas, eventos y salidas (no puede eliminar).
    - Asistir en la gestión de usuarios y solicitudes, siempre con autorización superior.
    - Acceder a reportes operativos del área.
- **Jerarquía:** Reporta al `profesional_area` y al `jefe_area`.

### 6. `coordinador` (Coordinador)
- **Descripción:** Planifica y ejecuta las actividades del día a día en un área.
- **Funciones Clave:**
    - Aprobar reglas de gamificación y disciplinas propuestas por los profesores.
    - Verificar el cumplimiento de la programación de los `profesor`.
    - Servir de enlace entre los profesores y el `jefe_area`.
- **Jerarquía:** Reporta al `jefe_area`. Supervisa a los `profesor`.

### 7. `profesor` (Instructor o Profesor)
- **Descripción:** Encargado de impartir las clases, talleres y entrenamientos.
- **Funciones Clave:**
    - Crear su plan de trabajo.
    - Registrar alumnos en sus clases.
    - Registrar asistencia y calificaciones.
    - Solicitar escenarios, eventos y salidas.
    - Solicitar permisos a los padres/acudientes.
    - Asignar puntos de gamificación a los alumnos.
- **Jerarquía:** Reporta al `coordinador` y al `jefe_area`.

### 8. `alumno` (Estudiante)
- **Descripción:** Usuario final que participa en las actividades de formación.
- **Funciones Clave:**
    - Inscribirse a cursos y eventos.
    - Consultar su horario, calificaciones y progreso.
    - Acceder a los materiales de clase.
    - Participar en el sistema de gamificación (ver puntos, medallas, ranking).
    - Solicitar elementos de inventario a su `profesor`.
- **Jerarquía:** Usuario base.

### 9. `padre_acudiente` (Padre o Acudiente)
- **Descripción:** Representante legal del `alumno`.
- **Funciones Clave:**
    - Inscribir a sus hijos/acudidos en los procesos de formación.
    - Otorgar consentimiento informado para salidas y eventos.
    - Consultar el progreso académico, asistencia y gamificación de sus acudidos.
- **Jerarquía:** Usuario externo con vistas específicas sobre los `alumno` a su cargo.

### 10. `jefe_almacen` (Jefe de Inventario / Almacenista)
- **Descripción:** Gestiona el inventario de materiales y equipos.
- **Funciones Clave:**
    - Registrar entradas y salidas de inventario.
    - Mantener el stock actualizado y generar reportes.
    - Diligenciar la hoja de vida de los elementos.
    - Entregar materiales únicamente a personal autorizado (`profesor`, `jefe_area`, etc.), no a alumnos.
- **Jerarquía:** Reporta al `jefe_area`.

### 11. `jefe_escenarios` (Jefe de Escenarios)
- **Descripción:** Responsable de la gestión de los espacios físicos (canchas, salones, etc.).
- **Funciones Clave:**
    - Administrar el calendario de reservas de los escenarios.
    - Asignar espacios para clases y eventos.
    - Coordinar el mantenimiento y la disponibilidad de los escenarios.
- **Jerarquía:** Reporta al `jefe_area`.
