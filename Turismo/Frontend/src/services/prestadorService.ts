import api from './api';

// Asumiendo que la categoría tiene un 'id' y 'slug'
interface Categoria {
    id: number;
    slug: string;
    nombre: string;
}

// Interfaz para el perfil del prestador
export interface PrestadorProfile {
  id: number;
  nombre_negocio: string;
  categoria: Categoria | null;
  // Añadir otros campos del perfil si son necesarios
}

/**
 * Obtiene el perfil del prestador de servicios para el usuario autenticado.
 */
export const getPrestadorProfile = async (): Promise<PrestadorProfile> => {
  const response = await api.get('/profile/prestador/');
  return response.data;
};