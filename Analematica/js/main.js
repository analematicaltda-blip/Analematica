/**
 * Analemática - Interactividad y Validaciones
 * Ecosistema de Presentación Institucional y Enrutamiento a SGA-CD
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Menú móvil
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mainNav = document.querySelector('.main-nav');

    if (mobileMenuBtn && mainNav) {
        mobileMenuBtn.addEventListener('click', () => {
            mainNav.classList.toggle('active');
        });

        // Cerrar menú al hacer clic en un enlace
        const navLinks = mainNav.querySelectorAll('.nav-link, .nav-cta');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                mainNav.classList.remove('active');
            });
        });
    }

    // 2. Formulario de Captura de Leads (Diagnóstico Técnico)
    const leadForm = document.getElementById('leadCaptureForm');
    const successBox = document.getElementById('formSuccessMessage');

    if (leadForm) {
        leadForm.addEventListener('submit', (e) => {
            e.preventDefault();

            let isValid = true;

            const fields = [
                { id: 'nombreCompleto', errorId: 'error-nombre', validator: val => val.trim().length >= 3 },
                { id: 'entidadOrganizacion', errorId: 'error-entidad', validator: val => val.trim().length >= 2 },
                { id: 'correoInstitucional', errorId: 'error-correo', validator: val => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()) },
                { id: 'telefonoContacto', errorId: 'error-telefono', validator: val => val.trim().length >= 7 }
            ];

            fields.forEach(field => {
                const input = document.getElementById(field.id);
                const parent = input ? input.closest('.form-group') : null;

                if (!input || !field.validator(input.value)) {
                    isValid = false;
                    if (parent) parent.classList.add('input-error');
                } else {
                    if (parent) parent.classList.remove('input-error');
                }
            });

            if (isValid) {
                // Simulación de envío exitoso
                const submitBtn = document.getElementById('submitFormBtn');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Procesando Diagnóstico...';
                }

                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Enviar Solicitud de Diagnóstico';
                    }
                    if (successBox) {
                        successBox.classList.remove('hidden');
                        successBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }
                    leadForm.reset();
                }, 600);
            }
        });

        // Limpieza de errores en tiempo real
        const inputs = leadForm.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                const parent = input.closest('.form-group');
                if (parent) parent.classList.remove('input-error');
            });
        });
    }

    // 3. Smooth scroll para anclas internas
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});
