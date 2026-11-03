document.addEventListener('DOMContentLoaded', () => {
    const registrationForm = document.getElementById('form-registro');
    const messageDiv = document.getElementById('form-mensaje');
    const findNearbyBtn = document.getElementById('find-nearby-btn');
    const nearbyResultsContainer = document.getElementById('nearby-results');

    // --- Geolocation Logic ---
    findNearbyBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            nearbyResultsContainer.innerHTML = '<p>La geolocalización no es soportada por tu navegador.</p>';
            return;
        }

        nearbyResultsContainer.innerHTML = '<p>Obteniendo tu ubicación...</p>';

        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;

            try {
                const response = await fetch(`${config.apiBaseUrl}/api/empresas_cercanas?lat=${latitude}&lon=${longitude}`);
                const tenants = await response.json();

                if (response.ok) {
                    renderNearbyTenants(tenants);
                } else {
                    nearbyResultsContainer.innerHTML = `<p>Error: ${tenants.error}</p>`;
                }
            } catch (error) {
                nearbyResultsContainer.innerHTML = '<p>Error al contactar el servidor.</p>';
            }

        }, () => {
            nearbyResultsContainer.innerHTML = '<p>No se pudo obtener tu ubicación. Por favor, asegúrate de haber dado permiso.</p>';
        });
    });

    function renderNearbyTenants(tenants) {
        if (tenants.length === 0) {
            nearbyResultsContainer.innerHTML = '<p>No se encontraron organizaciones cercanas. ¡Puedes ser la primera en tu área!</p>';
            return;
        }

        let html = '<h3>Organizaciones Cercanas:</h3><ul>';
        tenants.forEach(tenant => {
            html += `<li>${tenant.nombre_empresa} (${tenant.distancia_km} km) - ${tenant.municipio}</li>`;
        });
        html += '</ul>';
        nearbyResultsContainer.innerHTML = html;
    }


    // --- Registration Form Logic ---
    registrationForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = registrationForm.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.origText = submitBtn.innerHTML;
            submitBtn.innerHTML = 'Procesando...';
        }

        // Collect form data based on the new backend schema
        const tenantData = {
            nombre_empresa: document.getElementById('nombre_empresa').value,
            tipo_organizacion: document.getElementById('tipo_organizacion')?.value || 'entidad_publica',
            ambito_organizacional: document.getElementById('ambito_organizacional')?.value || 'municipal',
            admin_nombre_completo: document.getElementById('nombre_admin').value,
            admin_email: document.getElementById('correo_admin').value,
            admin_password: document.getElementById('password_admin').value,
        };

        // Basic validation
        if (!tenantData.nombre_empresa || !tenantData.admin_nombre_completo || !tenantData.admin_email || !tenantData.admin_password) {
            showMessage('Por favor, completa todos los campos requeridos.', 'error');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.origText || 'Registrar';
            }
            return;
        }

        showMessage('Registrando tu organización...', 'info');

        try {
            // Call the new, correct endpoint
            const response = await fetch(`${config.apiBaseUrl}/api/v1/tenants/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tenantData),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('¡Organización registrada con éxito! Serás redirigido a la página de inicio de sesión.', 'success');
                setTimeout(() => {
                    window.location.href = 'login.html'; // Redirect to login page on success
                }, 3000);
            } else {
                showMessage(result.detail || 'Ocurrió un error durante el registro.', 'error');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.dataset.origText || 'Registrar';
                }
            }
        } catch (error) {
            console.error('Error en el registro:', error);
            showMessage('No se pudo conectar con el servidor. Intenta de nuevo más tarde.', 'error');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.origText || 'Registrar';
            }
        }
    });

    function showMessage(message, type) {
        messageDiv.textContent = message;
        messageDiv.className = `message-${type}`; // e.g., message-error, message-success
    }
});
