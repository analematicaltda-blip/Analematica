import httpClient from './httpClient';

const api = httpClient;

export default api;

// --- Tipos y Funciones ---

export interface Categoria {
    id: number;
    nombre: string;
    slug: string;
}

export interface PrestadorPublico {
    id: number;
    nombre_negocio: string;
    categoria_nombre: string;
    foto_principal: string | null;
    municipio_nombre: string;
}

export interface PrestadorPublicoDetalle extends PrestadorPublico {
    descripcion: string;
    telefono_contacto: string;
    email_contacto: string;
    direccion: string;
    latitud: number | null;
    longitud: number | null;
}

export interface Location {
    id: number;
    latitud: number;
    longitud: number;
    nombre: string;
}

export interface FacturaVenta {
    id: string;
    number: string;
    cliente_nombre: string;
    issue_date: string;
    total: string;
    estado_display: string;
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export const getCategorias = async (): Promise<Categoria[]> => {
    const response = await api.get('/public/artesanos/rubros/');
    return response.data?.data;
};

export const getPrestadores = async (categoria?: string, search?: string): Promise<PrestadorPublico[]> => {
    const response = await api.get('/public/artesanos/', { params: { categoria, search } });
    return response.data?.data;
};

export const getPrestadorById = async (id: number): Promise<PrestadorPublicoDetalle> => {
    const response = await api.get(`/public/artesanos/${id}/`);
    return response.data?.data;
};

export const getLocations = async (): Promise<Location[]> => {
    const response = await api.get('/public/locations/');
    return response.data?.data;
};

// --- RESTAURACIÓN DE FUNCIONES PARA COMPATIBILIDAD ---

export const getCaracterizacionByPrestadorId = async (id: number) => api.get(`/admin/caracterizacion/?prestador=${id}`).then(res => res.data);
export const getAgroturismoCaracterizacionByPrestadorId = async (id: number) => api.get(`/admin/caracterizacion-agroturismo/?prestador=${id}`).then(res => res.data);
export const getGuiaCaracterizacionByPrestadorId = async (id: number) => api.get(`/admin/caracterizacion-guia/?prestador=${id}`).then(res => res.data);

export const updateCaracterizacion = async (id: number, data: any) => api.patch(`/admin/caracterizacion/${id}/`, data);
export const createCaracterizacion = async (data: any) => api.post(`/admin/caracterizacion/`, data);

export const updateAgroturismoCaracterizacion = async (id: number, data: any) => api.patch(`/admin/caracterizacion-agroturismo/${id}/`, data);
export const createAgroturismoCaracterizacion = async (data: any) => api.post(`/admin/caracterizacion-agroturismo/`, data);

export const updateGuiaCaracterizacion = async (id: number, data: any) => api.patch(`/admin/caracterizacion-guia/${id}/`, data);
export const createGuiaCaracterizacion = async (data: any) => api.post(`/admin/caracterizacion-guia/`, data);

export const getAdminPublicaciones = async () => api.get('/admin/publicaciones/').then(res => res.data);
export const approvePublicacion = async (id: number) => api.post(`/admin/publicaciones/${id}/approve/`);
export const deleteAdminPublicacion = async (id: number) => api.delete(`/admin/publicaciones/${id}/`);

export const getSiteConfig = async () => api.get('/config/site-config/').then(res => res.data);
export const updateSiteConfig = async (data: any) => api.patch('/config/site-config/', data);

export const getStatistics = async () => api.get('/dashboard/analytics/').then(res => res.data);

export const getUsers = async () => api.get('/admin/users/').then(res => res.data);
export const createUser = async (data: any) => api.post('/admin/users/', data);
export const updateUser = async (id: number, data: any) => api.patch(`/admin/users/${id}/`, data);
export const deleteUser = async (id: number) => api.delete(`/admin/users/${id}/`);

export const getPaginaInstitucional = async (slug: string) => api.get(`/paginas-institucionales/${slug}/`).then(res => res.data);

export const getArtesanoCaracterizacionByArtesanoId = async (id: number) => api.get(`/admin/artesanos/${id}/caracterizacion/`).then(res => res.data);
export const updateArtesanoCaracterizacion = async (id: number, data: any) => api.patch(`/admin/artesanos/caracterizacion/${id}/`, data);
export const createArtesanoCaracterizacion = async (data: any) => api.post(`/admin/artesanos/caracterizacion/`, data);

export const getPublicHabitaciones = async (prestadorId: number) => api.get(`/prestadores/${prestadorId}/habitaciones/`).then(res => res.data);
export const getPublicDisponibilidad = async (prestadorId: number, params: any) => api.get(`/prestadores/${prestadorId}/disponibilidad/`, { params }).then(res => res.data);

export const getRutasTuristicas = async () => api.get('/rutas-turisticas/').then(res => res.data);
export const getRutaTuristicaBySlug = async (slug: string) => api.get(`/rutas-turisticas/${slug}/`).then(res => res.data);

export const getGaleriaMedia = async () => api.get('/galeria-media/').then(res => res.data);
export const getPublicaciones = async (params?: any) => api.get('/publicaciones/', { params }).then(res => res.data);
export const getHechosHistoricos = async () => api.get('/hechos-historicos/').then(res => res.data);

export const getArtesanos = async () => api.get('/artesanos/').then(res => res.data);
export const getArtesanoById = async (id: number) => api.get(`/artesanos/${id}/`).then(res => res.data);
export const getRubrosArtesano = async () => api.get('/artesanos/rubros/').then(res => res.data);

// --- Infraestructura y Observabilidad (Fase 8) ---
export const getInfraMetrics = async () => api.get('/v1/infra/metrics/').then(res => res.data);
export const getInfraHealth = async () => api.get('/v1/infra/health/readiness/').then(res => res.data);

export const useApi = () => ({ api });
