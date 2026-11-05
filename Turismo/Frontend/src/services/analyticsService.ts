import api from './api';

// --- Tipos de Datos para el Nuevo Dashboard de Analíticas ---

// Tarjetas de resumen
export interface SummaryCardData {
  value: string | number;
  label: string;
}

// Distribución de roles de usuario (para gráfico de torta)
export interface RoleDistributionData {
  role: string;
  name: string;
  value: number;
}

// Conteo por categoría (para gráficos de barras)
export interface CountByCategoryData {
  name: string;
  value: number;
}

// Evolución de registros (para gráfico de líneas)
export interface RegistrationOverTimeData {
  date: string;
  Prestadores: number;
  Artesanos: number;
  Turistas: number;
}

// Ranking de proveedores (para tablas)
export interface TopProviderData {
  nombre_negocio?: string; // Para Prestadores
  nombre_taller?: string;  // Para Artesanos
  puntuacion_total: number;
}

// Métricas adicionales
export interface AdditionalMetricData {
    value: number;
    label: string;
}

// Estructura completa de la respuesta de la API de analíticas
export interface AnalyticsData {
  summary_cards: {
    total_prestadores: SummaryCardData;
    total_artesanos: SummaryCardData;
    total_publicaciones: SummaryCardData;
    calificacion_promedio: SummaryCardData;
  };
  user_roles_distribution: RoleDistributionData[];
  providers_by_category: {
    prestadores: CountByCategoryData[];
    artesanos: CountByCategoryData[];
  };
  registration_over_time: RegistrationOverTimeData[];
  top_providers: {
    prestadores: TopProviderData[];
    artesanos: TopProviderData[];
  };
  additional_metrics: {
      capacitaciones_realizadas: AdditionalMetricData;
      prestadores_con_rnt: AdditionalMetricData;
  };
}

/**
 * Obtiene los datos completos y estructurados para el panel de análisis.
 * @returns Una promesa que se resuelve en el objeto AnalyticsData.
 */
export const getAnalyticsData = async (): Promise<AnalyticsData> => {
  try {
    const response = await api.get<AnalyticsData>('/dashboard/analytics/');
    return response.data;
  } catch (error) {
    // El error será manejado por el componente que llama a esta función.
    throw error;
  }
};