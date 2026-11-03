// js/views/profesional_area.js — Dashboard Operativo de Profesional de Área con Cabecera B2B, Vocación Bloqueada y Bento Grid

async function fetchProfesionalTenantCaps(token) {
    const fallback = {
        inquilino_id: 0,
        nombre_empresa: 'Instituto Municipal de Deporte y Recreación — IMDER',
        tipo_organizacion: 'entidad_publica',
        ambito_organizacional: 'municipal',
        vocacion_institucional: 'deportiva',
        canonical_plan: 'basico',
        subscription_status: 'activa',
        is_active: true
    };
    if (!token) return fallback;
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/tenants/my-plan-capabilities`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return fallback;
        return await res.json();
    } catch (e) {
        return fallback;
    }
}

async function renderProfesionalAreaDashboardView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Panel del Profesional de Área...</p>
        </div>
    `;

    const caps = await fetchProfesionalTenantCaps(token);
    const isCultural = (caps.vocacion_institucional || 'deportiva') === 'cultural';

    const natureMap = {
        'entidad_publica': { label: 'Entidad Pública', icon: 'fa-landmark' },
        'entidad_privada': { label: 'Entidad Privada', icon: 'fa-building-columns' },
        'empresa_publica': { label: 'Empresa Pública', icon: 'fa-gears' },
        'empresa_privada': { label: 'Empresa Privada', icon: 'fa-briefcase' }
    };
    const natureInfo = natureMap[caps.tipo_organizacion] || { label: 'Organización Institucional', icon: 'fa-building' };

    const planBadge = caps.canonical_plan === 'full'
        ? `<span class="badge" style="background:rgba(16,185,129,0.15); border:1px solid #10B981; color:#34D399; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;"><i class="fas fa-gem"></i> Plan Full — Activo</span>`
        : `<span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;"><i class="fas fa-box-open"></i> Plan Básico — Operativo</span>`;

    const vocab = isCultural ? {
        title: 'Supervisión Técnica de Talleres Culturales',
        vocationLabel: 'ESPECIALIDAD: CULTURAL',
        sub: 'Supervisión técnica de modalidades artísticas (Danza: Joropo, Salsa | Instrumentos: Guitarra, Arpa).',
        kpiGroups: 'TALLERES CULTURALES',
        kpiCount: '24 Grupos',
        icon: 'fa-user-tie'
    } : {
        title: 'Supervisión Técnica de Disciplinas Deportivas',
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        sub: 'Supervisión técnica de disciplinas deportivas y preparación física de alta competencia.',
        kpiGroups: 'DISCIPLINAS DEPORTIVAS',
        kpiCount: '18 Activas',
        icon: 'fa-user-tie'
    };

    contentArea.innerHTML = `
        <div class="profesional-area-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa con Vocación Bloqueada y Badge de Rol -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas ${vocab.icon}" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800; tracking:-0.02em;">
                                ${caps.nombre_empresa}
                            </h1>
                            ${planBadge}
                            <span style="background:rgba(56,189,248,0.12); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-user-tie"></i> Profesional de Área
                            </span>
                        </div>
                        <div style="display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap; font-size:0.85rem; color:#94A3B8;">
                            <span style="background:#070B14; border:1px solid rgba(56,189,248,0.25); padding:0.25rem 0.75rem; border-radius:12px; color:#38BDF8; font-weight:700;">
                                <i class="fas ${natureInfo.icon}"></i> ${natureInfo.label}
                            </span>
                            <span style="color:#94A3B8;"><i class="fa-solid fa-shield-halved" style="color:#38BDF8;"></i> ${vocab.sub}</span>
                        </div>
                    </div>
                </div>

                <!-- Insignia de Vocación Bloqueada (Solo Lectura) -->
                <div style="background:#070B14; border:1px solid rgba(56,189,248,0.35); padding:0.6rem 1rem; border-radius:16px; text-align:right;">
                    <div style="color:#38BDF8; font-size:0.85rem; font-weight:800; display:flex; align-items:center; gap:0.5rem; justify-content:flex-end;">
                        <i class="fas ${isCultural ? 'fa-palette' : 'fa-running'}"></i> ${vocab.vocationLabel}
                        <i class="fas fa-lock" style="color:#F59E0B;" title="Vocación fijada por Administración de Empresa"></i>
                    </div>
                    <span style="font-size:0.72rem; color:#94A3B8;">Fijada por Administración — Solo Lectura</span>
                </div>
            </div>

            <!-- Matrix KPI Bento Grid 60-30-10 -->
            <div class="bento-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:1.25rem; margin-bottom:1.75rem;">
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94A3B8; margin-bottom:0.4rem;">${vocab.kpiGroups}</div>
                    <div style="font-size:1.9rem; font-weight:800; color:#38BDF8;">${vocab.kpiCount}</div>
                    <div style="font-size:0.75rem; color:#34D399; margin-top:0.25rem;"><i class="fas fa-check-circle"></i> Cobertura Técnica 100%</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94A3B8; margin-bottom:0.4rem;">SUPERVISIÓN DE CAMPO</div>
                    <div style="font-size:1.9rem; font-weight:800; color:#38BDF8;">96.5%</div>
                    <div style="font-size:0.75rem; color:#38BDF8; margin-top:0.25rem;"><i class="fas fa-check-double"></i> Verificación Aprobada</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#94A3B8; margin-bottom:0.4rem;">PERSONAL REGISTRADO</div>
                    <div style="font-size:1.9rem; font-weight:800; color:#38BDF8;">Whitelist 3 Roles</div>
                    <div style="font-size:0.75rem; color:#94A3B8; margin-top:0.25rem;"><i class="fas fa-user-plus"></i> Profesor, Escenarios, Almacén</div>
                </div>
            </div>

            <!-- Herramientas Operativas y Modal de Alta Restringido -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <h3 style="color:#38BDF8; margin:0; font-size:1.2rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-tasks"></i> Acciones de Supervisión Rápida & Registro Whitelisted
                    </h3>
                    <button class="btn-primary" style="min-height:42px; padding:0 1.25rem;" onclick="window.openWhitelistedStaffCreationModal(sessionStorage.getItem('jwt_token') || localStorage.getItem('sga_token'), '${caps.vocacion_institucional || 'deportiva'}')">
                        <i class="fas fa-user-plus"></i> Dar de Alta Personal
                    </button>
                </div>
                <div style="display:flex; gap:1rem; flex-wrap:wrap;">
                    <button class="btn-primary" style="background:#38BDF8; color:#070B14; font-weight:700; padding:0.6rem 1.2rem; border-radius:8px; border:none; min-height:44px; cursor:pointer;" onclick="renderSupervisarActividadesView(sessionStorage.getItem('jwt_token') || localStorage.getItem('sga_token'))">
                        <i class="fas fa-eye"></i> Supervisar Actividades en Curso
                    </button>
                    <button class="btn-secondary" style="background:rgba(56,189,248,0.1); color:#38BDF8; border:1px solid #38BDF8; font-weight:700; padding:0.6rem 1.2rem; border-radius:8px; min-height:44px; cursor:pointer;" onclick="renderGestionarDisciplinasView(sessionStorage.getItem('jwt_token') || localStorage.getItem('sga_token'))">
                        <i class="fas fa-edit"></i> Gestionar Disciplinas y Modalidades
                    </button>
                </div>
            </div>

        </div>
    `;
}

