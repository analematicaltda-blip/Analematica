// SaritaUnificado/frontend/src/hooks/useApi.ts
import { useState, useEffect, useCallback } from 'react';
import api from '@/services/api'; // Usar la instancia centralizada de Axios
import { AxiosError } from 'axios';

// Definir una interfaz base que todos los objetos de la API deben cumplir
interface ApiObject {
  id: number;
}

// El hook ahora usa un tipo genérico T, que debe extender de ApiObject
export const useApi = <T extends ApiObject>(endpoint: string) => {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<AxiosError | null>(null);

  // Usar useCallback para memorizar la función y evitar re-renders innecesarios
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<{ results: T[] }>(endpoint); // Esperar una respuesta paginada
      setData(response.data.results);
      setError(null);
    } catch (e) {
      setError(e as AxiosError);
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const createItem = useCallback(async (item: Omit<T, 'id'>): Promise<T | null> => {
    try {
      const response = await api.post<T>(endpoint, item);
      setData(prevData => [...prevData, response.data]);
      return response.data;
    } catch (e) {
      setError(e as AxiosError);
      console.error("Error creating item:", e);
      return null;
    }
  }, [endpoint]);

  const updateItem = useCallback(async (id: number, updatedItem: Partial<Omit<T, 'id'>>): Promise<T | null> => {
    try {
      const response = await api.patch<T>(`${endpoint}${id}/`, updatedItem);
      setData(prevData => prevData.map(item => (item.id === id ? response.data : item)));
      return response.data;
    } catch (e) {
      setError(e as AxiosError);
      console.error("Error updating item:", e);
      return null;
    }
  }, [endpoint]);

  const deleteItem = useCallback(async (id: number): Promise<boolean> => {
    try {
      await api.delete(`${endpoint}${id}/`);
      setData(prevData => prevData.filter(item => item.id !== id));
      return true;
    } catch (e) {
      setError(e as AxiosError);
      console.error("Error deleting item:", e);
      return false;
    }
  }, [endpoint]);

  return { data, loading, error, fetchData, createItem, updateItem, deleteItem };
};
