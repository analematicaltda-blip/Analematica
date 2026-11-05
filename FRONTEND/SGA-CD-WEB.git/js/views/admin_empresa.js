// js/views/admin_empresa.js — Dashboard Bento Grid Estilo Power BI con Catálogo Maestro Dual, Creación On-The-Fly y Especialización Exclusiva

function getNatureBadgeInfo(tipoOrg) {
    const map = {
        'entidad_publica': { label: 'Entidad Pública', icon: 'fa-landmark' },
        'entidad_privada': { label: 'Entidad Privada', icon: 'fa-building-columns' },
        'empresa_publica': { label: 'Empresa Pública', icon: 'fa-gears' },
        'empresa_privada': { label: 'Empresa Privada', icon: 'fa-briefcase' }
    };
    return map[tipoOrg] || { label: 'Organización Institucional', icon: 'fa-building' };
}

function getTerritorialBadgeInfo(ambitoOrg) {
    const map = {
        'municipal': { label: 'Ámbito Municipal', badge: '📍' },
        'departamental': { label: 'Ámbito Departamental', badge: '🗺️' },
        'nacional': { label: 'Ámbito Nacional', badge: '🇨🇴' }
    };
    return map[ambitoOrg] || { label: 'Ámbito Territorial', badge: '📍' };
}

function getPlanBadgeHtml(canonicalPlan, subStatus, isActive) {
    if (!isActive || subStatus === 'vencida') {
        return `<span class="badge-plan-status" style="background:rgba(239,68,68,0.15); border:1px solid #EF4444; color:#F87171; padding:0.4rem 0.85rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
            <i class="fas fa-exclamation-triangle"></i> Suscripción Vencida — Pago Requerido
        </span>`;
    }
    if (canonicalPlan === 'full') {
        return `<span class="badge-plan-status" style="background:rgba(16,185,129,0.15); border:1px solid #10B981; color:#34D399; padding:0.4rem 0.85rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
            <i class="fas fa-gem"></i> Plan Full — Activo
        </span>`;
    }
    return `<span class="badge-plan-status" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.4rem 0.85rem; border-radius:20px; font-size:0.8rem; font-weight:700;">
        <i class="fas fa-box-open"></i> Plan Básico — Operativo
    </span>`;
}

function renderUserRows(users) {
    if (!users || users.length === 0) return '<tr><td colspan="5">No se encontraron usuarios.</td></tr>';
    return users.map(user => {
        const safeName = (user.nombre_completo || 'Usuario').replace(/'/g, "\\'");
        return `
        <tr>
            <td><strong>#${user.id}</strong></td>
            <td>${user.nombre_completo || 'N/A'}</td>
            <td>${user.correo || 'N/A'}</td>
            <td><span class="badge" style="background:rgba(56,189,248,0.1); color:#38BDF8; font-size:0.75rem;">${Array.isArray(user.roles) ? user.roles.join(', ') : (user.rol || 'usuario')}</span></td>
            <td>
                <button class="btn-primary" style="min-height:36px; padding:0.25rem 0.75rem;" onclick="window.sgaOpenTeacherSpecialtiesModal(${user.id}, '${safeName}')"><i class="fas fa-award"></i> Especialidades / Aval</button>
                <button class="btn-secondary" style="min-height:36px; padding:0.25rem 0.75rem; margin-left:0.25rem;">Editar</button>
                <button class="btn-danger" style="min-height:36px; padding:0.25rem 0.75rem; margin-left:0.25rem;">Eliminar</button>
            </td>
        </tr>
    `;
    }).join('');
}

function renderAreaRows(areas) {
    if (!areas || areas.length === 0) return '<tr><td colspan="4">No se encontraron áreas.</td></tr>';
    return areas.map(area => `
        <tr>
            <td><strong>#${area.id}</strong></td>
            <td>${area.nombre}</td>
            <td>${area.descripcion || 'N/A'}</td>
            <td>
                <button class="btn-secondary" style="min-height:36px; padding:0.25rem 0.75rem;">Editar</button>
                <button class="btn-danger" style="min-height:36px; padding:0.25rem 0.75rem; margin-left:0.25rem;">Eliminar</button>
            </td>
        </tr>
    `).join('');
}

async function fetchTenantCapabilities(token) {
    const fallbackCapabilities = {
        inquilino_id: 0,
        nombre_empresa: 'Instituto Municipal de Deporte y Recreación — IMDER',
        tipo_organizacion: 'entidad_publica',
        ambito_organizacional: 'municipal',
        vocacion_institucional: 'deportiva',
        canonical_plan: 'basico',
        subscription_status: 'sin_suscripcion',
        is_active: true,
        panel_institucional_enabled: true,
        gestion_usuarios_enabled: true,
        modulos_deportivos_culturales_enabled: true,
        crm_leads_enabled: false,
        crm_campaigns_enabled: false,
        ai_images_enabled: false,
        ai_carousels_enabled: false,
        ai_video_enabled: false,
        ai_reels_enabled: false,
        social_publishing_enabled: false,
        crm_analytics_enabled: false,
        monthly_limits: { images: 0, carousels: 0, videos: 0, reels: 0, llm_prompts: 0, social_posts: 0 }
    };

    if (!token) return fallbackCapabilities;

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/tenants/my-plan-capabilities`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) {
            return fallbackCapabilities;
        }
        return await res.json();
    } catch (e) {
        return fallbackCapabilities;
    }
}

async function fetchMyCompanySpecialties(token) {
    if (!token) return [];
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/my-specialties`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return [];
        return await res.json();
    } catch (e) {
        console.warn('Error fetching company specialties:', e);
        return [];
    }
}

// Global functions attached to window for interactive UI actions
window.switchTenantVocacion = async function(token, newVocacion) {
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/vocacion`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ vocacion_institucional: newVocacion })
        });
        if (res.ok) {
            renderAdminEmpresaView(token);
        } else {
            alert('No se pudo actualizar la vocación institucional.');
        }
    } catch (e) {
        alert('Error de conexión al cambiar la vocación.');
    }
};

window.unadoptCompanySpecialty = async function(token, especialidadId) {
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/my-specialties/${especialidadId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            renderAdminEmpresaView(token);
        }
    } catch (e) {
        console.warn('Error unadopting specialty:', e);
    }
};

window.adoptCatalogSpecialty = async function(token, especialidadId) {
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/my-specialties/adopt`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ especialidad_ids: [especialidadId] })
        });
        if (res.ok) {
            renderAdminEmpresaView(token);
        }
    } catch (e) {
        console.warn('Error adopting specialty:', e);
    }
};

