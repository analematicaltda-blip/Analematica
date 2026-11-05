// js/views/coordinador.js — Dashboard del Coordinador General (Segundo en Jefe) Bento Grid 60-30-10

async function fetchCoordinadorTenantCaps(token) {
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

async function renderPlanificacionView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Panel de Coordinación General...</p>
        </div>
    `;

    const caps = await fetchCoordinadorTenantCaps(token);
    const isCultural = (caps.vocacion_institucional || 'deportiva') === 'cultural';

    const natureMap = {
        'entidad_publica': { label: 'Entidad Pública', icon: 'fa-landmark' },
        'entidad_privada': { label: 'Entidad Privada', icon: 'fa-building-columns' },
        'empresa_publica': { label: 'Empresa Pública', icon: 'fa-gears' },
        'empresa_privada': { label: 'Empresa Privada', icon: 'fa-briefcase' }
    };
    const natureInfo = natureMap[caps.tipo_organizacion] || { label: 'Organización Institucional', icon: 'fa-building' };

    const vocab = isCultural ? {
        vocationLabel: 'ESPECIALIDAD: CULTURAL',
        title: 'Supervisión en Campo & Aprobación Curricular de Talleres',
        liveBoard: [
            { profesor: 'Prof. Elena Ramos', clase: 'Taller de Danza Joropo A', escenario: 'Casa de Cultura - Salón 1', custody: 'Trajes Tipicos #10', estado: 'En Cancha / Taller' },
            { profesor: 'Prof. Roberto Silva', clase: 'Guitarra Clásica', escenario: 'Casa de Cultura - Sala de Musica', custody: 'Arpa Llanera #SER-01', estado: 'En Cancha / Taller' }
        ]
    } : {
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        title: 'Supervisión en Campo & Verificación Cruzada de Escuelas',
        liveBoard: [
            { profesor: 'Prof. Carlos Mendoza', clase: 'Escuela de Taekwondo WT', escenario: 'Villa Olímpica - Dojo Tatami A', custody: 'Peto Reversible #001', estado: 'En Cancha / Taller' },
            { profesor: 'Prof. Roberto Silva', clase: 'Fútbol Campo Sub-15', escenario: 'Villa Olímpica - Cancha 1', custody: 'Balones FIFA #010', estado: 'En Cancha / Taller' }
        ]
    };

    // Fetch curriculum plans for technical review
    let reviewPlanes = [];
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/curriculum/planes/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) reviewPlanes = await res.json();
    } catch (e) {
        console.warn('Error fetching curriculum plans for coordinator review:', e);
    }

    if (!reviewPlanes || reviewPlanes.length === 0) {
        reviewPlanes = [
            { id: 1, nombre_plan: 'Plan Anual Taekwondo Formativo 52w', area: 'Deportes', version: 1, estado_aprobacion: 'en_revision', observaciones_revision: 'Presentado para visto bueno técnico.' }
        ];
    }

    const pendingReviewCount = reviewPlanes.filter(p => (p.estado_aprobacion || 'borrador') === 'en_revision').length;

    contentArea.innerHTML = `
        <div class="coordinador-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas fa-crown" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            <span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                👑 COORDINADOR GENERAL — SEGUNDO EN JEFE
                            </span>
                        </div>
                        <div style="display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap; font-size:0.85rem; color:#94A3B8;">
                            <span style="background:#070B14; border:1px solid rgba(56,189,248,0.25); padding:0.25rem 0.75rem; border-radius:12px; color:#38BDF8; font-weight:700;">
                                <i class="fas ${natureInfo.icon}"></i> ${natureInfo.label}
                            </span>
                            <span style="color:#94A3B8;"><i class="fa-solid fa-shield-halved" style="color:#38BDF8;"></i> ${vocab.title}</span>
                        </div>
                    </div>
                </div>

                <div style="background:#070B14; border:1px solid rgba(56,189,248,0.35); padding:0.6rem 1rem; border-radius:16px; text-align:right;">
                    <div style="color:#38BDF8; font-size:0.85rem; font-weight:800; display:flex; align-items:center; gap:0.5rem; justify-content:flex-end;">
                        <i class="fas ${isCultural ? 'fa-palette' : 'fa-running'}"></i> ${vocab.vocationLabel}
                        <i class="fas fa-lock" style="color:#F59E0B;" title="Vocación fija de la organización"></i>
                    </div>
                    <span style="font-size:0.72rem; color:#94A3B8;">Supervisión de Sede & Aprobación Curricular</span>
                </div>
            </div>

            <!-- Bento Grid 60-30-10 Power BI -->
            <div class="bento-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1.25rem; margin-bottom:1.75rem;">
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">CLASES EJECUTADAS EN SEMANA</span>
                    <h3 style="color:#38BDF8; font-size:2rem; font-weight:800; margin:0.3rem 0;">48 / 50</h3>
                    <div style="font-size:0.75rem; color:#34D399;"><i class="fas fa-chart-line"></i> 96% de Cumplimiento Horario</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">COBERTURA DE SALONES</span>
                    <h3 style="color:#38BDF8; font-size:2rem; font-weight:800; margin:0.3rem 0;">100%</h3>
                    <div style="font-size:0.75rem; color:#38BDF8;"><i class="fas fa-map-marker-alt"></i> Sin Solapamientos</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">PLANES PENDIENTES DE VOBO</span>
                    <h3 style="color:#F59E0B; font-size:2rem; font-weight:800; margin:0.3rem 0;">${pendingReviewCount} Planes</h3>
                    <div style="font-size:0.75rem; color:#F59E0B;"><i class="fas fa-clipboard-check"></i> En Revisión Técnica</div>
                </div>
            </div>

            <!-- Módulo 1: Supervisión en Campo y Verificación Cruzada en Vivo -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem;">
                <h3 style="color:#38BDF8; margin:0 0 1rem 0; font-size:1.2rem; font-weight:800;">
                    <i class="fas fa-eye"></i> Módulo 1: Supervisión en Campo & Verificación Cruzada en Vivo
                </h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Profesor / Instructor</th>
                            <th>Disciplina / Taller</th>
                            <th>Escenario & Salón Asignado</th>
                            <th>Elementos en Custodia</th>
                            <th>Verificación Presencial</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${vocab.liveBoard.map(row => `
                            <tr>
                                <td><strong style="color:#F8FAFC;">${row.profesor}</strong></td>
                                <td>${row.clase}</td>
                                <td><span style="color:#38BDF8;"><i class="fas fa-door-open"></i> ${row.escenario}</span></td>
                                <td><span style="color:#94A3B8;"><i class="fas fa-box"></i> ${row.custody}</span></td>
                                <td>
                                    <button class="btn-primary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem; background:#34D399; color:#070B14;" onclick="alert('Verificación de presencia confirmada en cancha/taller.')">
                                        <i class="fas fa-check-circle"></i> ${row.estado}
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Módulo 3: Bandeja de Aprobación / VoBo Técnico del Plan Curricular de 52 Semanas -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <h3 style="color:#38BDF8; margin:0 0 1rem 0; font-size:1.2rem; font-weight:800;">
                    <i class="fas fa-clipboard-check"></i> Módulo 3: Bandeja de Visto Bueno Técnico Curricular (52 Semanas)
                </h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nombre del Plan Curricular</th>
                            <th>Área</th>
                            <th>Versión</th>
                            <th>Estado Aprobación</th>
                            <th>Acciones de Revisión Técnica</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${reviewPlanes.map(plan => {
                            const isEnRevision = (plan.estado_aprobacion || 'borrador') === 'en_revision';
                            return `
                                <tr>
                                    <td><strong>#${plan.id}</strong></td>
                                    <td>
                                        <strong style="color:#F8FAFC;">${plan.nombre_plan}</strong>
                                        <div style="font-size:0.75rem; color:#94A3B8;">${plan.observaciones_revision || 'Sin observaciones'}</div>
                                    </td>
                                    <td>${plan.area}</td>
                                    <td>v${plan.version || 1}</td>
                                    <td>
                                        <span class="badge" style="background:${isEnRevision ? 'rgba(245,158,11,0.2)' : 'rgba(56,189,248,0.2)'}; color:${isEnRevision ? '#FBBF24' : '#38BDF8'}; border:1px solid ${isEnRevision ? '#F59E0B' : '#38BDF8'}; font-weight:700;">
                                            ${plan.estado_aprobacion || 'borrador'}
                                        </span>
                                    </td>
                                    <td>
                                        ${isEnRevision ? `
                                            <button class="btn-primary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem;" onclick="window.grantCoordinatorVoBoAction(${plan.id}, '${token}')">
                                                <i class="fas fa-check"></i> Conceder VoBo Técnico
                                            </button>
                                            <button class="btn-danger" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem; margin-left:0.25rem;" onclick="window.returnCurriculumPlanAction(${plan.id}, '${token}')">
                                                <i class="fas fa-undo"></i> Devolver
                                            </button>
                                        ` : '<span style="color:#94A3B8; font-size:0.8rem;">VoBo Procesado</span>'}
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>

        </div>
    `;
}

window.grantCoordinatorVoBoAction = async function(planId, token) {
    const obs = prompt("Observaciones para conceder Visto Bueno Técnico:", "VoBo técnico concedido. Cumple con los objetivos de 52 semanas.");
    if (obs === null) return;

    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/curriculum/planes/${planId}/vobo`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ observaciones: obs })
        });
        if (res.ok) {
            alert('Visto Bueno Técnico concedido exitosamente. Plan remitido a Jefe de Área para ratificación.');
            renderPlanificacionView(token);
        } else {
            const err = await res.json();
            alert(`Error al conceder VoBo: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

window.returnCurriculumPlanAction = async function(planId, token) {
    const obs = prompt("Observaciones para devolver el plan al docente:", "Ajustar cargas de entrenamiento de la semana 10 a 14.");
    if (!obs) return;

    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/curriculum/planes/${planId}/devolver`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ observaciones: obs })
        });
        if (res.ok) {
            alert('Plan devuelto exitosamente al docente con observaciones.');
            renderPlanificacionView(token);
        } else {
            const err = await res.json();
            alert(`Error al devolver plan: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

async function renderVerificarProgramacionView(token) {
    await renderPlanificacionView(token);
}

async function renderAprobacionesView(token) {
    await renderPlanificacionView(token);
}

async function renderGestionarMisionesView(token) {
    await renderPlanificacionView(token);
}

if (typeof registerView === 'function') {
    registerView('coordinador', 'planificacion', renderPlanificacionView);
    registerView('coordinador', 'verificar-programacion', renderVerificarProgramacionView);
    registerView('coordinador', 'aprobaciones', renderAprobacionesView);
    registerView('coordinador', 'gestionar-misiones', renderGestionarMisionesView);
    registerView('coordinador', 'dashboard', renderPlanificacionView);
}
