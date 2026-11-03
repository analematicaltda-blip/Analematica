
// --- Registro Global de Vistas, ahora por Rol ---
window.sgaViewRegistry = {};

/**
 * Registra una función de renderizado para un rol y nombre de vista específicos.
 * @param {string} roleName - El rol para el que se registra la vista (ej. 'alumno').
 * @param {string} viewName - El identificador de la vista (ej. 'mis-cursos').
 * @param {Function} renderer - La función async que renderizará la vista.
 */
function registerView(roleName, viewName, renderer) {
    if (!window.sgaViewRegistry[roleName]) {
        window.sgaViewRegistry[roleName] = {};
    }
    if (window.sgaViewRegistry[roleName][viewName]) {
        console.warn(`ADVERTENCIA: La vista '${viewName}' para el rol '${roleName}' está siendo registrada de nuevo.`);
    }
    window.sgaViewRegistry[roleName][viewName] = renderer;
}

// --- Router Principal de Vistas ---
/**
 * Renderiza el contenido para una vista y rol dados.
 */
async function renderContentForView(viewName, token, roleName = 'default') {
    const contentArea = document.getElementById('content-area');
    if (!contentArea) {
        console.error("El área de contenido principal #content-area no fue encontrada.");
        return;
    }

    contentArea.innerHTML = `<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i><h2>Cargando...</h2></div>`;

    try {
        // Buscar un renderer específico para el rol y un renderer común/default.
        const roleSpecificRenderer = window.sgaViewRegistry[roleName]?.[viewName];
        const commonRenderer = window.sgaViewRegistry['common']?.[viewName];
        const renderer = roleSpecificRenderer || commonRenderer;

        if (typeof renderer === 'function') {
            await renderer(token, roleName);
        } else {
            // Fallback routing: look for default/dashboard or any common view registered for this role
            const roleViews = window.sgaViewRegistry[roleName];
            if (roleViews && typeof Object.values(roleViews)[0] === 'function') {
                console.warn(`Vista '${viewName}' no encontrada para '${roleName}'. Redirigiendo a vista por defecto.`);
                await Object.values(roleViews)[0](token, roleName);
            } else {
                console.warn(`No se encontró un renderer para la vista '${viewName}' para el rol '${roleName}' o en común.`);
                contentArea.innerHTML = `
                    <div class="card" style="text-align:center; padding:3rem; background:var(--color-surface-card); border:1px solid var(--color-border-specular);">
                        <h2><i class="fas fa-compass" style="color:var(--color-accent-cyan);"></i> Vista del Módulo Institucional</h2>
                        <p style="color:var(--color-text-muted); margin:1rem 0;">La sección (<strong>${viewName}</strong>) está configurada para el rol <strong>${roleName}</strong> en el Área de Deportes y Cultura.</p>
                        <button class="btn-primary" onclick="renderContentForView('dashboard', '${token}', '${roleName}')">
                            <i class="fas fa-arrow-left"></i> Volver al Panel Principal
                        </button>
                    </div>`;
            }
        }
    } catch (error) {
        console.error(`Error al renderizar la vista '${viewName}':`, error);
        contentArea.innerHTML = `<div class="view-error"><h2><i class="fas fa-times-circle"></i> Error al cargar la vista</h2><p>Ocurrió un problema al intentar mostrar <strong>${viewName}</strong>.</p><p class="error-message">Detalle: ${error.message}</p></div>`;
    }
}

/* ==========================================================================
   Implementación de la Vista para Admin General
   ========================================================================== */
