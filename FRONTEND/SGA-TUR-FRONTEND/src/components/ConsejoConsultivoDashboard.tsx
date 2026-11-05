"use client";

import React, { useState, useEffect } from 'react';
import { Formulario, getFormularios, getFormularioDetalle } from '@/services/formService';
import FormFiller from './FormFiller';
import { useAuth } from '@/contexts/AuthContext';

const ConsejoConsultivoDashboard: React.FC = () => {
  const [form, setForm] = useState<Formulario | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchForm = async () => {
      setIsLoading(true);
      try {
        const allForms = await getFormularios();
        const consejoFormInfo = allForms.find(f => f.titulo.includes("Consejo Consultivo de Turismo"));

        if (consejoFormInfo && consejoFormInfo.id) {
          // Inconsistencia subsanada: Obtenemos el detalle completo del formulario
          const formDetail = await getFormularioDetalle(consejoFormInfo.id);
          setForm(formDetail);
        } else {
          setError("No se encontró el formulario de caracterización para el Consejo Consultivo.");
        }
      } catch (err) {
        setError("No se pudo cargar el formulario de caracterización.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchForm();
  }, []);

  if (isLoading) {
    return <p>Cargando panel del Consejo Consultivo...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  if (!form) {
    return <p>No hay un formulario asignado a este rol.</p>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Panel del Consejo Consultivo de Turismo</h1>
        <p className="mt-2 text-lg text-gray-600">
          Por favor, complete o actualice la información de caracterización.
        </p>
      </div>
      <div className="bg-white p-4 sm:p-6 lg:p-8 rounded-2xl shadow-lg">
        {/* Usamos el FormFiller directamente, ya que solo hay un formulario */}
        <FormFiller form={form} onBack={() => {}} />
      </div>
    </div>
  );
};

export default ConsejoConsultivoDashboard;