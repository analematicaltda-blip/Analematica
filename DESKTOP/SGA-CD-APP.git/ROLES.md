# Documentación de Roles de Usuario y Agentes de IA

Este documento proporciona una descripción detallada de los roles de usuario en el sistema SGA-CD y su relación con la arquitectura de agentes de IA. Esta información ha sido actualizada basándose en un análisis del código fuente de la base de datos, las vistas de la interfaz y la lógica de los agentes.

## 1. Resumen de la Arquitectura

El sistema consta de dos componentes principales que **están conectados**:

1.  **Una Aplicación de Interfaz de Usuario (Flet):** Gestiona los roles de usuario, la autenticación y las vistas de la aplicación. Los usuarios interactúan con la IA a través de un componente `ChatAssistant` disponible en vistas específicas.
2.  **Un Sistema de Agentes de IA (LangGraph):** Una jerarquía de agentes de IA capaces de ejecutar tareas complejas. Son invocados desde la interfaz de usuario a través de `agent_interface.py`.

El documento anterior que indicaba que los sistemas no estaban conectados era incorrecto.

## 2. Descripción de Roles de Usuario y sus Capacidades

A continuación se detallan los roles definidos en la base de datos y sus responsabilidades deducidas del análisis de las vistas del sistema.

| Rol en DB | Nombre Común | Responsabilidades Clave | ¿Acceso a IA? |
| :--- | :--- | :--- | :--- |
| `admin_general` | Super Administrador | Gestiona toda la plataforma, incluyendo múltiples inquilinos. | **Sí** |
| `admin_empresa` | Administrador de Inquilino | Gestiona un único inquilino: personal, áreas, suscripción y auditoría. | **Sí** |
| `jefe_area` | Jefe de Área | Gestiona un área ('Cultura' o 'Deportes'), incluyendo equipo, eventos y análisis de datos. | **Sí** |
| `jefe_escenarios` | Jefe de Escenarios | Gestiona la creación de escenarios físicos (canchas, salones) y sus reservas. | **Sí** |
| `jefe_almacen` | Jefe de Almacén | Rol de supervisión para el inventario. No tiene vistas de IA dedicadas. | No |
| `coordinador` | Coordinador | Rol de gestión de nivel medio, reporta a un Jefe de Área. | **Sí** |
| `profesor` | Profesor / Instructor | Gestiona currículo, clases, calendarios y seguimiento de alumnos. | **Sí** |
| `alumno` | Alumno / Estudiante | Se inscribe y participa en clases, ve su progreso y contenido. | **Sí** |
| `almacenista` | Almacenista | Gestiona el préstamo y devolución de elementos de inventario. | **Sí** |
| `profesional` | Profesional | Rol de personal genérico, probablemente con acceso a un dashboard limitado. | No |
| `tecnico` | Técnico | Rol de personal genérico, probablemente con acceso a un dashboard limitado. | No |
| `asistencial` | Asistencial | Rol de personal genérico, probablemente con acceso a un dashboard limitado. | No |

## 3. Mapeo de Roles de Usuario a Agentes de IA

El acceso a los agentes de IA se proporciona a través del componente `ChatAssistant` en las vistas principales de ciertos roles. Cuando un usuario en uno de estos roles interactúa con el chat, se invoca a un agente "Coronel" de alto nivel.

El `área` de responsabilidad del usuario (p. ej., 'Cultura' o 'Deportes') determina qué Coronel se invoca:

*   **Jefe de Área (Cultura):** Invoca a `formacion_cultura_colonel`.
*   **Jefe de Área (Deportes):** Invoca a `formacion_deportiva_colonel`.
*   **Otros roles con acceso a la IA:** Probablemente invocan a uno de los dos coroneles dependiendo del contexto de la sesión del usuario, aunque la lógica exacta puede variar por vista.

**Roles con capacidad confirmada para dar órdenes a la IA:**

*   `admin_general`
*   `admin_empresa`
*   `jefe_area`
*   `jefe_escenarios`
*   `coordinador`
*   `profesor`
*   `alumno`
*   `almacenista`

Los roles `jefe_almacen`, `profesional`, `tecnico`, y `asistencial` no tienen una interfaz de chat visible en el código y, por lo tanto, no pueden dar órdenes directas a la jerarquía de agentes.