async function renderSupervisarActividadesView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `<div class="view-header"><h2 style="color:#F8FAFC;"><i class="fas fa-tasks" style="color:#38BDF8;"></i> Supervisar Actividades</h2></div><p style="color:#94A3B8;">Cargando actividades en curso...</p>`;

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const response = await fetch(`${baseUrl}/api/v1/eventos?estado=en-curso`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const actividades = response.ok ? await response.json() : [
            { nombre: 'Entrenamiento Selección Taekwondo', tipo: 'Entrenamiento', responsable: 'Carlos Mendoza', estado: 'en-curso' },
            { nombre: 'Ensayo General de Danza Joropo', tipo: 'Ensayo', responsable: 'Elena Ramos', estado: 'en-curso' }
        ];

        const rows = actividades.map(item => `
            <tr>
                <td style="color:#F8FAFC; font-weight:600;">${item.nombre}</td>
                <td style="color:#94A3B8;">${item.tipo}</td>
                <td style="color:#94A3B8;">${item.responsable || 'N/A'}</td>
                <td><span style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:700;">${item.estado}</span></td>
            </tr>
        `).join('');

        contentArea.innerHTML = `
            <div class="view-header" style="margin-bottom:1.5rem;">
                <h2 style="color:#38BDF8; font-size:1.5rem; display:flex; align-items:center; gap:0.5rem;">
                    <i class="fas fa-tasks"></i> Supervisar Actividades en Curso
                </h2>
                <p style="color:#94A3B8; font-size:0.9rem;">Panel de control y verificación técnica de actividades activas.</p>
            </div>
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; overflow-x:auto;">
                <table class="data-table" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(56,189,248,0.2); text-align:left;">
                            <th style="color:#94A3B8; padding:0.75rem;">Actividad/Evento</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Tipo</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Responsable</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Estado</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } catch (error) {
        contentArea.innerHTML = `<p class="message-error" style="color:#38BDF8; background:rgba(56,189,248,0.1); padding:1rem; border-radius:8px;">Error al cargar actividades: ${error.message}</p>`;
    }
}

async function renderGestionarEventosView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `<div class="view-header"><h2 style="color:#38BDF8;"><i class="fas fa-calendar-plus"></i> Gestionar Eventos</h2></div><p style="color:#94A3B8;">Cargando eventos...</p>`;

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const response = await fetch(`${baseUrl}/api/v1/eventos`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const eventos = response.ok ? await response.json() : [
            { id: 1, nombre: 'Torneo Abierto de Judo', tipo: 'Deporte', fecha: new Date().toISOString(), estado: 'programado' },
            { id: 2, nombre: 'Recital de Cuerdas y Arpa', tipo: 'Cultura', fecha: new Date().toISOString(), estado: 'programado' }
        ];

        const rows = eventos.map(item => `
            <tr>
                <td style="color:#F8FAFC; font-weight:600;">${item.nombre}</td>
                <td style="color:#94A3B8;">${item.tipo}</td>
                <td style="color:#94A3B8;">${new Date(item.fecha).toLocaleDateString()}</td>
                <td><span style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:700;">${item.estado || 'programado'}</span></td>
                <td>
                    <button class="btn-secondary" style="background:rgba(56,189,248,0.1); color:#38BDF8; border:1px solid #38BDF8; padding:0.3rem 0.7rem; border-radius:6px; cursor:pointer;">Editar</button>
                </td>
            </tr>
        `).join('');

        contentArea.innerHTML = `
            <div class="view-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                <div>
                    <h2 style="color:#38BDF8; font-size:1.5rem; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-calendar-plus"></i> Gestionar Eventos
                    </h2>
                    <p style="color:#94A3B8; font-size:0.9rem;">Creación y coordinación de eventos institucionales de área.</p>
                </div>
                <button class="btn-primary" style="background:#38BDF8; color:#070B14; font-weight:700; padding:0.6rem 1.2rem; border-radius:8px; border:none; min-height:44px; cursor:pointer;">Crear Evento</button>
            </div>
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; overflow-x:auto;">
                <table class="data-table" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(56,189,248,0.2); text-align:left;">
                            <th style="color:#94A3B8; padding:0.75rem;">Nombre</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Tipo</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Fecha</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Estado</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Acciones</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } catch (error) {
        contentArea.innerHTML = `<p class="message-error" style="color:#38BDF8;">Error al cargar eventos: ${error.message}</p>`;
    }
}

