// js/views/padre_acudiente.js — Panel del Padre o Acudiente (Postulación de Beneficiarios, Tutoría y Asistencia)

async function fetchPadreTenantCaps(token) {
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

async function renderPadreAcudienteView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Panel del Acudiente...</p>
        </div>
    `;

    const caps = await fetchPadreTenantCaps(token);
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
        title: 'Tutoría Legal & Seguimiento a Talleres Culturales',
        pupils: [
            { id: 101, nombre: 'Mateo Andrés Ríos', edad: '14 Años', curso: 'Taller de Guitarra Clásica', asistencia: '98.5%', estado: 'Matriculado' },
            { id: 102, nombre: 'Valeria Valentina Ríos', edad: '11 Años', curso: 'Danza Joropo / Folclor Llanero', asistencia: '95.0%', estado: 'Matriculado' }
        ]
    } : {
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        title: 'Tutoría Legal & Seguimiento a Escuelas Deportivas',
        pupils: [
            { id: 101, nombre: 'Mateo Andrés Ríos', edad: '14 Años', curso: 'Escuela de Taekwondo WT (Cinta Amarilla)', asistencia: '98.5%', estado: 'Matriculado' },
            { id: 102, nombre: 'Valeria Valentina Ríos', edad: '11 Años', curso: 'Escuela de Natación Formativa', asistencia: '95.0%', estado: 'Matriculado' }
        ]
    };

    contentArea.innerHTML = `
        <div class="padre-acudiente-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas fa-child" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            <span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-user-shield"></i> Tutor / Acudiente Responsable
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
                    </div>
                    <span style="font-size:0.72rem; color:#94A3B8;">Panel Multi-Estudiante Activo</span>
                </div>
            </div>

            <!-- Zona 2: Mis Hijos / Beneficiarios a Cargo -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.25rem; font-weight:800;"><i class="fas fa-users"></i> Mis Hijos & Pupilos Registrados</h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">Supervisión de asistencia, autorizaciones legales e inscripción</span>
                    </div>
                    <button class="btn-primary" style="min-height:42px; padding:0 1.25rem;" onclick="alert('Formulario de registro y postulación de nuevo hijo/pupilo.')"><i class="fas fa-user-plus"></i> Postular Nuevo Hijo</button>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1.25rem;">
                    ${vocab.pupils.map(p => `
                        <div style="background:#070B14; border:1px solid rgba(56,189,248,0.25); border-radius:12px; padding:1.25rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                                <strong style="color:#F8FAFC; font-size:1.15rem;">${p.nombre}</strong>
                                <span class="badge" style="background:rgba(34,197,94,0.15); border:1px solid #34D399; color:#34D399; font-size:0.75rem;"><i class="fas fa-check-circle"></i> ${p.estado}</span>
                            </div>
                            <p style="color:#94A3B8; font-size:0.85rem; margin:0.25rem 0;"><strong>Edad:</strong> ${p.edad} | <strong>Asistencia:</strong> <span style="color:#38BDF8; font-weight:700;">${p.asistencia}</span></p>
                            <p style="color:#94A3B8; font-size:0.85rem; margin:0.25rem 0 0.8rem 0;"><strong>Programa:</strong> ${p.curso}</p>

                            <div style="display:flex; gap:0.5rem; flex-wrap:wrap; border-top:1px dashed rgba(255,255,255,0.1); padding-top:0.75rem;">
                                <button class="btn-primary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem;" onclick="alert('Descargando reporte mensual de desarrollo técnico y conducta.')"><i class="fas fa-chart-bar"></i> Progreso</button>
                                <button class="btn-secondary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem;" onclick="alert('Autorización de salidas a torneos/festivales confirmada digitalmente.')"><i class="fas fa-file-signature"></i> Autorizaciones</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

        </div>
    `;
}

// --- Registrar vista de Padre/Acudiente ---
if (typeof registerView === 'function') {
    registerView('padre_acudiente', 'mis-alumnos', renderPadreAcudienteView);
}
