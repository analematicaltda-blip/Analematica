 import api from './api';

// Interfaz para el prestador en el panel de admin
export interface PrestadorAdmin {
  id: number;
  nombre_negocio: string;
  usuario_email: string;
  categoria_nombre: string;
  aprobado: boolean;
  puntuacion: number;
}

// Interfaz genérica para un usuario en el panel de admin (prestador, artesano, etc.)
export interface UsuarioAdmin {
  id: number;
  username: string;
  nombre_display: string;
  role: string;
  rol_display: string;
}

/**
 * Obtiene la lista completa de prestadores de servicio para el panel de administración.
 */
export const getPrestadoresAdmin = async (): Promise<PrestadorAdmin[]> => {
  const response = await api.get('/admin/prestadores/');
  return response.data;
};

/**
 * Obtiene la lista de todos los usuarios relevantes (prestadores, artesanos) para la gestión.
 */
export const getUsuariosAdmin = async (): Promise<UsuarioAdmin[]> => {
    const response = await api.get('/admin/usuarios/');
    return response.data;
};