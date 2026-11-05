"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/admin`;

interface Contenido {
  id: number;
  seccion: string;
  titulo: string;
  contenido: string;
  orden: number;
}

const SECCIONES = [
    { value: "INTRODUCCION", label: "Introducción General" },
    { value: "UBICACION_CLIMA", label: "Ubicación y Clima" },
    { value: "ALOJAMIENTO", label: "Alojamiento y Hotelería" },
    { value: "COMO_LLEGAR", label: "Cómo Llegar" },
    { value: "CONTACTOS", label: "Contactos de Interés" },
    { value: "FINANZAS", label: "Entidades Financieras" },
    { value: "OTRA", label: "Otra Sección" },
];

export default function MunicipioContentManager() {
  const { token } = useAuth();
  const [contenidos, setContenidos] = useState<Contenido[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingContenido, setEditingContenido] = useState<Contenido | null>(null);

  const fetchContenidos = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/contenido-municipio/`, {
        headers: { Authorization: `Token ${token}` },
      });
      setContenidos(response.data.results);
    } catch {
      setError('No se pudo cargar el contenido.');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchContenidos();
  }, [fetchContenidos]);

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Está seguro de que desea eliminar este bloque de contenido?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/contenido-municipio/${id}/`, {
        headers: { Authorization: `Token ${token}` },
      });
      fetchContenidos();
    } catch {
      alert('Error al eliminar el contenido.');
    }
  };

  const handleSave = async (contenido: Contenido) => {
    const data = { ...contenido };
    const url = contenido.id
      ? `${API_BASE_URL}/contenido-municipio/${contenido.id}/`
      : `${API_BASE_URL}/contenido-municipio/`;
    const method = contenido.id ? 'patch' : 'post';

    try {
      await axios[method](url, data, {
        headers: { Authorization: `Token ${token}` },
      });
      setEditingContenido(null);
      fetchContenidos();
    } catch {
      alert('Error al guardar el contenido.');
    }
  };

  if (isLoading) return <p>Cargando contenido...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Gestión de Contenido del Municipio</h2>
      <button onClick={() => setEditingContenido({} as Contenido)} className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        Crear Nuevo Bloque
      </button>

      {editingContenido && (
        <ContentForm
          contenido={editingContenido}
          onSave={handleSave}
          onCancel={() => setEditingContenido(null)}
        />
      )}

      <div className="space-y-4 mt-4">
        {contenidos.map(c => (
          <div key={c.id} className="p-4 border rounded-md flex justify-between items-center">
            <div>
              <h3 className="font-bold">{c.titulo}</h3>
              <p className="text-sm text-gray-500">{SECCIONES.find(s => s.value === c.seccion)?.label}</p>
            </div>
            <div>
              <button onClick={() => setEditingContenido(c)} className="mr-2 px-3 py-1 bg-yellow-500 text-white rounded">Editar</button>
              <button onClick={() => handleDelete(c.id)} className="px-3 py-1 bg-red-600 text-white rounded">Eliminar</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ContentForm({ contenido, onSave, onCancel }: { contenido: Contenido, onSave: (c: Contenido) => void, onCancel: () => void }) {
  const [formState, setFormState] = useState(contenido);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormState(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formState);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl">
        <h3 className="text-xl font-bold mb-4">{contenido.id ? 'Editar' : 'Crear'} Bloque de Contenido</h3>
        <div className="space-y-4">
          <select name="seccion" value={formState.seccion || ''} onChange={handleChange} className="w-full p-2 border rounded">
            <option value="">Seleccione una sección</option>
            {SECCIONES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          <input type="text" name="titulo" value={formState.titulo || ''} onChange={handleChange} placeholder="Título" className="w-full p-2 border rounded" />
          <textarea name="contenido" value={formState.contenido || ''} onChange={handleChange} placeholder="Contenido (Markdown soportado)" rows={10} className="w-full p-2 border rounded"></textarea>
          <input type="number" name="orden" value={formState.orden || 0} onChange={handleChange} placeholder="Orden" className="w-full p-2 border rounded" />
        </div>
        <div className="mt-6 flex justify-end">
          <button type="button" onClick={onCancel} className="mr-4 px-4 py-2 bg-gray-300 rounded">Cancelar</button>
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Guardar</button>
        </div>
      </form>
    </div>
  );
}