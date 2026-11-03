// --- Definición de la Estructura de Navegación por Rol ---

const navLinks = {
    // Rol 1: Super Admin (Estructurado con Submenús Jerárquicos)
    admin_general: [
        {
            text: 'Panel de Control',
            icon: 'fa-home',
            submenu: [
                { text: 'Resumen General', view: 'dashboard', icon: 'fa-chart-pie' },
                { text: 'Indicadores del Sistema', view: 'dashboard', icon: 'fa-tachometer-alt' }
            ]
        },
        {
            text: 'Gestión de Landing Page',
            icon: 'fa-sliders-h',
            submenu: [
                { text: 'Editor Comercial & Planes', view: 'gestor-landing', icon: 'fa-edit' },
                { text: 'Metadatos SEO Públicos', view: 'gestor-landing', icon: 'fa-search-dollar' }
            ]
        },
        {
            text: 'Marketing y Crecimiento',
            icon: 'fa-bullhorn',
            submenu: [
                { text: 'CRM & Campañas Social', view: 'dashboard', icon: 'fa-paper-plane' },
                { isHeader: true, text: '3.1. Motor de envió masivo' },
                { text: 'Generador de Videos IA (Predis)', view: 'motor-predis-media', icon: 'fas fa-magic' },
                { text: 'Config. Creacion de videos Cloud', view: 'motor-predis-media', icon: 'fas fa-video' },
                { text: 'Config. Creacion de imágenes Cloud', view: 'motor-predis-media', icon: 'fas fa-image' },
                { text: 'Config. Creacion de Reals Cloud', view: 'motor-predis-media', icon: 'fas fa-film' },
                { isHeader: true, text: '3.2. Motor de ADS' },
                { text: 'Config. WhatsApp Cloud', view: 'configuracion-whatsapp', icon: 'fab fa-whatsapp' },
                { text: 'Config. iNSTAGRAM Cloud', view: 'gestion-api-keys', icon: 'fab fa-instagram' },
                { text: 'Config. TIK TOK Cloud', view: 'gestion-api-keys', icon: 'fab fa-tiktok' },
                { text: 'Config. Gmail Cloud', view: 'gestion-api-keys', icon: 'fas fa-envelope' },
                { text: 'Config. X Cloud', view: 'gestion-api-keys', icon: 'fab fa-x-twitter' },
                { text: 'Config. Youtobe Cloud', view: 'gestion-api-keys', icon: 'fab fa-youtube' },
                { text: 'Promociones y Ofertas', view: 'promociones', icon: 'fa-tags' }
            ]
        },
        {
            text: 'Gestión Financiera',
            icon: 'fa-credit-card',
            submenu: [
                { text: 'Cobros y Transacciones', view: 'suscripcion', icon: 'fa-file-invoice-dollar' },
                { text: 'Suscripciones Activas', view: 'suscripcion', icon: 'fa-users-cog' }
            ]
        },
        {
            text: 'Usuarios y Permisos',
            icon: 'fa-user-shield',
            submenu: [
                { text: 'Gestionar Empresas', view: 'panel-empresa', icon: 'fa-building' },
                { text: 'Roles y Permisos', view: 'roles-permisos', icon: 'fa-shield-alt' },
                { text: 'Verificar Roles BD', view: 'verificar-roles-bd', icon: 'fa-database' }
            ]
        },
        {
            text: 'Configuración y Seguridad',
            icon: 'fa-cog',
            submenu: [
                { text: 'Proveedores de IA & Ollama', view: 'gestion-api-keys', icon: 'fa-key' },
                { text: 'Auditoría General', view: 'auditoria-empresa', icon: 'fa-history' },
                { text: 'Asistente de IA', view: 'asistente-ia', icon: 'fa-robot' }
            ]
        }
    ],
    // Rol 2: Admin de Empresa (Estructura Categorizada con Submenús)
    admin_empresa: [
        {
            text: 'PANEL PRINCIPAL',
            icon: 'fa-chart-pie',
            submenu: [
                { text: 'Dashboard General', view: 'panel-empresa', icon: 'fa-chart-pie' },
                { text: 'Indicadores de Gestión', view: 'panel-empresa', icon: 'fa-tachometer-alt' }
            ]
        },
        {
            text: 'GESTIÓN OPERATIVA',
            icon: 'fa-tasks',
            submenu: [
                { text: 'Escuelas Deportivas', view: 'programas-deportivos', icon: 'fa-running' },
                { text: 'Talleres Culturales', view: 'talleres-culturales', icon: 'fa-palette' },
                { text: 'Sedes y Escenarios', view: 'areas-empresa', icon: 'fa-map-marked-alt' }
            ]
        },
        {
            text: 'TALENTO Y USUARIOS',
            icon: 'fa-users-cog',
            submenu: [
                { text: 'Personal y Profesores', view: 'usuarios-empresa', icon: 'fa-users-cog' },
                { text: 'Roster de Estudiantes', view: 'usuarios-empresa', icon: 'fa-user-graduate' }
            ]
        },
        {
            text: 'MARKETING Y CRM',
            icon: 'fa-bullhorn',
            submenu: [
                { text: 'Campañas y Captación', view: 'crm-empresa', icon: 'fa-bullhorn' },
                { text: 'Generador Multimedia IA', view: 'media-ia-empresa', icon: 'fa-photo-video' }
            ]
        },
        {
            text: 'CONFIGURACIÓN Y CONTROL',
            icon: 'fa-shield-alt',
            submenu: [
                { text: 'Suscripción y Pagos', view: 'suscripcion', icon: 'fa-credit-card' },
                { text: 'Auditoría y Seguridad', view: 'auditoria-empresa', icon: 'fa-shield-alt' }
            ]
        }
    ],
    // Rol 3: Jefe de Área (Estructura Categorizada de 5 Bloques + Marketing/CRM)
    jefe_area: [
        {
            text: 'PANEL PRINCIPAL',
            icon: 'fa-chart-pie',
            submenu: [
                { text: 'Dashboard de Área', view: 'panel-area', icon: 'fa-tachometer-alt' },
                { text: 'Indicadores Operativos', view: 'panel-area', icon: 'fa-chart-line' }
            ]
        },
        {
            text: 'GESTIÓN OPERATIVA',
            icon: 'fa-tasks',
            submenu: [
                { text: 'Disciplinas / Talleres Activos', view: 'panel-area', icon: 'fa-running' },
                { text: 'Supervisión de Clases', view: 'panel-area', icon: 'fa-clipboard-list' }
            ]
        },
        {
            text: 'MARKETING Y CRM',
            icon: 'fa-bullhorn',
            submenu: [
                { text: 'Campañas y Captación', view: 'crm-empresa', icon: 'fa-bullhorn' },
                { text: 'Generador Multimedia IA', view: 'media-ia-empresa', icon: 'fa-photo-video' }
            ]
        },
        {
            text: 'LOGÍSTICA Y RECURSOS',
            icon: 'fa-boxes',
            submenu: [
                { text: 'Escenarios y Espacios', view: 'panel-area', icon: 'fa-map-marked-alt' },
                { text: 'Inventario de Área', view: 'panel-area', icon: 'fa-dolly-flatbed' }
            ]
        },
        {
            text: 'CONTROL Y AUDITORÍA',
            icon: 'fa-shield-alt',
            submenu: [
                { text: 'Trazabilidad de Operaciones', view: 'panel-area', icon: 'fa-history' }
            ]
        }
    ],
    // Rol 4: Profesional de Área (Estructura Categorizada de 5 Bloques + Marketing/CRM)
    profesional_area: [
        {
            text: 'PANEL PRINCIPAL',
            icon: 'fa-chart-pie',
            submenu: [
                { text: 'Dashboard Profesional', view: 'dashboard', icon: 'fa-tachometer-alt' },
                { text: 'Indicadores Técnicos', view: 'dashboard', icon: 'fa-chart-bar' }
            ]
        },
        {
            text: 'GESTIÓN OPERATIVA',
            icon: 'fa-tasks',
            submenu: [
                { text: 'Supervisar Actividades', view: 'supervisar-actividades', icon: 'fa-tasks' },
                { text: 'Gestionar Eventos', view: 'gestionar-eventos', icon: 'fa-calendar-plus' },
                { text: 'Disciplinas y Modalidades', view: 'gestionar-disciplinas', icon: 'fa-edit' }
            ]
        },
        {
            text: 'MARKETING Y CRM',
            icon: 'fa-bullhorn',
            submenu: [
                { text: 'Campañas y Captación', view: 'crm-empresa', icon: 'fa-bullhorn' },
                { text: 'Generador Multimedia IA', view: 'media-ia-empresa', icon: 'fa-photo-video' }
            ]
        },
        {
            text: 'LOGÍSTICA Y RECURSOS',
            icon: 'fa-boxes',
            submenu: [
                { text: 'Sedes y Espacios', view: 'supervisar-actividades', icon: 'fa-map-marker-alt' }
            ]
        },
        {
            text: 'CONTROL Y AUDITORÍA',
            icon: 'fa-shield-alt',
            submenu: [
                { text: 'Reportes Operativos', view: 'reportes-operativos', icon: 'fa-chart-line' }
            ]
        }
    ],
    // Rol 5: Técnico de Área (Estructura Categorizada de 5 Bloques + Marketing/CRM)
    tecnico_area: [
        {
            text: 'PANEL PRINCIPAL',
            icon: 'fa-chart-pie',
            submenu: [
                { text: 'Dashboard Técnico', view: 'dashboard', icon: 'fa-tachometer-alt' },
                { text: 'Estado Operativo', view: 'dashboard', icon: 'fa-wrench' }
            ]
        },
        {
            text: 'GESTIÓN OPERATIVA',
            icon: 'fa-tasks',
            submenu: [
                { text: 'Ver Actividades', view: 'asistir-gestion-usuarios', icon: 'fa-eye' },
                { text: 'Gestionar Eventos', view: 'gestionar-eventos', icon: 'fa-calendar-check' },
                { text: 'Ver Disciplinas y Modalidades', view: 'gestionar-disciplinas', icon: 'fa-search' }
            ]
        },
        {
            text: 'MARKETING Y CRM',
            icon: 'fa-bullhorn',
            submenu: [
                { text: 'Campañas y Captación', view: 'crm-empresa', icon: 'fa-bullhorn' },
                { text: 'Generador Multimedia IA', view: 'media-ia-empresa', icon: 'fa-photo-video' }
            ]
        },
        {
            text: 'LOGÍSTICA Y RECURSOS',
            icon: 'fa-boxes',
            submenu: [
                { text: 'Mantenimiento de Escenarios', view: 'gestionar-eventos', icon: 'fa-tools' }
            ]
        },
        {
            text: 'CONTROL Y AUDITORÍA',
            icon: 'fa-shield-alt',
            submenu: [
                { text: 'Reportes Operativos', view: 'reportes-operativos', icon: 'fa-file-alt' }
            ]
        }
    ],
    // Rol 6: Coordinador (Estructura Categorizada de 5 Bloques)
    coordinador: [
        {
            text: 'PANEL PRINCIPAL',
            icon: 'fa-chart-pie',
            submenu: [
                { text: 'Dashboard de Coordinación', view: 'planificacion', icon: 'fa-tachometer-alt' },
                { text: 'Telemetría Power BI', view: 'planificacion', icon: 'fa-chart-bar' }
            ]
        },
        {
            text: 'SUPERVISIÓN EN CAMPO',
            icon: 'fa-eye',
            submenu: [
                { text: 'Verificación Docentes en Cancha', view: 'verificar-programacion', icon: 'fa-check-circle' },
                { text: 'Control de Escenarios & Custodia', view: 'verificar-programacion', icon: 'fa-map-marker-alt' }
            ]
        },
        {
            text: 'GESTIÓN CURRICULAR',
            icon: 'fa-clipboard-check',
            submenu: [
                { text: 'Aprobación 52 Semanas', view: 'aprobaciones', icon: 'fa-calendar-week' }
            ]
        },
        {
            text: 'EQUIPO Y TAREAS',
            icon: 'fa-users-cog',
            submenu: [
                { text: 'Distribución Tareas Extraordinarias', view: 'planificacion', icon: 'fa-tasks' },
                { text: 'Roster de Profesores', view: 'planificacion', icon: 'fa-chalkboard-teacher' }
            ]
        },
        {
            text: 'CONTROL Y REPORTES',
            icon: 'fa-shield-alt',
            submenu: [
                { text: 'Libro de Novedades', view: 'planificacion', icon: 'fa-book' },
                { text: 'Informes de Supervisión', view: 'planificacion', icon: 'fa-file-alt' }
            ]
        }
    ],
    // Rol 7: Profesor (Estructura Categorizada)
    profesor: [
        {
            text: 'MI GESTIÓN FORMATIVA',
            icon: 'fa-chalkboard-teacher',
            submenu: [
                { text: 'Panel Docente', view: 'gestionar-cursos', icon: 'fa-tachometer-alt' },
                { text: 'Mis Cursos y Roster', view: 'gestionar-cursos', icon: 'fa-book' }
            ]
        },
        {
            text: 'PLANIFICACIÓN ANUAL',
            icon: 'fa-calendar-alt',
            submenu: [
                { text: 'Plan Curricular 52 Semanas', view: 'gestionar-cursos', icon: 'fa-calendar-week' }
            ]
        },
        {
            text: 'CUSTODIA Y LOGÍSTICA',
            icon: 'fa-boxes',
            submenu: [
                { text: 'Elementos en Custodia', view: 'gestionar-cursos', icon: 'fa-box-open' },
                { text: 'Solicitud de Escenarios', view: 'gestionar-cursos', icon: 'fa-map-marker-alt' }
            ]
        },
        {
            text: 'TELEMETRÍA Y ALUMNOS',
            icon: 'fa-chart-line',
            submenu: [
                { text: 'Asistencia & Alertas Deserción', view: 'gestionar-cursos', icon: 'fa-user-check' },
                { text: 'Suscripción y Plan', view: 'suscripcion', icon: 'fa-credit-card' }
            ]
        }
    ],
    // Rol 8: Alumno (Estructura Categorizada)
    alumno: [
        {
            text: 'MI ACTIVIDAD',
            icon: 'fa-user-graduate',
            submenu: [
                { text: 'Mis Disciplinas / Cursos', view: 'mis-cursos', icon: 'fa-book-reader' },
                { text: 'Mi Horario', view: 'mi-horario', icon: 'fa-clock' }
            ]
        },
        {
            text: 'OFERTA Y POSTULACIONES',
            icon: 'fa-store',
            submenu: [
                { text: 'Vitrina de Oferta', view: 'mis-cursos', icon: 'fa-graduation-cap' }
            ]
        },
        {
            text: 'MI ASISTENCIA Y NOTAS',
            icon: 'fa-check-circle',
            submenu: [
                { text: 'Check-In Asistencia PWA', view: 'mi-asistencia', icon: 'fa-fingerprint' },
                { text: 'Mis Calificaciones', view: 'mis-calificaciones', icon: 'fa-star' }
            ]
        },
        {
            text: 'CARNET DIGITAL',
            icon: 'fa-id-card',
            submenu: [
                { text: 'Credencial e Insignias', view: 'mi-progreso', icon: 'fa-qrcode' }
            ]
        }
    ],
    // Rol 9: Padre o Acudiente (Estructura Categorizada)
    padre_acudiente: [
        {
            text: 'MIS ESTUDIANTES',
            icon: 'fa-child',
            submenu: [
                { text: 'Mis Hijos / Pupilos', view: 'mis-alumnos', icon: 'fa-users' }
            ]
        },
        {
            text: 'POSTULAR BENEFICIARIOS',
            icon: 'fa-user-plus',
            submenu: [
                { text: 'Postular a Disciplina', view: 'mis-alumnos', icon: 'fa-file-signature' }
            ]
        },
        {
            text: 'SEGUIMIENTO FORMATIVO',
            icon: 'fa-chart-line',
            submenu: [
                { text: 'Asistencia y Progreso', view: 'mis-alumnos', icon: 'fa-chart-bar' }
            ]
        },
        {
            text: 'AUTORIZACIONES',
            icon: 'fa-file-contract',
            submenu: [
                { text: 'Permisos Legales y Médicos', view: 'mis-alumnos', icon: 'fa-user-edit' }
            ]
        }
    ],
    // Rol 10: Jefe de Almacén
    jefe_almacen: [
        { text: 'Dashboard Inventario', view: 'dashboard-inventario', icon: 'fa-boxes' },
        { text: 'Registrar Movimientos', view: 'registrar-movimientos', icon: 'fa-dolly-flatbed' },
        { text: 'Stock y Reposición', view: 'stock-y-reposicion', icon: 'fa-sort-amount-up' },
        { text: 'Hojas de Vida', view: 'hojas-de-vida', icon: 'fa-file-invoice' },
        { text: 'Reportes de Inventario', view: 'reportes-de-inventario', icon: 'fa-file-excel' }
    ],
    // Rol 11: Almacenista (hereda de jefe_almacen, pero con menos permisos)
    almacenista: [
        { text: 'Ver Inventario', view: 'ver-inventario', icon: 'fa-boxes' },
        { text: 'Registrar Movimientos', view: 'registrar-movimientos', icon: 'fa-dolly-flatbed' }
    ],
    // Rol 12: Jefe de Escenarios
    jefe_escenarios: [
        { text: 'Calendario de Escenarios', view: 'calendario-de-escenarios', icon: 'fa-calendar-alt' },
        { text: 'Asignar Espacios', view: 'asignar-espacios', icon: 'fa-map-marker-alt' },
        { text: 'Mantenimiento', view: 'mantenimiento', icon: 'fa-tools' }
    ],
    // Rol por defecto si no se encuentra uno
    default: [
        { text: 'Mi Perfil', icon: 'fa-user' }
    ]
};

