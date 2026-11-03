// SGA-CD - Gestor de Consentimiento de Cookies y Privacidad
// --------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    // Inject Cookie Banner if no consent stored
    if (!localStorage.getItem('sgacd_cookie_consent')) {
        showCookieBanner();
    }
});

function showCookieBanner() {
    const banner = document.createElement('div');
    banner.id = 'cookie-consent-banner';
    banner.style.position = 'fixed';
    banner.style.bottom = '0';
    banner.style.left = '0';
    banner.style.right = '0';
    banner.style.backgroundColor = '#0D1424';
    banner.style.backdropFilter = 'blur(12px)';
    banner.style.webkitBackdropFilter = 'blur(12px)';
    banner.style.borderTop = '1px solid rgba(56, 189, 248, 0.3)';
    banner.style.color = '#E2E8F0';
    banner.style.padding = '1.25rem 2rem';
    banner.style.zIndex = '999999';
    banner.style.boxShadow = '0 -10px 30px rgba(0,0,0,0.8)';
    banner.style.display = 'flex';
    banner.style.flexWrap = 'wrap';
    banner.style.alignItems = 'center';
    banner.style.justifyContent = 'space-between';
    banner.style.gap = '1rem';
    banner.style.fontSize = '0.9rem';

    banner.innerHTML = `
        <div style="flex: 1 1 500px;">
            <strong style="color:#E2E8F0; font-size:1rem;"><i class="fa-solid fa-shield-halved" style="color:#38BDF8; margin-right:0.5rem;"></i>Protección de Datos y Cookies en SGA-CD</strong>
            <p style="margin: 0.35rem 0 0 0; color: #94A3B8; line-height: 1.5;">
                Utilizamos cookies técnicas estrictamente necesarias para autenticación y funcionamiento del sistema SaaS.
                Los datos de estudiantes desde los 5 años están resguardados con acceso exclusivo para la institución, instructores asignados y padres/acudientes.
                Consulta nuestra <a href="privacy.html" style="color: #38BDF8; text-decoration: underline; font-weight:600;" target="_blank">Política de Privacidad</a> y <a href="terms.html" style="color: #38BDF8; text-decoration: underline; font-weight:600;" target="_blank">Términos</a>.
            </p>
        </div>
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; align-items:center;">
            <button id="accept-cookies-btn" class="cta-button" style="background: linear-gradient(135deg, #38BDF8 0%, #0284C7 100%); color: #070B14; border: none; padding: 0.65rem 1.4rem; border-radius: 8px; font-weight: 800; cursor: pointer; min-height: 44px; box-shadow: 0 4px 14px rgba(56, 189, 248, 0.3); transition: transform 0.25s ease, box-shadow 0.25s ease;">
                Aceptar Todo
            </button>
            <button id="reject-cookies-btn" style="background: rgba(255, 255, 255, 0.08); color: #E2E8F0; border: 1px solid rgba(56, 189, 248, 0.25); padding: 0.65rem 1.2rem; border-radius: 8px; cursor: pointer; min-height: 44px; font-weight: 600; transition: background 0.25s ease;">
                Sólo Esenciales
            </button>
        </div>
    `;

    document.body.appendChild(banner);

    document.getElementById('accept-cookies-btn').addEventListener('click', () => {
        localStorage.setItem('sgacd_cookie_consent', 'accepted_all');
        banner.remove();
    });

    document.getElementById('reject-cookies-btn').addEventListener('click', () => {
        localStorage.setItem('sgacd_cookie_consent', 'essential_only');
        banner.remove();
    });
}
