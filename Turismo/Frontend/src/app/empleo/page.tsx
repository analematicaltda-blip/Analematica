'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { toast } from 'react-toastify';
import api from '@/services/api';
import FormField from '@/components/ui/FormField';
import { Button } from '@/components/ui/Button';
import { FiSearch, FiMapPin, FiClock, FiDollarSign } from 'react-icons/fi';

interface Vacante {
  id: number;
  titulo: string;
  descripcion: string;
  tipo_contrato: string;
  ubicacion: string;
  salario: string | null;
  fecha_publicacion: string;
  empresa_nombre: string;
}

interface SearchFormData {
  search: string;
  ubicacion: string;
  tipo_contrato: string;
}

const VacanteCard = ({ vacante }: { vacante: Vacante }) => (
  <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
    <h3 className="text-xl font-bold text-blue-700">{vacante.titulo}</h3>
    <p className="text-md font-semibold text-gray-800 mt-1">{vacante.empresa_nombre}</p>
    <div className="flex items-center text-gray-500 text-sm mt-2">
      <FiMapPin className="mr-2" />
      <span>{vacante.ubicacion}</span>
    </div>
    <p className="text-gray-600 mt-4 line-clamp-3">{vacante.descripcion}</p>
    <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center text-gray-700">
            <FiClock className="mr-2" />
            <span>{vacante.tipo_contrato.replace(/_/g, ' ')}</span>
        </div>
        {vacante.salario && (
            <div className="flex items-center text-gray-700">
                <FiDollarSign className="mr-2" />
                <span>{vacante.salario}</span>
            </div>
        )}
    </div>
    <div className="mt-5">
        <Button>Ver Detalles</Button>
    </div>
  </div>
);

const EmpleoPage = () => {
  const [vacantes, setVacantes] = useState<Vacante[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { register, handleSubmit, reset } = useForm<SearchFormData>();

  const fetchVacantes = useCallback(async (params = {}) => {
    setIsLoading(true);
    try {
      const response = await api.get('/empleo/vacantes/', { params });
      setVacantes(response.data.results || response.data);
    } catch (error) {
      toast.error('Error al cargar las oportunidades de empleo.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchVacantes();
  }, [fetchVacantes]);

  const onSearch = (data: SearchFormData) => {
    const cleanedData = Object.fromEntries(
        Object.entries(data).filter(([_, v]) => v != null && v !== '')
    );
    fetchVacantes(cleanedData);
  };

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">Portal de Empleo</h1>
        <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500">
          Encuentra tu próxima oportunidad profesional en el corazón de Puerto Gaitán.
        </p>
      </header>

      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <form onSubmit={handleSubmit(onSearch)} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div className="md:col-span-2">
            <FormField
              name="search"
              label="Buscar por palabra clave"
              register={register}
              errors={{}}
              placeholder="Ej: Mesero, Recepcionista..."
            />
          </div>
          <div>
            <FormField
              name="ubicacion"
              label="Ubicación"
              register={register}
              errors={{}}
              placeholder="Ej: Puerto Gaitán"
            />
          </div>
          <div className="flex space-x-2">
            <Button type="submit" className="w-full flex justify-center">
              <FiSearch className="mr-2" /> Buscar
            </Button>
             <Button type="button" variant="outline" onClick={() => { reset(); fetchVacantes(); }}>
                Limpiar
            </Button>
          </div>
        </form>
      </div>

      {isLoading ? (
        <div className="text-center">Cargando vacantes...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {vacantes.length > 0 ? (
            vacantes.map((vacante) => (
              <VacanteCard key={vacante.id} vacante={vacante} />
            ))
          ) : (
            <p className="md:col-span-3 text-center text-gray-500">No se encontraron vacantes con los criterios seleccionados.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default EmpleoPage;