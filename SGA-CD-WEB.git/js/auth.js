document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const messageDiv = document.getElementById('login-mensaje');

    // Helper XSS Sanitization
    function sanitizeHTML(str) {
        if (!str) return '';
        const temp = document.createElement('div');
        temp.textContent = String(str);
        return temp.innerHTML;
    }

    // Redirigir si el usuario ya está logueado
    if (localStorage.getItem('accessToken')) {
        window.location.href = 'app.html';
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = loginForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.dataset.origText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Autenticando...';
            }

            const rawUsername = document.getElementById('username').value;
            const rawPassword = document.getElementById('password').value;

            // Sanitización estricta perimetral
            const username = sanitizeHTML(rawUsername.trim());
            const password = rawPassword; // Se envía codificado URI en body form-urlencoded

            if (!username || !password) {
                triggerLoginShake(loginForm, 'Por favor, ingresa usuario y contraseña válidos.', 'STD-ERR-SECURITY-LOGIN');
                resetSubmitButton(submitBtn);
                return;
            }

            showMessage('Iniciando sesión segura con cifrado JWT...', 'info');

            try {
                const response = await fetch(`${config.apiBaseUrl}/api/v1/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
                });

                const data = await response.json();

                if (response.ok && data.access_token) {
                    localStorage.setItem('accessToken', data.access_token);
                    localStorage.setItem('refreshToken', data.refresh_token);

                    try {
                        const payloadBase64 = data.access_token.split('.')[1];
                        const decodedPayload = JSON.parse(atob(payloadBase64));

                        localStorage.setItem('userRoles', JSON.stringify(decodedPayload.roles || []));
                        localStorage.setItem('userId', decodedPayload.sub);
                        localStorage.setItem('userInquilinoId', decodedPayload.inquilino_id);
                        localStorage.setItem('userName', sanitizeHTML(decodedPayload.nombre_completo || ''));

                        console.log('[Login Exitoso] Roles:', decodedPayload.roles);
                    } catch (e) {
                        console.error('Error decodificando token JWT:', e);
                    }

                    showMessage('Inicio de sesión verificado. Cargando panel...', 'success');
                    setTimeout(() => {
                        window.location.href = 'app.html';
                    }, 1000);
                } else {
                    const status = response.status || 401;
                    const maskedCode = (status === 403 || status === 429) ? 'STD-ERR-SECURITY-BREACH' : 'STD-ERR-SECURITY-LOGIN';
                    triggerLoginShake(loginForm, data.detail || 'Credenciales inválidas o acceso bloqueado temporalmente.', maskedCode);

                    if (window.SGADynamicIsland && (status === 403 || status === 429)) {
                        window.SGADynamicIsland.notify({
                            message: `ALERTA DE SEGURIDAD [${maskedCode}]: Acceso restringido o tasa de solicitudes excedida.`,
                            type: 'breach',
                            duration: 6000
                        });
                    }

                    if (submitBtn) {
                        submitBtn.disabled = true;
                        submitBtn.style.background = '#0D1424';
                        submitBtn.style.color = '#EF4444';
                        submitBtn.style.borderColor = '#EF4444';
                        submitBtn.innerHTML = `<i class="fa-solid fa-lock"></i> Bloqueado [${maskedCode}]`;

                        setTimeout(() => {
                            resetSubmitButton(submitBtn);
                        }, 4000);
                    }
                }
            } catch (error) {
                console.error('Error de red en inicio de sesión:', error);
                triggerLoginShake(loginForm, 'Error de conexión o fallo perimetral en el servidor.', 'STD-ERR-SECURITY-LOGIN');
                resetSubmitButton(submitBtn);
            }
        });
    }

    function triggerLoginShake(element, msgText, codeText) {
        showMessage(`[${codeText}] ${msgText}`, 'error');
        if (window.gsap) {
            gsap.fromTo(element,
                { x: -12 },
                { x: 12, duration: 0.08, repeat: 5, yoyo: true, ease: 'power1.inOut', onComplete: () => gsap.set(element, { x: 0 }) }
            );
        }
    }

    function resetSubmitButton(btn) {
        if (!btn) return;
        btn.disabled = false;
        btn.style.background = '';
        btn.style.color = '';
        btn.style.borderColor = '';
        btn.innerHTML = btn.dataset.origText || 'Ingresar';
    }

    function showMessage(message, type) {
        if (messageDiv) {
            messageDiv.textContent = message;
            messageDiv.className = `message-${type}`;
            messageDiv.style.color = type === 'error' ? '#EF4444' : type === 'success' ? '#38BDF8' : '#94A3B8';
            messageDiv.style.fontWeight = 'bold';
            messageDiv.style.marginTop = '0.75rem';
        }
    }
});
