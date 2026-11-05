import api from './api';

// --- Interfaces para Tipos de Datos ---

export interface Opcion {
  id?: number;
  texto_opcion: string;
  orden: number;
}

export interface Pregunta {
  id?: number;
  texto_pregunta: string;
  tipo_pregunta: 'TEXTO_CORTO' | 'TEXTO_LARGO' | 'NUMERO' | 'FECHA' | 'SELECCION_UNICA' | 'SELECCION_MULTIPLE';
  es_obligatoria: boolean;
  orden: number;
  opciones?: Opcion[];
}

export interface Formulario {
  id?: number;
  titulo: string;
  descripcion: string;
  es_publico: boolean;
  preguntas?: Pregunta[];
}

export interface Respuesta {
  [pregunta_id: string]: string | number | boolean | string[];
}

export interface RespuestaDetalle {
    id: number;
    pregunta: number;
    pregunta_texto: string;
    usuario_username: string;
    respuesta: Record<string, unknown>; // JSONField
    fecha_respuesta: string;
}

export interface RespuestaAgrupada {
  usuario_id: number;
  nombre_display: string;
  rol: string;
  fecha_ultima_respuesta: string | null;
  respuestas: RespuestaDetalle[];
}

// --- Funciones de Servicio ---

// FORMULARIOS

export const getFormularios = async (): Promise<Formulario[]> => {
  const response = await api.get('/formularios/');
  return response.data;
};

export const getFormularioDetalle = async (id: number): Promise<Formulario> => {
  const response = await api.get(`/formularios/${id}/`);
  return response.data;
};

export const createFormulario = async (data: Formulario): Promise<Formulario> => {
  const response = await api.post('/formularios/', data);
  return response.data;
};

export const updateFormulario = async (id: number, data: Formulario): Promise<Formulario> => {
  const response = await api.put(`/formularios/${id}/`, data);
  return response.data;
};

export const deleteFormulario = async (id: number): Promise<void> => {
  await api.delete(`/formularios/${id}/`);
};

// PREGUNTAS (Anidadas bajo formularios)

export const addPregunta = async (formId: number, pregunta: Pregunta): Promise<Pregunta> => {
  const response = await api.post(`/formularios/${formId}/preguntas/`, pregunta);
  return response.data;
};

export const updatePregunta = async (formId: number, preguntaId: number, pregunta: Pregunta): Promise<Pregunta> => {
  const response = await api.put(`/formularios/${formId}/preguntas/${preguntaId}/`, pregunta);
  return response.data;
};

export const deletePregunta = async (formId: number, preguntaId: number): Promise<void> => {
  await api.delete(`/formularios/${formId}/preguntas/${preguntaId}/`);
};

// RESPUESTAS

export const getRespuestasPorFormulario = async (formId: number): Promise<RespuestaAgrupada[]> => {
    const response = await api.get(`/formularios/${formId}/respuestas/`);
    return response.data;
};

export const submitRespuestas = async (formId: number, respuestas: Respuesta): Promise<{status: string}> => {
  const response = await api.post(`/formularios/${formId}/respuestas/`, { respuestas });
  return response.data;
};