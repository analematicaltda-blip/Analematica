# Sistema de Gestión Académica para formación cultural y deportivo (SGA-CD)

Este es un sistema de gestión académica para formación cultural y deportivo, multifuncional y multi-inquilino, construido con Flet (Python).

## Core Features

La plataforma se basa en una arquitectura modular, con varios sistemas clave que trabajan juntos:

*   **Arquitectura Multi-Inquilino:** Permite que múltiples organizaciones (inquilinos) utilicen la misma instancia de la aplicación de forma segura y con datos completamente aislados.
*   **Control de Acceso Basado en Roles (RBAC):** Un sistema jerárquico de roles define los permisos para cada tipo de usuario, desde el Súper Administrador hasta el estudiante.
*   **Gestión de Escenarios y Reservas:** Herramientas para que los Jefes de Escenarios definan ubicaciones (por ejemplo, canchas, salones) y gestionen las reservas de las mismas.
*   **Gestión Académica:** Funcionalidades para crear clases, gestionar inscripciones y realizar un seguimiento de la asistencia de los alumnos.
*   **MILA (Módulo de Internacionalización Lingüística Aplicada):** Soporte completo para múltiples idiomas (español e inglés) en toda la interfaz de usuario.
*   **SNAT (Sistema de Notificación en Tiempo Real):** Envía notificaciones instantáneas dentro de la aplicación para eventos importantes como nuevas reservas o logros.
*   **STAR (Sistema de Trazabilidad y Auditoría de Registros):** Un registro de auditoría completo que rastrea todas las acciones críticas realizadas en el sistema.
*   **Agente de IA:** Un asistente de IA integrado (construido con LangChain) que puede ayudar a los usuarios con tareas como la generación de informes.
*   **Sitio Web Promocional y Registro:** Un sitio web público para atraer nuevos clientes, con un flujo de registro para crear nuevas cuentas de inquilinos.

## Nuevo Módulo: SIGA (Sistema Integrado de Gamificación Académica)

Para mejorar la participación y la motivación de los estudiantes, hemos introducido el módulo de gamificación SIGA.

*   **Sistema de Puntos:** Los estudiantes ganan puntos por diversas actividades, como asistir a clases, participar en eventos y completar tareas.
*   **Niveles de Progreso:** A medida que los estudiantes acumulan puntos, suben de nivel, lo que proporciona una sensación de logro.
*   **Medallas y Logros:** Los instructores pueden otorgar medallas especiales a los estudiantes por logros destacados o un rendimiento excepcional.
*   **Tablas de Clasificación (Rankings):** Se muestran tablas de clasificación semanales y generales para fomentar una competencia sana.
*   **Control de Privacidad:** Conscientes de la privacidad, los estudiantes tienen una opción de "opt-out" que les permite ocultar su nombre de las tablas de clasificación públicas si lo desean.

## Cómo Empezar

1.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Inicializar la base de datos:**
    ```bash
    python database/database_setup.py
    ```
3.  **Ejecutar la aplicación:**
    ```bash
    flet run main.py
    ```

## Estructura del Proyecto

```
/
├── api/                # Servidor API para el sitio web y el agente de IA
├── assets/             # Activos estáticos como iconos y logos
├── database/           # Configuración y scripts de la base de datos
├── gamification/       # Lógica del motor de gamificación (SIGA)
├── i18n/               # Archivos de traducción para MILA
├── utils/              # Servicios compartidos (auditoría, notificaciones)
├── views/              # Todos los archivos de la interfaz de usuario de Flet
├── website/            # Archivos para el sitio web público
├── main.py             # Punto de entrada principal de la aplicación Flet
└── requirements.txt    # Dependencias de Python
```
