'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'react-toastify';
import { FaKey, FaSave, FaSpinner } from 'react-icons/fa';
import { FiInfo } from 'react-icons/fi';

interface ProviderOption {
  value: string;
  label: string;
}

interface LLMConfig {
  provider: string;
  api_key_saved: boolean;
  api_key_preview?: string;
  provider_options: ProviderOption[];
}

const LLMConfigForm: React.FC = () => {
  const { apiClient } = useAuth();

  const [config, setConfig] = useState<LLMConfig | null>(null);
  const [provider, setProvider] = useState<string>('');
  const [apiKey, setApiKey] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get<LLMConfig>('/config/my-llm/');
        setConfig(response.data);
        setProvider(response.data.provider);
      } catch (error) {
        toast.error('No se pudo cargar la configuración de IA. Inténtalo de nuevo.');
        console.error('Error fetching LLM config:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, [apiClient]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    const payload: { provider: string; api_key?: string } = { provider };
    // Solo envía la clave si el usuario ha escrito algo en el campo
    if (apiKey) {
      payload.api_key = apiKey;
    }

    try {
      const response = await apiClient.put<LLMConfig>('/config/my-llm/', payload);
      setConfig(response.data); // Actualiza el estado con la nueva configuración
      setProvider(response.data.provider);
      setApiKey(''); // Limpia el campo de la clave después de guardar
      toast.success('¡Configuración de IA guardada con éxito!');
    } catch (error) {
      toast.error('Ocurrió un error al guardar la configuración.');
      console.error('Error saving LLM config:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-10">
        <FaSpinner className="animate-spin text-4xl text-blue-500" />
        <p className="ml-4 text-lg text-gray-600 dark:text-gray-300">Cargando configuración...</p>
      </div>
    );
  }

  if (!config) {
    return <p className="text-red-500">No se pudo cargar la configuración.</p>;
  }

  const providerRequiresKey = provider === 'GROQ';

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="provider" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
          Proveedor de Modelo de Lenguaje
        </label>
        <select
          id="provider"
          name="provider"
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
        >
          {config.provider_options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
          Selecciona &apos;Usar Configuración del Sistema&apos; para utilizar el modelo híbrido por defecto.
        </p>
      </div>

      {providerRequiresKey && (
        <div>
          <label htmlFor="api-key" className="block text-sm font-medium text-gray-700 dark:text-gray-200">
            Clave de API de Groq
          </label>
          <div className="mt-1 relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FaKey className="text-gray-400" />
            </div>
            <input
              type="password"
              name="api-key"
              id="api-key"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Introduce una nueva clave solo para cambiarla"
            />
          </div>
          {config.api_key_saved && (
            <div className="mt-2 text-xs text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 p-2 rounded-md flex items-center">
              <FiInfo className="mr-2" />
              <span>
                Ya tienes una clave de API guardada. Introduce una nueva solo si deseas actualizarla.
              </span>
            </div>
          )}
        </div>
      )}

      <div className="flex justify-end pt-4">
        <button
          type="submit"
          disabled={saving}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
        >
          {saving ? (
            <FaSpinner className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
          ) : (
            <FaSave className="-ml-1 mr-2 h-5 w-5" />
          )}
          {saving ? 'Guardando...' : 'Guardar Cambios'}
        </button>
      </div>
    </form>
  );
};

export default LLMConfigForm;