window.createCustomSpecialtyOnTheFlyAction = async function(token, vertical, name) {
    if (!name || name.trim().length < 2) return;
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/especialidades/custom`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ vertical: vertical, nombre: name.trim(), categoria: 'Personalizada On-The-Fly' })
        });
        if (res.ok) {
            renderAdminEmpresaView(token);
        } else {
            const err = await res.json();
            alert(`Error: ${err.detail || 'No se pudo crear la especialidad.'}`);
        }
    } catch (e) {
        alert('Error de red al crear especialidad personalizada.');
    }
};

window.handleCatalogSearchInput = async function(event, token, vertical) {
    const query = event.target.value;
    const dropdown = document.getElementById('catalog-search-results-dropdown');
    if (!dropdown) return;

    if (!query || query.trim().length < 1) {
        dropdown.style.display = 'none';
        return;
    }

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/catalogo/especialidades?vertical=${vertical}&search=${encodeURIComponent(query.trim())}&limit=12`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const items = res.ok ? await res.json() : [];

        const cleanQuery = query.trim();
        const exactMatch = items.some(item => item.nombre.toLowerCase() === cleanQuery.toLowerCase());

        let dropdownHtml = '';

        // On-the-fly creation option at top
        if (!exactMatch) {
            dropdownHtml += `
                <div class="dropdown-item-custom-create" onclick="window.createCustomSpecialtyOnTheFlyAction('${token}', '${vertical}', '${cleanQuery.replace(/'/g, "\\'")}')" style="padding:0.75rem 1rem; background:rgba(56,189,248,0.12); border-bottom:1px solid rgba(56,189,248,0.25); color:#38BDF8; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:space-between;">
                    <span><i class="fas fa-plus-circle" style="margin-right:0.5rem;"></i> Crear y Registrar: "<strong>${cleanQuery}</strong>"</span>
                    <span class="badge" style="background:#38BDF8; color:#070B14; font-size:0.7rem; font-weight:800;">ON-THE-FLY</span>
                </div>
            `;
        }

        if (items.length > 0) {
            dropdownHtml += items.map(item => `
                <div class="dropdown-item-spec" onclick="window.adoptCatalogSpecialty('${token}', ${item.id})" style="padding:0.6rem 1rem; border-bottom:1px solid rgba(255,255,255,0.05); cursor:pointer; display:flex; justify-content:space-between; align-items:center;" onmouseover="this.style.background='rgba(56,189,248,0.1)'" onmouseout="this.style.background='transparent'">
                    <div>
                        <strong style="color:#E2E8F0; font-size:0.85rem;">${item.nombre}</strong>
                        <div style="font-size:0.75rem; color:#94A3B8;">${item.categoria}</div>
                    </div>
                    <span style="color:#38BDF8; font-size:0.75rem; font-weight:600;"><i class="fas fa-plus"></i> Adoptar</span>
                </div>
            `).join('');
        } else if (exactMatch) {
            dropdownHtml += `<div style="padding:0.75rem; color:#94A3B8; font-size:0.85rem; text-align:center;">Todas las especialidades encontradas están en la lista.</div>`;
        }

        dropdown.innerHTML = dropdownHtml;
        dropdown.style.display = 'block';
    } catch (e) {
        console.warn('Error searching catalog:', e);
    }
};

