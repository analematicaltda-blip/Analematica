import api from './api';

// --- Interfaces de TypeScript para el Módulo de Verificación ---

export interface ItemVerificacion {
  id: number;
  texto_requisito: string;
  puntaje: number;
  orden: number;
  es_obligatorio: boolean;
}

export interface PlantillaVerificacion {
  id: number;
  nombre: string;
  descripcion: string;
  categoria_prestador: number | null;
  items?: ItemVerificacion[]; // Opcional, para la vista de detalle
}

export interface RespuestaItemVerificacion {
  id: number;
  item_original_id: number;
  texto_requisito: string; // Para lectura
  puntaje: number; // Para lectura
  cumple: boolean;
  justificacion: string;
}

// Para enviar los datos al guardar
export interface RespuestaItemVerificacionWrite {
    item_original_id: number;
    cumple: boolean;
    justificacion: string;
}

export interface Verificacion {
  id: number;
  fecha_visita: string;
  puntaje_obtenido: number;
  observaciones_generales: string;
  recomendaciones: string;
  plantilla_usada: number;
  plantilla_nombre: string;
  prestador: number;
  prestador_nombre: string;
  funcionario_evaluador: number;
  funcionario_nombre: string;
  respuestas_items: RespuestaItemVerificacion[];
}

// Tipo para los datos que se envían al guardar la verificación
export interface GuardarVerificacionPayload {
  fecha_visita: string;
  observaciones_generales: string;
  recomendaciones: string;
  respuestas_items: RespuestaItemVerificacionWrite[];
}


// --- Funciones del Servicio de Verificación ---

/**
 * Obtiene la lista de todas las plantillas de verificación disponibles.
 * @returns Una promesa que se resuelve con un array de plantillas.
 */
export const getPlantillas = async (): Promise<PlantillaVerificacion[]> => {
  const response = await api.get('/plantillas-verificacion/');
  return response.data;
};

/**
 * Obtiene el detalle de una plantilla de verificación específica, incluyendo sus ítems.
 * @param id - El ID de la plantilla.
 * @returns Una promesa que se resuelve con el objeto de la plantilla.
 */
export const getPlantillaDetalle = async (id: number): Promise<PlantillaVerificacion> => {
    const response = await api.get(`/plantillas-verificacion/${id}/`);
    return response.data;
}

/**
 * Inicia una nueva verificación para un prestador usando una plantilla específica.
 * @param plantillaId - El ID de la plantilla a usar.
 * @param prestadorId - El ID del prestador a verificar.
 * @returns Una promesa que se resuelve con la nueva instancia de verificación creada.
 */
export const iniciarVerificacion = async (plantillaId: number, prestadorId: number): Promise<Verificacion> => {
  const response = await api.post('/verificaciones/iniciar/', {
    plantilla_id: plantillaId,
    prestador_id: prestadorId,
  });
  return response.data;
};

/**
 * Guarda (actualiza) una verificación existente con las respuestas del formulario.
 * @param id - El ID de la verificación a guardar.
 * @param data - Los datos del formulario, incluyendo las respuestas.
 * @returns Una promesa que se resuelve con la verificación actualizada.
 */
export const guardarVerificacion = async (id: number, data: GuardarVerificacionPayload): Promise<Verificacion> => {
  const response = await api.patch(`/verificaciones/${id}/`, data);
  return response.data;
};

/**
 * Obtiene la lista de todas las verificaciones.
 * Para funcionarios/admins, devuelve todas.
 * Para prestadores, el backend filtra y devuelve solo las suyas.
 * @returns Una promesa que se resuelve con un array de verificaciones.
 */
export const getVerificaciones = async (): Promise<Verificacion[]> => {
    const response = await api.get('/verificaciones/');
    return response.data;
}

/**
 * Obtiene el detalle completo de una verificación específica.
 * @param id - El ID de la verificación.
 * @returns Una promesa que se resuelve con el objeto de la verificación.
 */
export const getVerificacionDetalle = async (id: number): Promise<Verificacion> => {
    const response = await api.get(`/verificaciones/${id}/`);
    return response.data;
}