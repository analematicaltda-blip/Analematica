/**
 * SGA-CD Phase 11 Vanguard Dynamic Island Engine
 * Controls glassmorphic alert notifications, security breach responses, and status mutations.
 */
(function() {
    if (window.SGADynamicIsland) return;

    class DynamicIslandEngine {
        constructor() {
            this.container = null;
            this.island = null;
            this.iconEl = null;
            this.textEl = null;
            this.activeTimer = null;

            this.init();
        }

        init() {
            if (document.getElementById('dynamic-island-container')) return;

            this.container = document.createElement('div');
            this.container.id = 'dynamic-island-container';

            this.island = document.createElement('div');
            this.island.className = 'dynamic-island';

            this.island.innerHTML = `
                <svg class="dynamic-island-icon" viewBox="0 0 24 24" aria-hidden="true">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <span class="dynamic-island-text">SGA-CD — Sistema Activo</span>
            `;

            this.container.appendChild(this.island);
            document.body.appendChild(this.container);

            this.iconEl = this.island.querySelector('.dynamic-island-icon');
            this.textEl = this.island.querySelector('.dynamic-island-text');
        }

        notify(options = {}) {
            const {
                message = 'SGA-CD Operativo',
                type = 'info', // 'info', 'success', 'warning', 'breach'
                duration = 4000
            } = options;

            if (!this.island) this.init();

            if (this.activeTimer) {
                clearTimeout(this.activeTimer);
                this.activeTimer = null;
            }

            this.textEl.textContent = message;
            this.island.classList.remove('alert-breach', 'expanded');

            let iconSvg = '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>';

            if (type === 'breach' || type === 'error') {
                this.island.classList.add('alert-breach', 'expanded');
                iconSvg = '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>';
            } else if (type === 'success') {
                this.island.classList.add('expanded');
                iconSvg = '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>';
            } else {
                this.island.classList.add('expanded');
            }

            this.iconEl.innerHTML = iconSvg;

            if (typeof gsap !== 'undefined') {
                gsap.fromTo(this.island,
                    { scale: 0.9, opacity: 0.8 },
                    { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(1.7)' }
                );
            }

            this.activeTimer = setTimeout(() => {
                this.collapse();
            }, duration);
        }

        collapse() {
            if (!this.island) return;
            this.island.classList.remove('expanded', 'alert-breach');
            this.textEl.textContent = 'SGA-CD — Sistema Activo';
            this.iconEl.innerHTML = '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>';

            if (typeof gsap !== 'undefined') {
                gsap.to(this.island, { scale: 1, opacity: 1, duration: 0.3, ease: 'power2.out' });
            }
        }
    }

    window.SGADynamicIsland = new DynamicIslandEngine();

    // Attach to global error handler if present
    document.addEventListener('DOMContentLoaded', () => {
        if (window.SGAErrorHandler) {
            const originalBreach = window.SGAErrorHandler.handleSecurityBreach;
            window.SGAErrorHandler.handleSecurityBreach = function(statusCode) {
                if (window.SGADynamicIsland) {
                    window.SGADynamicIsland.notify({
                        message: `ALERTA DE SEGURIDAD [STD-ERR-SECURITY-BREACH]: Código ${statusCode} interceptado.`,
                        type: 'breach',
                        duration: 6000
                    });
                }
                if (typeof originalBreach === 'function') {
                    originalBreach.call(window.SGAErrorHandler, statusCode);
                }
            };
        }
    });
})();
