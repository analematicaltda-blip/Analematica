"use client";

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import Image from 'next/image';
import { useAuth } from '@/contexts/AuthContext';
import { FiX, FiSave, FiCheckCircle, FiXCircle, FiTrash2, FiLoader, FiPaperclip, FiUser, FiPhone, FiMail, FiLink } from 'react-icons/fi';
import { FaWhatsapp } from 'react-icons/fa';
import { toast } from 'react-toastify';

// --- Type Definitions ---
interface GalleryImage {
  id: number;
  imagen: string;
  alt_text: string;
}

interface LegalDocument {
  id: number;
  documento: string;
  nombre_documento: string;
}

interface UserInfo {
    email?: string;
}

interface CategoryInfo {
    nombre?: string;
}

interface ProviderDetail {
  id: number;
  aprobado: boolean;
  nombre_negocio?: string;
  nombre_taller?: string;
  nombre_artesano?: string;
  descripcion?: string;
  telefono?: string;
  email_contacto?: string;
  ubicacion_mapa?: string;
  red_social_facebook?: string;
  red_social_instagram?: string;
  red_social_whatsapp?: string;
  promociones_ofertas?: string;
  categoria?: CategoryInfo;
  rubro?: CategoryInfo;
  galeria_imagenes: GalleryImage[];
  documentos_legalizacion?: LegalDocument[];
  usuario?: UserInfo;
}

interface AdminProviderManagerProps {
  providerId: number;
  providerType: 'prestadores' | 'artesanos';
  onClose: () => void;
  onUpdate: () => void;
}

// --- Helper Components ---
const DetailRow: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div className="py-2 sm:grid sm:grid-cols-3 sm:gap-4">
    <dt className="text-sm font-medium text-gray-500">{label}</dt>
    <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{value || <span className="text-gray-400">No disponible</span>}</dd>
  </div>
);

const EditableField: React.FC<{ id: string; name: string; label: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void; icon: React.ReactNode; type?: string; placeholder?: string }> = ({ id, name, label, value, onChange, icon, type = 'text', placeholder }) => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <div className="relative">
        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">{icon}</span>
        <input
          type={type}
          id={id}
          name={name}
          value={value || ''}
          onChange={onChange}
          placeholder={placeholder}
          className="pl-10 pr-4 py-2.5 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all"
        />
      </div>
    </div>
  );

