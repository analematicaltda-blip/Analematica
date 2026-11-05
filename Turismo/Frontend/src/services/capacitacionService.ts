import api from './api';
import { Publicacion } from './publicacionService'; // Asumiendo que existe un servicio de publicaciones

// --- Interfaces de TypeScript para el Módulo de Capacitaciones ---

export interface Asistencia {
    id: number;
    usuario: number;
    usuario_nombre: string;
    usuario_rol: string;
    fecha_asistencia: string;
}

// Extiende la interfaz de Publicacion para incluir los campos de capacitación
export interface Capacitacion extends Publicacion {
    puntos_asistencia: number;
    asistentes: Asistencia[];
}

/**
 * Obtiene la lista de todas las publicaciones de tipo 'CAPACITACION'.
 * @returns Una promesa que se resuelve con un array de capacitaciones.
 */
export const getCapacitaciones = async (): Promise<Publicacion[]> => {
    // El endpoint de publicaciones se filtra por tipo en el backend,
    // aquí asumimos que el componente que llama pasará los query params.
    // O podemos crear un endpoint específico si se prefiere.
    // Por ahora, usamos el endpoint general y recomendamos filtrar en el componente.
    const response = await api.get('/admin/publicaciones/', {
        params: { tipo: 'CAPACITACION' }
    });
    return response.data;
};

/**
 * Obtiene el detalle completo de una capacitación específica, incluyendo sus asistentes.
 * @param id - El ID de la publicación (capacitación).
 * @returns Una promesa que se resuelve con el objeto de la capacitación.
 */
export const getCapacitacionDetalle = async (id: number): Promise<Capacitacion> => {
    const response = await api.get(`/admin/publicaciones/${id}/`);
    return response.data;
};

interface AsistenciaResponse {
    status: string;
    message: string;
}

/**
 * Registra la asistencia de múltiples usuarios a una capacitación.
 * @param id - El ID de la capacitación.
 * @param asistentesIds - Un array con los IDs de los usuarios que asistieron.
 * @returns Una promesa que se resuelve con el resultado de la operación.
 */
export const registrarAsistencia = async (id: number, asistentesIds: number[]): Promise<AsistenciaResponse> => {
    const response = await api.post(`/admin/publicaciones/${id}/registrar-asistencia/`, {
        asistentes_ids: asistentesIds,
    });
    return response.data;
};