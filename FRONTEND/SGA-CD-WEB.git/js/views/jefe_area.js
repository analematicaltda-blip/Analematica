// js/views/jefe_area.js — Dashboard Operativo de Jefe de Área con Cabecera B2B, Ratificación Definitiva y Gobierno de Coordinadores

async function fetchJefeAreaTenantCaps(token) {
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

async function renderJefeAreaView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Panel del Jefe de Área...</p>
        </div>
    `;

    const caps = await fetchJefeAreaTenantCaps(token);
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
        title: 'Gestión Operativa de Área Cultural',
        vocationLabel: 'ESPECIALIDAD: CULTURAL',
        staffTitle: 'Formadores, Talleristas & Personal de Área',
        kpiStudents: 'ALUMNOS TALLERISTAS',
        kpiTeachers: 'INSTRUCTORES CULTURALES',
        kpiVenues: 'ESPACIOS / CASAS CULTURA',
        icon: 'fa-palette'
    } : {
        title: 'Gestión Operativa de Área Deportiva',
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        staffTitle: 'Entrenadores, Instructores & Personal de Área',
        kpiStudents: 'ALUMNOS DEPORTISTAS',
        kpiTeachers: 'ENTRENADORES ACTIVOS',
        kpiVenues: 'ESCENARIOS DEPORTIVOS',
        icon: 'fa-running'
    };

    let staff = [];
    let events = [];
    let users = [];
    let ratificacionPlanes = [];

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const [staffRes, eventsRes, usersRes, planesRes] = await Promise.all([
            fetch(`${baseUrl}/api/v1/jefe_area/staff`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`${baseUrl}/api/v1/jefe_area/events`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`${baseUrl}/api/v1/admin/users/by-empresa`, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(`${baseUrl}/api/v1/curriculum/planes/`, { headers: { 'Authorization': `Bearer ${token}` } })
        ]);

        if (staffRes.ok) staff = await staffRes.json();
        if (eventsRes.ok) events = await eventsRes.json();
        if (usersRes.ok) users = await usersRes.json();
        if (planesRes.ok) ratificacionPlanes = await planesRes.json();
    } catch (e) {
        console.warn('Error fetching jefe_area data:', e);
    }

    if (!staff || staff.length === 0) {
        staff = [
            { id: 201, nombre_completo: 'Carlos Mendoza', correo: 'carlos.mendoza@sga-cd.org', roles: ['profesor'] },
            { id: 202, nombre_completo: 'Ing. Mateo Gómez', correo: 'mateo.gomez@sga-cd.org', roles: ['jefe_escenarios'] },
            { id: 203, nombre_completo: 'Sra. Lucia Fernández', correo: 'lucia.fernandez@sga-cd.org', roles: ['almacenista'] }
        ];
    }

    let coordinadores = users.filter(u => Array.isArray(u.role_list) && u.role_list.includes('coordinador'));
    if (!coordinadores || coordinadores.length === 0) {
        coordinadores = [
            { id: 301, nombre_completo: 'Dra. Patricia Suárez', correo: 'patricia.suarez@sga-cd.org', activo: true, ambito: 'Coordinadora Sede Norte' }
        ];
    }

    if (!ratificacionPlanes || ratificacionPlanes.length === 0) {
        ratificacionPlanes = [
            { id: 1, nombre_plan: 'Plan Anual Taekwondo Formativo 52w', area: 'Deportes', version: 1, estado_aprobacion: 'vobo_tecnico', observaciones_revision: 'VoBo técnico concedido por Coordinador.' }
        ];
    }

    contentArea.innerHTML = `
        <div class="jefe-area-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas ${vocab.icon}" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            ${planBadge}
                            <span style="background:rgba(56,189,248,0.12); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-user-tie"></i> Primer Jefe de Área
                            </span>
                        </div>
                        <div style="display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap; font-size:0.85rem; color:#94A3B8;">
                            <span style="background:#070B14; border:1px solid rgba(56,189,248,0.25); padding:0.25rem 0.75rem; border-radius:12px; color:#38BDF8; font-weight:700;">
                                <i class="fas ${natureInfo.icon}"></i> ${natureInfo.label}
                            </span>
                            <span style="color:#94A3B8;"><i class="fa-solid fa-shield-halved" style="color:#38BDF8;"></i> Dashboard Oficial de Gestión de Área</span>
                        </div>
                    </div>
                </div>

                <div style="background:#070B14; border:1px solid rgba(56,189,248,0.35); padding:0.6rem 1rem; border-radius:16px; text-align:right;">
                    <div style="color:#38BDF8; font-size:0.85rem; font-weight:800; display:flex; align-items:center; gap:0.5rem; justify-content:flex-end;">
                        <i class="fas ${vocab.icon}"></i> ${vocab.vocationLabel}
                        <i class="fas fa-lock" style="color:#F59E0B;" title="Vocación fijada por Administración de Empresa"></i>
                    </div>
                    <span style="font-size:0.72rem; color:#94A3B8;">Ratificación Administrativa Curricular</span>
                </div>
            </div>

            <!-- Bento Grid KPIs -->
            <div class="bento-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1.25rem; margin-bottom:1.75rem;">
                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">COORDINADORES (SEGUNDOS EN JEFE)</span>
                    <h3 style="color:#38BDF8; font-size:2rem; font-weight:800; margin:0.3rem 0;">${coordinadores.length}</h3>
                    <div style="font-size:0.75rem; color:#34D399;"><i class="fa-solid fa-crown"></i> Alta/Baja Autorizada</div>
                </div>
                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">${vocab.kpiStudents}</span>
                    <h3 style="color:#38BDF8; font-size:2rem; font-weight:800; margin:0.3rem 0;">480</h3>
                    <div style="font-size:0.75rem; color:#34D399;"><i class="fa-solid fa-arrow-trend-up"></i> +8.5% este mes</div>
                </div>
                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">PLANES PENDIENTES DE RATIFICACIÓN</span>
                    <h3 style="color:#38BDF8; font-size:2rem; font-weight:800; margin:0.3rem 0;">${ratificacionPlanes.filter(p => p.estado_aprobacion === 'vobo_tecnico').length}</h3>
                    <div style="font-size:0.75rem; color:#38BDF8;"><i class="fas fa-check-double"></i> Con VoBo Técnico</div>
                </div>
            </div>

            <!-- Módulo de Bandeja de Ratificación Administrativa de 52 Semanas -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem; box-shadow:0 8px 30px rgba(0,0,0,0.3);">
                <h3 style="color:#38BDF8; margin:0 0 1rem 0; font-size:1.25rem; font-weight:800;">
                    <i class="fas fa-check-double"></i> Bandeja de Ratificación Administrativa de Planes Curriculares (52 Semanas)
                </h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID Plan</th>
                            <th>Nombre del Plan Curricular</th>
                            <th>Área</th>
                            <th>Estado Aprobación</th>
                            <th>Acción de Ratificación Definitiva</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${ratificacionPlanes.map(p => {
                            const isVoBo = (p.estado_aprobacion || 'borrador') === 'vobo_tecnico';
                            const isAprobado = (p.estado_aprobacion || 'borrador') === 'aprobado_definitivo';
                            return `
                                <tr>
                                    <td><strong>#${p.id}</strong></td>
                                    <td>
                                        <strong style="color:#F8FAFC;">${p.nombre_plan}</strong>
                                        <div style="font-size:0.75rem; color:#94A3B8;">${p.observaciones_revision || 'Sin observaciones'}</div>
                                    </td>
                                    <td>${p.area}</td>
                                    <td>
                                        <span class="badge" style="background:${isAprobado ? 'rgba(34,197,94,0.15)' : (isVoBo ? 'rgba(56,189,248,0.15)' : 'rgba(255,255,255,0.1)')}; color:${isAprobado ? '#34D399' : (isVoBo ? '#38BDF8' : '#94A3B8')}; border:1px solid ${isAprobado ? '#34D399' : (isVoBo ? '#38BDF8' : '#94A3B8')}; font-weight:700;">
                                            ${p.estado_aprobacion || 'borrador'}
                                        </span>
                                    </td>
                                    <td>
                                        ${isVoBo ? `
                                            <button class="btn-primary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem; background:#34D399; color:#070B14;" onclick="window.ratifyCurriculumPlanAction(${p.id}, '${token}')">
                                                <i class="fas fa-check-double"></i> Ratificar Definitivamente
                                            </button>
                                            <button class="btn-danger" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem; margin-left:0.25rem;" onclick="window.returnCurriculumPlanAction(${p.id}, '${token}')">
                                                <i class="fas fa-undo"></i> Devolver
                                            </button>
                                        ` : (isAprobado ? '<span style="color:#34D399; font-weight:700; font-size:0.8rem;"><i class="fas fa-shield-check"></i> Ratificado</span>' : '<span style="color:#94A3B8; font-size:0.8rem;">En espera de VoBo Técnico</span>')}
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Módulo de Gobierno de Coordinadores -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.25rem; font-weight:800;">
                            <i class="fas fa-crown"></i> Gestión & Gobierno de Coordinadores (Segundos en Jefe)
                        </h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">El Jefe de Área es la única autoridad para nombrar, asignar ámbito y dar de baja coordinadores</span>
                    </div>
                    <button class="btn-primary" style="min-height:42px; padding:0 1.25rem;" onclick="window.openCoordinatorCreationModal('${token}')">
                        <i class="fas fa-plus-circle"></i> Nombrar Nuevo Coordinador
                    </button>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre del Coordinador</th>
                            <th>Correo Electrónico</th>
                            <th>Estado</th>
                            <th>Acciones de Gobierno</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${coordinadores.map(c => `
                            <tr>
                                <td><strong>#${c.id}</strong></td>
                                <td>
                                    <strong style="color:#F8FAFC;">${c.nombre_completo || c.nombre_usuario}</strong>
                                    <div style="font-size:0.75rem; color:#94A3B8;">${c.ambito || 'Coordinación Operativa de Sede'}</div>
                                </td>
                                <td>${c.correo || 'N/A'}</td>
                                <td>
                                    <span class="badge" style="background:${c.activo ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)'}; border:1px solid ${c.activo ? '#34D399' : '#EF4444'}; color:${c.activo ? '#34D399' : '#F87171'}; font-weight:700;">
                                        <i class="fas ${c.activo ? 'fa-check-circle' : 'fa-ban'}"></i> ${c.activo ? 'Activo / Nombrado' : 'Dado de Baja'}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn-danger" style="min-height:34px; padding:0.2rem 0.75rem; font-size:0.8rem;" onclick="window.toggleCoordinatorStatus(${c.id}, ${!c.activo}, '${token}')">
                                        <i class="fas ${c.activo ? 'fa-user-slash' : 'fa-user-check'}"></i> ${c.activo ? 'Dar de Baja' : 'Reactivar'}
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Tabla de Personal Operativo -->
            <div class="admin-section" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.25rem; font-weight:800;">
                            <i class="fas fa-users"></i> ${vocab.staffTitle}
                        </h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">Altas de Personal Operativo (profesor, jefe_escenarios, almacenista)</span>
                    </div>
                    <button class="btn-primary" style="min-height:42px; padding:0 1.25rem;" onclick="window.openWhitelistedStaffCreationModal('${token}', '${caps.vocacion_institucional || 'deportiva'}')">
                        <i class="fas fa-user-plus"></i> Dar de Alta Personal
                    </button>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre Completo</th>
                            <th>Correo Electrónico</th>
                            <th>Rol Institucional</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${renderStaffRows(staff)}
                    </tbody>
                </table>
            </div>

        </div>
    `;
}

function renderStaffRows(staff) {
    if (!staff || staff.length === 0) {
        return '<tr><td colspan="5">No se encontró personal en tu área.</td></tr>';
    }
    return staff.map(user => `
        <tr>
            <td><strong>#${user.id}</strong></td>
            <td>${user.nombre_completo || 'Usuario Operativo'}</td>
            <td>${user.correo || 'N/A'}</td>
            <td><span class="badge" style="background:rgba(56,189,248,0.12); color:#38BDF8; font-size:0.75rem; font-weight:700;">${Array.isArray(user.roles) ? user.roles.join(', ') : (user.rol || 'profesor')}</span></td>
            <td>
                <button class="btn-secondary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem;">Ver Detalle</button>
            </td>
        </tr>
    `).join('');
}

window.ratifyCurriculumPlanAction = async function(planId, token) {
    const obs = prompt("Observaciones para Ratificación Administrativa Definitiva:", "Plan Curricular de 52 Semanas ratificado administrativamente para ejecución.");
    if (obs === null) return;

    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/curriculum/planes/${planId}/ratificar`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ observaciones: obs })
        });
        if (res.ok) {
            alert('Plan Curricular de 52 semanas ratificado administrativamente en forma definitiva.');
            renderJefeAreaView(token);
        } else {
            const err = await res.json();
            alert(`Error al ratificar plan: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

window.openWhitelistedStaffCreationModal = async function(token, vocacion) {
    let modal = document.getElementById('whitelisted-staff-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'whitelisted-staff-modal';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(7,11,20,0.88); backdrop-filter:blur(8px); z-index:99999; display:flex; justify-content:center; align-items:center; padding:1.5rem;';
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';

    const isCultural = vocacion === 'cultural';
    const specLabel = isCultural ? 'Modalidades Culturales Adoptadas' : 'Disciplinas Deportivas Adoptadas';

    let activeSpecs = [];
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/my-specialties`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) activeSpecs = await res.json();
    } catch (e) {
        console.warn('Error loading company specialties for modal:', e);
    }

    const filteredSpecs = activeSpecs.filter(s => s.vertical === (isCultural ? 'cultura' : 'deporte'));

    modal.innerHTML = `
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.35); border-radius:16px; width:100%; max-width:620px; padding:2rem; box-shadow:0 20px 40px rgba(0,0,0,0.6); color:#F8FAFC;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.75rem;">
                <div>
                    <h3 style="color:#38BDF8; margin:0; font-size:1.25rem;"><i class="fas fa-user-plus"></i> Dar de Alta Personal de Área</h3>
                    <p style="color:#94A3B8; font-size:0.8rem; margin:0.25rem 0 0 0;">Control de Registro Whitelisted (Whitelist: Profesor, Jefe de Escenarios, Almacenista)</p>
                </div>
                <button onclick="document.getElementById('whitelisted-staff-modal').style.display='none'" style="background:transparent; border:none; color:#94A3B8; font-size:1.5rem; cursor:pointer;"><i class="fas fa-times"></i></button>
            </div>

            <form id="whitelisted-staff-form" onsubmit="window.submitWhitelistedStaffForm(event, '${token}')">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Nombre Completo *</label>
                        <input type="text" id="staff-name" required placeholder="Ej. Prof. Roberto Silva" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Correo Electrónico *</label>
                        <input type="email" id="staff-email" required placeholder="roberto.silva@sga-cd.org" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Nombre de Usuario *</label>
                        <input type="text" id="staff-username" required placeholder="roberto_silva" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Rol Permitido (Whitelist) *</label>
                        <select id="staff-role" required style="width:100%; background:#070B14; border:1px solid #38BDF8; border-radius:8px; padding:0.5rem 0.75rem; color:#38BDF8; font-weight:700; font-size:0.88rem;">
                            <option value="profesor">${isCultural ? 'profesor (Formador / Tallerista)' : 'profesor (Instructor Deportivo / Entrenador)'}</option>
                            <option value="jefe_escenarios">jefe_escenarios (Encargado de Escenarios / Espacios)</option>
                            <option value="almacenista">almacenista (Encargado de Inventario y Dotaciones)</option>
                        </select>
                    </div>
                </div>

                <div style="margin-bottom:1.25rem;">
                    <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">${specLabel} (Para rol Profesor)</label>
                    <select id="staff-specialty" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                        ${filteredSpecs.length > 0 ? filteredSpecs.map(s => `<option value="${s.empresa_especialidad_id}">${s.nombre} (${s.categoria})</option>`).join('') : '<option value="">No hay especialidades adoptadas actualmente</option>'}
                    </select>
                    <small style="color:#94A3B8; font-size:0.72rem; display:block; margin-top:0.25rem;">* La creación de especialidades personalizadas On-The-Fly está restringida a admin_empresa.</small>
                </div>

                <div style="display:flex; justify-content:flex-end; gap:0.75rem; margin-top:1.5rem;">
                    <button type="button" onclick="document.getElementById('whitelisted-staff-modal').style.display='none'" class="btn-secondary" style="min-height:40px; padding:0 1.25rem;">Cancelar</button>
                    <button type="submit" class="btn-primary" style="min-height:40px; padding:0 1.5rem;"><i class="fas fa-check-circle"></i> Registrar Personal</button>
                </div>
            </form>
        </div>
    `;
};