function renderNavigation(roleName) {
    const navContainer = document.getElementById('app-nav');
    if (!navContainer) return;

    const links = navLinks[roleName] || navLinks.default;

    let navHtml = '';
    links.forEach(link => {
        if (link.submenu && Array.isArray(link.submenu)) {
            // Renderizar grupo con submenú
            let subHtml = '';
            link.submenu.forEach(sub => {
                if (sub.isHeader) {
                    subHtml += `<div class="nav-submenu-header" style="color:#38BDF8; font-size:0.75rem; font-weight:800; text-transform:uppercase; tracking:0.05em; padding:0.6rem 0.85rem 0.2rem 0.85rem; border-top:1px solid rgba(56,189,248,0.1); margin-top:0.3rem;">
                                    ${sub.text}
                                </div>`;
                } else {
                    const subView = sub.view || sub.text.toLowerCase().replace(/ /g, '-');
                    subHtml += `<a href="#" data-view="${subView}" class="nav-subitem" tabindex="0">
                                    <i class="fas ${sub.icon}"></i>
                                    <span class="nav-text">${sub.text}</span>
                                </a>`;
                }
            });

            navHtml += `<div class="nav-group">
                            <button class="nav-group-title" aria-expanded="false" tabindex="0">
                                <span><i class="fas ${link.icon}"></i> <span class="nav-text">${link.text}</span></span>
                                <i class="fas fa-chevron-down nav-arrow"></i>
                            </button>
                            <div class="nav-submenu">
                                ${subHtml}
                            </div>
                        </div>`;
        } else {
            // Renderizar enlace plano
            const viewName = link.view || link.text.toLowerCase().replace(/ /g, '-');
            navHtml += `<a href="#" data-view="${viewName}" tabindex="0">
                            <i class="fas ${link.icon}"></i>
                            <span class="nav-text">${link.text}</span>
                        </a>`;
        }
    });

    navContainer.innerHTML = navHtml;
    setupSubmenuInteractions(navContainer);
}

function setupSubmenuInteractions(navContainer) {
    // Interacción Click/Touch para desplegar submenús
    navContainer.querySelectorAll('.nav-group-title').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const group = btn.closest('.nav-group');
            const isOpen = group.classList.contains('open');

            // Cerrar otros grupos
            navContainer.querySelectorAll('.nav-group').forEach(g => g.classList.remove('open'));
            if (!isOpen) {
                group.classList.add('open');
                btn.setAttribute('aria-expanded', 'true');
            } else {
                btn.setAttribute('aria-expanded', 'false');
            }
        });

        // Accesibilidad por Teclado
        btn.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                btn.click();
            }
        });
    });
}
