import api from './api';

export interface Atractivo {
  id?: number;
  slug?: string;
  nombre: string;
  descripcion: string;
  como_llegar?: string;
  latitud?: number;
  longitud?: number;
  categoria_color: 'AMARILLO' | 'ROJO' | 'BLANCO';
  imagen_principal?: FileList;
  imagen_principal_url?: string;
  horario_funcionamiento?: string;
  tarifas?: string;
  recomendaciones?: string;
  accesibilidad?: string;
  informacion_contacto?: string;
  es_publicado: boolean;
  autor_username?: string;
  department?: number;
  municipality?: number;
}

export const getMisAtractivos = async (): Promise<Atractivo[]> => {
    const response = await api.get<Atractivo[]>('/atractivos/');
    return response.data;
};

export const createAtractivo = async (data: FormData): Promise<Atractivo> => {
    const response = await api.post<Atractivo>('/atractivos/', data, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
};

export const updateAtractivo = async (slug: string, data: FormData): Promise<Atractivo> => {
    const response = await api.put<Atractivo>(`/atractivos/${slug}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
};

export const deleteAtractivo = async (slug: string): Promise<void> => {
    await api.delete(`/atractivos/${slug}/`);
};

export const approveAtractivo = async (slug: string): Promise<void> => {
    await api.post(`/atractivos/${slug}/approve/`);
};