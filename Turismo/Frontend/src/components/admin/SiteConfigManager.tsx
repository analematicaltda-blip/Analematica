'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { toast } from 'react-toastify';
import api from '@/services/api';
import FormField from '@/components/ui/FormField';
import { Button } from '@/components/ui/Button';

interface SiteConfigData {
  nombre_entidad_principal: string;
  nombre_entidad_secundaria: string;
  nombre_secretaria: string;
  correo_institucional: string;
  // ... otros campos según el modelo
}

const SiteConfigManager = () => {
  const [isLoading, setIsLoading] = useState(true);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SiteConfigData>();

  const fetchConfig = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/config/site-config/');
      reset(response.data); // Cargar los datos actuales en el formulario
    } catch (error) {
      toast.error('Error al cargar la configuración del sitio.');
    } finally {
      setIsLoading(false);
    }
  }, [reset]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const onSubmit: SubmitHandler<SiteConfigData> = async (data) => {
    try {
      await api.patch('/config/site-config/', data);
      toast.success('Configuración guardada con éxito.');
    } catch (error) {
      toast.error('Ocurrió un error al guardar la configuración.');
    }
  };

  if (isLoading) {
    return <p>Cargando configuración...</p>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Configuración General del Sitio</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="bg-white p-6 rounded-lg shadow-md space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormField
                name="nombre_entidad_principal"
                label="Nombre de la Entidad Principal"
                register={register}
                errors={errors}
                required
            />
            <FormField
                name="nombre_entidad_secundaria"
                label="Nombre de la Entidad Secundaria"
                register={register}
                errors={errors}
                required
            />
             <FormField
                name="nombre_secretaria"
                label="Nombre de la Secretaría"
                register={register}
                errors={errors}
            />
             <FormField
                name="correo_institucional"
                label="Correo Institucional"
                type="email"
                register={register}
                errors={errors}
            />
        </div>

        {/* Aquí se podrían añadir más campos de configuración */}

        <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Guardando...' : 'Guardar Configuración'}
            </Button>
        </div>
      </form>
    </div>
  );
};

export default SiteConfigManager;