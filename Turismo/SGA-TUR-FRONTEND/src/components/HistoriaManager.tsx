"use client";

import React, { useState, useEffect, useCallback, FormEvent } from 'react';
import Image from 'next/image';
import { FiPlus, FiEdit, FiTrash2, FiImage, FiCheckCircle, FiXCircle } from 'react-icons/fi';
import {
  getHechosHistoricos,
  createHechoHistorico,
  updateHechoHistorico,
  deleteHechoHistorico,
  HechoHistorico,
} from '@/services/api';

// --- Formulario Modal ---
const HechoHistoricoForm = ({
  onSubmit,
  onCancel,
  initialData,
}: {
  onSubmit: (data: FormData) => void;
  onCancel: () => void;
  initialData?: HechoHistorico | null;
}) => {
  const [formData, setFormData] = useState({
    ano: initialData?.ano || new Date().getFullYear(),
    titulo: initialData?.titulo || '',
    descripcion: initialData?.descripcion || '',
    es_publicado: initialData?.es_publicado || false,
  });
  const [imagenFile, setImagenFile] = useState<File | null>(null);
  const [imagenPreview, setImagenPreview] = useState<string | null>(initialData?.imagen_url || null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const isCheckbox = type === 'checkbox';
    const inputValue = isCheckbox ? (e.target as HTMLInputElement).checked : value;
    setFormData(prev => ({ ...prev, [name]: inputValue }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const file = e.target.files[0];
      setImagenFile(file);
      setImagenPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const data = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      data.append(key, String(value));
    });
    if (imagenFile) {
      data.append('imagen', imagenFile);
    }
    onSubmit(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl">
        <h2 className="text-2xl font-bold mb-6">{initialData ? 'Editar' : 'Crear'} Hecho Histórico</h2>
        <form onSubmit={handleSubmit} className="space-y-4 max-h-[85vh] overflow-y-auto pr-4">
          <input type="number" name="ano" value={formData.ano} onChange={handleInputChange} placeholder="Año" className="w-full px-3 py-2 border rounded-md" required />
          <input type="text" name="titulo" value={formData.titulo} onChange={handleInputChange} placeholder="Título del Hecho" className="w-full px-3 py-2 border rounded-md" required />
          <textarea name="descripcion" value={formData.descripcion} onChange={handleInputChange} placeholder="Descripción" rows={5} className="w-full px-3 py-2 border rounded-md" required />
          <div>
            <label className="block text-sm font-medium text-gray-700">Imagen (Opcional)</label>
            <div className="mt-2 flex items-center space-x-4">
              {imagenPreview ? <Image src={imagenPreview} alt="Vista previa" width={128} height={72} className="h-20 w-auto rounded-md object-cover bg-gray-100" /> : <div className="h-20 w-32 bg-gray-100 rounded-md flex items-center justify-center text-gray-400"><FiImage size={32}/></div>}
              <input type="file" accept="image/*" onChange={handleFileChange} className="block text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
            </div>
          </div>
          <div className="flex items-center">
            <input type="checkbox" id="es_publicado" name="es_publicado" checked={formData.es_publicado} onChange={handleInputChange} className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
            <label htmlFor="es_publicado" className="ml-2 block text-sm text-gray-900">Visible en la línea de tiempo pública</label>
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Guardar Hecho Histórico</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Componente Principal del Gestor ---
export default function HistoriaManager() {
  const [hechos, setHechos] = useState<HechoHistorico[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingHecho, setEditingHecho] = useState<HechoHistorico | null>(null);

  const fetchHechos = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getHechosHistoricos();
      setHechos(data || []);
    } catch {
      setError("No se pudieron cargar los hechos históricos.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchHechos(); }, [fetchHechos]);

  const handleOpenModal = (hecho?: HechoHistorico) => {
    setEditingHecho(hecho || null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingHecho(null);
  };

  const handleSave = async (data: FormData) => {
    setError(null);
    try {
      if (editingHecho?.id) {
        await updateHechoHistorico(editingHecho.id, data);
      } else {
        await createHechoHistorico(data);
      }
      fetchHechos();
      handleCloseModal();
    } catch (err) {
      setError(`Error al guardar: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("¿Está seguro de que desea eliminar este hecho histórico?")) return;
    setError(null);
    try {
      await deleteHechoHistorico(id);
      fetchHechos();
    } catch (err) {
      setError(`Error al eliminar: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  if (isLoading) return <p className="text-center py-8">Cargando línea de tiempo...</p>;
  if (error) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      {isModalOpen && <HechoHistoricoForm onSubmit={handleSave} onCancel={handleCloseModal} initialData={editingHecho} />}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de la Línea de Tiempo Histórica</h2>
        <button onClick={() => handleOpenModal()} className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm">
          <FiPlus className="mr-2" />Añadir Hecho Histórico
        </button>
      </div>
      <div className="space-y-4">
        {hechos.length > 0 ? hechos.map(hecho => (
          <div key={hecho.id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex items-start gap-4">
            {hecho.imagen_url && <Image src={hecho.imagen_url} alt={hecho.titulo} width={150} height={100} className="w-36 h-24 object-cover rounded-md bg-gray-100 hidden sm:block" />}
            <div className="flex-grow">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-bold text-blue-600 text-xl">{hecho.ano}</p>
                  <h3 className="font-semibold text-lg text-gray-900">{hecho.titulo}</h3>
                </div>
                <span className={`flex items-center text-xs font-semibold px-2 py-1 rounded-full ${hecho.es_publicado ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {hecho.es_publicado ? <FiCheckCircle className="mr-1"/> : <FiXCircle className="mr-1"/>}
                  {hecho.es_publicado ? 'Publicado' : 'Borrador'}
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-2">{hecho.descripcion}</p>
            </div>
            <div className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-2">
              <button onClick={() => handleOpenModal(hecho)} className="p-2 text-gray-500 hover:text-blue-600 rounded-full hover:bg-blue-100 transition-colors"><FiEdit size={16} /></button>
              <button onClick={() => handleDelete(hecho.id)} className="p-2 text-gray-500 hover:text-red-600 rounded-full hover:bg-red-100 transition-colors"><FiTrash2 size={16} /></button>
            </div>
          </div>
        )) : (
          <p className="text-center text-gray-500 py-12">No hay hechos históricos creados.</p>
        )}
      </div>
    </div>
  );
}