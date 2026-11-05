"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import Link from 'next/link';
import Image from 'next/image';
import { useForm } from 'react-hook-form';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { FiSave, FiArrowLeft } from 'react-icons/fi';

// Interfaces
interface AtractivoForm {
  nombre: string;
  slug: string;
  descripcion: string;
  como_llegar: string;
  ubicacion_mapa: string;
  categoria_color: 'AMARILLO' | 'ROJO' | 'BLANCO';
  imagen_principal?: File | null;
  horario_funcionamiento: string;
  tarifas: string;
  recomendaciones: string;
  accesibilidad: string;
  informacion_contacto: string;
  es_publicado: boolean;
}

const AtractivoEditPage = () => {
  const { token } = useAuth();
  const router = useRouter();
  const params = useParams();
  const slug = params.slug;
  const isCreating = slug === 'crear';

  const [isLoading, setIsLoading] = useState(!isCreating);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<AtractivoForm>();

  const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    headers: { 'Authorization': `Token ${token}` },
  });

  const fetchAtractivo = useCallback(async (atractivoSlug: string) => {
    try {
      const response = await apiClient.get(`/atractivos/${atractivoSlug}/`);
      const data = response.data;
      reset(data); // Cargar datos en el formulario
      if (data.imagen_principal_url) {
        setImagePreview(data.imagen_principal_url);
      }
    } catch (error) {
      toast.error("No se pudo cargar el atractivo turístico.");
    } finally {
      setIsLoading(false);
    }
  }, [apiClient, reset]);

  useEffect(() => {
    if (!isCreating && typeof slug === 'string' && token) {
      fetchAtractivo(slug);
    }
  }, [slug, token, isCreating, fetchAtractivo]);

  const onSubmit = async (data: AtractivoForm) => {
    setIsSubmitting(true);
    const formData = new FormData();

    // Convertir el objeto de datos a FormData
    for (const key in data) {
        const value = data[key as keyof AtractivoForm];
        if (key === 'imagen_principal') {
            if (value instanceof File) {
                formData.append(key, value);
            }
        } else if (value !== null && value !== undefined) {
            formData.append(key, value.toString());
        }
    }

    try {
      const url = isCreating ? '/atractivos/' : `/atractivos/${slug}/`;
      const method = isCreating ? 'post' : 'patch';

      await apiClient({ method, url, data: formData, headers: { 'Content-Type': 'multipart/form-data' } });

      toast.success(`Atractivo ${isCreating ? 'creado' : 'actualizado'} con éxito.`);
      router.push('/dashboard/atractivos');
    } catch (error) {
      toast.error("Hubo un error al guardar el atractivo.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setValue('imagen_principal', file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  if (isLoading) return <p>Cargando atractivo...</p>;

  return (
    <div className="container mx-auto">
      <ToastContainer />
      <Link href="/dashboard/atractivos" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
        <FiArrowLeft className="mr-2" />
        Volver a Atractivos
      </Link>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        {isCreating ? 'Crear Nuevo Atractivo Turístico' : 'Editar Atractivo Turístico'}
      </h1>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-8 rounded-lg shadow-md space-y-6">
        {/* Nombre y Slug */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">Nombre</label>
            <input type="text" id="nombre" {...register('nombre', { required: 'El nombre es obligatorio' })} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
            {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
          </div>
          <div>
            <label htmlFor="slug" className="block text-sm font-medium text-gray-700">Slug (URL amigable)</label>
            <input type="text" id="slug" {...register('slug')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm bg-gray-50" readOnly placeholder="Se genera automáticamente" />
          </div>
        </div>

        {/* Descripción */}
        <div>
          <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">Descripción</label>
          <textarea id="descripcion" {...register('descripcion')} rows={5} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"></textarea>
        </div>

        {/* Cómo Llegar */}
        <div>
          <label htmlFor="como_llegar" className="block text-sm font-medium text-gray-700">¿Cómo Llegar?</label>
          <textarea id="como_llegar" {...register('como_llegar')} rows={3} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm"></textarea>
        </div>

        {/* Categoria y Ubicación */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label htmlFor="categoria_color" className="block text-sm font-medium text-gray-700">Categoría</label>
                <select id="categoria_color" {...register('categoria_color')} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
                    <option value="AMARILLO">Cultural/Histórico (Amarillo)</option>
                    <option value="ROJO">Urbano/Parque (Rojo)</option>
                    <option value="BLANCO">Natural (Blanco)</option>
                </select>
            </div>
            <div>
                <label htmlFor="ubicacion_mapa" className="block text-sm font-medium text-gray-700">Ubicación (Lat, Lng)</label>
                <input type="text" id="ubicacion_mapa" {...register('ubicacion_mapa')} placeholder="Ej: 4.144,-72.98" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
            </div>
        </div>

        {/* Imagen Principal */}
        <div>
            <label className="block text-sm font-medium text-gray-700">Imagen Principal</label>
            <div className="mt-2 flex items-center space-x-6">
                {imagePreview && <Image src={imagePreview} alt="Vista previa" width={96} height={96} className="h-24 w-24 object-cover rounded-md" />}
                <input type="file" id="imagen_principal" onChange={handleImageChange} className="text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
            </div>
        </div>

        {/* Publicar */}
        <div className="flex items-center">
            <input type="checkbox" id="es_publicado" {...register('es_publicado')} className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
            <label htmlFor="es_publicado" className="ml-2 block text-sm text-gray-900">Marcar como Publicado</label>
        </div>

        <div className="border-t pt-6">
          <button type="submit" disabled={isSubmitting} className="w-full inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700">
            <FiSave className="mr-2" />
            {isSubmitting ? 'Guardando...' : 'Guardar Atractivo'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AtractivoEditPage;