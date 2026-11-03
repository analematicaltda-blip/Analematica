/**
 * SGAErrorHandler - Centralized Error Handling Component & AgentShield ECC Security Engine
 * SGA-CD Architecture - Dark Metallic Blue (60-30-10)
 */
window.SGAErrorHandler = (function() {
    // Official HTTP Error Catalog (11 Codes + Security Breach)
    const ERROR_CATALOG = {
        400: {
            code: 'STD-ERR-400',
            title: 'Petición Incorrecta',
            message: 'La solicitud enviada contiene datos no válidos. Por favor verifica la información ingresada en la inscripción de disciplinas deportivas o talleres culturales.',
            action: 'Entendido'
        },
        401: {
            code: 'STD-ERR-401',
            title: 'Sesión No Autorizada',
            message: 'Tu sesión ha expirado o no cuentas con autenticación válida. Reingresa al sistema para continuar gestionando tus modalidades culturales y registros deportivos.',
            action: 'Iniciar Sesión'
        },
        403: {
            code: 'STD-ERR-403',
            title: 'Acceso Restringido',
            message: 'No posees los permisos necesarios para acceder a este módulo institucional de disciplinas deportivas o talleres.',
            action: 'Volver al Inicio'
        },
        404: {
            code: 'STD-ERR-404',
            title: 'Recurso No Encontrado',
            message: 'La ruta o módulo solicitado no está disponible. Verifica el enlace o regresa al panel principal para explorar las disciplinas deportivas y talleres culturales habilitados.',
            action: 'Volver al Inicio'
        },
        405: {
            code: 'STD-ERR-405',
            title: 'Método No Permitido',
            message: 'La operación solicitada no está permitida en este servidor para la gestión de modalidades culturales.',
            action: 'Cerrar'
        },
        408: {
            code: 'STD-ERR-408',
            title: 'Tiempo de Espera Agotado',
            message: 'La solicitud tardó demasiado en responder. Por favor verifica tu conexión a red e intenta cargar de nuevo el catálogo de talleres y disciplinas deportivas.',
            action: 'Reintentar'
        },
        429: {
            code: 'STD-ERR-429',
            title: 'Límite de Solicitudes Excedido',
            message: 'Has realizado demasiadas peticiones en un corto período. Por favor espera unos momentos antes de interactuar nuevamente con las plataformas de formación.',
            action: 'Entendido'
        },
        500: {
            code: 'STD-ERR-500',
            title: 'Error Interno del Servidor',
            message: 'Ocurrió una falla imprevista en la plataforma central. El equipo técnico ha sido notificado para resguardar la información de disciplinas deportivas y modalidades culturales.',
            action: 'Entendido'
        },
        502: {
            code: 'STD-ERR-502',
            title: 'Puerta de Enlace Inválida',
            message: 'Se recibió una respuesta no válida del servidor intermedio. Intentando restablecer el enlace con la base de datos de talleres y deportes.',
            action: 'Reintentar'
        },
        503: {
            code: 'STD-ERR-503',
            title: 'Servicio No Disponible',
            message: 'El servicio se encuentra temporalmente en mantenimiento o sin conectividad de red. Si estás desconectado, puedes seguir registrado mediante la asistencia offline PWA.',
            action: 'Aceptar'
        },
        504: {
            code: 'STD-ERR-504',
            title: 'Tiempo de Espera de la Puerta de Enlace',
            message: 'El servidor principal no respondió a tiempo. Por favor verifica tu conectividad e intenta nuevamente la sincronización de modalidades culturales.',
            action: 'Reintentar'
        }
    };

    function escapeHTML(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function createOverlay() {
        let overlay = document.getElementById('sga-error-modal-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'sga-error-modal-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(7, 11, 20, 0.85);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                z-index: 999999;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                pointer-events: none;
                transition: none;
            `;

            const card = document.createElement('div');
            card.id = 'sga-error-modal-card';
            card.style.cssText = `
                background: #0D1424;
                border: 1px solid rgba(56, 189, 248, 0.3);
                box-shadow: 0 0 30px rgba(56, 189, 248, 0.15), inset 0 0 15px rgba(56, 189, 248, 0.05);
                border-radius: 16px;
                padding: 32px 28px;
                max-width: 480px;
                width: 90%;
                text-align: center;
                color: #E2E8F0;
                transform: translate3d(0, 30px, 0);
                will-change: transform, opacity;
            `;

            card.innerHTML = `
                <div style="display:inline-block; padding: 6px 14px; background: rgba(56,189,248,0.1); border: 1px solid rgba(56,189,248,0.3); border-radius: 20px; color: #38BDF8; font-size: 12px; font-weight: 700; font-family: monospace; letter-spacing: 1px; margin-bottom: 16px;" id="sga-error-code">
                    STD-ERR-500
                </div>
                <h3 id="sga-error-title" style="margin: 0 0 12px 0; color: #FFFFFF; font-size: 22px; font-weight: 700; font-family: system-ui, -apple-system, sans-serif;">
                    Error
                </h3>
                <p id="sga-error-message" style="margin: 0 0 24px 0; color: #94A3B8; font-size: 14px; line-height: 1.6; font-family: system-ui, -apple-system, sans-serif;">
                    Ha ocurrido un inconveniente.
                </p>
                <button id="sga-error-btn" style="
                    background: #38BDF8;
                    color: #070B14;
                    font-weight: 700;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 28px;
                    font-size: 15px;
                    cursor: pointer;
                    min-height: 44px;
                    min-width: 120px;
                    box-shadow: 0 0 15px rgba(56,189,248,0.4);
                    transition: transform 0.2s ease, background-color 0.2s ease;
                ">
                    Aceptar
                </button>
            `;

            overlay.appendChild(card);
            document.body.appendChild(overlay);

            document.getElementById('sga-error-btn').addEventListener('click', function() {
                window.SGAErrorHandler.hide();
            });
        }
        return overlay;
    }

    return {
        handleSecurityBreach: function(status) {
            console.error(`[AgentShield Security Incident]: STD-ERR-SECURITY-BREACH registrado ante status ${status}`);
            this.show({
                code: 'STD-ERR-SECURITY-BREACH',
                title: 'Alerta de Seguridad Perimetral AgentShield',
                message: 'Se ha detectado una anomalía de red o intento de acceso masivo. Tu sesión ha sido bloqueada temporalmente para proteger tus datos de disciplinas deportivas y talleres.',
                actionText: 'Reiniciar Sesión',
                status: status,
                isBreach: true
            });
        },

        handleHTTPError: function(status, customMsg) {
            if (status === 403 || status === 429) {
                this.handleSecurityBreach(status);
                return;
            }

            const errInfo = ERROR_CATALOG[status] || {
                code: `STD-ERR-${status}`,
                title: 'Error HTTP ' + status,
                message: customMsg || 'Se ha detectado una respuesta no esperada del servidor. Consulta el panel de disciplinas deportivas y talleres.',
                action: 'Aceptar'
            };

            this.show({
                code: errInfo.code,
                title: errInfo.title,
                message: customMsg || errInfo.message,
                actionText: errInfo.action,
                status: status
            });
        },

        show: function(opts) {
            const overlay = createOverlay();
            const card = document.getElementById('sga-error-modal-card');
            const codeEl = document.getElementById('sga-error-code');
            const titleEl = document.getElementById('sga-error-title');
            const msgEl = document.getElementById('sga-error-message');
            const btnEl = document.getElementById('sga-error-btn');

            codeEl.textContent = escapeHTML(opts.code || 'STD-ERR-UNKNOWN');
            titleEl.textContent = escapeHTML(opts.title || 'Inconveniente del Sistema');
            msgEl.textContent = escapeHTML(opts.message || 'Se ha producido una novedad en el sistema SGA-CD.');
            btnEl.textContent = escapeHTML(opts.actionText || 'Aceptar');

            overlay.style.pointerEvents = 'auto';

            if (window.gsap) {
                gsap.killTweensOf([overlay, card]);
                gsap.set(overlay, { opacity: 0 });
                gsap.set(card, { transform: 'translate3d(0, 30px, 0)', opacity: 0 });

                gsap.to(overlay, {
                    opacity: 1,
                    duration: 0.25,
                    ease: 'power2.out'
                });
                gsap.to(card, {
                    transform: 'translate3d(0, 0px, 0)',
                    opacity: 1,
                    duration: 0.35,
                    ease: 'back.out(1.2)'
                });
            } else {
                overlay.style.opacity = '1';
                card.style.transform = 'translate3d(0, 0px, 0)';
                card.style.opacity = '1';
            }

            if (opts.status === 401 || opts.isBreach) {
                btnEl.onclick = function() {
                    window.SGAErrorHandler.hide();
                    try {
                        sessionStorage.clear();
                        localStorage.removeItem('sga_access_token');
                    } catch(e) {}
                    if (window.location.pathname !== '/login.html') {
                        window.location.href = '/login.html';
                    }
                };
            } else {
                btnEl.onclick = function() {
                    window.SGAErrorHandler.hide();
                };
            }
        },

        hide: function() {
            const overlay = document.getElementById('sga-error-modal-overlay');
            const card = document.getElementById('sga-error-modal-card');
            if (!overlay) return;

            if (window.gsap) {
                gsap.to(card, {
                    transform: 'translate3d(0, 20px, 0)',
                    opacity: 0,
                    duration: 0.2,
                    ease: 'power2.in'
                });
                gsap.to(overlay, {
                    opacity: 0,
                    duration: 0.25,
                    ease: 'power2.in',
                    onComplete: function() {
                        overlay.style.pointerEvents = 'none';
                    }
                });
            } else {
                overlay.style.opacity = '0';
                overlay.style.pointerEvents = 'none';
            }
        }
    };
})();
