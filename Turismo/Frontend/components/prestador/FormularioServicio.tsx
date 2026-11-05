"use client";

import React, { useState } from 'react';

interface FormularioServicioProps {
  onServicioCreado: () => void;
}

const FormularioServicio: React.FC<FormularioServicioProps> = ({ onServicioCreado }) => {
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [precio, setPrecio] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const token = localStorage.getItem('access_token');
    if (!token) {
      setError("No estás autenticado. Por favor, inicia sesión.");
      return;
    }

    try {
      const response = await fetch('/api/prestador/servicios/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ nombre, descripcion, precio }),
      });

      if (response.ok) {
        alert('Servicio guardado con éxito.');
        setNombre('');
        setDescripcion('');
        setPrecio('');
        onServicioCreado(); // Llama a la función para recargar la lista
      } else {
        const errorData = await response.json();
        setError(`Error al guardar el servicio: ${JSON.stringify(errorData)}`);
      }
    } catch (err) {
      setError('Error de red al intentar guardar el servicio.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg">
      <h2 className="text-xl font-semibold">Crear Nuevo Servicio</h2>
      {error && <p className="text-red-500">{error}</p>}
      <div>
        <label htmlFor="nombre" className="block text-sm font-medium text-gray-700">Nombre del Servicio</label>
        <input
          type="text"
          id="nombre"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          required
        />
      </div>
      <div>
        <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700">Descripción</label>
        <textarea
          id="descripcion"
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          rows={3}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          required
        />
      </div>
      <div>
        <label htmlFor="precio" className="block text-sm font-medium text-gray-700">Precio</label>
        <input
          type="number"
          id="precio"
          value={precio}
          onChange={(e) => setPrecio(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          required
        />
      </div>
      <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        Guardar Servicio
      </button>
    </form>
  );
};

export default FormularioServicio;