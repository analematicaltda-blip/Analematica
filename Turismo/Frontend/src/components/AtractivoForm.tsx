"use client";

"use client";

import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { Atractivo, createAtractivo, updateAtractivo } from '@/services/atractivoService';
import { getDepartments, getMunicipalitiesByDepartment, Department, Municipality } from '@/services/locationService';
import Image from 'next/image';
import axios from 'axios';

interface AtractivoFormProps {
  atractivo?: Atractivo;
  onSuccess: () => void;
  onCancel: () => void;
}

const AtractivoForm: React.FC<AtractivoFormProps> = ({ atractivo, onSuccess, onCancel }) => {
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<Atractivo>({
    defaultValues: atractivo || { es_publicado: false }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(atractivo?.imagen_principal_url || null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);

  const selectedDepartment = watch('department');

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const data = await getDepartments();
        setDepartments(data);
      } catch (error) {
        console.error("Failed to fetch departments", error);
      }
    };
    fetchDepartments();
  }, []);

  useEffect(() => {
    if (selectedDepartment) {
      const fetchMunicipalities = async () => {
        try {
          const data = await getMunicipalitiesByDepartment(selectedDepartment);
          setMunicipalities(data);
        } catch (error) {
          console.error("Failed to fetch municipalities", error);
        }
      };
      fetchMunicipalities();
    } else {
      setMunicipalities([]);
    }
  }, [selectedDepartment]);

  useEffect(() => {
    reset(atractivo || { es_publicado: false });
    setPreview(atractivo?.imagen_principal_url || null);
  }, [atractivo, reset]);

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setPreview(URL.createObjectURL(file));
    }
  };

  const onSubmit: SubmitHandler<Atractivo> = async (data) => {
    setIsLoading(true);
    setServerError(null);

    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (key === 'imagen_principal') {
        if (value instanceof FileList && value.length > 0) {
          formData.append(key, value[0]);
        }
      } else if (value !== null && value !== undefined) {
        formData.append(key, String(value));
      }
    });

    try {
      if (atractivo?.slug) {
        await updateAtractivo(atractivo.slug, formData);
      } else {
        await createAtractivo(formData);
      }
      onSuccess();
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        setServerError(JSON.stringify(error.response.data) || 'Ocurrió un error inesperado.');
      } else {
        setServerError('Ocurrió un error inesperado.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white p-8 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800">{atractivo ? 'Editar' : 'Crear'} Atractivo Turístico</h2>

      {serverError && <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg">{serverError}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">Nombre del Atractivo</label>
          <input
            id="nombre"
            {...register('nombre', { required: 'El nombre es obligatorio' })}
            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
          {errors.nombre && <p className="mt-2 text-sm text-red-600">{errors.nombre.message}</p>}
        </div>
        <div>
          <label htmlFor="categoria_color" className="block text-sm font-medium text-gray-700">Categoría</label>
          <select
            id="categoria_color"
            {...register('categoria_color', { required: 'La categoría es obligatoria' })}
            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="BLANCO">Natural</option>
            <option value="AMARILLO">Cultural/Histórico</option>
            <option value="ROJO">Urbano/Parque</option>
          </select>
          {errors.categoria_color && <p className="mt-2 text-sm text-red-600">{errors.categoria_color.message}</p>}
        </div>
        <div>
          <label htmlFor="department" className="block text-sm font-medium text-gray-700">Departamento</label>
          <select
            id="department"
            {...register('department', { required: 'El departamento es obligatorio' })}
            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Seleccione un departamento</option>
            {departments.map(dep => (
              <option key={dep.id} value={dep.id}>{dep.name}</option>
            ))}
          </select>
          {errors.department && <p className="mt-2 text-sm text-red-600">{errors.department.message}</p>}
        </div>
        <div>
          <label htmlFor="municipality" className="block text-sm font-medium text-gray-700">Municipio</label>
          <select
            id="municipality"
            {...register('municipality', { required: 'El municipio es obligatorio' })}
            disabled={!selectedDepartment || municipalities.length === 0}
            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-200"
          >
            <option value="">Seleccione un municipio</option>
            {municipalities.map(mun => (
              <option key={mun.id} value={mun.id}>{mun.name}</option>
            ))}
          </select>
          {errors.municipality && <p className="mt-2 text-sm text-red-600">{errors.municipality.message}</p>}
        </div>
      </div>

      <div>
        <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">Descripción</label>
        <textarea
          id="descripcion"
          {...register('descripcion', { required: 'La descripción es obligatoria' })}
          rows={4}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
        {errors.descripcion && <p className="mt-2 text-sm text-red-600">{errors.descripcion.message}</p>}
      </div>

      <div>
        <label htmlFor="como_llegar" className="block text-sm font-medium text-gray-700">¿Cómo Llegar?</label>
        <textarea
          id="como_llegar"
          {...register('como_llegar')}
          rows={3}
          className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="horario_funcionamiento" className="block text-sm font-medium text-gray-700">Horario</label>
          <input id="horario_funcionamiento" {...register('horario_funcionamiento')} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm"/>
        </div>
        <div>
          <label htmlFor="tarifas" className="block text-sm font-medium text-gray-700">Tarifas</label>
          <input id="tarifas" {...register('tarifas')} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm"/>
        </div>
        <div>
          <label htmlFor="recomendaciones" className="block text-sm font-medium text-gray-700">Recomendaciones</label>
          <input id="recomendaciones" {...register('recomendaciones')} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm"/>
        </div>
        <div>
          <label htmlFor="accesibilidad" className="block text-sm font-medium text-gray-700">Accesibilidad</label>
          <input id="accesibilidad" {...register('accesibilidad')} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm"/>
        </div>
      </div>
      <div>
          <label htmlFor="informacion_contacto" className="block text-sm font-medium text-gray-700">Información de Contacto</label>
          <input id="informacion_contacto" {...register('informacion_contacto')} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm"/>
      </div>
       <div>
          <label htmlFor="ubicacion_mapa" className="block text-sm font-medium text-gray-700">Ubicación (lat,lng)</label>
          <input id="ubicacion_mapa" {...register('ubicacion_mapa')} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm"/>
      </div>

      <div>
        <label htmlFor="imagen_principal" className="block text-sm font-medium text-gray-700">Imagen Principal</label>
        <input
          id="imagen_principal"
          type="file"
          {...register('imagen_principal')}
          onChange={handleImageChange}
          className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100"
        />
        {preview && (
            <div className="mt-2">
                <p className="text-sm text-gray-500">Vista previa:</p>
                <Image src={preview} alt="Vista previa de la imagen" width={80} height={80} className="h-20 w-auto rounded-md object-cover" />
            </div>
        )}
      </div>

      <div className="flex justify-end space-x-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 disabled:bg-indigo-300"
        >
          {isLoading ? 'Guardando...' : (atractivo ? 'Actualizar Atractivo' : 'Crear Atractivo')}
        </button>
      </div>
    </form>
  );
};

export default AtractivoForm;