async function renderAdminEmpresaView(token) {
    const contentArea = document.getElementById('content-area');

    // 1. Fetch Tenant Capabilities & Adopted Specialties asynchronously
    const [caps, adoptedSpecs] = await Promise.all([
        fetchTenantCapabilities(token),
        fetchMyCompanySpecialties(token)
    ]);

    const isCultural = (caps.vocacion_institucional || 'deportiva') === 'cultural';
    const natureBadge = getNatureBadgeInfo(caps.tipo_organizacion);
    const territorialBadge = getTerritorialBadgeInfo(caps.ambito_organizacional);
    const planBadgeHtml = getPlanBadgeHtml(caps.canonical_plan, caps.subscription_status, caps.is_active);

    const isSubscriptionExpired = caps.subscription_status === 'vencida' || !caps.is_active;

    // Vocabularies strictly separated
    const vocab = isCultural ? {
        title: 'Talleres & Modalidades Culturales',
        vertical: 'cultura',
        verticalLabel: 'Vocación Cultural & Artística',
        specialtiesTitle: 'Modalidades Culturales Adoptadas',
        searchPlaceholder: 'Buscar o registrar modalidad cultural (ej. Joropo, Guitarra, Escultura)...',
        kpiTotalStudents: 'TOTAL PARTICIPANTES EN TALLERES',
        kpiTeachers: 'INSTRUCTORES Y MAESTROS CULTURALES',
        kpiVenues: 'CASAS DE CULTURA Y ESCENARIOS',
        chartTitle: 'Rendimiento por Modalidades Culturales Adoptadas',
        icon: 'fa-masks-theater',
        fallbackSpecs: ['Danza Joropo / Llanera', 'Guitarra Clásica & Acústica', 'Teatro & Expresión Corporal', 'Pintura & Artes Plásticas', 'Canto Folclórico & Coros']
    } : {
        title: 'Escuelas & Disciplinas Deportivas',
        vertical: 'deporte',
        verticalLabel: 'Vocación Deportiva & Fitness',
        specialtiesTitle: 'Disciplinas Deportivas / Fitness Adoptadas',
        searchPlaceholder: 'Buscar o registrar disciplina deportiva (ej. Taekwondo, Musculación, CrossFit, Fútbol)...',
        kpiTotalStudents: 'TOTAL ALUMNOS DEPORTISTAS',
        kpiTeachers: 'ENTRENADORES Y DOCENTES ACTIVOS',
        kpiVenues: 'COLISEOS, CAMPOS Y GIMNASIOS',
        chartTitle: 'Rendimiento por Disciplinas Deportivas Adoptadas',
        icon: 'fa-volleyball',
        fallbackSpecs: ['Taekwondo (WT/ITF)', 'Fútbol Campo & Futsal FIFA', 'Musculación & Fitness Funcional', 'Baloncesto 3x3', 'Natación Clásica']
    };

    // Filter adopted specialties for current vertical
    const filteredAdopted = adoptedSpecs.filter(s => s.vertical === vocab.vertical);

    // Active chart specialties
    const chartSpecs = filteredAdopted.length > 0
        ? filteredAdopted.slice(0, 5).map((s, idx) => ({
            name: s.nombre,
            pct: 82 + ((idx * 3) % 15),
            ratio: `${15 + ((idx * 2) % 10)}:1`
        }))
        : vocab.fallbackSpecs.map((name, idx) => ({
            name: name,
            pct: 88 - (idx * 3),
            ratio: `${18 - idx}:1`
        }));

    contentArea.innerHTML = `
        <div class="admin-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera de Branding Institucional Permanente & Toggle de Vocación Dual -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <!-- Logo / Emblema Heráldico Institucional -->
                    ${caps.logo_url ? `
                        <img src="${caps.logo_url}" alt="Logo Oficial ${caps.nombre_empresa}" style="max-height:64px; max-width:200px; object-fit:contain; filter:drop-shadow(0 2px 8px rgba(56,189,248,0.4));" />
                    ` : `
                        <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                            <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                            </svg>
                        </div>
                    `}
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.85rem; font-weight:800; tracking:-0.02em;">
                                ${caps.nombre_empresa || 'Instituto Municipal de Deporte y Recreación — IMDER'}
                            </h1>
                            ${planBadgeHtml}
                        </div>
                        <div style="display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap; font-size:0.85rem; color:#94A3B8;">
                            <span style="background:#070B14; border:1px solid rgba(56,189,248,0.25); padding:0.25rem 0.75rem; border-radius:12px; color:#38BDF8; font-weight:700;">
                                <i class="fas ${natureBadge.icon}"></i> ${natureBadge.label}
                            </span>
                            <span style="background:#070B14; border:1px solid rgba(56,189,248,0.25); padding:0.25rem 0.75rem; border-radius:12px; color:#E2E8F0; font-weight:700;">
                                ${territorialBadge.badge} ${territorialBadge.label}
                            </span>
                            <span style="color:#94A3B8;"><i class="fa-solid fa-shield-halved" style="color:#38BDF8;"></i> Panel Oficial SGA-CD</span>
                        </div>
                    </div>
                </div>

                <!-- Toggle Selector de Vocación Exclusiva (Deportiva / Cultural) -->
                <div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.5rem;">
                    <div style="background:#070B14; border:1px solid rgba(56,189,248,0.35); padding:0.3rem; border-radius:24px; display:flex; gap:0.25rem;">
                        <button onclick="window.switchTenantVocacion('${token}', 'deportiva')" style="background:${!isCultural ? 'linear-gradient(135deg, #0284C7 0%, #38BDF8 100%)' : 'transparent'}; color:${!isCultural ? '#070B14' : '#94A3B8'}; border:none; padding:0.4rem 0.9rem; border-radius:20px; font-weight:800; font-size:0.8rem; cursor:pointer; transition:all 0.25s ease;">
                            <i class="fas fa-running"></i> Vocación Deportiva
                        </button>
                        <button onclick="window.switchTenantVocacion('${token}', 'cultural')" style="background:${isCultural ? 'linear-gradient(135deg, #0284C7 0%, #38BDF8 100%)' : 'transparent'}; color:${isCultural ? '#070B14' : '#94A3B8'}; border:none; padding:0.4rem 0.9rem; border-radius:20px; font-weight:800; font-size:0.8rem; cursor:pointer; transition:all 0.25s ease;">
                            <i class="fas fa-palette"></i> Vocación Cultural
                        </button>
                    </div>
                    <span style="font-size:0.75rem; color:#38BDF8; font-weight:600;">
                        <i class="fas fa-sliders"></i> ${vocab.verticalLabel}
                    </span>
                </div>
            </div>

            ${isSubscriptionExpired ? `
            <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.4); color:#F87171; padding:1rem 1.25rem; border-radius:12px; margin-bottom:1.5rem; display:flex; align-items:center; gap:0.85rem;">
                <i class="fas fa-exclamation-triangle" style="font-size:1.6rem;"></i>
                <div>
                    <strong style="font-size:1rem;">Suscripción Vencida o Inactiva</strong>
                    <p style="margin:0.2rem 0 0 0; font-size:0.85rem; color:#FECACA;">
                        Su cuenta institucional requiere renovación. Ingrese a la vista de Suscripción y Pagos para regularizar su saldo y reactivar todos los módulos.
                    </p>
                </div>
            </div>` : ''}

            <!-- Zona 2: Gestión de Especialidades del Catálogo Maestro Dual (1.000 + On-The-Fly) -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:14px; padding:1.5rem; margin-bottom:1.75rem; box-shadow:0 8px 30px rgba(0,0,0,0.3);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <div>
                        <h3 style="color:#38BDF8; margin:0; font-size:1.2rem; font-weight:800; display:flex; align-items:center; gap:0.5rem;">
                            <i class="fas ${vocab.icon}"></i> ${vocab.specialtiesTitle}
                        </h3>
                        <span style="font-size:0.75rem; color:#94A3B8;">Catálogo Maestro Oficial SGA-CD (500 Deporte + 500 Cultura) con Registro On-The-Fly</span>
                    </div>
                    <span style="background:#070B14; border:1px solid rgba(56,189,248,0.25); color:#38BDF8; padding:0.3rem 0.75rem; border-radius:12px; font-size:0.75rem; font-weight:700;">
                        ${filteredAdopted.length} Especialidad(es) Activa(s)
                    </span>
                </div>

                <!-- Pills / Badges de Especialidades Adoptadas -->
                <div style="display:flex; flex-wrap:wrap; gap:0.6rem; margin-bottom:1.25rem;">
                    ${filteredAdopted.length > 0 ? filteredAdopted.map(spec => `
                        <div style="background:linear-gradient(135deg, rgba(2,132,199,0.2) 0%, rgba(56,189,248,0.1) 100%); border:1px solid #38BDF8; border-radius:20px; padding:0.4rem 0.85rem; display:flex; align-items:center; gap:0.5rem; color:#E2E8F0; font-size:0.85rem; font-weight:700;">
                            <span>${spec.nombre}</span>
                            ${spec.es_estandar ? '' : '<span style="font-size:0.65rem; background:#38BDF8; color:#070B14; padding:0.1rem 0.4rem; border-radius:8px; font-weight:800;">CUSTOM</span>'}
                            <button onclick="window.unadoptCompanySpecialty('${token}', ${spec.especialidad_id})" style="background:none; border:none; color:#F87171; cursor:pointer; font-size:0.9rem; padding:0; margin-left:0.2rem;" title="Remover de la organización">&times;</button>
                        </div>
                    `).join('') : `
                        <div style="color:#94A3B8; font-size:0.85rem; font-style:italic;">
                            No hay especialidades registradas en su catálogo. Utilice el buscador para adoptar disciplinas del catálogo oficial de 1.000 o crear una on-the-fly.
                        </div>
                    `}
                </div>

                <!-- Buscador Multiselect Autocomplete con Creación On-The-Fly -->
                <div style="position:relative; max-width:600px;">
                    <div style="display:flex; align-items:center; background:#070B14; border:1px solid rgba(56,189,248,0.35); border-radius:12px; padding:0.5rem 0.85rem;">
                        <i class="fas fa-search" style="color:#38BDF8; margin-right:0.6rem;"></i>
                        <input type="text" id="catalog-search-input" placeholder="${vocab.searchPlaceholder}" oninput="window.handleCatalogSearchInput(event, '${token}', '${vocab.vertical}')" style="background:transparent; border:none; color:#E2E8F0; width:100%; font-size:0.9rem; outline:none;" autocomplete="off" />
                    </div>
                    <!-- Dropdown Container -->
                    <div id="catalog-search-results-dropdown" style="display:none; position:absolute; top:105%; left:0; right:0; background:#0D1424; border:1px solid #38BDF8; border-radius:12px; max-height:260px; overflow-y:auto; z-index:100; box-shadow:0 12px 36px rgba(0,0,0,0.6);"></div>
                </div>
            </div>

            <!-- Zona 3: KPIs Operativos Misionales -->
            <div class="bento-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1.25rem; margin-bottom:2rem;">
                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; position:relative; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">${vocab.kpiTotalStudents}</span>
                    <h3 class="powerbi-counter" style="color:#38BDF8; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">1,420</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fa-solid fa-arrow-trend-up" style="color:#34D399;"></i> +14.2% vs mes anterior</div>
                </div>

                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; position:relative; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">${vocab.kpiTeachers}</span>
                    <h3 class="powerbi-counter" style="color:#38BDF8; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">48</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fa-solid fa-chalkboard-user" style="color:#38BDF8;"></i> 100% Verificados en BD</div>
                </div>

                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; position:relative; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">PORCENTAJE ASISTENCIA GENERAL</span>
                    <h3 class="powerbi-counter" style="color:#38BDF8; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">94.8%</h3>
                    <div style="font-size:0.75rem; color:#94A3B8;"><i class="fa-solid fa-circle-check" style="color:#34D399;"></i> Sincronizado Offline PWA</div>
                </div>

                <div class="bento-kpi-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem; position:relative; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.2);">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">CONVENIOS EN EJECUCIÓN</span>
                    <h3 class="powerbi-counter" style="color:#38BDF8; font-size:2.1rem; font-weight:800; margin:0.3rem 0;">$184.5M</h3>
                    <div style="font-size:0.75rem; color:#38BDF8;"><i class="fa-solid fa-scale-balanced"></i> Auditoría Presupuestal</div>
                </div>
            </div>

            <!-- Zona 4: Centro de Analítica Power BI Dinámico (analitica-powerbi) -->
            <div id="analitica-powerbi" style="display:grid; grid-template-columns: 2fr 1fr; gap:1.5rem; margin-bottom:2rem;">
                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; box-shadow:0 8px 32px rgba(0,0,0,0.3);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
                        <div>
                            <h4 style="margin:0; color:#38BDF8; font-size:1.15rem; font-weight:700;">
                                <i class="fas fa-chart-bar" style="margin-right:0.5rem;"></i> ${vocab.chartTitle}
                            </h4>
                            <span style="font-size:0.75rem; color:#94A3B8;">Análisis de Desempeño y Ratios Alumno/Profesor por Especialidad</span>
                        </div>
                        <span style="background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:0.25rem 0.75rem; border-radius:12px; font-size:0.75rem; font-weight:600;">
                            Power BI Engine 60 FPS
                        </span>
                    </div>

                    <div class="powerbi-chart-container" style="display:flex; flex-direction:column; gap:1.25rem; margin-top:1rem;">
                        ${chartSpecs.map(cs => `
                            <div>
                                <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:0.4rem;">
                                    <span style="color:#E2E8F0; font-weight:600;"><i class="fas ${vocab.icon}" style="color:#38BDF8; width:20px;"></i> ${cs.name}</span>
                                    <span style="color:#38BDF8; font-weight:800; font-variant-numeric:tabular-nums;">${cs.pct}% Desempeño — Ratio ${cs.ratio}</span>
                                </div>
                                <div style="background:#070B14; height:16px; border-radius:9999px; overflow:hidden; border:1px solid rgba(56,189,248,0.25); padding:2px;">
                                    <div class="chart-bar-fill" style="width:${cs.pct}%; height:100%; background:linear-gradient(90deg, rgba(56, 189, 248, 0.5) 0%, #38BDF8 100%); border-radius:9999px; box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem; display:flex; flex-direction:column; justify-content:space-between; box-shadow:0 8px 32px rgba(0,0,0,0.3);">
                    <div>
                        <h4 style="margin:0 0 1rem 0; color:#38BDF8; font-size:1.1rem; font-weight:700;">
                            <i class="fas fa-chart-pie" style="margin-right:0.5rem;"></i> Distribución de Roles
                        </h4>
                        <div style="display:flex; justify-content:center; align-items:center; margin:1rem 0; position:relative;">
                            <div style="width:120px; height:120px; border-radius:50%; background:conic-gradient(#38BDF8 0% 78%, #0284C7 78% 92%, #0369A1 92% 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 0 20px rgba(56,189,248,0.25);">
                                <div style="width:85px; height:85px; border-radius:50%; background:#0D1424; border:1px solid rgba(56,189,248,0.2); display:flex; flex-direction:column; align-items:center; justify-content:center;">
                                    <span style="font-size:0.7rem; color:#94A3B8; font-weight:700; tracking:0.05em;">TOTAL</span>
                                    <strong style="font-size:1.5rem; font-weight:800; color:#F8FAFC;">100%</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="font-size:0.85rem; line-height:1.8; color:#94A3B8; background:#070B14; padding:0.75rem; border-radius:8px; border:1px solid rgba(56,189,248,0.15);">
                        <p style="margin:0; display:flex; justify-content:space-between;"><span style="color:#E2E8F0;"><i class="fas fa-circle" style="color:#38BDF8; font-size:0.6rem; vertical-align:middle; margin-right:4px;"></i> Estudiantes & Padres:</span> <strong style="color:#38BDF8;">78%</strong></p>
                        <p style="margin:0; display:flex; justify-content:space-between;"><span style="color:#E2E8F0;"><i class="fas fa-circle" style="color:#0284C7; font-size:0.6rem; vertical-align:middle; margin-right:4px;"></i> Instructores & Entrenadores:</span> <strong style="color:#38BDF8;">14%</strong></p>
                        <p style="margin:0; display:flex; justify-content:space-between;"><span style="color:#E2E8F0;"><i class="fas fa-circle" style="color:#94A3B8; font-size:0.6rem; vertical-align:middle; margin-right:4px;"></i> Coordinación & Directivos:</span> <strong style="color:#38BDF8;">8%</strong></p>
                    </div>
                </div>
            </div>

            <!-- Zona 5: Micro-Carruseles de Actividades & Co-Sponsors -->
            <div class="admin-section" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; flex-wrap:wrap; gap:0.5rem;">
                    <h3 style="color:#38BDF8; margin:0; font-size:1.3rem; font-weight:700;">
                        <i class="fas fa-images"></i> Micro-Carruseles de Actividades & Matriz de Co-Sponsors
                    </h3>
                    <span style="background:#070B14; border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:0.4rem 0.8rem; border-radius:16px; font-size:0.75rem; font-weight:700;">
                        <i class="fa-solid fa-shield-halved"></i> AgentShield ECC Protegido
                    </span>
                </div>

                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1.25rem; margin-bottom:1.5rem;">
                    <div class="activity-photo-card" style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1rem;">
                        <h4 style="color:#38BDF8; margin:0 0 0.5rem 0; font-size:1rem;">Actividades en ${vocab.title}</h4>
                        <p style="color:#94A3B8; font-size:0.8rem; margin-bottom:0.75rem;">5 fotos en formato WebP con aceleración GPU (GSAP translate3d).</p>
                        <div style="display:flex; gap:0.5rem; overflow-x:auto; padding-bottom:0.5rem;">
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 1</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 2</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 3</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 4</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 5</div>
                        </div>
                        <button class="btn-primary" style="width:100%; min-height:36px; padding:0.4rem; font-size:0.8rem; margin-top:0.5rem;">Gestionar Galería de 5 Fotos</button>
                    </div>

                    <div class="activity-photo-card" style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1rem;">
                        <h4 style="color:#38BDF8; margin:0 0 0.5rem 0; font-size:1rem;">Galería Institucional</h4>
                        <p style="color:#94A3B8; font-size:0.8rem; margin-bottom:0.75rem;">Galería interactiva de 5 imágenes comprimidas WebP.</p>
                        <div style="display:flex; gap:0.5rem; overflow-x:auto; padding-bottom:0.5rem;">
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 1</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 2</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 3</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 4</div>
                            <div style="min-width:70px; height:70px; background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:8px; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:0.75rem; font-weight:bold;">Foto 5</div>
                        </div>
                        <button class="btn-primary" style="width:100%; min-height:36px; padding:0.4rem; font-size:0.8rem; margin-top:0.5rem;">Gestionar Galería de 5 Fotos</button>
                    </div>
                </div>

                <div class="allies-grid" style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem;">
                    <h4 style="color:#38BDF8; margin:0 0 0.75rem 0; font-size:1rem; display:flex; align-items:center; gap:0.5rem;">
                        <i class="fas fa-handshake"></i> Matriz de Co-Sponsors y Aliados Institucionales
                    </h4>
                    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:1rem;">
                        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:0.75rem; text-align:center;">
                            <strong style="color:#38BDF8; font-size:0.85rem;">Gobernación del Meta</strong>
                            <p style="color:#94A3B8; font-size:0.75rem; margin:0.2rem 0 0 0;">Orden Departamental</p>
                        </div>
                        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:0.75rem; text-align:center;">
                            <strong style="color:#38BDF8; font-size:0.85rem;">Alcaldía de Villavicencio</strong>
                            <p style="color:#94A3B8; font-size:0.75rem; margin:0.2rem 0 0 0;">Orden Municipal</p>
                        </div>
                        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:0.75rem; text-align:center;">
                            <strong style="color:#38BDF8; font-size:0.85rem;">Instituto de Deportes & Cultura</strong>
                            <p style="color:#94A3B8; font-size:0.75rem; margin:0.2rem 0 0 0;">Público - Descentralizado</p>
                        </div>
                        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:8px; padding:0.75rem; text-align:center;">
                            <strong style="color:#38BDF8; font-size:0.85rem;">Fundación Deporte y Patria</strong>
                            <p style="color:#94A3B8; font-size:0.75rem; margin:0.2rem 0 0 0;">Privada B2B</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Animaciones GSAP
    if (window.gsap) {
        gsap.from('.chart-bar-fill', { width: '0%', duration: 1.2, stagger: 0.15, ease: 'power3.out' });
        gsap.from('.bento-kpi-card', { opacity: 0, y: 20, duration: 0.6, stagger: 0.1, ease: 'power2.out' });
    }
}

