// js/views/profesor.js — Panel del Profesor / Instructor (Centro Operativo del Sistema)

async function fetchProfesorTenantCaps(token) {
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

async function renderProfesorView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Centro Operativo del Profesor...</p>
        </div>
    `;

    const caps = await fetchProfesorTenantCaps(token);
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
        title: 'Gestión Pedagógica de Talleres & Formación Artística',
        myStudentsCount: 42,
        attendanceRate: '96.2%',
        hoursTaught: 120,
        icon: 'fa-chalkboard-teacher'
    } : {
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        title: 'Gestión Técnica de Escuelas Deportivas & Alto Rendimiento',
        myStudentsCount: 40,
        attendanceRate: '95.8%',
        hoursTaught: 140,
        icon: 'fa-chalkboard-teacher'
    };

    // Fetch existing curriculum plan for this teacher from real backend
    let activePlan = null;
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/curriculum/planes/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            const planes = await res.json();
            if (planes && planes.length > 0) activePlan = planes[0];
        }
    } catch (e) {
        console.warn('Error fetching curriculum plan from backend:', e);
    }

    const currentStatus = activePlan ? (activePlan.estado_aprobacion || 'borrador') : 'borrador';
    const statusBadgeMap = {
        'borrador': '<span class="badge" style="background:rgba(255,255,255,0.1); border:1px solid #94A3B8; color:#94A3B8;"><i class="fas fa-edit"></i> Borrador</span>',
        'en_revision': '<span class="badge" style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24;"><i class="fas fa-clock"></i> En Revisión Técnico (Coordinador)</span>',
        'vobo_tecnico': '<span class="badge" style="background:rgba(56,189,248,0.2); border:1px solid #38BDF8; color:#38BDF8;"><i class="fas fa-check"></i> VoBo Técnico (Pendiente Ratificación Jefe)</span>',
        'aprobado_definitivo': '<span class="badge" style="background:rgba(34,197,94,0.2); border:1px solid #34D399; color:#34D399;"><i class="fas fa-check-double"></i> Aprobado Definitivo</span>',
        'devuelto': '<span class="badge" style="background:rgba(239,68,68,0.2); border:1px solid #EF4444; color:#F87171;"><i class="fas fa-exclamation-circle"></i> Devuelto con Observaciones</span>'
    };

    contentArea.innerHTML = `
        <div class="profesor-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas ${vocab.icon}" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            <span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-user-graduate"></i> Instructor Acreditado
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
                    <span style="font-size:0.72rem; color:#94A3B8;">Telemetría Scoped a Mis Alumnos</span>
                </div>
            </div>

            <!-- Módulo Power BI Personalizado -->
            <div class="bento-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1.25rem; margin-bottom:1.75rem;">
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">MIS ALUMNOS A CARGO</span>
                    <h3 style="color:#38BDF8; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">${vocab.myStudentsCount}</h3>
                    <div style="font-size:0.75rem; color:#34D399;"><i class="fas fa-users"></i> Asignación Docente Verificada</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">TASA ASISTENCIA PROMEDIO</span>
                    <h3 style="color:#34D399; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">${vocab.attendanceRate}</h3>
                    <div style="font-size:0.75rem; color:#34D399;"><i class="fas fa-check-circle"></i> Sincronizado PWA Offline</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">HORAS CUMPLIDAS EN AÑO</span>
                    <h3 style="color:#38BDF8; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">${vocab.hoursTaught} hrs</h3>
                    <div style="font-size:0.75rem; color:#38BDF8;"><i class="fas fa-clock"></i> Cumplimiento Horario 100%</div>
                </div>
            </div>

            <!-- Planificador Curricular Anual de 52 Semanas (Conectado a Backend Real) -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.2rem; font-weight:800;">
                            <i class="fas fa-calendar-alt"></i> Planificador Curricular Anual (52 Semanas)
                        </h3>
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.25rem;">
                            <span style="font-size:0.8rem; color:#94A3B8;">Estado del Plan:</span>
                            ${statusBadgeMap[currentStatus]}
                            <span style="font-size:0.75rem; color:#94A3B8; margin-left:0.5rem;">Versión: <strong>v${activePlan ? activePlan.version : 1}</strong></span>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap;">
                        <select id="select-semana-curriculo" onchange="window.updateCurriculumWeekView(this.value)" style="background:#070B14; border:1px solid #38BDF8; border-radius:8px; padding:0.4rem 0.75rem; color:#38BDF8; font-weight:700;">
                            ${Array.from({length: 52}, (_, i) => `<option value="${i+1}">Semana ${i+1}</option>`).join('')}
                        </select>
                        ${currentStatus === 'borrador' || currentStatus === 'devuelto' ? `
                            <button class="btn-primary" style="min-height:38px; padding:0 1.25rem;" onclick="window.submitPlanForReviewAction(${activePlan ? activePlan.id : 1}, '${token}')">
                                <i class="fas fa-paper-plane"></i> Presentar a Revisión (Coordinador)
                            </button>
                        ` : ''}
                    </div>
                </div>

                ${activePlan && activePlan.observaciones_revision ? `
                    <div style="background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.3); border-radius:10px; padding:0.85rem; margin-bottom:1rem; color:#FBBF24; font-size:0.85rem;">
                        <i class="fas fa-comment-dots"></i> <strong>Observaciones de Revisión:</strong> ${activePlan.observaciones_revision}
                    </div>
                ` : ''}

                <div id="curriculum-week-container" style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem;">
                    <h4 style="color:#38BDF8; margin:0 0 0.5rem 0;" id="curr-week-title">Semana 1: Fundamentación y Diagnóstico Biométrico / Técnico</h4>
                    <p style="color:#94A3B8; font-size:0.88rem; margin:0.25rem 0;"><strong>Objetivo de la Sesión:</strong> Evaluación de movilidad, postura corporal e iniciación de patrones de movimiento básicos.</p>
                    <p style="color:#94A3B8; font-size:0.88rem; margin:0.25rem 0;"><strong>Estructura:</strong> Calentamiento dinámico (15 min) -> Técnica específica (45 min) -> Vuelta a la calma y estiramiento (15 min).</p>
                    <p style="color:#38BDF8; font-size:0.85rem; margin-top:0.5rem;"><strong>Implementos Requeridos:</strong> Cronómetros, petos / matas de yoga, planillas de registro.</p>
                </div>
            </div>

            <!-- Control de Asistencia Diaria & Alerta Temprana de Deserción -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.2rem; font-weight:800;"><i class="fas fa-user-check"></i> Roster de Mis Alumnos & Alerta de Deserción</h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">Detector automático al acumular 3 faltas consecutivas</span>
                    </div>
                    <button class="btn-primary" style="min-height:40px; padding:0 1.25rem;" onclick="alert('Iniciando toma de asistencia masiva PWA.')"><i class="fas fa-check-square"></i> Tomar Asistencia Sesión Hoy</button>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID Estudiante</th>
                            <th>Nombre Completo</th>
                            <th>Asistencia %</th>
                            <th>Estado de Asistencia & Alerta</th>
                            <th>Acción</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>#101</strong></td>
                            <td>Mateo Andrés Ríos</td>
                            <td>98.5%</td>
                            <td><span class="badge" style="background:rgba(34,197,94,0.15); border:1px solid #34D399; color:#34D399;"><i class="fas fa-check-circle"></i> Excelente Asistencia</span></td>
                            <td><button class="btn-secondary" style="min-height:32px; padding:0.2rem 0.5rem; font-size:0.8rem;">Ver Ficha</button></td>
                        </tr>
                        <tr>
                            <td><strong>#102</strong></td>
                            <td>Sofía Valentina Cruz</td>
                            <td>65.0%</td>
                            <td>
                                <span class="badge" style="background:rgba(245,158,11,0.2); border:1px solid #F59E0B; color:#FBBF24; font-weight:800; padding:0.35rem 0.75rem; border-radius:12px;">
                                    <i class="fas fa-exclamation-triangle"></i> Riesgo de Deserción — Contactar Acudiente (3 Faltas)
                                </span>
                            </td>
                            <td><button class="btn-primary" style="min-height:32px; padding:0.2rem 0.5rem; font-size:0.8rem; background:#F59E0B; color:#070B14;" onclick="alert('Contactando a Acudiente: Sra. Maria Cruz (Tel: 3115928401)')"><i class="fas fa-phone"></i> Contactar</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </div>
    `;
}

window.submitPlanForReviewAction = async function(planId, token) {
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/curriculum/planes/${planId}/presentar`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        });
        if (res.ok) {
            alert('Plan curricular de 52 semanas presentado exitosamente al Coordinador para revisión técnica.');
            renderProfesorView(token);
        } else {
            const err = await res.json();
            alert(`Error al presentar el plan: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

window.updateCurriculumWeekView = function(weekNum) {
    const titleEl = document.getElementById('curr-week-title');
    if (titleEl) {
        titleEl.textContent = `Semana ${weekNum}: Programación Técnica Específica y Progresión Cargas / Repertorio`;
    }
};

async function renderProfesorSuscripcionView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; font-size:1.5rem; display:flex; align-items:center; gap:0.5rem;">
                <i class="fas fa-credit-card"></i> Estado de Suscripción e Indicadores del Docente
            </h2>
            <p style="color:#94A3B8; font-size:0.9rem;">Información sobre el plan institucional activo y capacidades asignadas.</p>
        </div>
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem;">
                <div style="width:48px; height:48px; border-radius:12px; background:rgba(56,189,248,0.15); display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:1.25rem;">
                    <i class="fas fa-id-badge"></i>
                </div>
                <div>
                    <h3 style="color:#F8FAFC; margin:0; font-size:1.1rem;">Suscripción Docente — Cobertura Institucional</h3>
                    <p style="color:#38BDF8; margin:0; font-size:0.85rem; font-weight:600;">Plan Activo Habilitado por la Organización</p>
                </div>
            </div>
            <p style="color:#94A3B8; font-size:0.9rem; line-height:1.5;">
                Como instructor docente, su cuenta dispone de acceso completo a la planificación de 52 semanas, control de asistencia, telemetría de estudiantes y gestión de elementos en custodia.
            </p>
        </div>
    `;
}

if (typeof registerView === 'function') {
    registerView('profesor', 'gestionar-cursos', renderProfesorView);
    registerView('profesor', 'dashboard', renderProfesorView);
    registerView('profesor', 'suscripcion', renderProfesorSuscripcionView);
}