window.submitWhitelistedStaffForm = async function(event, token) {
    event.preventDefault();
    const name = document.getElementById('staff-name').value;
    const email = document.getElementById('staff-email').value;
    const username = document.getElementById('staff-username').value;
    const role = document.getElementById('staff-role').value;

    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';

    try {
        const capsRes = await fetch(`${baseUrl}/api/v1/tenants/my-plan-capabilities`, { headers: { 'Authorization': `Bearer ${token}` } });
        const caps = capsRes.ok ? await capsRes.json() : { inquilino_id: 100 };

        const payload = {
            nombre_completo: name,
            correo: email,
            email: email,
            nombre_usuario: username,
            rol: role,
            password: 'TempPassword123!',
            inquilino_id: caps.inquilino_id
        };

        const res = await fetch(`${baseUrl}/api/v1/admin/users/by-empresa`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert(`Personal registrado con éxito (${role}).`);
            document.getElementById('whitelisted-staff-modal').style.display = 'none';
            renderJefeAreaView(token);
        } else {
            const err = await res.json();
            alert(`Error: ${err.detail || 'No se pudo crear el usuario.'}`);
        }
    } catch (e) {
        alert(`Error de conexión: ${e.message}`);
    }
};

window.openCoordinatorCreationModal = function(token) {
    let modal = document.getElementById('coordinator-creation-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'coordinator-creation-modal';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(7,11,20,0.88); backdrop-filter:blur(8px); z-index:99999; display:flex; justify-content:center; align-items:center; padding:1.5rem;';
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';

    modal.innerHTML = `
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.35); border-radius:16px; width:100%; max-width:550px; padding:2rem; box-shadow:0 20px 40px rgba(0,0,0,0.6); color:#F8FAFC;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.75rem;">
                <div>
                    <h3 style="color:#38BDF8; margin:0; font-size:1.25rem;"><i class="fas fa-crown"></i> Nombrar Coordinador (Segundo en Jefe)</h3>
                    <p style="color:#94A3B8; font-size:0.8rem; margin:0.25rem 0 0 0;">Nombramiento de Coordinadores de Sede o Disciplina</p>
                </div>
                <button onclick="document.getElementById('coordinator-creation-modal').style.display='none'" style="background:transparent; border:none; color:#94A3B8; font-size:1.5rem; cursor:pointer;"><i class="fas fa-times"></i></button>
            </div>

            <form onsubmit="window.submitCoordinatorCreation(event, '${token}')">
                <div style="margin-bottom:1rem;">
                    <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Nombre Completo *</label>
                    <input type="text" id="coord-name" required placeholder="Ej. Dra. Patricia Suárez" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC;">
                </div>
                <div style="margin-bottom:1rem;">
                    <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Correo Electrónico *</label>
                    <input type="email" id="coord-email" required placeholder="patricia.suarez@sga-cd.org" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC;">
                </div>
                <div style="margin-bottom:1.25rem;">
                    <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Nombre de Usuario *</label>
                    <input type="text" id="coord-username" required placeholder="patricia_suarez" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC;">
                </div>

                <div style="display:flex; justify-content:flex-end; gap:0.75rem;">
                    <button type="button" onclick="document.getElementById('coordinator-creation-modal').style.display='none'" class="btn-secondary" style="min-height:40px; padding:0 1.25rem;">Cancelar</button>
                    <button type="submit" class="btn-primary" style="min-height:40px; padding:0 1.5rem;"><i class="fas fa-check"></i> Emitir Nombramiento</button>
                </div>
            </form>
        </div>
    `;
};

window.submitCoordinatorCreation = async function(event, token) {
    event.preventDefault();
    const name = document.getElementById('coord-name').value;
    const email = document.getElementById('coord-email').value;
    const username = document.getElementById('coord-username').value;

    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';

    try {
        const capsRes = await fetch(`${baseUrl}/api/v1/tenants/my-plan-capabilities`, { headers: { 'Authorization': `Bearer ${token}` } });
        const caps = capsRes.ok ? await capsRes.json() : { inquilino_id: 100 };

        const payload = {
            nombre_completo: name,
            correo: email,
            email: email,
            nombre_usuario: username,
            rol: 'coordinador',
            password: 'TempPassword123!',
            inquilino_id: caps.inquilino_id
        };

        const res = await fetch(`${baseUrl}/api/v1/admin/users/by-empresa`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            alert('Coordinador nombrado exitosamente.');
            document.getElementById('coordinator-creation-modal').style.display = 'none';
            renderJefeAreaView(token);
        } else {
            const err = await res.json();
            alert(`Error: ${err.detail || 'No se pudo nombrar al coordinador.'}`);
        }
    } catch (e) {
        alert(`Error de conexión: ${e.message}`);
    }
};

window.toggleCoordinatorStatus = async function(userId, newActiveStatus, token) {
    if (!confirm(`¿Está seguro de ${newActiveStatus ? 'reactivar' : 'dar de baja'} a este Coordinador?`)) return;
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/admin/users/${userId}/status?active=${newActiveStatus}`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            alert(`Estado del Coordinador actualizado (${newActiveStatus ? 'Activo' : 'Dado de Baja'}).`);
            renderJefeAreaView(token);
        } else {
            const err = await res.json();
            alert(`Error: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de conexión: ${e.message}`);
    }
};

if (typeof registerView === 'function') {
    registerView('jefe_area', 'panel-area', renderJefeAreaView);
    registerView('jefe_area', 'dashboard', renderJefeAreaView);
}
