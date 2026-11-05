// js/views/alumno.js — Panel del Alumno / Estudiante (Vitrina, Postulación, Asistencia PWA y Carnet Digital)

async function fetchAlumnoTenantCaps(token) {
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

async function renderMisCursosView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Panel del Alumno...</p>
        </div>
    `;

    const caps = await fetchAlumnoTenantCaps(token);
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
        title: 'Talleres Culturales & Modalidades Artísticas',
        catalog: [
            { id: 1, nombre: 'Danza Joropo / Folclor Llanero', nivel: 'Iniciación', horario: 'Lun y Mié 16:00 - 18:00', cupos: 8, profesor: 'Prof. Elena Ramos' },
            { id: 2, nombre: 'Taller de Guitarra Clásica & Acústica', nivel: 'Intermedio', horario: 'Mar y Jue 14:00 - 16:00', cupos: 5, profesor: 'Prof. Roberto Silva' },
            { id: 3, nombre: 'Teatro y Expresión Corporal', nivel: 'Abierto', horario: 'Sábados 09:00 - 12:00', cupos: 12, profesor: 'Prof. Carlos Mendoza' }
        ]
    } : {
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        title: 'Escuelas Deportivas & Formación de Atletas',
        catalog: [
            { id: 1, nombre: 'Escuela de Taekwondo WT', nivel: 'Cinta Blanca / Amarilla', horario: 'Lun y Mié 14:00 - 16:00', cupos: 10, profesor: 'Prof. Carlos Mendoza' },
            { id: 2, nombre: 'Fútbol Campo Formativo', nivel: 'Sub-15', horario: 'Mar y Jue 16:00 - 18:00', cupos: 6, profesor: 'Prof. Roberto Silva' },
            { id: 3, nombre: 'Natación y Acondicionamiento', nivel: 'Intermedio', horario: 'Viernes 15:00 - 17:00', cupos: 4, profesor: 'Prof. Elena Ramos' }
        ]
    };

    contentArea.innerHTML = `
        <div class="alumno-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas fa-user-graduate" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            <span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-certificate"></i> Suscripción Estudiantil Costo 0
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
                    <span style="font-size:0.72rem; color:#94A3B8;">Acceso Gratuito Estudiantil</span>
                </div>
            </div>

            <!-- Zona 2: Carnet Digital Institucional & QR Verification -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:grid; grid-template-columns: 280px 1fr; gap:1.5rem; box-shadow:0 8px 30px rgba(0,0,0,0.3);">
                <div style="background:linear-gradient(135deg, #070B14 0%, #162032 100%); border:1.5px solid #38BDF8; border-radius:14px; padding:1.25rem; text-align:center; box-shadow:0 0 20px rgba(56,189,248,0.2);">
                    <div style="width:70px; height:70px; border-radius:50%; background:#0D1424; border:2px solid #38BDF8; margin:0 auto 0.75rem auto; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:2rem;">
                        <i class="fas fa-user"></i>
                    </div>
                    <strong style="color:#F8FAFC; font-size:1.05rem; display:block;">Mateo Andrés Ríos</strong>
                    <span style="color:#38BDF8; font-size:0.78rem; font-weight:700;">COD: STD-2024-8810</span>
                    <div style="margin:0.75rem 0; background:#FFF; padding:0.5rem; border-radius:8px; display:inline-block;">
                        <i class="fas fa-qrcode" style="font-size:3.5rem; color:#070B14;"></i>
                    </div>
                    <span class="badge" style="background:rgba(34,197,94,0.15); border:1px solid #34D399; color:#34D399; font-size:0.75rem; font-weight:700;"><i class="fas fa-check-circle"></i> MATRICULADO OFICIAL</span>
                </div>

                <div>
                    <h3 style="color:#38BDF8; margin:0 0 0.5rem 0; font-size:1.25rem;"><i class="fas fa-id-card"></i> Credencial Digital Institucional</h3>
                    <p style="color:#94A3B8; font-size:0.88rem; margin-bottom:1rem;">Presenta esta credencial en la entrada de los escenarios o eventos para registrar tu ingreso automático.</p>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.85rem; color:#94A3B8; background:#070B14; padding:1rem; border-radius:10px; border:1px solid rgba(56,189,248,0.2);">
                        <div><strong>Entidad:</strong> <span style="color:#F8FAFC;">${caps.nombre_empresa}</span></div>
                        <div><strong>Especialidad:</strong> <span style="color:#38BDF8;">${vocab.vocationLabel}</span></div>
                        <div><strong>Contacto Emergencia:</strong> <span style="color:#F8FAFC;">Sra. Maria Cruz (3115928401)</span></div>
                        <div><strong>Puntos Gamificación:</strong> <span style="color:#34D399; font-weight:800;">250 Pts (Nivel 2)</span></div>
                    </div>
                </div>
            </div>

            <!-- Zona 3: Vitrina de Oferta Institucional & Motor de Postulación -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.25rem; font-weight:800;"><i class="fas fa-store"></i> Vitrina de Oferta & Postulación en Línea</h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">Inscríbete a nuevas disciplinas o talleres según disponibilidad de cupos</span>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:1.25rem;">
                    ${vocab.catalog.map(prog => `
                        <div style="background:#070B14; border:1px solid rgba(56,189,248,0.25); border-radius:12px; padding:1.25rem; display:flex; flex-direction:column; justify-content:space-between;">
                            <div>
                                <strong style="color:#F8FAFC; font-size:1.1rem; display:block; margin-bottom:0.3rem;">${prog.nombre}</strong>
                                <span class="badge" style="background:rgba(56,189,248,0.12); color:#38BDF8; font-size:0.75rem; margin-bottom:0.6rem; inline-block;">Nivel: ${prog.nivel}</span>
                                <p style="color:#94A3B8; font-size:0.82rem; margin:0.2rem 0;"><i class="fas fa-clock" style="color:#38BDF8;"></i> Horario: ${prog.horario}</p>
                                <p style="color:#94A3B8; font-size:0.82rem; margin:0.2rem 0;"><i class="fas fa-chalkboard-teacher" style="color:#38BDF8;"></i> ${prog.profesor}</p>
                            </div>
                            <div style="margin-top:1rem; border-top:1px dashed rgba(255,255,255,0.1); padding-top:0.75rem; display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.78rem; color:#34D399; font-weight:700;"><i class="fas fa-user-check"></i> ${prog.cupos} Cupos Disponibles</span>
                                <button class="btn-primary" style="min-height:36px; padding:0 1rem; font-size:0.82rem;" onclick="alert('Postulación enviada exitosamente. Estado: En Evaluación por Docente.')">Postularme</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

        </div>
    `;
}

async function renderMiHorarioView(token) {
    await renderMisCursosView(token);
}

async function renderMisCalificacionesView(token) {
    await renderMisCursosView(token);
}

async function renderMiGamificacionView(token) {
    await renderMisCursosView(token);
}

async function renderMiAsistenciaView(token) {
    await renderMisCursosView(token);
}

// --- Registrar vistas de Alumno ---
if (typeof registerView === 'function') {
    registerView('alumno', 'mis-cursos', renderMisCursosView);
    registerView('alumno', 'mi-horario', renderMiHorarioView);
    registerView('alumno', 'mis-calificaciones', renderMisCalificacionesView);
    registerView('alumno', 'mi-progreso', renderMiGamificacionView);
    registerView('alumno', 'mi-asistencia', renderMiAsistenciaView);
}
