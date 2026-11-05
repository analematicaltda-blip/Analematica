"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Formulario, getFormularios, deleteFormulario } from '@/services/formService';
import { FiEye, FiTrash2, FiPlusCircle } from 'react-icons/fi';

const FormManager: React.FC = () => {
  const [formularios, setFormularios] = useState<Formulario[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFormularios = async () => {
    setIsLoading(true);
    try {
      const data = await getFormularios();
      setFormularios(data);
    } catch (err) {
      setError('No se pudieron cargar los formularios.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFormularios();
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este formulario? Esta acción no se puede deshacer.')) {
      try {
        await deleteFormulario(id);
        fetchFormularios(); // Recargar la lista
      } catch (err) {
        setError('Error al eliminar el formulario.');
      }
    }
  };

  if (isLoading) {
    return <p>Cargando formularios...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <div className="bg-white p-8 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Gestionar Formularios</h2>
        {/* Futuro botón para crear formularios desde aquí */}
        {/* <Link href="/dashboard/formularios/crear">
          <a className="flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700">
            <FiPlusCircle className="mr-2" />
            Crear Nuevo Formulario
          </a>
        </Link> */}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {formularios.map((form) => (
          <div key={form.id} className="bg-gray-50 border border-gray-200 rounded-lg p-4 flex flex-col justify-between">
            <div>
              <h3 className="font-bold text-lg text-gray-800">{form.titulo}</h3>
              <p className="text-sm text-gray-600 mt-2 line-clamp-3">{form.descripcion}</p>
            </div>
            <div className="flex justify-end items-center mt-4 space-x-2">
              <Link href={`/dashboard/formularios/${form.id}`} passHref>
                <a className="p-2 text-blue-600 hover:text-blue-900" title="Ver Respuestas y Gestionar">
                  <FiEye />
                </a>
              </Link>
              <button onClick={() => handleDelete(form.id!)} className="p-2 text-red-600 hover:text-red-900" title="Eliminar Formulario">
                <FiTrash2 />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FormManager;