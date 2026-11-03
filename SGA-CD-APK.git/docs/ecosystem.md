# Arquitectura y Ecosistema del SGA-CD

Este documento describe la arquitectura técnica y los componentes modulares que conforman el Sistema de Gestión Académica para formación cultural y deportivo (SGA-CD).

## Arquitectura General

El SGA-CD está construido sobre una arquitectura modular que separa las diferentes preocupaciones de la aplicación.

*   **Aplicación Principal (Flet):** El corazón de la plataforma es una aplicación de escritorio y web construida con el framework Flet. Orquesta toda la interfaz de usuario para los usuarios autenticados.
*   **Base de Datos (SQLite):** Una única base de datos SQLite (`formacion.db`) actúa como la fuente central de verdad para toda la aplicación, asegurando la consistencia de los datos. El esquema está diseñado para ser multi-inquilino, con un `inquilino_id` que aísla los datos de cada organización cliente.
*   **Servidor API (Flask):** Una API ligera basada en Flask (`api/api_server.py`) se ejecuta como un proceso separado. Su propósito es doble:
    1.  Proporcionar puntos finales (endpoints) para el sitio web público (por ejemplo, para el registro de nuevos inquilinos).
    2.  Servir como backend para el agente de IA, permitiéndole consultar datos de la base de datos de forma segura.
*   **Sitio Web Público:** Un sitio web estático (`website/`) sirve como la cara pública de la plataforma. Está construido con HTML, CSS y JavaScript y se comunica con la API de Flask para la funcionalidad dinámica.

## Subsistemas con Nombre

Hemos desarrollado varios subsistemas reutilizables, cada uno con un acrónimo, que proporcionan funcionalidades clave en toda la plataforma.

### MILA (Módulo de Internacionalización Lingüística Aplicada)
*   **Componentes:** `i18n/`, `utils/i18n_service.py`
*   **Descripción:** MILA es el servicio de traducción. Carga cadenas de texto desde archivos JSON (uno para cada idioma admitido, por ejemplo, `es.json`, `en.json`) y las proporciona a la interfaz de usuario. Esto permite que toda la aplicación cambie de idioma dinámicamente.

### SNAT (Sistema de Notificación en Tiempo Real)
*   **Componentes:** `utils/notification_service.py`, `views/components/notification_bell.py`
*   **Descripción:** SNAT utiliza la funcionalidad Pub/Sub integrada de Flet para enviar notificaciones en tiempo real a los clientes conectados. Cuando ocurre un evento importante (por ejemplo, una nueva reserva), el servicio publica un mensaje en un tema específico del usuario, y el componente de la campana de notificación en la UI del usuario recibe la alerta al instante.

### STAR (Sistema de Trazabilidad y Auditoría de Registros)
*   **Componentes:** `utils/audit_logger.py`, `views/admin_empresa/audit_log_view.py`
*   **Descripción:** STAR es el sistema de registro de auditoría. Proporciona una función simple para registrar eventos críticos (por ejemplo, `log_event(user_id, 'user_login', 'User logged in successfully')`). Estos eventos se almacenan en la tabla `audit_log` y pueden ser revisados por los administradores de inquilinos para monitorear la actividad y mejorar la seguridad.

### SIGA (Sistema Integrado de Gamificación Académica)
*   **Componentes:** `gamification/engine.py`, `views/alumno/mi_progreso.py`, `views/profesor/gamificacion_dashboard.py`, `views/shared/rankings_view.py`
*   **Descripción:** SIGA es el motor de gamificación. Está diseñado para aumentar la participación de los estudiantes.
    *   El **motor** (`engine.py`) contiene la lógica para definir acciones que otorgan puntos y para procesar estos eventos.
    *   Las **vistas de alumno** muestran el progreso (puntos, nivel, medallas) y permiten el control de la privacidad.
    *   Las **vistas de profesor** permiten monitorear el progreso de los estudiantes y otorgar logros.
    *   La **vista de rankings** consume los datos de gamificación para mostrar tablas de clasificación, respetando la configuración de privacidad de cada usuario.