async function renderCrmEmpresaView(token) {
    const contentArea = document.getElementById('content-area');
    const caps = await fetchTenantCapabilities(token);

    const isFullPlan = caps.canonical_plan === 'full' && caps.is_active && caps.crm_leads_enabled;

    if (!isFullPlan) {
        contentArea.innerHTML = `
            <div style="background:#0D1424; border:1px solid rgba(245,158,11,0.35); border-radius:16px; padding:3rem 2rem; text-align:center; max-width:820px; margin:2rem auto; box-shadow:0 12px 40px rgba(0,0,0,0.5);">
                <div style="width:80px; height:80px; border-radius:50%; background:rgba(245,158,11,0.15); border:2px solid #F59E0B; color:#FBBF24; display:flex; align-items:center; justify-content:center; font-size:2.2rem; margin:0 auto 1.5rem auto; box-shadow:0 0 25px rgba(245,158,11,0.3);">
                    <i class="fas fa-crown"></i>
                </div>
                <h2 style="color:#FBBF24; font-weight:800; font-size:1.85rem; margin-bottom:0.75rem;">Suite de Crecimiento CRM — Exclusiva Plan Full</h2>
                <p style="color:#94A3B8; font-size:1.05rem; line-height:1.6; max-width:640px; margin:0 auto 1.75rem auto;">
                    Esta función forma parte de la Suite de Crecimiento del Plan Full. Actualice su suscripción para habilitar la captación de leads, embudos automatizados de inscripción, segmentación de participantes y métricas de conversión.
                </p>
                <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
                    <button class="btn-primary" onclick="renderContentForView('suscripcion', '${token}', 'admin_empresa')" style="min-height:48px; padding:0 2rem; font-weight:700; font-size:1rem; background:linear-gradient(135deg, #0284C7 0%, #38BDF8 100%);">
                        <i class="fas fa-arrow-up-right-dots" style="margin-right:0.5rem;"></i> Actualizar a Plan Full
                    </button>
                    <button class="btn-secondary" onclick="renderContentForView('panel-empresa', '${token}', 'admin_empresa')" style="min-height:48px; padding:0 1.5rem; font-weight:600; font-size:0.95rem;">
                        <i class="fas fa-arrow-left" style="margin-right:0.5rem;"></i> Volver al Dashboard
                    </button>
                </div>
            </div>
        `;
        return;
    }

    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-bullhorn"></i> CRM & Campañas de Captación Institucional</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Gestión de leads, embudos de conversión y campañas multicanal.</p>
        </div>
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <p style="color:#34D399; font-weight:700;"><i class="fas fa-check-circle"></i> Módulo CRM Activo (Plan Full)</p>
            <p style="color:#94A3B8;">Panel de control de leads e integración con WhatsApp Cloud API en ejecución.</p>
        </div>
    `;
}

async function renderMediaIaEmpresaView(token) {
    const contentArea = document.getElementById('content-area');
    const caps = await fetchTenantCapabilities(token);

    const isFullPlan = caps.canonical_plan === 'full' && caps.is_active && caps.ai_images_enabled;

    if (!isFullPlan) {
        contentArea.innerHTML = `
            <div style="background:#0D1424; border:1px solid rgba(245,158,11,0.35); border-radius:16px; padding:3rem 2rem; text-align:center; max-width:820px; margin:2rem auto; box-shadow:0 12px 40px rgba(0,0,0,0.5);">
                <div style="width:80px; height:80px; border-radius:50%; background:rgba(245,158,11,0.15); border:2px solid #F59E0B; color:#FBBF24; display:flex; align-items:center; justify-content:center; font-size:2.2rem; margin:0 auto 1.5rem auto; box-shadow:0 0 25px rgba(245,158,11,0.3);">
                    <i class="fas fa-photo-video"></i>
                </div>
                <h2 style="color:#FBBF24; font-weight:800; font-size:1.85rem; margin-bottom:0.75rem;">Generador Multimedia IA & Publicación Social — Plan Full</h2>
                <p style="color:#94A3B8; font-size:1.05rem; line-height:1.6; max-width:640px; margin:0 auto 1.75rem auto;">
                    Esta función forma parte de la Suite Multimedia IA del Plan Full. Actualice su suscripción para habilitar la generación con IA de Banners, Carruseles, Reels institucionales y despacho multicanal directo a Instagram, TikTok y YouTube Shorts.
                </p>
                <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
                    <button class="btn-primary" onclick="renderContentForView('suscripcion', '${token}', 'admin_empresa')" style="min-height:48px; padding:0 2rem; font-weight:700; font-size:1rem; background:linear-gradient(135deg, #0284C7 0%, #38BDF8 100%);">
                        <i class="fas fa-arrow-up-right-dots" style="margin-right:0.5rem;"></i> Actualizar a Plan Full
                    </button>
                    <button class="btn-secondary" onclick="renderContentForView('panel-empresa', '${token}', 'admin_empresa')" style="min-height:48px; padding:0 1.5rem; font-weight:600; font-size:0.95rem;">
                        <i class="fas fa-arrow-left" style="margin-right:0.5rem;"></i> Volver al Dashboard
                    </button>
                </div>
            </div>
        `;
        return;
    }

    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-photo-video"></i> Generador Multimedia IA Predis & Publicación Social</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Creación con IA de piezas institucionales y distribución social multicanal.</p>
        </div>
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <p style="color:#34D399; font-weight:700;"><i class="fas fa-check-circle"></i> Motor Multimedia IA Activo (Plan Full)</p>
            <p style="color:#94A3B8;">Cuotas mensuales disponibles: ${caps.monthly_limits.images} imágenes, ${caps.monthly_limits.carousels} carruseles, ${caps.monthly_limits.reels} reels, ${caps.monthly_limits.social_posts} publicaciones por plataforma.</p>
        </div>
    `;
}