// --- Main Component ---
const AdminProviderManager: React.FC<AdminProviderManagerProps> = ({ providerId, providerType, onClose, onUpdate }) => {
  const { token } = useAuth();
  const [provider, setProvider] = useState<ProviderDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'details' | 'edit'>('details');

  const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    headers: { 'Authorization': `Token ${token}` },
  });

  const fetchProviderDetails = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.get(`/admin/${providerType}/${providerId}/`);
      setProvider(response.data);
    } catch (error) {
      toast.error(`No se pudo cargar el perfil.`);
      onClose();
    } finally {
      setIsLoading(false);
    }
  }, [providerId, providerType, token, apiClient, onClose]);

  useEffect(() => {
    fetchProviderDetails();
  }, [fetchProviderDetails]);

  const handleFieldChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (!provider) return;
    const { name, value } = e.target;
    setProvider({ ...provider, [name]: value });
  };

  const handleSaveChanges = async () => {
    if (!provider) return;
    setIsSaving(true);
    const toastId = toast.loading("Guardando cambios...");
    try {
      // Excluir campos de solo lectura antes de enviar
      const { galeria_imagenes, documentos_legalizacion, usuario, categoria, rubro, ...dataToSave } = provider;
      await apiClient.put(`/admin/${providerType}/${provider.id}/`, dataToSave);
      toast.update(toastId, { render: "Perfil actualizado con éxito", type: "success", isLoading: false, autoClose: 3000 });
      onUpdate(); // Recargar la lista en la página principal
      setActiveTab('details'); // Volver a la vista de detalles
    } catch (error) {
      toast.update(toastId, { render: "Error al guardar los cambios", type: "error", isLoading: false, autoClose: 3000 });
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleApproval = async () => {
    if (!provider) return;
    const newStatus = !provider.aprobado;
    const actionText = newStatus ? 'Aprobando' : 'Desactivando';
    const toastId = toast.loading(`${actionText} perfil...`);
    setIsSaving(true);
    try {
      await apiClient.patch(`/admin/${providerType}/${provider.id}/`, { aprobado: newStatus });
      toast.update(toastId, { render: `Perfil ${newStatus ? 'aprobado' : 'desactivado'}`, type: "success", isLoading: false, autoClose: 3000 });
      setProvider({ ...provider, aprobado: newStatus });
      onUpdate();
    } catch (error) {
      toast.update(toastId, { render: `Error al ${actionText.toLowerCase()} el perfil`, type: "error", isLoading: false, autoClose: 3000 });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!provider || !window.confirm("¿Estás seguro de que quieres eliminar este perfil de forma permanente? Esta acción no se puede deshacer.")) return;
    const toastId = toast.loading("Eliminando perfil...");
    setIsSaving(true);
    try {
      await apiClient.delete(`/admin/${providerType}/${provider.id}/`);
      toast.update(toastId, { render: "Perfil eliminado con éxito", type: "success", isLoading: false, autoClose: 3000 });
      onUpdate();
      onClose();
    } catch (error) {
      toast.update(toastId, { render: "Error al eliminar el perfil", type: "error", isLoading: false, autoClose: 3000 });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading || !provider) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
        <div className="bg-white p-8 rounded-lg shadow-xl text-center">
          <FiLoader className="animate-spin h-12 w-12 text-blue-600 mx-auto" />
          <p className="mt-4 text-lg">Cargando perfil...</p>
        </div>
      </div>
    );
  }

  const renderDetailsView = () => (
    <div className="space-y-6">
        <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">Información General</h3>
            <dl className="mt-2 border-t border-b border-gray-200 divide-y divide-gray-200">
                <DetailRow label="Nombre" value={provider.nombre_negocio || provider.nombre_taller} />
                {provider.nombre_artesano && <DetailRow label="Artesano" value={provider.nombre_artesano} />}
                <DetailRow label="Email de Usuario" value={provider.usuario?.email} />
                <DetailRow label="Categoría/Rubro" value={provider.categoria?.nombre || provider.rubro?.nombre} />
                <DetailRow label="Descripción" value={<p className="whitespace-pre-wrap">{provider.descripcion}</p>} />
            </dl>
        </div>
        <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">Contacto y Redes</h3>
            <dl className="mt-2 border-t border-b border-gray-200 divide-y divide-gray-200">
                <DetailRow label="Teléfono" value={provider.telefono} />
                <DetailRow label="Email de Contacto" value={<a href={`mailto:${provider.email_contacto}`} className="text-blue-600 hover:underline">{provider.email_contacto}</a>} />
                <DetailRow label="WhatsApp" value={provider.red_social_whatsapp} />
                <DetailRow label="Facebook" value={<a href={provider.red_social_facebook} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Visitar</a>} />
                <DetailRow label="Instagram" value={<a href={provider.red_social_instagram} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Visitar</a>} />
            </dl>
        </div>
        <div>
            <h3 className="text-lg leading-6 font-medium text-gray-900">Galería de Imágenes</h3>
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {provider.galeria_imagenes.length > 0 ? provider.galeria_imagenes.map(img => (
                    <img key={img.id} src={img.imagen} alt={img.alt_text} className="rounded-lg object-cover aspect-square shadow-md" />
                )) : <p className="text-gray-500 col-span-full">No hay imágenes en la galería.</p>}
            </div>
        </div>
        {provider.documentos_legalizacion && (
            <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">Documentos de Legalización</h3>
                <ul className="mt-4 space-y-2">
                    {provider.documentos_legalizacion.length > 0 ? provider.documentos_legalizacion.map(doc => (
                        <li key={doc.id}>
                            <a href={doc.documento} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center gap-2">
                                <FiPaperclip /> {doc.nombre_documento}
                            </a>
                        </li>
                    )) : <p className="text-gray-500">No hay documentos subidos.</p>}
                </ul>
            </div>
        )}
    </div>
  );

  const renderEditView = () => (
      <div className="space-y-6">
        <EditableField id="nombre_negocio" name={providerType === 'prestadores' ? 'nombre_negocio' : 'nombre_taller'} label="Nombre del Negocio/Taller" value={provider.nombre_negocio || provider.nombre_taller} onChange={handleFieldChange} icon={<FiUser />} />
        {providerType === 'artesanos' && <EditableField id="nombre_artesano" name="nombre_artesano" label="Nombre del Artesano" value={provider.nombre_artesano} onChange={handleFieldChange} icon={<FiUser />} />}
        <EditableField id="telefono" name="telefono" label="Teléfono" value={provider.telefono} onChange={handleFieldChange} icon={<FiPhone />} />
        <EditableField id="email_contacto" name="email_contacto" label="Email de Contacto" value={provider.email_contacto} onChange={handleFieldChange} icon={<FiMail />} type="email"/>
        <EditableField id="red_social_facebook" name="red_social_facebook" label="Facebook URL" value={provider.red_social_facebook} onChange={handleFieldChange} icon={<FiLink />} type="url"/>
        <EditableField id="red_social_instagram" name="red_social_instagram" label="Instagram URL" value={provider.red_social_instagram} onChange={handleFieldChange} icon={<FiLink />} type="url"/>
        <EditableField id="red_social_whatsapp" name="red_social_whatsapp" label="WhatsApp" value={provider.red_social_whatsapp} onChange={handleFieldChange} icon={<FaWhatsapp />} />
        <div>
            <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
            <textarea name="descripcion" id="descripcion" value={provider.descripcion} onChange={handleFieldChange} rows={5} className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"></textarea>
        </div>
        <div className="flex justify-end pt-4">
            <button onClick={handleSaveChanges} disabled={isSaving} className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400">
                {isSaving ? <FiLoader className="animate-spin h-5 w-5"/> : <FiSave className="h-5 w-5" />}
                Guardar Cambios
            </button>
        </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex justify-center items-start p-4 overflow-y-auto">
      <div className="bg-gray-50 rounded-2xl shadow-2xl w-full max-w-4xl my-8 transform transition-all">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
            <div>
                <h2 className="text-2xl font-bold text-gray-800">{provider.nombre_negocio || provider.nombre_taller}</h2>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-2 ${provider.aprobado ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {provider.aprobado ? 'Aprobado' : 'Pendiente de Aprobación'}
                </span>
            </div>
            <button onClick={onClose} className="p-2 rounded-full text-gray-500 hover:bg-gray-200"><FiX className="h-6 w-6" /></button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                <button onClick={() => setActiveTab('details')} className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'details' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                    Detalles
                </button>
                <button onClick={() => setActiveTab('edit')} className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'edit' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                    Editar
                </button>
            </nav>
        </div>

        {/* Content */}
        <div className="p-6">
            {activeTab === 'details' ? renderDetailsView() : renderEditView()}
        </div>

        {/* Footer Actions */}
        <div className="bg-gray-100 px-6 py-4 border-t border-gray-200 flex flex-col sm:flex-row justify-end items-center gap-4 rounded-b-2xl">
            <button onClick={handleDelete} disabled={isSaving} className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50">
                <FiTrash2 /> Eliminar Perfil
            </button>
            <button onClick={handleToggleApproval} disabled={isSaving} className={`w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 ${provider.aprobado ? 'text-yellow-700 bg-yellow-100 hover:bg-yellow-200 focus:ring-yellow-500' : 'text-green-700 bg-green-100 hover:bg-green-200 focus:ring-green-500'}`}>
                {provider.aprobado ? <><FiXCircle /> Desactivar</> : <><FiCheckCircle /> Aprobar</>}
            </button>
        </div>

      </div>
    </div>
  );
};

export default AdminProviderManager;