async function renderGestionarDisciplinasView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `<div class="view-header"><h2 style="color:#38BDF8;"><i class="fas fa-edit"></i> Gestionar Disciplinas y Modalidades</h2></div><p style="color:#94A3B8;">Cargando especialidades...</p>`;

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const response = await fetch(`${baseUrl}/api/v1/catalogo/my-specialties`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const list = response.ok ? await response.json() : [
            { nombre: 'Taekwondo WT', vertical: 'deporte', categoria: 'Artes Marciales' },
            { nombre: 'Danza Joropo / Llanera', vertical: 'cultura', categoria: 'Danza Folclórica' }
        ];

        const rows = list.map(item => `
            <tr>
                <td style="color:#F8FAFC; font-weight:600;">${item.nombre}</td>
                <td style="color:#38BDF8; font-weight:700;">${(item.vertical || 'deporte').toUpperCase()}</td>
                <td style="color:#94A3B8;">${item.categoria || 'General'}</td>
            </tr>
        `).join('');

        contentArea.innerHTML = `
            <div class="view-header" style="margin-bottom:1.5rem;">
                <h2 style="color:#38BDF8; font-size:1.5rem; display:flex; align-items:center; gap:0.5rem;">
                    <i class="fas fa-edit"></i> Disciplinas Deportivas & Modalidades Culturales Adoptadas
                </h2>
                <p style="color:#94A3B8; font-size:0.85rem;">Consulta de catálogo oficial asignado a la organización.</p>
            </div>
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; overflow-x:auto;">
                <table class="data-table" style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(56,189,248,0.2); text-align:left;">
                            <th style="color:#94A3B8; padding:0.75rem;">Nombre de Especialidad</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Vocación / Vertical</th>
                            <th style="color:#94A3B8; padding:0.75rem;">Categoría</th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        `;
    } catch (error) {
        contentArea.innerHTML = `<p class="message-error" style="color:#38BDF8;">Error al cargar catálogo: ${error.message}</p>`;
    }
}

// --- Registrar vistas de Profesional de Área ---
if (typeof registerView === 'function') {
    registerView('profesional_area', 'dashboard', renderProfesionalAreaDashboardView);
    registerView('profesional_area', 'supervisar-actividades', renderSupervisarActividadesView);
    registerView('profesional_area', 'gestionar-eventos', renderGestionarEventosView);
    registerView('profesional_area', 'gestionar-disciplinas', renderGestionarDisciplinasView);
    if (typeof renderReportesOperativosView === 'function') {
        registerView('profesional_area', 'reportes-operativos', renderReportesOperativosView);
    }
}