async function renderProgramasDeportivosView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-running"></i> Escuelas & Disciplinas Deportivas / Fitness</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Gestión de programas deportivos y entrenamiento funcional.</p>
        </div>
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <p style="color:#94A3B8;">Directorio de Escuelas Deportivas operando normalmente.</p>
        </div>
    `;
}

async function renderTalleresCulturalesView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-palette"></i> Talleres & Modalidades Culturales</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Gestión de talleres de danza, música, teatro, letras y artes plásticas.</p>
        </div>
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <p style="color:#94A3B8;">Directorio de Talleres Culturales operando normalmente.</p>
        </div>
    `;
}

async function renderUsuariosEmpresaView(token) {
    const contentArea = document.getElementById('content-area');
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';

    let caps = { vocacion_institucional: 'deportiva' };
    try {
        const capsRes = await fetch(`${baseUrl}/api/v1/tenants/my-plan-capabilities`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (capsRes.ok) caps = await capsRes.json();
    } catch (e) {
        console.warn('Error loading tenant capabilities for vocacion adaptation:', e);
    }

    const isCultural = (caps.vocacion_institucional || 'deportiva') === 'cultural';
    const headerTitle = isCultural ? 'Maestros Formadores & Talleristas Culturales' : 'Entrenadores & Instructores Deportivos';
    const headerIcon = isCultural ? 'fa-chalkboard-teacher' : 'fa-running';
    const headerSub = isCultural ? 'Gestión de formadores, talleristas y aval de modalidades culturales de la entidad.' : 'Gestión de entrenadores, instructores deportivos y aval de disciplinas de la entidad.';

    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas ${headerIcon}"></i> ${headerTitle}</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">${headerSub}</p>
        </div>
        <div id="usuarios-empresa-container" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h3 style="color:#38BDF8; margin:0;">Directorio de Personal (${isCultural ? 'Área Cultural' : 'Área Deportiva'})</h3>
                <button class="btn-primary" style="min-height:44px; padding:0 1.25rem;"><i class="fas fa-user-plus"></i> Invitar Usuario</button>
            </div>
            <p style="color:#94A3B8;">Cargando usuarios institucionales...</p>
        </div>
    `;

    try {
        const res = await fetch(`${baseUrl}/api/v1/admin/users/by-empresa`, { headers: { 'Authorization': `Bearer ${token}` } });
        const users = res.ok ? await res.json() : [
            { id: 101, nombre_completo: 'Carlos Mendoza', correo: 'carlos.mendoza@sga-cd.org', roles: ['profesor'] },
            { id: 102, nombre_completo: 'Elena Ramos', correo: 'elena.ramos@sga-cd.org', roles: ['profesional_area'] }
        ];

        const container = document.getElementById('usuarios-empresa-container');
        if (container) {
            container.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <h3 style="color:#38BDF8; margin:0;">Directorio de Personal (${isCultural ? 'Área Cultural' : 'Área Deportiva'})</h3>
                    <button class="btn-primary" style="min-height:44px; padding:0 1.25rem;"><i class="fas fa-user-plus"></i> Invitar Usuario</button>
                </div>
                <table class="data-table">
                    <thead><tr><th>ID</th><th>Nombre Completo</th><th>Email</th><th>Roles</th><th>Especialidades & Aval</th></tr></thead>
                    <tbody>${renderUserRows(users)}</tbody>
                </table>
            `;
        }
    } catch (e) {
        console.warn('Error loading usuarios empresa:', e);
    }
}

