import { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

let requestCount = 0;
let lastReset = Date.now();
// Ajuste Fase Establecimiento: 300 req/min para evitar bloqueos en carga inicial de dashboards
const MAX_REQUESTS_PER_MINUTE = 300;

export const setupInterceptors = (httpClient: AxiosInstance) => {
  httpClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const now = Date.now();
      if (now - lastReset > 60000) {
        requestCount = 0;
        lastReset = now;
      }

      requestCount++;
      if (requestCount > MAX_REQUESTS_PER_MINUTE) {
        console.error('S-0.2: Bloqueo de Rate Limit preventivo en cliente activado.');
        return Promise.reject({
            status: 429,
            message: 'PROTECCIÓN SOBERANA: Frecuencia de peticiones excesiva. Acción contenida preventivamente en el cliente.',
            action: 'WAIT'
        });
      }

      if (typeof window !== 'undefined') {
        // Telemetría: Registrar tiempo de inicio
        config.metadata = { startTime: Date.now() };

        const token = localStorage.getItem('token') || localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Token ${token}`;
        }

        // Multi-tenant / Context headers (Fase 2: UCE Normalization)
        const tenantId = localStorage.getItem('activeCompanyId');
        if (tenantId) {
          config.headers['X-Tenant-ID'] = tenantId;
          config.headers['X-Company-ID'] = tenantId; // Retrocompatibilidad
        }

        const periodId = localStorage.getItem('activePeriodId');
        if (periodId) {
          config.headers['X-Accounting-Period'] = periodId;
        }
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  httpClient.interceptors.response.use(
    (response) => {
      // Telemetría: Calcular latencia del cliente
      const startTime = (response.config as any).metadata?.startTime;
      if (startTime) {
        const duration = Date.now() - startTime;
        if (duration > 1000) {
            console.warn(`S-0.3: Latencia elevada detectada en cliente: ${response.config.url} (${duration}ms)`);
        }
      }
      return response;
    },
    (error: AxiosError) => {
      const status = error.response?.status;

      if (status === 401) {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
          localStorage.removeItem('authToken');
          // Optional: redirect to login
          // window.location.href = '/dashboard/login';
        }
      }

      // Normalized error handling - Phase 4 Functional Language
      let functionalMessage = 'No fue posible completar esta acción por una interrupción en el flujo.';
      const backendMessage = (error.response?.data as any)?.detail || (error.response?.data as any)?.message;

      if (status === 401) functionalMessage = 'Su sesión ha expirado o requiere una nueva validación de autoridad.';
      if (status === 403) functionalMessage = 'Esta operación requiere un nivel de soberanía del que su perfil actual no dispone.';
      if (status === 404) functionalMessage = 'El recurso solicitado no fue localizado. El sistema sigue operativo.';
      if (status === 429) functionalMessage = 'Límite de peticiones excedido. El sistema ha detectado una frecuencia inusual y ha bloqueado temporalmente su acceso para prevenir abusos.';
      if (error.message.includes('timeout')) functionalMessage = 'El sistema no respondió a tiempo. Estamos registrando este evento para auditoría.';

      const normalizedError = {
        code: status || 500,
        message: functionalMessage,
        original: backendMessage,
        technical: error.message,
        action: status === 401 ? 'REAUTH' : 'RETRY'
      };

      return Promise.reject(normalizedError);
    }
  );
};
