/* ==========================================================================
   Lógica para el Modal Genérico SGA-CD
   Contiene la lógica interactiva para diálogos y ventanas emergentes.
   ========================================================================== */

/* --- Config defensiva --- */
const config = (typeof window !== 'undefined' && window.config) ? window.config : {
  apiBaseUrl: '/api'
};

/**
 * Abre el modal con un título y contenido específico.
 * @param {string} title - El título a mostrar en el header del modal.
 * @param {string} bodyContent - El contenido HTML a insertar en el cuerpo del modal.
 */
function openModal(title, bodyContent) {
    const modal = document.getElementById('generic-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');

    if (!modal || !modalTitle || !modalBody) {
        console.error("No se encontraron los elementos del modal en el DOM.");
        alert(`${title}\n\n${(bodyContent || '').replace(/<[^>]*>/g, '')}`);
        return;
    }

    modalTitle.textContent = title;
    modalBody.innerHTML = bodyContent;
    modal.style.display = 'flex';
}

/**
 * Cierra el modal y limpia su contenido para evitar datos residuales.
 */
function closeModal() {
    const modal = document.getElementById('generic-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');

    if (modal) { modal.style.display = 'none'; }
    if (modalTitle) { modalTitle.textContent = ''; }
    if (modalBody) { modalBody.innerHTML = ''; }
}

/**
 * Configura los listeners para el modal.
 */
function setupModalListeners() {
    const modal = document.getElementById('generic-modal');
    const closeModalButton = document.getElementById('modal-close-btn') || document.querySelector('.modal-close');

    if (closeModalButton) {
        closeModalButton.addEventListener('click', closeModal);
    }

    if (modal) {
        modal.addEventListener('click', (event) => {
            if (event.target.id === 'generic-modal') {
                closeModal();
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', setupModalListeners);