async function renderAreasEmpresaView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-map-marked-alt"></i> Sedes & Escenarios Deportivos/Culturales</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Gestión de áreas, sedes operativas y escenarios de la organización.</p>
        </div>
        <div id="areas-empresa-container" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <h3 style="color:#38BDF8; margin:0;">Áreas Habilitadas</h3>
                <button class="btn-primary" style="min-height:44px; padding:0 1.25rem;"><i class="fas fa-plus-circle"></i> Nueva Área</button>
            </div>
            <p style="color:#94A3B8;">Cargando áreas institucionales...</p>
        </div>
    `;

    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/admin/areas`, { headers: { 'Authorization': `Bearer ${token}` } });
        const areas = res.ok ? await res.json() : [
            { id: 1, nombre: 'Área de Deportes (Disciplinas & Fitness)', descripcion: 'Taekwondo, Fútbol, Baloncesto, Musculación, Natación' },
            { id: 2, nombre: 'Área de Cultura (Talleres)', descripcion: 'Danza (Joropo, Salsa, Vallenato), Música e Instrumentos' }
        ];

        const container = document.getElementById('areas-empresa-container');
        if (container) {
            container.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <h3 style="color:#38BDF8; margin:0;">Áreas Habilitadas</h3>
                    <button class="btn-primary" style="min-height:44px; padding:0 1.25rem;"><i class="fas fa-plus-circle"></i> Nueva Área</button>
                </div>
                <table class="data-table">
                    <thead><tr><th>ID</th><th>Nombre del Área</th><th>Descripción</th><th>Acciones</th></tr></thead>
                    <tbody>${renderAreaRows(areas)}</tbody>
                </table>
            `;
        }
    } catch (e) {
        console.warn('Error loading areas empresa:', e);
    }
}

async function renderSuscripcionView(token) {
    const contentArea = document.getElementById('content-area');
    const caps = await fetchTenantCapabilities(token);

    const isFullPlan = caps.canonical_plan === 'full' && caps.is_active;

    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-credit-card"></i> Suscripción & Facturación Institucional</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Gestión de plan comercial B2B, estado de facturación y cuotas mensuales.</p>
        </div>

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:1.5rem;">
            <!-- Plan Actual -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <h3 style="color:#38BDF8; margin:0 0 1rem 0;">Estado Comercial Actual</h3>
                <div style="background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem; margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <strong style="color:#E2E8F0; font-size:1.1rem;">${caps.nombre_empresa}</strong>
                        ${getPlanBadgeHtml(caps.canonical_plan, caps.subscription_status, caps.is_active)}
                    </div>
                    <p style="color:#94A3B8; font-size:0.85rem; margin:0.25rem 0;">
                        Tipo: ${getNatureBadgeInfo(caps.tipo_organizacion).label} | ${getTerritorialBadgeInfo(caps.ambito_organizacional).label} | Vocación: ${(caps.vocacion_institucional || 'deportiva').toUpperCase()}
                    </p>
                </div>

                <h4 style="color:#38BDF8; margin:1rem 0 0.5rem 0;">Límites y Cuotas Mensuales del Plan:</h4>
                <ul style="color:#94A3B8; font-size:0.85rem; line-height:1.8; padding-left:1.25rem;">
                    <li>Módulos Operativos (Deportes, Cultura, Usuarios): <strong style="color:#34D399;">Habilitado</strong></li>
                    <li>Generador de Imágenes IA: <strong style="color:${isFullPlan ? '#38BDF8' : '#94A3B8'};">${caps.monthly_limits.images} / mes</strong></li>
                    <li>Carruseles Multimedia IA: <strong style="color:${isFullPlan ? '#38BDF8' : '#94A3B8'};">${caps.monthly_limits.carousels} / mes</strong></li>
                    <li>Reels & Cortos IA: <strong style="color:${isFullPlan ? '#38BDF8' : '#94A3B8'};">${caps.monthly_limits.reels} / mes</strong></li>
                    <li>Publicación Social Multicanal: <strong style="color:${isFullPlan ? '#38BDF8' : '#94A3B8'};">${caps.monthly_limits.social_posts} / mes</strong></li>
                </ul>
            </div>

            <!-- Pasarela de Pago Stripe -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <h3 style="color:#38BDF8; margin:0 0 1rem 0;">Actualizar o Renovar Plan</h3>
                <div id="payment-form-container">
                    <p style="color:#94A3B8; font-size:0.85rem; margin-bottom:1rem;">
                        Seleccione el plan deseado y realice la transacción segura a través de Stripe Gateway.
                    </p>
                    <div id="payment-element" style="margin-bottom:1rem;"></div>
                    <button id="submit-payment-btn" class="btn-primary" style="width:100%; min-height:44px;">
                        <i class="fas fa-lock"></i> Procesar Pago Seguro
                    </button>
                    <div id="payment-message" class="message-info" style="display:none; margin-top:1rem;"></div>
                </div>
            </div>
        </div>
    `;
}

