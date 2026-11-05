'use client';

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { toast } from 'react-toastify';
import { FiFileText, FiUpload, FiCheckCircle, FiXCircle, FiClock } from 'react-icons/fi';
import { AuthGuard } from '@/components/ui/AuthGuard';

// --- Tipos ---
interface TipoDocumento {
  id: string;
  nombre: string;
  descripcion: string;
  requerido: boolean;
}

interface DocumentoSubido {
  id: string;
  tipo_documento_nombre: string;
  archivo_url: string;
  estado: 'PENDIENTE' | 'APROBADO' | 'RECHAZADO';
  observaciones: string;
  fecha_subida: string;
}

interface FormData {
  tipo_documento: string;
  archivo: FileList;
}

const DocumentosManager = () => {
  const [tiposDocumento, setTiposDocumento] = useState<TipoDocumento[]>([]);
  const [documentosSubidos, setDocumentosSubidos] = useState<DocumentoSubido[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<FormData>();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [tiposRes, subidosRes] = await Promise.all([
        api.get('/documentos/tipos/'),
        api.get('/documentos/')
      ]);
      setTiposDocumento(tiposRes.data.results || tiposRes.data);
      setDocumentosSubidos(subidosRes.data.results || subidosRes.data);
    } catch (error) {
      toast.error('No se pudo cargar la información de documentos.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onSubmit: SubmitHandler<FormData> = async (data) => {
    if (!data.archivo || data.archivo.length === 0) {
      toast.error('Por favor, selecciona un archivo.');
      return;
    }
    const formData = new FormData();
    formData.append('tipo_documento', data.tipo_documento);
    formData.append('archivo', data.archivo[0]);

    try {
      await api.post('/documentos/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      toast.success('Documento subido con éxito. Queda pendiente de verificación.');
      reset();
      fetchData(); // Recargar
    } catch (error) {
      toast.error('Error al subir el documento.');
    }
  };

  const estadoEstilos: { [key: string]: { icon: React.ElementType, color: string } } = {
    PENDIENTE: { icon: FiClock, color: 'text-yellow-500' },
    APROBADO: { icon: FiCheckCircle, color: 'text-green-500' },
    RECHAZADO: { icon: FiXCircle, color: 'text-red-500' },
  };

  if (isLoading) {
    return <div>Cargando gestión de documentos...</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Documentos y Certificaciones</h1>

      {/* --- Formulario de subida --- */}
      <form onSubmit={handleSubmit(onSubmit)} className="mb-8 p-4 border rounded-lg bg-gray-50">
        <h2 className="text-xl font-semibold mb-4">Subir Nuevo Documento</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <label htmlFor="tipo_documento" className="block text-sm font-medium text-gray-700 mb-1">Tipo de Documento</label>
                <select
                    id="tipo_documento"
                    {...register('tipo_documento', { required: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                    <option value="">Selecciona un tipo...</option>
                    {tiposDocumento.map(tipo => (
                        <option key={tipo.id} value={tipo.id}>{tipo.nombre}</option>
                    ))}
                </select>
            </div>
            <div>
                <label htmlFor="archivo" className="block text-sm font-medium text-gray-700 mb-1">Archivo (PDF, JPG, PNG)</label>
                <input
                    id="archivo"
                    type="file"
                    {...register('archivo', { required: true })}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
            </div>
        </div>
        <div className="mt-4">
            <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300"
            >
                <FiUpload className="mr-2 -ml-1 h-5 w-5" />
                {isSubmitting ? 'Subiendo...' : 'Subir Documento'}
            </button>
        </div>
      </form>

      {/* --- Lista de documentos subidos --- */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Mis Documentos Subidos</h2>
        <div className="space-y-3">
            {documentosSubidos.length > 0 ? documentosSubidos.map(doc => {
                const Estilo = estadoEstilos[doc.estado];
                return (
                    <div key={doc.id} className="p-3 border rounded-lg flex justify-between items-center">
                        <div className="flex items-center">
                            <Estilo.icon className={`h-6 w-6 mr-3 ${Estilo.color}`} />
                            <div>
                                <a href={doc.archivo_url} target="_blank" rel="noopener noreferrer" className="font-bold text-blue-600 hover:underline">{doc.tipo_documento_nombre}</a>
                                <p className="text-sm text-gray-500">Subido el: {new Date(doc.fecha_subida).toLocaleDateString()}</p>
                                {doc.observaciones && <p className="text-sm text-red-600 mt-1">Observaciones: {doc.observaciones}</p>}
                            </div>
                        </div>
                        <span className={`font-medium text-sm ${Estilo.color}`}>{doc.estado}</span>
                    </div>
                )
            }) : (
                <div className="text-center py-10 px-4 border-2 border-dashed rounded-lg">
                    <FiFileText className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-2 text-sm font-medium text-gray-600">No has subido ningún documento.</p>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

const DocumentosPage = () => {
    return (
        <AuthGuard allowedRoles={['PRESTADOR']}>
            <DocumentosManager />
        </AuthGuard>
    )
}

export default DocumentosPage;