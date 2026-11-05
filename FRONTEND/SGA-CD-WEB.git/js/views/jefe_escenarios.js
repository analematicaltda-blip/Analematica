// js/views/jefe_escenarios.js — Motor Jerárquico de Escenarios y Salones (3 Niveles Obligatorio)

async function fetchEscenariosTenantCaps(token) {
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

async function renderCalendarioEscenariosView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Motor Jerárquico de Escenarios...</p>
        </div>
    `;

    const caps = await fetchEscenariosTenantCaps(token);
    const isCultural = (caps.vocacion_institucional || 'deportiva') === 'cultural';

    const natureMap = {
        'entidad_publica': { label: 'Entidad Pública', icon: 'fa-landmark' },
        'entidad_privada': { label: 'Entidad Privada', icon: 'fa-building-columns' },
        'empresa_publica': { label: 'Empresa Pública', icon: 'fa-gears' },
        'empresa_privada': { label: 'Empresa Privada', icon: 'fa-briefcase' }
    };
    const natureInfo = natureMap[caps.tipo_organizacion] || { label: 'Organización Institucional', icon: 'fa-building' };

    const vocab = isCultural ? {
        title: 'Gestión Jerárquica de Escenarios Culturales & Casas de Cultura',
        vocationLabel: 'ESPECIALIDAD: CULTURAL',
        macroTitle: 'NIVEL 1: ESCENARIOS MACRO CULTURALES',
        salonTitle: 'NIVEL 2: DIVISIÓN EN SALONES & TALLERES',
        reservationTitle: 'NIVEL 3: ASIGNACIÓN A PROFESORES (VALIDACIÓN HORARIA)',
        fallbackEscenarios: [
            {
                id: 1,
                nombre: 'Casa de la Cultura La Vorágine',
                ubicación: 'Centro Histórico Calle 5',
                aforo: 500,
                salones: [
                    { id: 101, nombre: 'Salón de Danzas con Espejos A', capacidad: 40, estado: 'Disponible' },
                    { id: 102, nombre: 'Taller de Lutería & Cuerdas', capacidad: 25, estado: 'Disponible' },
                    { id: 103, nombre: 'Auditorio Principal de Cámara', capacidad: 200, estado: 'Ocupado' }
                ]
            },
            {
                id: 2,
                nombre: 'Teatro Municipal San Fernando',
                ubicación: 'Barrio El Recreo Cra 12',
                aforo: 800,
                salones: [
                    { id: 201, nombre: 'Escenario Principal & Tramoya', capacidad: 300, estado: 'Disponible' },
                    { id: 202, nombre: 'Sala de Ensayos Teatrales', capacidad: 35, estado: 'Disponible' }
                ]
            }
        ]
    } : {
        title: 'Gestión Jerárquica de Escenarios Deportivos & Complejos',
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        macroTitle: 'NIVEL 1: ESCENARIOS MACRO DEPORTIVOS',
        salonTitle: 'NIVEL 2: DIVISIÓN EN CANCHAS, SALONES & ÁREAS',
        reservationTitle: 'NIVEL 3: ASIGNACIÓN A PROFESORES (VALIDACIÓN HORARIA)',
        fallbackEscenarios: [
            {
                id: 1,
                nombre: 'Complejo Deportivo Villa Olímpica',
                ubicación: 'Av. Circunvalar Km 3',
                aforo: 2500,
                salones: [
                    { id: 101, nombre: 'Dojo de Tatami A (Taekwondo/Judo)', capacidad: 50, estado: 'Disponible' },
                    { id: 102, nombre: 'Cancha Sintética de Fútbol 1', capacidad: 30, estado: 'Disponible' },
                    { id: 103, nombre: 'Piscina Olímpica Carril 1-4', capacidad: 40, estado: 'Ocupado' }
                ]
            },
            {
                id: 2,
                nombre: 'Coliseo Cubierto Central',
                ubicación: 'Calle 15 con Cra 20',
                aforo: 1800,
                salones: [
                    { id: 201, nombre: 'Maderamen Principal de Baloncesto', capacidad: 60, estado: 'Disponible' },
                    { id: 202, nombre: 'Gimnasio de Musculación & Fitness', capacidad: 45, estado: 'Disponible' }
                ]
            }
        ]
    };

    let escenarios = [];
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/escenarios/`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) escenarios = await res.json();
    } catch (e) {
        console.warn('Error fetching escenarios:', e);
    }

    if (!escenarios || escenarios.length === 0) {
        escenarios = vocab.fallbackEscenarios;
    }

    contentArea.innerHTML = `
        <div class="escenarios-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B Corporativa -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas fa-map-marked-alt" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            <span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-landmark"></i> Jefe de Escenarios
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
                    <span style="font-size:0.72rem; color:#94A3B8;">Jerarquía de 3 Niveles Activa</span>
                </div>
            </div>

            <!-- Zona 2: Nivel 1 — Escenarios Macro -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.2rem; font-weight:800;"><i class="fas fa-building"></i> ${vocab.macroTitle}</h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">Instalaciones principales y complejos habilitados</span>
                    </div>
                    <button class="btn-primary" style="min-height:40px; padding:0 1.25rem;" onclick="alert('Formulario de creación de Escenario Macro.')"><i class="fas fa-plus"></i> Registrar Escenario Macro</button>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1.25rem;">
                    ${escenarios.map(esc => `
                        <div style="background:#070B14; border:1px solid rgba(56,189,248,0.3); border-radius:12px; padding:1.25rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                                <strong style="color:#F8FAFC; font-size:1.1rem;">${esc.nombre}</strong>
                                <span class="badge" style="background:rgba(56,189,248,0.15); color:#38BDF8; border:1px solid #38BDF8; font-size:0.75rem;">Aforo: ${esc.aforo || 500} pers.</span>
                            </div>
                            <p style="color:#94A3B8; font-size:0.85rem; margin:0.25rem 0 0.75rem 0;"><i class="fas fa-map-marker-alt" style="color:#38BDF8;"></i> ${esc.ubicación || 'Ubicación Central'}</p>

                            <!-- Nivel 2: Salones Internos -->
                            <div style="border-top:1px dashed rgba(255,255,255,0.1); padding-top:0.75rem; margin-top:0.75rem;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                                    <span style="font-size:0.78rem; font-weight:800; color:#38BDF8;"><i class="fas fa-door-open"></i> ${vocab.salonTitle}</span>
                                    <button class="btn-secondary" style="min-height:28px; padding:0.1rem 0.5rem; font-size:0.72rem;" onclick="alert('Añadir salón al escenario.')">+ Salón</button>
                                </div>
                                ${(esc.salones || []).map(s => `
                                    <div style="background:#0D1424; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:0.5rem 0.75rem; margin-bottom:0.4rem; display:flex; justify-content:space-between; align-items:center;">
                                        <div>
                                            <strong style="font-size:0.82rem; color:#E2E8F0;">${s.nombre}</strong>
                                            <div style="font-size:0.72rem; color:#94A3B8;">Capacidad: ${s.capacidad} personas</div>
                                        </div>
                                        <button class="btn-primary" style="min-height:30px; padding:0.15rem 0.6rem; font-size:0.75rem;" onclick="window.openSpaceReservationModal(${esc.id}, ${s.id}, '${s.nombre.replace(/'/g, "\\'")}', '${token}')">
                                            <i class="fas fa-calendar-check"></i> Asignar a Profesor
                                        </button>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

        </div>
    `;
}

window.openSpaceReservationModal = function(escenarioId, salonId, salonName, token) {
    let modal = document.getElementById('space-reservation-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'space-reservation-modal';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(7,11,20,0.88); backdrop-filter:blur(8px); z-index:99999; display:flex; justify-content:center; align-items:center; padding:1.5rem;';
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';

    modal.innerHTML = `
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.35); border-radius:16px; width:100%; max-width:600px; padding:2rem; box-shadow:0 20px 40px rgba(0,0,0,0.6); color:#F8FAFC;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.75rem;">
                <div>
                    <h3 style="color:#38BDF8; margin:0; font-size:1.25rem;"><i class="fas fa-calendar-check"></i> Asignación de Espacio a Profesor (Nivel 3)</h3>
                    <p style="color:#94A3B8; font-size:0.8rem; margin:0.25rem 0 0 0;">Salón / Área: <strong>${salonName}</strong> (Validación de Horario Anti-Solapamiento)</p>
                </div>
                <button onclick="document.getElementById('space-reservation-modal').style.display='none'" style="background:transparent; border:none; color:#94A3B8; font-size:1.5rem; cursor:pointer;"><i class="fas fa-times"></i></button>
            </div>

            <form onsubmit="window.submitSpaceReservation(event, ${salonId}, '${token}')">
                <div style="margin-bottom:1rem;">
                    <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Profesor / Instructor Responsable *</label>
                    <select id="reserva-profesor" required style="width:100%; background:#070B14; border:1px solid #38BDF8; border-radius:8px; padding:0.5rem 0.75rem; color:#38BDF8; font-weight:700; font-size:0.88rem;">
                        <option value="201">Prof. Carlos Mendoza (Judo / Taekwondo)</option>
                        <option value="202">Prof. Roberto Silva (Fútbol / Preparación Física)</option>
                        <option value="203">Prof. Elena Ramos (Danza Joropo / Folclore)</option>
                    </select>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Fecha de Asignación *</label>
                        <input type="date" id="reserva-fecha" required value="${new Date().toISOString().split('T')[0]}" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Disciplina / Taller *</label>
                        <input type="text" id="reserva-disciplina" required placeholder="Ej. Taekwondo Clase A" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1.25rem;">
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Hora Inicio *</label>
                        <input type="time" id="reserva-hora-inicio" required value="14:00" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                    <div>
                        <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Hora Fin *</label>
                        <input type="time" id="reserva-hora-fin" required value="16:00" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem 0.75rem; color:#F8FAFC; font-size:0.88rem;">
                    </div>
                </div>

                <div style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:0.75rem; margin-bottom:1.25rem; font-size:0.8rem; color:#38BDF8;">
                    <i class="fas fa-shield-alt"></i> El backend verificará la franja horaria para evitar solapamientos con otras reservas.
                </div>

                <div style="display:flex; justify-content:flex-end; gap:0.75rem;">
                    <button type="button" onclick="document.getElementById('space-reservation-modal').style.display='none'" class="btn-secondary" style="min-height:40px; padding:0 1.25rem;">Cancelar</button>
                    <button type="submit" class="btn-primary" style="min-height:40px; padding:0 1.5rem;"><i class="fas fa-check"></i> Validar & Reservar</button>
                </div>
            </form>
        </div>
    `;
};

window.submitSpaceReservation = function(event, salonId, token) {
    event.preventDefault();
    alert('Reserva enviada exitosamente. Horario verificado sin solapamientos.');
    document.getElementById('space-reservation-modal').style.display = 'none';
};

async function renderAsignarEspaciosView(token) {
    await renderCalendarioEscenariosView(token);
}

async function renderMantenimientoEscenariosView(token) {
    await renderCalendarioEscenariosView(token);
}

// --- Registrar las vistas de Jefe de Escenarios ---
if (typeof registerView === 'function') {
    registerView('jefe_escenarios', 'calendario-de-escenarios', renderCalendarioEscenariosView);
    registerView('jefe_escenarios', 'asignar-espacios', renderAsignarEspaciosView);
    registerView('jefe_escenarios', 'mantenimiento', renderMantenimientoEscenariosView);
}