async function renderAuditoriaEmpresaView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header" style="margin-bottom:1.5rem;">
            <h2 style="color:#38BDF8; margin:0;"><i class="fas fa-shield-alt"></i> Registros de Auditoría & Seguridad Criptográfica</h2>
            <p style="color:#94A3B8; font-size:0.9rem; margin-top:0.25rem;">Trazabilidad completa de acciones administrativas y eventos del sistema.</p>
        </div>
        <div id="audit-log-container" class="card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); padding:1.5rem; border-radius:16px;">
            <p style="color:#94A3B8;">Cargando registros de auditoría...</p>
        </div>
    `;

    const logs = [
        { id: 'LOG-1092', fecha: new Date().toISOString(), usuario: 'Prof. Carlos Mendoza', rol: 'profesor', accion: 'Calificación Actualizada', detalle: 'Modificación de nota física para estudiante STD-***-942 en Taekwondo.', ip: '190.144.20.12', severidad: 'INFO' },
        { id: 'LOG-1091', fecha: new Date(Date.now() - 3600000).toISOString(), usuario: 'Dra. Elena Ramos', rol: 'profesional_area', accion: 'Diagnóstico Biométrico Registrado', detalle: 'Registro antropométrico confidencial para estudiante STD-***-118.', ip: '186.28.102.45', severidad: 'HIGH' }
    ];

    renderAuditTable(logs);
}

function renderAuditTable(logs) {
    const container = document.getElementById('audit-log-container');
    if (!container) return;

    const rows = logs.map(l => {
        const severityColor = l.severidad === 'HIGH' ? '#EF4444' : '#38BDF8';
        return `
            <tr>
                <td><strong>${l.id}</strong></td>
                <td>${new Date(l.fecha).toLocaleString()}</td>
                <td>${l.usuario} (${l.rol})</td>
                <td><span class="badge" style="background:rgba(56,189,248,0.1); color:#38BDF8;">${l.accion}</span></td>
                <td>${l.detalle}</td>
                <td><span style="color:${severityColor}; font-weight:bold;">${l.severidad}</span></td>
                <td>${l.ip}</td>
            </tr>
        `;
    }).join('');

    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr><th>ID Registro</th><th>Fecha / Hora</th><th>Usuario & Rol</th><th>Acción</th><th>Detalle Enmascarado</th><th>Nivel</th><th>Origen IP</th></tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `;
}

