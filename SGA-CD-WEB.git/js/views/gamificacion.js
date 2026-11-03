/* ==========================================================================
   Vistas de Gamificación Social (Misiones y Mercado)
   ========================================================================== */

/**
 * Renderiza la vista de "Misiones" para el alumno.
 * Llama a la API para obtener las misiones y las muestra en tarjetas.
 */
async function renderMisionesView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header">
            <h2><i class="fas fa-tasks"></i> Misiones Disponibles</h2>
        </div>
        <p>Cargando misiones...</p>
    `;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/v1/misiones/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error('No se pudo obtener la lista de misiones.');
        }

        const misiones = await response.json();

        let misionCards = '<p>No hay misiones disponibles en este momento.</p>';
        if (misiones && misiones.length > 0) {
            misionCards = misiones.map(mision => `
                <div class="card card-mision">
                    <div class="card-header">
                        <h3>${mision.nombre}</h3>
                        <span class="mision-recompensa">+${mision.puntos_recompensa} Puntos</span>
                    </div>
                    <div class="card-body">
                        <p>${mision.descripcion}</p>
                        ${mision.medalla_recompensa_key ? `<p><strong>Recompensa extra:</strong> Medalla "${mision.medalla_recompensa_key}"</p>` : ''}
                    </div>
                    <div class="card-footer">
                        <div class="progress-bar">
                            <div class="progress" style="width: 25%;"></div> <!-- Placeholder progress -->
                        </div>
                        <button class="btn-secondary" data-mision-id="${mision.id}">Ver Progreso</button>
                    </div>
                </div>
            `).join('');
        }

        contentArea.innerHTML = `
            <div class="view-header">
                <h2><i class="fas fa-tasks"></i> Misiones Disponibles</h2>
                <!-- Aquí podría ir un botón para crear misiones si el rol es 'coordinador' -->
            </div>
            <div class="card-container">
                ${misionCards}
            </div>
        `;
    } catch (error) {
        contentArea.innerHTML += `<p class="message-error">Error al cargar las misiones: ${error.message}</p>`;
    }
}

/**
 * Renderiza la vista de "Mercado de Puntos" para el alumno.
 * Llama a la API para obtener los ítems y los muestra en tarjetas.
 */
async function renderMercadoView(token) {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="view-header">
            <h2><i class="fas fa-store"></i> Mercado de Puntos</h2>
        </div>
        <p>Cargando ítems del mercado...</p>
    `;

    try {
        const response = await fetch(`${config.apiBaseUrl}/api/v1/mercado/items/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error('No se pudo obtener la lista de ítems del mercado.');
        }

        const items = await response.json();

        let itemCards = '<p>No hay ítems disponibles en el mercado en este momento.</p>';
        if (items && items.length > 0) {
            itemCards = items.map(item => `
                <div class="card card-mercado">
                    <div class="card-header">
                        <h3>${item.nombre}</h3>
                    </div>
                    <div class="card-body">
                        <p>${item.descripcion}</p>
                        <p class="item-stock">
                            ${item.stock === -1 ? 'Stock ilimitado' : `Disponibles: ${item.stock}`}
                        </p>
                    </div>
                    <div class="card-footer">
                        <span class="item-costo">${item.costo_puntos} Puntos</span>
                        <button class="btn-primary" data-item-id="${item.id}" ${item.stock === 0 ? 'disabled' : ''}>
                            Comprar
                        </button>
                    </div>
                </div>
            `).join('');
        }

        contentArea.innerHTML = `
            <div class="view-header">
                <h2><i class="fas fa-store"></i> Mercado de Puntos</h2>
                <!-- Aquí podría ir un botón para crear ítems si el rol es 'admin' -->
            </div>
            <div class="card-container">
                ${itemCards}
            </div>
        `;
    } catch (error) {
        contentArea.innerHTML += `<p class="message-error">Error al cargar el mercado: ${error.message}</p>`;
    }
}
