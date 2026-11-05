 'use client';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { FiKey, FiSave, FiLoader, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// --- Type Definitions ---
interface KeysStatus {
  openai_api_key: string; // "Configurada" o "No configurada"
  google_api_key: string;
}

// --- Helper Components ---
const ApiKeyInput: React.FC<{
  id: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
  status: string;
  placeholder: string;
}> = ({ id, value, onChange, label, status, placeholder }) => (
  <div>
    <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
      {label}
      <span
        className={`ml-2 text-xs font-semibold px-2 py-0.5 rounded-full ${
          status === 'Configurada'
            ? 'bg-green-100 text-green-800'
            : 'bg-gray-100 text-gray-600'
        }`}
      >
        {status}
      </span>
    </label>
    <div className="relative">
      <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
        <FiKey />
      </span>
      <input
        type="password"
        id={id}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="pl-10 pr-4 py-2.5 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all"
        autoComplete="new-password"
      />
    </div>
  </div>
);

// --- Main Component ---
export default function LLMKeysManager() {
  const { token } = useAuth();
  const [status, setStatus] = useState<KeysStatus | null>(null);
  const [openaiKey, setOpenaiKey] = useState('');
  const [googleKey, setGoogleKey] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchKeysStatus = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/llm-keys/`, {
        headers: { Authorization: `Token ${token}` },
      });
      setStatus(response.data);
    } catch {
      setError('No se pudo cargar el estado de las claves de API.');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchKeysStatus();
  }, [fetchKeysStatus]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    const payload: { openai_api_key?: string; google_api_key?: string } = {};
    if (openaiKey) payload.openai_api_key = openaiKey;
    if (googleKey) payload.google_api_key = googleKey;

    if (Object.keys(payload).length === 0) {
      setError('No has introducido ninguna clave nueva para guardar.');
      setIsSaving(false);
      return;
    }

    try {
      await axios.patch(`${API_BASE_URL}/llm-keys/`, payload, {
        headers: { Authorization: `Token ${token}` },
      });
      setSuccess('¡Claves actualizadas con éxito!');
      setOpenaiKey('');
      setGoogleKey('');
      await fetchKeysStatus();
      setTimeout(() => setSuccess(null), 5000);
    } catch {
      setError('Error al guardar las claves. Por favor, inténtalo de nuevo.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading)
    return (
      <div className="flex justify-center items-center p-8">
        <FiLoader className="animate-spin h-8 w-8 text-blue-600" />
        <p className="ml-4">Cargando...</p>
      </div>
    );

  if (error && !status)
    return <p className="text-red-500 text-center p-8">{error}</p>;

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 mt-8 font-sans">
      <h2 className="text-xl font-bold text-gray-800 mb-2">
        Gestión de Claves de API (LLM)
      </h2>
      <p className="text-sm text-gray-600 mb-6">
        Introduce tus claves de API para habilitar las funcionalidades de
        inteligencia artificial. Las claves se guardan de forma segura y
        encriptada.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ApiKeyInput
            id="openai_api_key"
            value={openaiKey}
            onChange={(e) => setOpenaiKey(e.target.value)}
            label="OpenAI API Key"
            status={status?.openai_api_key || 'No configurada'}
            placeholder="Introduce una nueva clave para actualizar"
          />
          <ApiKeyInput
            id="google_api_key"
            value={googleKey}
            onChange={(e) => setGoogleKey(e.target.value)}
            label="Google API Key"
            status={status?.google_api_key || 'No configurada'}
            placeholder="Introduce una nueva clave para actualizar"
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-gray-200">
          <div className="w-full sm:w-auto">
            {success && (
              <div className="flex items-center gap-2 text-green-600 font-semibold text-sm">
                <FiCheckCircle /> {success}
              </div>
            )}
            {error && (
              <div className="flex items-center gap-2 text-red-600 font-semibold text-sm">
                <FiAlertCircle /> {error}
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={isSaving}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 transition-all transform hover:scale-105"
          >
            {isSaving ? (
              <FiLoader className="animate-spin h-5 w-5" />
            ) : (
              <FiSave className="h-5 w-5" />
            )}
            {isSaving ? 'Guardando...' : 'Guardar Claves'}
          </button>
        </div>
      </form>
    </div>
  );
}