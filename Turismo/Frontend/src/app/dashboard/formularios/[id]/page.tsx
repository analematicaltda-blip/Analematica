"use client";

import React from 'react';
import { useParams } from 'next/navigation';
import FormularioDetailView from '@/components/FormularioDetailView';
import Link from 'next/link';
import { FiArrowLeft } from 'react-icons/fi';

const FormularioDetailPage = () => {
  const params = useParams();
  const id = params.id as string;

  // El ID debe ser un número para pasarlo al componente
  const formId = parseInt(id, 10);

  if (isNaN(formId)) {
    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold text-red-600">ID de Formulario Inválido</h1>
            <p className="mt-2">El identificador proporcionado no es un número válido.</p>
            <Link href="/dashboard" passHref>
                <a className="mt-4 inline-flex items-center text-blue-600 hover:underline">
                    <FiArrowLeft className="mr-2" />
                    Volver al Dashboard
                </a>
            </Link>
        </div>
    );
  }

  return (
    <div>
      <div className="mb-4">
        <Link href="/dashboard" passHref>
            <a className="inline-flex items-center text-sm font-medium text-gray-600 hover:text-gray-900">
                <FiArrowLeft className="mr-2" />
                Volver a la lista de formularios
            </a>
        </Link>
      </div>
      <FormularioDetailView formId={formId} />
    </div>
  );
};

export default FormularioDetailPage;