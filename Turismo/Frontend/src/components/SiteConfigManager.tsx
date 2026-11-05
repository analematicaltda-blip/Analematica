"use client";

import { useState, useEffect, useCallback, FormEvent } from 'react';
import { FiSettings } from 'react-icons/fi';
import { getSiteConfig, updateSiteConfig, SiteConfiguration } from '@/services/api';
import SaveButton from './SaveButton';

// Componente para un interruptor (toggle switch)
const ToggleSwitch = ({ label, checked, onChange, name }: { label: string; checked: boolean; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; name: string; }) => (
  <label htmlFor={name} className="flex items-center cursor-pointer">
    <div className="relative">
      <input type="checkbox" id={name} name={name} className="sr-only" checked={checked} onChange={onChange} />
      <div className={`block w-14 h-8 rounded-full ${checked ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
      <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${checked ? 'transform translate-x-6' : ''}`}></div>
    </div>
    <div className="ml-3 text-gray-700 font-medium">{label}</div>
  </label>
);


export default function SiteConfigManager() {
  const [config, setConfig] = useState<Partial<SiteConfiguration>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchConfig = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getSiteConfig();
      setConfig(data);
    } catch (err) {
      setError("No se pudo cargar la configuración del sitio.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await updateSiteConfig(config);
      setSuccess("¡Configuración guardada con éxito!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      const error = err as { response?: { data: unknown }, message: string };
      const errorMessage = error.response?.data ? JSON.stringify(error.response.data) : error.message;
      setError(`Error al guardar la configuración: ${errorMessage}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setConfig(prevConfig => ({
      ...prevConfig,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  if (isLoading) return <p className="text-center py-8 text-gray-500">Cargando configuración...</p>;
  if (error && !config.id) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center"><FiSettings className="mr-3" />Gestión de Configuración del Sitio</h2>
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Sección General */}
        <div className="p-6 bg-white rounded-lg shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-3">Configuración General</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="site_name" className="block text-sm font-medium text-gray-700">Nombre del Sitio</label>
              <input type="text" name="site_name" id="site_name" value={config.site_name || ''} onChange={handleChange} className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
            </div>
             <div>
              <label htmlFor="google_maps_api_key" className="block text-sm font-medium text-gray-700">Clave de API de Google Maps</label>
              <input type="password" name="google_maps_api_key" id="google_maps_api_key" value={config.google_maps_api_key || ''} onChange={handleChange} className="mt-1 w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" placeholder="************" />
            </div>
          </div>
        </div>

        {/* Sección de Activación de Módulos */}
        <div className="p-6 bg-white rounded-lg shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-3">Activación de Módulos Públicos</h3>
          <div className="space-y-5">
            <ToggleSwitch label="Modo Mantenimiento" name="maintenance_mode" checked={!!config.maintenance_mode} onChange={handleChange} />
            <ToggleSwitch label="Sección de Publicaciones" name="seccion_publicaciones_activa" checked={!!config.seccion_publicaciones_activa} onChange={handleChange} />
            <ToggleSwitch label="Sección de Atractivos Turísticos" name="seccion_atractivos_activa" checked={!!config.seccion_atractivos_activa} onChange={handleChange} />
            <ToggleSwitch label="Sección de Prestadores de Servicios" name="seccion_prestadores_activa" checked={!!config.seccion_prestadores_activa} onChange={handleChange} />
          </div>
        </div>

        <div className="flex justify-end items-center mt-8">
            {error && <p className="text-sm text-red-600 mr-4">{error}</p>}
            {success && <p className="text-sm text-green-600 mr-4">{success}</p>}
            <SaveButton isSaving={isSaving} />
        </div>
      </form>
    </div>
  );
}