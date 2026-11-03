document.addEventListener('DOMContentLoaded', () => {
    const googleLoginBtn = document.getElementById('google-login-btn');
    const facebookLoginBtn = document.getElementById('facebook-login-btn');
    const microsoftLoginBtn = document.getElementById('microsoft-login-btn');

    // --- 1. Configuración de Proveedores OAuth ---
    // IMPORTANTE: Los client_id deben ser reemplazados con los IDs reales
    // obtenidos al registrar la aplicación en cada plataforma.
    const oauthConfig = {
        google: {
            authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
            clientId: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
            redirectUri: window.location.origin + '/login.html', // Redirigir de vuelta a la página de login
            scope: 'openid email profile',
            responseType: 'code'
        },
        facebook: {
            authUrl: 'https://www.facebook.com/v12.0/dialog/oauth',
            clientId: 'YOUR_FACEBOOK_APP_ID',
            redirectUri: window.location.origin + '/login.html',
            scope: 'email public_profile',
            responseType: 'code'
        },
        microsoft: {
            authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
            clientId: 'YOUR_MICROSOFT_CLIENT_ID',
            redirectUri: window.location.origin + '/login.html',
            scope: 'openid email profile User.Read',
            responseType: 'code'
        }
    };

    // --- 2. Manejadores de Eventos para los Botones ---
    if (googleLoginBtn) {
        googleLoginBtn.addEventListener('click', () => {
            redirectToProvider('google');
        });
    }
    if (facebookLoginBtn) {
        facebookLoginBtn.addEventListener('click', () => {
            redirectToProvider('facebook');
        });
    }
    if (microsoftLoginBtn) {
        microsoftLoginBtn.addEventListener('click', () => {
            redirectToProvider('microsoft');
        });
    }

    function redirectToProvider(provider) {
        const config = oauthConfig[provider];
        const params = new URLSearchParams({
            client_id: config.clientId,
            redirect_uri: config.redirectUri,
            scope: config.scope,
            response_type: config.responseType,
            // state: 'un_valor_aleatorio_y_seguro' // Opcional pero recomendado para seguridad
        });

        const authorizationUrl = `${config.authUrl}?${params.toString()}`;
        window.location.href = authorizationUrl;
    }

    // --- 3. Manejo del Callback del Proveedor ---
    // Al cargar la página, verificar si venimos de una redirección de OAuth
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state'); // Si se usa 'state'

    if (code) {
        // Asumimos que podemos identificar al proveedor por el 'state' o por un parámetro adicional.
        // Para este ejemplo, supondremos un endpoint genérico en el backend.
        // El backend necesita saber de qué proveedor viene el código.
        const providerName = 'google'; // Esto debería determinarse dinámicamente.

        console.log(`Código de autorización recibido: ${code}`);
        // Limpiar la URL para no dejar el código visible
        window.history.replaceState({}, document.title, "/login.html");

        // Enviar el código al backend para intercambiarlo por un token de la app
        exchangeCodeForToken(providerName, code);
    }

    async function exchangeCodeForToken(provider, authCode) {
        const messageDiv = document.getElementById('login-mensaje');
        if (messageDiv) {
            messageDiv.textContent = 'Verificando autorización...';
            messageDiv.className = 'message-info';
        }

        try {
            // El backend debe tener un endpoint como /api/auth/{provider}/callback
            const response = await fetch(`${config.apiBaseUrl}/api/auth/${provider}/callback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: authCode }),
            });

            const data = await response.json();

            if (response.ok && data.access_token) {
                localStorage.setItem('accessToken', data.access_token);
                if (messageDiv) {
                    messageDiv.textContent = 'Inicio de sesión exitoso. Redirigiendo...';
                    messageDiv.className = 'message-success';
                }
                setTimeout(() => {
                    window.location.href = 'app.html';
                }, 1500);
            } else {
                throw new Error(data.detail || 'No se pudo iniciar sesión con el proveedor.');
            }
        } catch (error) {
            console.error('Error en el intercambio de código:', error);
             if (messageDiv) {
                messageDiv.textContent = `Error: ${error.message}`;
                messageDiv.className = 'message-error';
            }
        }
    }
});
