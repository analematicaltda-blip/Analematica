/**
 * Network Interceptor - SGA-CD Global HTTP Error Interception & AgentShield ECC Hardening
 * Intercepts window.fetch calls for response.status >= 400, network drops, or security breaches (403, 429)
 */
(function() {
    if (window.__sga_network_interceptor_loaded) return;
    window.__sga_network_interceptor_loaded = true;

    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const url = (typeof args[0] === 'string') ? args[0] : (args[0] && args[0].url) || '';
        const options = args[1] || {};
        const isSilent = options.silent === true || (options.headers && (options.headers['X-Silent-Error'] || options.headers['x-silent-error']));
        const isBackgroundRequest = url.includes('/telemetry') || url.includes('/analytics') || url.includes('/health') || url.includes('/beacon') || url.includes('/api/website/content') || url.includes('/api/v1/public/events');

        try {
            const response = await originalFetch(...args);

            // AgentShield ECC Security Hardening: Intercepción ante sospecha de ciberataque o denegación (403 Forbidden, 429 Rate Limit)
            if ((response.status === 403 || response.status === 429) && !isSilent && !isBackgroundRequest) {
                console.warn(`[AgentShield ECC Security Interceptor] Potencial comportamiento anómalo detectado HTTP ${response.status} en: ${url}`);

                // Activar código unificado de brecha de seguridad y bloqueo temporal
                if (window.SGAErrorHandler && typeof window.SGAErrorHandler.handleSecurityBreach === 'function') {
                    window.SGAErrorHandler.handleSecurityBreach(response.status);
                } else if (window.SGAErrorHandler && typeof window.SGAErrorHandler.handleHTTPError === 'function') {
                    window.SGAErrorHandler.handleHTTPError(response.status);
                }
                return response;
            }

            if (!response.ok && response.status >= 400 && !isSilent && !isBackgroundRequest) {
                // Intercepción inmediata ante fallas HTTP de peticiones primarias de usuario
                if (window.SGAErrorHandler && typeof window.SGAErrorHandler.handleHTTPError === 'function') {
                    window.SGAErrorHandler.handleHTTPError(response.status);
                }
            }
            return response;
        } catch (error) {
            // Intercepción ante caídas críticas de red para peticiones primarias
            if (!isSilent && !isBackgroundRequest && window.SGAErrorHandler && typeof window.SGAErrorHandler.handleHTTPError === 'function') {
                window.SGAErrorHandler.handleHTTPError(503);
            }
            throw error;
        }
    };
})();
