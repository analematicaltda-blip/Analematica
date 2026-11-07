-- =================================================================
-- Script de Migración de Base de Datos para Implementar RBAC
-- =================================================================
-- Este script crea las tablas necesarias para el nuevo sistema de
-- control de acceso basado en roles (RBAC).
--
-- **IMPORTANTE:** Haga una copia de seguridad de su base de datos
-- antes de ejecutar este script. Este script está escrito para
-- PostgreSQL. Es posible que necesite pequeñas adaptaciones para
-- otras bases de datos (ej. cambiar SERIAL por AUTO_INCREMENT en MySQL).
--
-- A ser ejecutado por el `admin_general`.
-- =================================================================

BEGIN;

-- Paso 1: Crear la tabla `roles` para almacenar la definición de roles.
-- Esta tabla servirá como un catálogo central de todos los roles disponibles en el sistema.
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Imprime un aviso en la consola de psql
\echo 'Tabla `roles` creada o ya existente.'

-- Paso 2: Poblar la tabla `roles` con los 11 roles oficiales del sistema.
-- Paso 2: Poblar la tabla `roles` con los 12 roles oficiales del sistema.
-- Se utiliza `ON CONFLICT (nombre) DO NOTHING` para evitar errores si los roles ya existen.
INSERT INTO roles (nombre, descripcion) VALUES
('admin_general', 'Super Administrador del Sistema con acceso total.'),
('admin_empresa', 'Administrador de una empresa/inquilino específico.'),
('jefe_area', 'Jefe de un área específica como Cultura o Deportes.'),
('profesional_area', 'Asistente principal del Jefe de Área.'),
('tecnico_area', 'Soporte operativo para un área.'),
('coordinador', 'Coordina actividades y al personal de instructores.'),
('profesor', 'Instructor o profesor que imparte clases.'),
('alumno', 'Estudiante que recibe la formación.'),
('padre_acudiente', 'Representante legal de uno o más alumnos.'),
('jefe_almacen', 'Gestiona el inventario de materiales y equipos.'),
('almacenista', 'Asistente de almacén, reporta al Jefe de Almacén.'),
('jefe_escenarios', 'Gestiona la disponibilidad de los espacios físicos.')
ON CONFLICT (nombre) DO NOTHING;

\echo 'Tabla `roles` poblada con los 12 roles oficiales.'

-- Paso 3: Crear la tabla `user_roles` para la relación muchos-a-muchos.
-- Esto permite que un usuario pueda tener múltiples roles.
-- La tabla `usuario` es la tabla de usuarios existente.
CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE (user_id, role_id)
);

\echo 'Tabla `user_roles` creada o ya existente.'

-- Paso 4: Nota sobre la migración de datos y la eliminación de la columna antigua.
\echo '--------------------------------------------------------------------------------'
\echo 'PASOS MANUALES IMPORTANTES:'
\echo '1. MIGRACIÓN DE DATOS: Si tiene usuarios existentes, debe migrar sus roles de la'
\echo '   antigua columna `usuario.rol` a la nueva tabla `user_roles`.'
\echo '   Ejemplo conceptual: INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM usuario u JOIN roles r ON u.rol::text = r.nombre;'
\echo ''
\echo '2. ELIMINACIÓN DE COLUMNA ANTIGUA: Una vez verificada la migración, considere'
\echo '   eliminar la columna `rol` de la tabla `usuario` para limpiar el esquema:'
\echo '   `ALTER TABLE usuario DROP COLUMN rol;`'
\echo '--------------------------------------------------------------------------------'

COMMIT;

-- =================================================================
-- Fin del script.
-- =================================================================
