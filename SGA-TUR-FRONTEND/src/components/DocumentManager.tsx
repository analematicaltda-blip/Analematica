"use client";

import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Document {
  id: number;
  documento: string;
  nombre_documento: string;
  fecha_subida: string;
}

interface DocumentManagerProps {
  initialDocuments: Document[];
  onUpdate: () => void; // Función para refrescar los datos del perfil
}

export default function DocumentManager({ initialDocuments, onUpdate }: DocumentManagerProps) {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [docName, setDocName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !docName) {
      setError('Por favor, seleccione un archivo y asígnele un nombre.');
      return;
    }
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('documento', file);
    formData.append('nombre_documento', docName);

    try {
      await axios.post(`${API_BASE_URL}/documentos/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Token ${token}`,
        },
      });
      onUpdate();
      setFile(null);
      setDocName('');
    } catch (err) {
      setError('Error al subir el documento.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Está seguro de que desea eliminar este documento?')) {
      return;
    }
    try {
      await axios.delete(`${API_BASE_URL}/documentos/${id}/`, {
        headers: { Authorization: `Token ${token}` },
      });
      onUpdate();
    } catch (err) {
      alert('Error al eliminar el documento.');
    }
  };

  return (
    <div className="p-4 border-t border-gray-200">
      <h3 className="text-lg font-bold">Documentos de Legalización</h3>

      <form onSubmit={handleUpload} className="my-4 p-4 border rounded-md">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label htmlFor="documento" className="block text-sm font-medium text-gray-700">Nuevo Documento (PDF, JPG, etc.)</label>
            <input type="file" name="documento" id="documento" onChange={handleFileChange} className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100"/>
          </div>
          <div>
            <label htmlFor="nombre_documento" className="block text-sm font-medium text-gray-700">Nombre del Documento (Ej: RUT, Cámara de Comercio)</label>
            <input type="text" name="nombre_documento" id="nombre_documento" value={docName} onChange={(e) => setDocName(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm" />
          </div>
        </div>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        <button type="submit" disabled={isUploading} className="mt-4 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400">
          {isUploading ? 'Subiendo...' : 'Subir Documento'}
        </button>
      </form>

      <ul className="space-y-3 mt-4">
        {initialDocuments.map((doc) => (
          <li key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
            <div>
              <a href={doc.documento} target="_blank" rel="noopener noreferrer" className="font-medium text-indigo-600 hover:text-indigo-800">
                {doc.nombre_documento}
              </a>
              <p className="text-xs text-gray-500">Subido: {new Date(doc.fecha_subida).toLocaleDateString()}</p>
            </div>
            <button onClick={() => handleDelete(doc.id)} className="px-3 py-1 text-xs font-bold text-white bg-red-600 rounded-full hover:bg-red-700">
              Eliminar
            </button>
          </li>
        ))}
      </ul>
      {initialDocuments.length === 0 && <p className="text-sm text-gray-500">No hay documentos subidos.</p>}
    </div>
  );
}