import sqlite3

def setup_database():
    """Crea todas las tablas necesarias para la aplicación en la base de datos formacion.db."""
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()

    # --- 0. Tabla de Inquilinos (Tenants) ---
    # La tabla principal para el modelo SaaS. Cada empresa cliente es un inquilino.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquilinos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_empresa TEXT NOT NULL,
        fecha_suscripcion TEXT,
        plan TEXT, -- 'gratis', 'mensual', 'anual'
        api_key TEXT UNIQUE,
        google_api_key TEXT, -- For per-tenant AI features
        activo INTEGER DEFAULT 1,
        -- New location columns
        direccion TEXT,
        municipio TEXT,
        pais TEXT,
        latitud REAL,
        longitud REAL
    );
    """)

    # --- 1. Gestión de Usuarios y Roles (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre_usuario TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin_empresa', 'admin_general', 'jefe_area', 'coordinador', 'profesor', 'alumno', 'almacenista', 'jefe_almacen', 'jefe_escenarios')),
        nombre_completo TEXT,
        correo TEXT,
        reporta_a_usuario_id INTEGER, -- For hierarchy
        reset_token TEXT,
        reset_token_expires TEXT,
        activo INTEGER DEFAULT 1,
        UNIQUE(inquilino_id, nombre_usuario),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (reporta_a_usuario_id) REFERENCES usuarios(id)
    );
    """)

    # --- 2. Tablas Específicas por Rol (Ahora con inquilino_id) ---
    # Nota: El inquilino_id se puede obtener a través de la tabla de usuarios,
    # pero añadirlo aquí simplifica las consultas y el aislamiento de datos.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        area TEXT NOT NULL CHECK(area IN ('Cultura', 'Deportes')),
        telefono TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS jefes_area (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        area_responsabilidad TEXT CHECK(area_responsabilidad IN ('Cultura', 'Deportes')), -- Now nullable
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS coordinadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        jefe_area_id INTEGER,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (jefe_area_id) REFERENCES jefes_area(id)
    );

    CREATE TABLE IF NOT EXISTS jefes_almacen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS jefes_escenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alumnos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        tipo_documento TEXT,
        documento TEXT,
        fecha_nacimiento TEXT,
        genero TEXT,
        grupo_etario TEXT,
        escolaridad TEXT,
        discapacidad TEXT,
        grupo_poblacional TEXT,
        barrio TEXT,
        vereda TEXT,
        resguardo TEXT,
        zona_geografica TEXT,
        telefono TEXT,
        UNIQUE(inquilino_id, documento),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS almacenistas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        area_almacen TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    # --- 3. Tablas de Gestión Académica (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS procesos_formacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre_proceso TEXT NOT NULL,
        tipo_proceso TEXT,
        descripcion TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS escenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        ubicacion TEXT,
        capacidad INTEGER,
        tipo TEXT,
        area TEXT CHECK(area IN ('Cultura', 'Deportes')), -- Can be NULL if it's a general tenant scenario
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );

    CREATE TABLE IF NOT EXISTS escenario_partes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        escenario_id INTEGER NOT NULL,
        nombre_parte TEXT NOT NULL, -- e.g., "Cancha Principal", "Salón A"
        descripcion TEXT,
        capacidad INTEGER,
        area TEXT CHECK(area IN ('Cultura', 'Deportes')),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (escenario_id) REFERENCES escenarios(id)
    );

    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        escenario_parte_id INTEGER NOT NULL,
        usuario_id_reserva INTEGER NOT NULL,
        proposito TEXT, -- "Clase", "Evento", "Reunión", etc.
        descripcion_proposito TEXT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        estado TEXT DEFAULT 'Confirmada', -- "Confirmada", "Cancelada"
        area TEXT CHECK(area IN ('Cultura', 'Deportes')),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (escenario_parte_id) REFERENCES escenario_partes(id),
        FOREIGN KEY (usuario_id_reserva) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre_clase TEXT,
        proceso_id INTEGER,
        instructor_id INTEGER,
        fecha TEXT,
        hora_inicio TEXT,
        hora_fin TEXT,
        escenario_id INTEGER,
        espacio TEXT,
        grupo TEXT,
        novedad TEXT,
        area TEXT NOT NULL CHECK(area IN ('Cultura', 'Deportes')),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (proceso_id) REFERENCES procesos_formacion(id),
        FOREIGN KEY (instructor_id) REFERENCES profesores(id),
        FOREIGN KEY (escenario_id) REFERENCES escenarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inscripciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        alumno_id INTEGER,
        clase_id INTEGER,
        fecha_inscripcion TEXT,
        nivel_formacion TEXT,
        area TEXT NOT NULL CHECK(area IN ('Cultura', 'Deportes')),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        alumno_id INTEGER,
        clase_id INTEGER,
        fecha_hora TEXT,
        evidencia_path TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    # --- 4. Tablas de Gestión de Inventario (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elementos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        codigo TEXT NOT NULL,
        descripcion TEXT,
        area TEXT CHECK(area IN ('Cultura', 'Deportes')),
        UNIQUE(inquilino_id, codigo),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        elemento_id INTEGER,
        instructor_id INTEGER,
        almacenista_id INTEGER,
        fecha_prestamo TEXT,
        observaciones_prestamo TEXT,
        foto_prestamo TEXT,
        estado TEXT,
        fecha_entrega TEXT,
        observaciones_entrega TEXT,
        foto_entrega TEXT,
        estado_entrega TEXT,
        area TEXT CHECK(area IN ('Cultura', 'Deportes')),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (elemento_id) REFERENCES elementos(id),
        FOREIGN KEY (instructor_id) REFERENCES profesores(id),
        FOREIGN KEY (almacenista_id) REFERENCES almacenistas(id)
    );
    """)

    # --- 5. Tablas para Listas Desplegables (Pueden ser por inquilino o globales) ---
    # Por ahora, las haremos por inquilino para máxima flexibilidad.
    dropdown_tables = [
        "generos", "grupos_etarios", "tipos_documento", "escolaridades",
        "discapacidades", "grupos_poblacionales", "barrios", "veredas", "resguardos",
        "tipos_escenario"
    ]
    for table_name in dropdown_tables:
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inquilino_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            UNIQUE(inquilino_id, nombre),
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
        );
        """)

    # --- Tablas adicionales (Ahora con inquilino_id) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        tipo TEXT NOT NULL CHECK(tipo IN ('evento', 'salida')), -- 'evento' o 'salida' (viaje)
        alcance TEXT NOT NULL CHECK(alcance IN ('nacional', 'regional', 'internacional')),
        area TEXT NOT NULL CHECK(area IN ('Cultura', 'Deportes')),
        fecha_inicio TEXT,
        fecha_fin TEXT,
        lugar TEXT,
        creado_por_usuario_id INTEGER, -- Creado por el Jefe de Área
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (creado_por_usuario_id) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evento_participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        evento_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        rol_participacion TEXT, -- e.g., 'competidor', 'asistente', 'organizador'
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (evento_id) REFERENCES eventos(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notificaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        usuario_id INTEGER,
        mensaje TEXT,
        fecha_hora TEXT,
        leido INTEGER DEFAULT 0,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    # --- 6. Tabla de Auditoría ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        usuario_id_actor INTEGER, -- Can be NULL if action is by the system
        accion TEXT NOT NULL, -- e.g., 'CREAR_USUARIO', 'MODIFICAR_RESERVA'
        detalles TEXT, -- JSON string with relevant data, e.g., {"usuario_creado_id": 5, "rol": "profesor"}
        timestamp TEXT NOT NULL,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (usuario_id_actor) REFERENCES usuarios(id)
    );
    """)

    # --- 7. Tablas de Gamificación (SIGA) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamificacion_acciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        accion_key TEXT NOT NULL, -- e.g., 'ASISTENCIA_CLASE'
        puntos INTEGER NOT NULL,
        UNIQUE(inquilino_id, accion_key)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamificacion_puntos_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        alumno_id INTEGER NOT NULL,
        accion_key TEXT NOT NULL,
        puntos_ganados INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamificacion_medallas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        medalla_key TEXT NOT NULL, -- e.g., 'COMPROMISO_TOTAL'
        nombre TEXT NOT NULL,
        descripcion TEXT,
        icono_path TEXT,
        es_manual INTEGER DEFAULT 0, -- 0 for automatic, 1 for manual award
        UNIQUE(inquilino_id, medalla_key)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamificacion_medallas_obtenidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        alumno_id INTEGER NOT NULL,
        medalla_key TEXT NOT NULL,
        fecha_obtencion TEXT NOT NULL,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
    );
    """)

    # --- 8. Tablas para Planificación Curricular ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plan_curricular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        nombre_plan TEXT NOT NULL,
        descripcion TEXT,
        creado_por_usuario_id INTEGER NOT NULL,
        proceso_id INTEGER,
        area TEXT NOT NULL CHECK(area IN ('Cultura', 'Deportes')),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id),
        FOREIGN KEY (creado_por_usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (proceso_id) REFERENCES procesos_formacion(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plan_curricular_temas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_curricular_id INTEGER NOT NULL,
        nombre_tema TEXT NOT NULL,
        descripcion_tema TEXT,
        orden INTEGER NOT NULL,
        FOREIGN KEY (plan_curricular_id) REFERENCES plan_curricular(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planificador_clases_eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema_id INTEGER NOT NULL,
        instructor_id INTEGER NOT NULL,
        clase_id INTEGER,
        fecha_programada TEXT NOT NULL,
        estado TEXT NOT NULL CHECK(estado IN ('planificado', 'completado', 'retrasado', 'cancelado')),
        FOREIGN KEY (tema_id) REFERENCES plan_curricular_temas(id),
        FOREIGN KEY (instructor_id) REFERENCES usuarios(id),
        FOREIGN KEY (clase_id) REFERENCES clases(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progreso_alumno_tema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alumno_usuario_id INTEGER NOT NULL,
        tema_id INTEGER NOT NULL,
        estado TEXT NOT NULL CHECK(estado IN ('no_iniciado', 'en_progreso', 'completado', 'necesita_refuerzo')),
        fecha_completado TEXT,
        observaciones TEXT,
        evaluacion TEXT,
        UNIQUE(alumno_usuario_id, tema_id),
        FOREIGN KEY (alumno_usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (tema_id) REFERENCES plan_curricular_temas(id)
    );
    """)

    # --- 9. Tablas para Facturación y Suscripciones ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suscripciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER UNIQUE NOT NULL,
        plan TEXT NOT NULL,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT,
        estado TEXT NOT NULL CHECK(estado IN ('en_prueba', 'activa', 'cancelada', 'vencida')),
        stripe_customer_id TEXT,
        stripe_subscription_id TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        suscripcion_id INTEGER NOT NULL,
        inquilino_id INTEGER NOT NULL,
        monto REAL NOT NULL,
        fecha_emision TEXT NOT NULL,
        fecha_pago TEXT,
        estado TEXT NOT NULL CHECK(estado IN ('pendiente', 'pagada', 'fallida')),
        stripe_invoice_id TEXT UNIQUE,
        pdf_url TEXT,
        FOREIGN KEY (suscripcion_id) REFERENCES suscripciones(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    # --- 10. Tablas para Chat y Mensajería ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_conversaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquilino_id INTEGER NOT NULL,
        fecha_creacion TEXT NOT NULL,
        ultimo_mensaje_timestamp TEXT,
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversacion_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        FOREIGN KEY (conversacion_id) REFERENCES chat_conversaciones(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversacion_id INTEGER NOT NULL,
        remitente_usuario_id INTEGER NOT NULL,
        contenido TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        leido INTEGER DEFAULT 0,
        FOREIGN KEY (conversacion_id) REFERENCES chat_conversaciones(id),
        FOREIGN KEY (remitente_usuario_id) REFERENCES usuarios(id)
    );
    """)

    # --- 11. Tablas para Contenido E-learning ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contenido_curricular (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema_id INTEGER NOT NULL,
        tipo_contenido TEXT NOT NULL CHECK(tipo_contenido IN ('pdf', 'video', 'enlace')),
        titulo TEXT NOT NULL,
        ruta_archivo_o_url TEXT NOT NULL,
        subido_por_usuario_id INTEGER,
        FOREIGN KEY (tema_id) REFERENCES plan_curricular_temas(id),
        FOREIGN KEY (subido_por_usuario_id) REFERENCES usuarios(id)
    );
    """)

    # --- 12. Tablas para Foros de Clase ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS foros_clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clase_id INTEGER UNIQUE NOT NULL,
        inquilino_id INTEGER NOT NULL,
        nombre_foro TEXT NOT NULL,
        FOREIGN KEY (clase_id) REFERENCES clases(id),
        FOREIGN KEY (inquilino_id) REFERENCES inquilinos(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS foros_hilos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        foro_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        creado_por_usuario_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (foro_id) REFERENCES foros_clases(id),
        FOREIGN KEY (creado_por_usuario_id) REFERENCES usuarios(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS foros_publicaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hilo_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        contenido TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        responde_a_id INTEGER,
        FOREIGN KEY (hilo_id) REFERENCES foros_hilos(id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (responde_a_id) REFERENCES foros_publicaciones(id)
    );
    """)

    # Add columns to alumnos table using ALTER TABLE for safety
    try:
        cursor.execute("ALTER TABLE alumnos ADD COLUMN puntos_totales INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists
    try:
        cursor.execute("ALTER TABLE alumnos ADD COLUMN nivel INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass # Column already exists
    try:
        cursor.execute("ALTER TABLE alumnos ADD COLUMN mostrar_en_rankings INTEGER DEFAULT 1") # 1 for True, 0 for False
    except sqlite3.OperationalError:
        pass # Column already exists

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN dashboard_layout TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists


    conn.commit()
    conn.close()
    print("Base de datos y tablas actualizadas para el modelo multi-inquilino.")

if __name__ == "__main__":
    setup_database()
