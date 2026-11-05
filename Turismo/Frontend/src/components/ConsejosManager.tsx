"use client";

import React, { useState, useEffect, useCallback, FormEvent } from 'react';
import {
  getConsejosLocales,
  createConsejoLocal,
  updateConsejoLocal,
  deleteConsejoLocal,
  ConsejoLocal,
  IntegranteConsejo,
} from '@/services/api';
import { FiPlus, FiEdit, FiTrash2, FiX } from 'react-icons/fi';

// Formulario Modal para Consejo Local
const ConsejoForm = ({
  onSubmit,
  onCancel,
  initialData,
}: {
  onSubmit: (data: FormData) => void;
  onCancel: () => void;
  initialData?: Partial<ConsejoLocal> | null;
}) => {
  const [formData, setFormData] = useState<Partial<ConsejoLocal>>({});
  const [integrantes, setIntegrantes] = useState<Partial<IntegranteConsejo>[]>([]);
  const [planFile, setPlanFile] = useState<File | null>(null);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
      setIntegrantes(initialData.integrantes || []);
    } else {
      setFormData({ municipio: '', integrantes: [] });
      setIntegrantes([]);
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === 'checkbox';
    const { checked } = e.target as HTMLInputElement;
    setFormData(prev => ({ ...prev, [name]: isCheckbox ? checked : value }));
  };

  const handleIntegranteChange = (index: number, field: keyof IntegranteConsejo, value: string) => {
    const updatedIntegrantes = [...integrantes];
    updatedIntegrantes[index] = { ...updatedIntegrantes[index], [field]: value };
    setIntegrantes(updatedIntegrantes);
  };

  const addIntegrante = () => {
    setIntegrantes([...integrantes, { nombre_completo: '' }]);
  };

  const removeIntegrante = (index: number) => {
    setIntegrantes(integrantes.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const data = new FormData();
    (Object.keys(formData) as Array<keyof ConsejoLocal>).forEach(key => {
        if (key !== 'integrantes' && key !== 'plan_accion_adjunto') {
            const value = formData[key];
            if (value !== null && value !== undefined) {
              data.append(key, String(value));
            }
        }
    });
    data.append('integrantes', JSON.stringify(integrantes));
    if (planFile) {
        data.append('plan_accion_adjunto', planFile);
    }
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <h2 className="text-xl font-bold">{initialData?.id ? 'Editar' : 'Crear'} Consejo Local</h2>
      <input name="municipio" value={formData.municipio || ''} onChange={handleChange} placeholder="Municipio" className="input w-full" required />

      <div>
        <label htmlFor="plan_accion_adjunto" className="block text-sm font-medium text-gray-700">Plan de Acción (PDF)</label>
        <input id="plan_accion_adjunto" type="file" accept=".pdf" onChange={(e) => setPlanFile(e.target.files ? e.target.files[0] : null)} className="input w-full" />
      </div>

      <FormSection>
        <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b pb-2">Integrantes del Consejo</h3>
        {integrantes.map((integrante, index) => (
          <div key={index} className="p-4 border rounded-md relative">
            <button type="button" onClick={() => removeIntegrante(index)} className="absolute top-2 right-2 text-red-500"><FiX /></button>
            <input value={integrante.nombre_completo || ''} onChange={(e) => handleIntegranteChange(index, 'nombre_completo', e.target.value)} placeholder="Nombre Completo" className="input w-full mb-2" />
            <input value={integrante.sector_representa || ''} onChange={(e) => handleIntegranteChange(index, 'sector_representa', e.target.value)} placeholder="Sector que representa" className="input w-full" />
          </div>
        ))}
        <button type="button" onClick={addIntegrante} className="btn-secondary">+ Añadir Integrante</button>
      </FormSection>

      <div className="flex justify-end space-x-4">
        <button type="button" onClick={onCancel} className="btn-secondary">Cancelar</button>
        <button type="submit" className="btn-primary">Guardar</button>
      </div>
    </form>
  );
};

const FormSection: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className="p-4 border-t">{children}</div>
);

// Componente Principal
export default function ConsejosManager() {
  const [consejos, setConsejos] = useState<ConsejoLocal[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingConsejo, setEditingConsejo] = useState<ConsejoLocal | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchConsejos = useCallback(async () => {
    try {
      const data = await getConsejosLocales();
      setConsejos(data);
    } catch {
      setError('No se pudo cargar la lista de consejos locales.');
    }
  }, []);

  useEffect(() => {
    fetchConsejos();
  }, [fetchConsejos]);

  const handleOpenModal = (consejo?: ConsejoLocal) => {
    setEditingConsejo(consejo || null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingConsejo(null);
  };

  const handleSubmit = async (data: FormData) => {
    try {
      if (editingConsejo) {
        await updateConsejoLocal(editingConsejo.id, data);
      } else {
        await createConsejoLocal(data);
      }
      fetchConsejos();
      handleCloseModal();
    } catch {
      setError('Error al guardar el consejo local.');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Está seguro de que desea eliminar este consejo?')) {
      try {
        await deleteConsejoLocal(id);
        fetchConsejos();
      } catch {
        setError('Error al eliminar el consejo.');
      }
    }
  };

  return (
    <div className="p-6 bg-gray-50 rounded-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Gestión de Consejos Locales de Turismo</h2>
        <button onClick={() => handleOpenModal()} className="btn-primary flex items-center gap-2"><FiPlus /> Crear Consejo</button>
      </div>

      {error && <p className="text-red-500 bg-red-100 p-3 rounded-md">{error}</p>}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
          <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-2xl">
            <ConsejoForm onSubmit={handleSubmit} onCancel={handleCloseModal} initialData={editingConsejo} />
          </div>
        </div>
      )}

      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-4 text-left">Municipio</th>
              <th className="p-4 text-left"># Integrantes</th>
              <th className="p-4 text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {consejos.map(consejo => (
              <tr key={consejo.id} className="border-b">
                <td className="p-4">{consejo.municipio}</td>
                <td className="p-4">{consejo.integrantes.length}</td>
                <td className="p-4 space-x-2">
                  <button onClick={() => handleOpenModal(consejo)} className="text-blue-600"><FiEdit /></button>
                  <button onClick={() => handleDelete(consejo.id)} className="text-red-600"><FiTrash2 /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}