async function renderVerificarRolesView(token) {
    const contentArea = document.getElementById('content-area');
    const rolesRequeridos = [
        'admin_general', 'admin_empresa', 'jefe_area', 'profesional_area',
        'tecnico_area', 'coordinador', 'profesor', 'alumno', 'padre_acudiente',
        'jefe_almacen', 'almacenista', 'jefe_escenarios'
    ];

    let rolesDesdeAPI = [];
    try {
        const res = await fetch(`${config.apiBaseUrl}/api/v1/roles`, { 
            headers: { 'Authorization': `Bearer ${token}` } 
        });
        if (!res.ok) throw new Error(`El servidor respondió con estado ${res.status}`);
        rolesDesdeAPI = await res.json();
    } catch (e) {
        contentArea.innerHTML = `<p class="message-error">No se pudieron obtener los roles desde la API: ${e.message}</p>`;
        return;
    }

    const rolesEncontrados = new Set(rolesDesdeAPI.map(r => r.nombre));
    const faltantes = rolesRequeridos.filter(r => !rolesEncontrados.has(r));

    const rows = rolesDesdeAPI
        .map(r => `<tr><td>${r.id ?? '—'}</td><td>${r.nombre ?? 'N/A'}</td><td>${r.descripcion ?? '—'}</td></tr>`)
        .join('');

    const faltHtml = faltantes.length
        ? `<div class="missing-roles">${faltantes.map(n => `<button class="btn-primary btn-crear-rol" data-rol-nombre="${n}">Crear rol: ${n}</button>`).join(' ')}</div>`
        : '<p class="message-success">¡Excelente! Todos los roles requeridos existen.</p>';

    contentArea.innerHTML = `
        <div class="view-header"><h2><i class="fas fa-user-shield"></i> Verificar Roles en la BD</h2></div>
        <table class="data-table">
            <thead><tr><th>ID</th><th>Nombre</th><th>Descripción</th></tr></thead>
            <tbody>${rows || '<tr><td colspan="3">No se encontraron roles.</td></tr>'}</tbody>
        </table>
        <div class="actions-footer"><h3>Roles Faltantes</h3>${faltHtml}</div>
    `;

    setupVerificarRolesListeners(token);
}

function setupVerificarRolesListeners(token) {
    const contentArea = document.getElementById('content-area');
    if (!contentArea) return;

    contentArea.addEventListener('click', async (e) => {
        if (e.target?.classList.contains('btn-crear-rol')) {
            abrirModalCrearRol(e.target.dataset.rolNombre, token);
        }
    });
}

function abrirModalCrearRol(rolNombre, token) {
    const modalBodyContent = `
        <form id="crear-rol-form" style="display: flex; flex-direction: column; gap: 1rem;">
            <p>Creando el rol: <strong>${rolNombre}</strong></p>
            <div class="form-group">
                <label for="rol-descripcion-input">Descripción</label>
                <textarea id="rol-descripcion-input" class="form-textarea" required></textarea>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn-primary">Confirmar</button>
            </div>
        </form>
        <div id="modal-feedback"></div>
    `;

    openModal(`Crear Rol: ${rolNombre}`, modalBodyContent);

    document.getElementById('crear-rol-form').addEventListener('submit', async (submitEvent) => {
        submitEvent.preventDefault();
        const feedbackDiv = document.getElementById('modal-feedback');
        feedbackDiv.textContent = 'Creando...';
        try {
            const res = await fetch(`${config.apiBaseUrl}/api/v1/roles`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json', 
                    'Authorization': `Bearer ${token}` 
                },
                body: JSON.stringify({ 
                    nombre: rolNombre, 
                    descripcion: document.getElementById('rol-descripcion-input').value 
                })
            });
            const result = await res.json();
            if (!res.ok) throw new Error(result.detail || 'Error del servidor');

            feedbackDiv.textContent = '¡Rol creado! Refrescando...';
            setTimeout(() => { 
                closeModal(); 
                renderContentForView('verificar-roles-bd', token, 'admin_general'); 
            }, 1200);
        } catch (error) {
            feedbackDiv.textContent = `Error: ${error.message}`;
        }
    });
}

// Registrar la vista de admin_general para su rol específico
registerView('admin_general', 'verificar-roles-bd', renderVerificarRolesView);