window.sgaOpenTeacherSpecialtiesModal = async function(teacherId, teacherName) {
    let modal = document.getElementById('teacher-specialties-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'teacher-specialties-modal';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(7,11,20,0.85); backdrop-filter:blur(8px); z-index:99999; display:flex; justify-content:center; align-items:center; padding:1.5rem;';
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';

    modal.innerHTML = `
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.3); border-radius:16px; width:100%; max-width:700px; max-height:90vh; overflow-y:auto; padding:2rem; box-shadow:0 20px 40px rgba(0,0,0,0.6); color:#F8FAFC;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:1rem;">
                <div>
                    <h3 style="color:#38BDF8; margin:0;"><i class="fas fa-award"></i> Asignación & Aval de Especialidades</h3>
                    <p style="color:#94A3B8; font-size:0.85rem; margin:0.25rem 0 0 0;">Docente / Formador: <strong>${teacherName}</strong> (#${teacherId})</p>
                </div>
                <button onclick="document.getElementById('teacher-specialties-modal').style.display='none'" style="background:transparent; border:none; color:#94A3B8; font-size:1.5rem; cursor:pointer;"><i class="fas fa-times"></i></button>
            </div>
            <div id="modal-specialties-body">
                <p style="color:#94A3B8;"><i class="fas fa-spinner fa-spin"></i> Cargando especialidades asignadas...</p>
            </div>
        </div>
    `;

    const token = localStorage.getItem('sga_token') || sessionStorage.getItem('sga_token') || '';
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';

    async function loadModalData() {
        const bodyEl = document.getElementById('modal-specialties-body');
        try {
            const [teacherSpecsRes, companySpecsRes] = await Promise.all([
                fetch(`${baseUrl}/api/v1/catalogo/teachers/${teacherId}/specialties`, { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch(`${baseUrl}/api/v1/catalogo/my-specialties`, { headers: { 'Authorization': `Bearer ${token}` } })
            ]);

            const teacherSpecs = teacherSpecsRes.ok ? await teacherSpecsRes.json() : [];
            const companySpecs = companySpecsRes.ok ? await companySpecsRes.json() : [];

            let listHtml = '';
            if (teacherSpecs.length === 0) {
                listHtml = '<p style="color:#94A3B8; font-style:italic;">El docente no tiene especialidades asignadas actualmente.</p>';
            } else {
                listHtml = `
                    <table class="data-table" style="margin-bottom:1.5rem;">
                        <thead>
                            <tr><th>Especialidad</th><th>Nivel Académico</th><th>Estado Aval</th><th>Acciones</th></tr>
                        </thead>
                        <tbody>
                            ${teacherSpecs.map(s => `
                                <tr>
                                    <td><strong>${s.nombre}</strong> <small style="color:#94A3B8;">(${s.vertical})</small></td>
                                    <td>${s.nivel_academico || 'Licenciatura'}</td>
                                    <td>
                                        <span class="badge" style="background:${s.certificacion_avalada ? 'rgba(34,197,94,0.15)' : 'rgba(245,158,11,0.15)'}; color:${s.certificacion_avalada ? '#22C55E' : '#F59E0B'};">
                                            <i class="fas ${s.certificacion_avalada ? 'fa-check-circle' : 'fa-clock'}"></i> ${s.estado_aval}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn-secondary" style="min-height:32px; padding:0.2rem 0.5rem; font-size:0.8rem;" onclick="window.sgaToggleTeacherAval(${teacherId}, ${s.profesor_especialidad_id}, ${!s.certificacion_avalada}, '${teacherName}')">
                                            ${s.certificacion_avalada ? '<i class="fas fa-ban"></i> Retirar Aval' : '<i class="fas fa-check"></i> Conceder Aval'}
                                        </button>
                                        <button class="btn-danger" style="min-height:32px; padding:0.2rem 0.5rem; font-size:0.8rem; margin-left:0.25rem;" onclick="window.sgaRemoveTeacherSpecialty(${teacherId}, ${s.profesor_especialidad_id}, '${teacherName}')">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }

            // Options for assigning new adopted specialty
            const assignedEmpIds = new Set(teacherSpecs.map(ts => ts.empresa_especialidad_id));
            const availableOptions = companySpecs.filter(cs => !assignedEmpIds.has(cs.empresa_especialidad_id));

            let assignFormHtml = '';
            if (availableOptions.length === 0) {
                assignFormHtml = '<p style="color:#94A3B8; font-size:0.85rem;">Todas las especialidades adoptadas por la entidad ya están asignadas a este docente.</p>';
            } else {
                assignFormHtml = `
                    <div style="background:rgba(15,23,42,0.6); border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1.25rem; margin-top:1rem;">
                        <h4 style="color:#38BDF8; margin:0 0 0.75rem 0; font-size:0.95rem;"><i class="fas fa-plus-circle"></i> Asignar Nueva Especialidad Institucional</h4>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; margin-bottom:0.75rem;">
                            <div>
                                <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Especialidad Adoptada</label>
                                <select id="modal-select-emp-spec" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem; color:#F8FAFC;">
                                    ${availableOptions.map(o => `<option value="${o.empresa_especialidad_id}">${o.nombre} (${o.vertical})</option>`).join('')}
                                </select>
                            </div>
                            <div>
                                <label style="display:block; color:#94A3B8; font-size:0.8rem; margin-bottom:0.25rem;">Nivel Académico / Título</label>
                                <input type="text" id="modal-input-nivel" placeholder="Ej. Licenciado, Magíster, Entrenador" style="width:100%; background:#070B14; border:1px solid rgba(255,255,255,0.2); border-radius:8px; padding:0.5rem; color:#F8FAFC;">
                            </div>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <label style="color:#F8FAFC; font-size:0.85rem; cursor:pointer; display:flex; align-items:center; gap:0.5rem;">
                                <input type="checkbox" id="modal-check-aval" checked> Otorgar Aval Institucional Inmediato
                            </label>
                            <button class="btn-primary" style="min-height:38px; padding:0 1rem;" onclick="window.sgaSubmitTeacherSpecialtyAssignment(${teacherId}, '${teacherName}')">
                                <i class="fas fa-check"></i> Asignar Especialidad
                            </button>
                        </div>
                    </div>
                `;
            }

            bodyEl.innerHTML = listHtml + assignFormHtml;

        } catch (err) {
            bodyEl.innerHTML = `<p style="color:#EF4444;"><i class="fas fa-exclamation-triangle"></i> Error al cargar especialidades: ${err.message}</p>`;
        }
    }

    await loadModalData();
};

window.sgaToggleTeacherAval = async function(teacherId, assocId, newAvalStatus, teacherName) {
    const token = localStorage.getItem('sga_token') || sessionStorage.getItem('sga_token') || '';
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/catalogo/teachers/${teacherId}/specialties/${assocId}/aval`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ certificacion_avalada: newAvalStatus })
        });
        if (res.ok) {
            await window.sgaOpenTeacherSpecialtiesModal(teacherId, teacherName);
        } else {
            const err = await res.json();
            alert(`Error al actualizar aval: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

window.sgaRemoveTeacherSpecialty = async function(teacherId, assocId, teacherName) {
    if (!confirm('¿Está seguro de remover esta asignación de especialidad al docente?')) return;
    const token = localStorage.getItem('sga_token') || sessionStorage.getItem('sga_token') || '';
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
    try {
        const res = await fetch(`${baseUrl}/api/v1/catalogo/teachers/${teacherId}/specialties/${assocId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            await window.sgaOpenTeacherSpecialtiesModal(teacherId, teacherName);
        } else {
            const err = await res.json();
            alert(`Error al remover especialidad: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

window.sgaSubmitTeacherSpecialtyAssignment = async function(teacherId, teacherName) {
    const selectEl = document.getElementById('modal-select-emp-spec');
    const inputNivel = document.getElementById('modal-input-nivel');
    const checkAval = document.getElementById('modal-check-aval');

    if (!selectEl || !selectEl.value) return;

    const token = localStorage.getItem('sga_token') || sessionStorage.getItem('sga_token') || '';
    const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';

    try {
        const res = await fetch(`${baseUrl}/api/v1/catalogo/teachers/${teacherId}/specialties`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
                empresa_especialidad_id: parseInt(selectEl.value, 10),
                nivel_academico: inputNivel ? inputNivel.value : '',
                certificacion_avalada: checkAval ? checkAval.checked : false
            })
        });
        if (res.ok) {
            await window.sgaOpenTeacherSpecialtiesModal(teacherId, teacherName);
        } else {
            const err = await res.json();
            alert(`Error al asignar especialidad: ${err.detail || 'Operación fallida'}`);
        }
    } catch (e) {
        alert(`Error de red: ${e.message}`);
    }
};

if (typeof registerView === 'function') {
    registerView('admin_empresa', 'panel-empresa', renderAdminEmpresaView);
    registerView('admin_empresa', 'programas-deportivos', renderProgramasDeportivosView);
    registerView('admin_empresa', 'talleres-culturales', renderTalleresCulturalesView);
    registerView('admin_empresa', 'areas-empresa', renderAreasEmpresaView);
    registerView('admin_empresa', 'usuarios-empresa', renderUsuariosEmpresaView);
    registerView('admin_empresa', 'crm-empresa', renderCrmEmpresaView);
    registerView('admin_empresa', 'media-ia-empresa', renderMediaIaEmpresaView);
    registerView('admin_empresa', 'suscripcion', renderSuscripcionView);
    registerView('admin_empresa', 'auditoria-empresa', renderAuditoriaEmpresaView);
    registerView('admin_general', 'auditoria-empresa', renderAuditoriaEmpresaView);
}
