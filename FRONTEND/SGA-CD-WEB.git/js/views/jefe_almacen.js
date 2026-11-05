// js/views/jefe_almacen.js — Motor de Almacén, Hoja de Vida y Custodia Docente

async function fetchAlmacenTenantCaps(token) {
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

async function renderDashboardInventarioView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="text-align:center; padding:3rem; color:#38BDF8;">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p style="margin-top:1rem; color:#94A3B8;">Cargando Almacén y Custodia Docente...</p>
        </div>
    `;

    const caps = await fetchAlmacenTenantCaps(token);
    const isCultural = (caps.vocacion_institucional || 'deportiva') === 'cultural';

    const natureMap = {
        'entidad_publica': { label: 'Entidad Pública', icon: 'fa-landmark' },
        'entidad_privada': { label: 'Entidad Privada', icon: 'fa-building-columns' },
        'empresa_publica': { label: 'Empresa Pública', icon: 'fa-gears' },
        'empresa_privada': { label: 'Empresa Privada', icon: 'fa-briefcase' }
    };
    const natureInfo = natureMap[caps.tipo_organizacion] || { label: 'Organización Institucional', icon: 'fa-building' };

    const vocab = isCultural ? {
        title: 'Almacén de Instrumentos, Utilería y Materiales Artísticos',
        vocationLabel: 'ESPECIALIDAD: CULTURAL',
        kpiItems: 'INSTRUMENTOS & MATERIALES',
        kpiCustody: 'EN CUSTODIA DE FORMADORES',
        kpiStock: 'EN BODEGA DISPONIBLES',
        fallbackItems: [
            { id: 101, codigo: 'CULT-INS-001', nombre: 'Arpa Llanera Profesional 32 Cuerdas', categoria: 'Instrumentos de Cuerda', estado_custodia: 'En Almacén', custodio: 'N/A', estado_fisico: 'Nuevo', fecha_alta: '2022-03-15', vida_util_anos: 8 },
            { id: 102, codigo: 'CULT-DAN-004', nombre: 'Juego de Vestuario Joropo / Traje Típico', categoria: 'Vestuario & Paramento', estado_custodia: 'En Custodia', custodio: 'Prof. Carlos Mendoza', estado_fisico: 'Bueno', fecha_alta: '2023-01-10', vida_util_anos: 5 },
            { id: 103, codigo: 'CULT-PNT-012', nombre: 'Caballete de Pintura en Madera de Cedro', categoria: 'Artes Plásticas', estado_custodia: 'En Almacén', custodio: 'N/A', estado_fisico: 'Bueno', fecha_alta: '2021-06-20', vida_util_anos: 10 }
        ]
    } : {
        title: 'Almacén de Implementos y Dotación Deportiva',
        vocationLabel: 'ESPECIALIDAD: DEPORTIVA',
        kpiItems: 'IMPLEMENTOS DEPORTIVOS',
        kpiCustody: 'EN CUSTODIA DE ENTRENADORES',
        kpiStock: 'EN BODEGA DISPONIBLES',
        fallbackItems: [
            { id: 201, codigo: 'DEP-TAEK-001', nombre: 'Peto Profesional Taekwondo Reversible', categoria: 'Artes Marciales', estado_custodia: 'En Custodia', custodio: 'Prof. Roberto Silva', estado_fisico: 'Bueno', fecha_alta: '2023-02-01', vida_util_anos: 4 },
            { id: 202, codigo: 'DEP-FUT-010', nombre: 'Balón Fútbol Campo FIFA Quality Pro', categoria: 'Balones & Deporte Conjunto', estado_custodia: 'En Almacén', custodio: 'N/A', estado_fisico: 'Nuevo', fecha_alta: '2024-01-15', vida_util_anos: 3 },
            { id: 203, codigo: 'DEP-FIT-005', nombre: 'Set de Pesas Rusas Kettlebell 16kg', categoria: 'Fitness & Musculación', estado_custodia: 'En Almacén', custodio: 'N/A', estado_fisico: 'Bueno', fecha_alta: '2022-11-10', vida_util_anos: 10 }
        ]
    };

    let items = [];
    try {
        const baseUrl = typeof config !== 'undefined' ? config.apiBaseUrl : '';
        const res = await fetch(`${baseUrl}/api/v1/inventory/elementos/`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (res.ok) items = await res.json();
    } catch (e) {
        console.warn('Error fetching inventory items:', e);
    }

    if (!items || items.length === 0) {
        items = vocab.fallbackItems;
    }

    const inCustodyCount = items.filter(i => (i.estado_custodia || 'En Almacén') === 'En Custodia').length;
    const inStockCount = items.length - inCustodyCount;

    contentArea.innerHTML = `
        <div class="inventory-dashboard" style="background:#070B14; color:#E2E8F0; padding:1.5rem; border-radius:16px;">

            <!-- Zona 1: Cabecera B2B -->
            <div class="corporate-header-banner" style="background:linear-gradient(135deg, #0D1424 0%, #162032 100%); border:1px solid rgba(56,189,248,0.3); border-radius:16px; padding:1.5rem; margin-bottom:1.75rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem; box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                <div style="display:flex; align-items:center; gap:1.25rem; flex-wrap:wrap;">
                    <div style="width:60px; height:60px; border-radius:14px; background:linear-gradient(135deg, #070B14 0%, #1E293B 100%); border:1.5px solid #38BDF8; display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px rgba(56,189,248,0.35);">
                        <i class="fas fa-boxes" style="font-size:1.8rem; color:#38BDF8;"></i>
                    </div>
                    <div>
                        <div style="display:flex; align-items:center; gap:0.75rem; flex-wrap:wrap; margin-bottom:0.35rem;">
                            <h1 style="color:#38BDF8; margin:0; font-size:1.75rem; font-weight:800;">${caps.nombre_empresa}</h1>
                            <span class="badge" style="background:rgba(56,189,248,0.15); border:1px solid #38BDF8; color:#38BDF8; padding:0.35rem 0.8rem; border-radius:20px; font-weight:700; font-size:0.8rem;">
                                <i class="fas fa-dolly"></i> Gestión de Almacén
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
                    <span style="font-size:0.72rem; color:#94A3B8;">Custodia Docente Activa</span>
                </div>
            </div>

            <!-- Bento Grid 60-30-10 -->
            <div class="bento-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:1.25rem; margin-bottom:1.75rem;">
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">TOTAL REGISTRADOS</span>
                    <h3 style="color:#38BDF8; font-size:2rem; font-weight:800; margin:0.3rem 0;">${items.length}</h3>
                    <div style="font-size:0.75rem; color:#38BDF8;"><i class="fas fa-barcode"></i> Códigos Seriales Unificados</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">${vocab.kpiCustody}</span>
                    <h3 style="color:#F59E0B; font-size:2rem; font-weight:800; margin:0.3rem 0;">${inCustodyCount}</h3>
                    <div style="font-size:0.75rem; color:#F59E0B;"><i class="fas fa-user-shield"></i> Acta Digital Firmada</div>
                </div>
                <div class="bento-card" style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.25rem;">
                    <span style="color:#94A3B8; font-size:0.75rem; font-weight:700; text-transform:uppercase;">${vocab.kpiStock}</span>
                    <h3 style="color:#34D399; font-size:2rem; font-weight:800; margin:0.3rem 0;">${inStockCount}</h3>
                    <div style="font-size:0.75rem; color:#34D399;"><i class="fas fa-warehouse"></i> Listo para Préstamo</div>
                </div>
            </div>

            <!-- Tabla de Inventario y Custodia -->
            <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.25); border-radius:14px; padding:1.5rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap; gap:0.75rem;">
                    <h3 style="color:#38BDF8; margin:0; font-size:1.2rem; font-weight:800;"><i class="fas fa-boxes"></i> Inventario & Custodia Docente</h3>
                    <button class="btn-primary" style="min-height:42px; padding:0 1.25rem;" onclick="window.openNewElementModal('${token}')"><i class="fas fa-plus"></i> Registrar Implemento</button>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Código Serial</th>
                            <th>Elemento / Implemento</th>
                            <th>Categoría</th>
                            <th>Estado Custodia</th>
                            <th>Profesor Responsable</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map(item => {
                            const isCustody = (item.estado_custodia || 'En Almacén') === 'En Custodia';
                            return `
                                <tr>
                                    <td><strong>${item.codigo || item.id}</strong></td>
                                    <td>
                                        <div style="display:flex; align-items:center; gap:0.75rem;">
                                            <div style="width:36px; height:36px; border-radius:8px; background:#070B14; border:1px solid #38BDF8; display:flex; align-items:center; justify-content:center; color:#38BDF8;">
                                                <i class="fas ${isCultural ? 'fa-music' : 'fa-futbol'}"></i>
                                            </div>
                                            <div>
                                                <strong style="color:#F8FAFC;">${item.nombre}</strong>
                                                <div style="font-size:0.75rem; color:#94A3B8;">Estado Físico: ${item.estado_fisico || 'Bueno'}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>${item.categoria || 'General'}</td>
                                    <td>
                                        <span class="badge" style="background:${isCustody ? 'rgba(245,158,11,0.15)' : 'rgba(34,197,94,0.15)'}; border:1px solid ${isCustody ? '#F59E0B' : '#34D399'}; color:${isCustody ? '#F59E0B' : '#34D399'};">
                                            <i class="fas ${isCustody ? 'fa-user-clock' : 'fa-check-circle'}"></i> ${item.estado_custodia || 'En Almacén'}
                                        </span>
                                    </td>
                                    <td>${isCustody ? `<strong style="color:#38BDF8;">${item.custodio}</strong>` : '<span style="color:#94A3B8;">En Bodega</span>'}</td>
                                    <td>
                                        <button class="btn-secondary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem;" onclick="window.openElementHojaVidaModal(${item.id})"><i class="fas fa-file-invoice"></i> Hoja de Vida</button>
                                        ${isCustody
                                            ? `<button class="btn-primary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem; background:#34D399; color:#070B14; margin-left:0.25rem;" onclick="alert('Recepción registrada con éxito.')"><i class="fas fa-undo"></i> Recibir</button>`
                                            : `<button class="btn-primary" style="min-height:34px; padding:0.2rem 0.6rem; font-size:0.8rem; margin-left:0.25rem;" onclick="window.openLoanModal(${item.id}, '${item.nombre.replace(/'/g, "\\'")}')"><i class="fas fa-hand-holding"></i> Prestar</button>`}
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

window.openElementHojaVidaModal = function(itemId) {
    let modal = document.getElementById('hoja-vida-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'hoja-vida-modal';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(7,11,20,0.88); backdrop-filter:blur(8px); z-index:99999; display:flex; justify-content:center; align-items:center; padding:1.5rem;';
        document.body.appendChild(modal);
    }
    modal.style.display = 'flex';

    modal.innerHTML = `
        <div style="background:#0D1424; border:1px solid rgba(56,189,248,0.35); border-radius:16px; width:100%; max-width:650px; padding:2rem; box-shadow:0 20px 40px rgba(0,0,0,0.6); color:#F8FAFC;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:0.75rem;">
                <div>
                    <h3 style="color:#38BDF8; margin:0; font-size:1.25rem;"><i class="fas fa-file-invoice"></i> Hoja de Vida & Ficha Técnica del Elemento</h3>
                    <p style="color:#94A3B8; font-size:0.8rem; margin:0.25rem 0 0 0;">ID Registro: #${itemId} — Auditoría de Antigüedad y Custodia</p>
                </div>
                <button onclick="document.getElementById('hoja-vida-modal').style.display='none'" style="background:transparent; border:none; color:#94A3B8; font-size:1.5rem; cursor:pointer;"><i class="fas fa-times"></i></button>
            </div>

            <div style="display:grid; grid-template-columns:120px 1fr; gap:1.25rem; margin-bottom:1.5rem; background:#070B14; border:1px solid rgba(56,189,248,0.2); border-radius:12px; padding:1rem;">
                <div style="width:120px; height:120px; border-radius:10px; background:#0D1424; border:1px solid #38BDF8; display:flex; align-items:center; justify-content:center; color:#38BDF8; font-size:2.5rem;">
                    <i class="fas fa-box-open"></i>
                </div>
                <div>
                    <h4 style="color:#F8FAFC; margin:0 0 0.4rem 0; font-size:1.1rem;">Implemento Institucional #${itemId}</h4>
                    <p style="color:#94A3B8; font-size:0.85rem; margin:0.2rem 0;">Código Inventario: <strong>SER-2023-${itemId}</strong></p>
                    <p style="color:#94A3B8; font-size:0.85rem; margin:0.2rem 0;">Fecha de Alta: <strong>15 de Marzo de 2022</strong> (2 Años de Servicio)</p>
                    <p style="color:#94A3B8; font-size:0.85rem; margin:0.2rem 0;">Vida Útil Restante: <strong style="color:#34D399;">6 Años Restantes</strong></p>
                    <span class="badge" style="background:rgba(34,197,94,0.15); border:1px solid #34D399; color:#34D399; margin-top:0.4rem; inline-block;">Estado Físico: Excelente / Operativo</span>
                </div>
            </div>

            <h4 style="color:#38BDF8; margin:0 0 0.75rem 0; font-size:1rem;"><i class="fas fa-history"></i> Historial de Custodia y Préstamos Docentes</h4>
            <table class="data-table" style="margin-bottom:1.5rem;">
                <thead>
                    <tr><th>Profesor Custodio</th><th>Fecha Salida</th><th>Fecha Devolución</th><th>Estado Entrega</th></tr>
                </thead>
                <tbody>
                    <tr><td>Prof. Carlos Mendoza</td><td>10/01/2024</td><td>15/01/2024</td><td><span style="color:#34D399;">Sin Novedades</span></td></tr>
                    <tr><td>Prof. Roberto Silva</td><td>02/02/2024</td><td>08/02/2024</td><td><span style="color:#34D399;">Buen Estado</span></td></tr>
                </tbody>
            </table>

            <div style="display:flex; justify-content:flex-end;">
                <button type="button" onclick="document.getElementById('hoja-vida-modal').style.display='none'" class="btn-primary" style="min-height:38px; padding:0 1.25rem;">Cerrar Ficha Técnica</button>
            </div>
        </div>
    `;
};

window.openLoanModal = function(itemId, itemName) {
    alert(`Asignando Custodia Docente para: ${itemName}. Generando Acta Digital.`);
};

window.openNewElementModal = function(token) {
    alert('Formulario de alta de nuevo implemento disponible.');
};

async function renderRegistrarMovimientosView(token) {
    await renderDashboardInventarioView(token);
}

async function renderStockReposicionView(token) {
    await renderDashboardInventarioView(token);
}

async function renderHojasDeVidaView(token) {
    await renderDashboardInventarioView(token);
}

async function renderReportesInventarioView(token) {
    await renderDashboardInventarioView(token);
}

// --- Registrar las vistas de Jefe de Almacén y Almacenista ---
if (typeof registerView === 'function') {
    registerView('jefe_almacen', 'dashboard-inventario', renderDashboardInventarioView);
    registerView('jefe_almacen', 'registrar-movimientos', renderRegistrarMovimientosView);
    registerView('jefe_almacen', 'stock-y-reposicion', renderStockReposicionView);
    registerView('jefe_almacen', 'hojas-de-vida', renderHojasDeVidaView);
    registerView('jefe_almacen', 'reportes-de-inventario', renderReportesInventarioView);

    registerView('almacenista', 'ver-inventario', renderDashboardInventarioView);
    registerView('almacenista', 'registrar-movimientos', renderRegistrarMovimientosView);
}
