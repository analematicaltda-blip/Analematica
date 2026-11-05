'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import api from '@/services/api';
import FormField from '@/components/ui/FormField';
import { Button } from '@/components/ui/Button';
import { FiSearch, FiUser, FiAward, FiMail } from 'react-icons/fi';

interface Guia {
  id: number;
  nombre_negocio: string; // En este caso, el nombre del guía
  descripcion: string;
  telefono: string;
  email_contacto: string;
  // Añadiríamos campos como 'especialidades' o 'idiomas' si el modelo los soportara
}

interface SearchFormData {
  search: string;
}

const GuiaCard = ({ guia }: { guia: Guia }) => (
  <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 text-center">
    <div className="mb-4">
      <FiUser className="mx-auto h-16 w-16 text-blue-500 bg-blue-100 rounded-full p-3" />
    </div>
    <h3 className="text-xl font-bold text-gray-900">{guia.nombre_negocio}</h3>
    <p className="text-gray-600 mt-2 line-clamp-3">{guia.descripcion || "Guía profesional con amplia experiencia en la región."}</p>
    <div className="mt-4 flex flex-col items-center text-sm space-y-2">
        {guia.email_contacto && (
            <div className="flex items-center text-gray-700">
                <FiMail className="mr-2" />
                <a href={`mailto:${guia.email_contacto}`} className="hover:underline">{guia.email_contacto}</a>
            </div>
        )}
        {guia.telefono && (
             <div className="flex items-center text-gray-700">
                <FiAward className="mr-2" />
                <span>Contacto: {guia.telefono}</span>
            </div>
        )}
    </div>
    <div className="mt-5">
        <Button>Contactar Guía</Button>
    </div>
  </div>
);

const GuiasPage = () => {
  const [guias, setGuias] = useState<Guia[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { register, handleSubmit } = useForm<SearchFormData>();

  const fetchGuias = useCallback(async (params = {}) => {
    setIsLoading(true);
    try {
      const response = await api.get('/prestadores/', {
          params: {
              ...params,
              categoria__slug: 'guias-de-turismo' // Filtro clave
          }
       });
      setGuias(response.data.results || response.data);
    } catch (error) {
      toast.error('Error al cargar los guías turísticos.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGuias();
  }, [fetchGuias]);

  const onSearch = (data: SearchFormData) => {
    const cleanedData = {
        nombre_negocio__icontains: data.search
    }
    fetchGuias(cleanedData);
  };

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Directorio de Guías Turísticos</h1>
        <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500">
          Conecta con guías expertos y descubre los secretos de Puerto Gaitán.
        </p>
      </header>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8 max-w-lg mx-auto">
        <form onSubmit={handleSubmit(onSearch)} className="flex items-center space-x-4">
          <div className="flex-grow">
            <FormField
              name="search"
              label=""
              register={register}
              errors={{}}
              placeholder="Buscar por nombre o especialidad..."
            />
          </div>
          <Button type="submit" className="flex items-center">
            <FiSearch className="mr-2 h-4 w-4" /> Buscar
          </Button>
        </form>
      </div>

      {isLoading ? (
        <div className="text-center">Cargando guías...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {guias.length > 0 ? (
            guias.map((guia) => (
              <GuiaCard key={guia.id} guia={guia} />
            ))
          ) : (
            <p className="md:col-span-4 text-center text-gray-500">No se encontraron guías con los criterios seleccionados.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default GuiasPage;