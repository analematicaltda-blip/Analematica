"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useMiNegocioApi } from '../../../hooks/useMiNegocioApi';

// Interfaz para tipar los datos del perfil recibidos de la API
interface PerfilData {
  nombre_comercial: string;
  telefono_principal: string;
  email_comercial: string;
  descripcion_corta: string;
  // Añadir otros campos del modelo si es necesario
}

export default function PerfilPage() {
  const { getPerfil, updatePerfil, isLoading, error } = useMiNegocioApi();

  const [formData, setFormData] = useState<PerfilData>({
    nombre_comercial: '',
    telefono_principal: '',
    email_comercial: '',
    descripcion_corta: '',
  });

  // Cargar los datos del perfil al montar el componente
  const cargarDatos = useCallback(async () => {
    const data = await getPerfil();
    if (data) {
      setFormData(data);
    }
  }, [getPerfil]);

  useEffect(() => {
    cargarDatos();
  }, [cargarDatos]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updatePerfil(formData);
  };

  if (isLoading && !formData.nombre_comercial) { // Condición de carga más robusta
    return <div className="p-8">Cargando perfil...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">Error al cargar el perfil: {error}</div>;
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Gestionar Mi Perfil</h1>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md max-w-2xl">
        <div className="space-y-6">
          <div>
            <label htmlFor="nombre_comercial" className="block text-sm font-medium text-gray-700">
              Nombre Comercial
            </label>
            <input
              type="text"
              name="nombre_comercial"
              id="nombre_comercial"
              value={formData.nombre_comercial}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="telefono_principal" className="block text-sm font-medium text-gray-700">
                Teléfono Principal
              </label>
              <input
                type="tel"
                name="telefono_principal"
                id="telefono_principal"
                value={formData.telefono_principal}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="email_comercial" className="block text-sm font-medium text-gray-700">
                Email Comercial
              </label>
              <input
                type="email"
                name="email_comercial"
                id="email_comercial"
                value={formData.email_comercial}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <div>
            <label htmlFor="descripcion_corta" className="block text-sm font-medium text-gray-700">
              Descripción Corta
            </label>
            <textarea
              name="descripcion_corta"
              id="descripcion_corta"
              value={formData.descripcion_corta}
              onChange={handleChange}
              rows={4}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
            <p className="mt-2 text-sm text-gray-500">
              Una breve descripción de tu negocio que será visible para los turistas.
            </p>
          </div>
        </div>

        <div className="mt-8 pt-5 border-t border-gray-200">
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="bg-blue-600 text-white px-4 py-2 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
            >
              {isLoading ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
