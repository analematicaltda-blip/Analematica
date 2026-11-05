"use client";

import React, { useState, useEffect, useCallback, FormEvent } from 'react';
import {
  getDiagnosticosRuta,
  createDiagnosticoRuta,
  updateDiagnosticoRuta,
  deleteDiagnosticoRuta,
  DiagnosticoRutaTuristica,
} from '@/services/api';
import { FiPlus, FiEdit, FiTrash2, FiX } from 'react-icons/fi';

type ListItem = Record<string, string>;

// Helper component for dynamic JSON fields
const DynamicListInput = ({
  label,
  items,
  setItems,
  fields,
  readOnly = false,
}: {
  label: string;
  items: ListItem[];
  setItems: (items: ListItem[]) => void;
  fields: { name: string; placeholder: string; type?: string }[];
  readOnly?: boolean;
}) => {
  const handleItemChange = (index: number, fieldName: string, value: string) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [fieldName]: value };
    setItems(newItems);
  };

  const addItem = () => {
    const newItem: ListItem = {};
    fields.forEach(field => {
      newItem[field.name] = '';
    });
    setItems([...items, newItem]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  return (
    <div>
      <h4 className="font-semibold text-gray-700 mb-2">{label}</h4>
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={index} className="p-3 border rounded-md bg-gray-50 relative">
            {!readOnly && (
              <button type="button" onClick={() => removeItem(index)} className="absolute top-2 right-2 text-red-500 hover:text-red-700">
                <FiX />
              </button>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {fields.map(field => (
                <input
                  key={field.name}
                  type={field.type || 'text'}
                  placeholder={field.placeholder}
                  value={item[field.name] || ''}
                  onChange={(e) => handleItemChange(index, field.name, e.target.value)}
                  className="input"
                  disabled={readOnly}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      {!readOnly && (
        <button type="button" onClick={addItem} className="btn-secondary mt-3 text-sm">
          + Añadir {label.slice(0, -1)}
        </button>
      )}
    </div>
  );
};

// Formulario Modal para Diagnóstico de Ruta
const RutaForm = ({
  onSubmit,
  onCancel,
  initialData,
}: {
  onSubmit: (data: Partial<DiagnosticoRutaTuristica>) => void;
  onCancel: () => void;
  initialData?: Partial<DiagnosticoRutaTuristica> | null;
}) => {
  const [formData, setFormData] = useState<Partial<DiagnosticoRutaTuristica>>({});

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...initialData,
        actores_cadena_valor: initialData.actores_cadena_valor || [],
        entidades_responsables: initialData.entidades_responsables || [],
        eventos_turisticos: initialData.eventos_turisticos || [],
        atractivos_turisticos: initialData.atractivos_turisticos || [],
      });
    } else {
      setFormData({
        nombre_ruta: '',
        descripcion_general: '',
        actores_cadena_valor: [],
        entidades_responsables: [],
        eventos_turisticos: [],
        atractivos_turisticos: [],
      });
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-2xl font-bold">{initialData?.id ? 'Editar' : 'Crear'} Diagnóstico de Ruta</h2>
      <input name="nombre_ruta" value={formData.nombre_ruta || ''} onChange={handleChange} placeholder="Nombre de la Ruta" className="input w-full" required />
      <textarea name="descripcion_general" value={formData.descripcion_general || ''} onChange={handleChange} placeholder="Descripción General" className="input w-full" rows={4} />

      <DynamicListInput
        label="Actores de la Cadena de Valor"
        items={formData.actores_cadena_valor || []}
        setItems={(items) => setFormData(prev => ({ ...prev, actores_cadena_valor: items }))}
        fields={[
          { name: 'municipio', placeholder: 'Municipio' },
          { name: 'actor', placeholder: 'Actor (Ej: Hotel ABC)' },
          { name: 'caracterizado', placeholder: 'Caracterizado (SI/NO)' },
          { name: 'rnt', placeholder: 'RNT (SI/NO)' },
          { name: 'promocion', placeholder: 'Promoción (SI/NO)' },
        ]}
      />

      <div className="flex justify-end space-x-4">
        <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        <button type="submit" className="btn-primary">Guardar</button>
      </div>
    </form>
  );
};

// Componente Principal
export default function RutasManager() {
  const [rutas, setRutas] = useState<DiagnosticoRutaTuristica[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRuta, setEditingRuta] = useState<DiagnosticoRutaTuristica | null>(null);

  const fetchRutas = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getDiagnosticosRuta();
      setRutas(data);
    } catch (err) {
      setError('No se pudo cargar la lista de diagnósticos de ruta.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRutas();
  }, [fetchRutas]);

  const handleOpenModal = (ruta?: DiagnosticoRutaTuristica) => {
    setEditingRuta(ruta || null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingRuta(null);
  };

  const handleSubmit = async (data: Partial<DiagnosticoRutaTuristica>) => {
    try {
      if (editingRuta) {
        await updateDiagnosticoRuta(editingRuta.id, data);
      } else {
        await createDiagnosticoRuta(data);
      }
      fetchRutas();
      handleCloseModal();
    } catch (err) {
      setError('Error al guardar el diagnóstico.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Está seguro de que desea eliminar este diagnóstico?')) {
      try {
        await deleteDiagnosticoRuta(id);
        fetchRutas();
      } catch (err) {
        setError('Error al eliminar el diagnóstico.');
      }
    }
  };

  return (
    <div className="p-6 bg-gray-50 rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Gestión de Diagnósticos de Rutas Turísticas</h2>
        <button onClick={() => handleOpenModal()} className="btn-primary flex items-center gap-2"><FiPlus /> Crear Diagnóstico</button>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
          <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <RutaForm onSubmit={handleSubmit} onCancel={handleCloseModal} initialData={editingRuta} />
          </div>
        </div>
      )}

      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-4 text-left">Nombre de la Ruta</th>
              <th className="p-4 text-left">Elaborado por</th>
              <th className="p-4 text-left">Fecha</th>
              <th className="p-4 text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {rutas.map(ruta => (
              <tr key={ruta.id} className="border-b">
                <td className="p-4 font-semibold">{ruta.nombre_ruta}</td>
                <td className="p-4">{ruta.elaborado_por_username}</td>
                <td className="p-4">{new Date(ruta.fecha_elaboracion).toLocaleDateString()}</td>
                <td className="p-4 space-x-2">
                  <button onClick={() => handleOpenModal(ruta)} className="text-blue-600 p-2 hover:bg-blue-100 rounded-full"><FiEdit /></button>
                  <button onClick={() => handleDelete(ruta.id)} className="text-red-600 p-2 hover:bg-red-100 rounded-full"><FiTrash2 /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}