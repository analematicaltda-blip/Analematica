"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import ImageGalleryManager from './ImageGalleryManager';
import DocumentManager from './DocumentManager';
import FeedbackProveedor from './FeedbackProveedor';
import CaracterizacionEventosForm from './CaracterizacionEventosForm';
import CaracterizacionAgroturismoForm from './CaracterizacionAgroturismoForm';
import {
    getCaracterizacionByPrestadorId, createCaracterizacion, updateCaracterizacion, CaracterizacionEmpresaEventos,
    getAgroturismoCaracterizacionByPrestadorId, createAgroturismoCaracterizacion, updateAgroturismoCaracterizacion, CaracterizacionAgroturismo
} from '@/services/api';
import { FiUser, FiPhone, FiMail, FiMapPin, FiLink, FiTag, FiCheckCircle, FiAlertCircle, FiSave, FiLoader, FiFileText } from 'react-icons/fi';
import { FaWhatsapp } from 'react-icons/fa';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// --- Type Definitions ---
interface Image {
  id: number;
  imagen: string;
  alt_text: string;
}

interface Document {
  id: number;
  documento: string;
  nombre_documento: string;
  fecha_subida: string;
}

interface ProfileData {
  id: number;
  nombre_negocio: string;
  descripcion: string;
  telefono: string;
  email_contacto: string;
  red_social_facebook: string;
  red_social_instagram: string;
  red_social_whatsapp: string;
  ubicacion_mapa: string;
  promociones_ofertas: string;
  reporte_ocupacion_nacional: number;
  reporte_ocupacion_internacional: number;
  categoria_nombre: string;
  aprobado: boolean;
  galeria_imagenes: Image[];
  documentos_legalizacion: Document[];
}

// --- Helper Components ---
const FormSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
    <h3 className="text-xl font-bold text-gray-800 mb-6">{title}</h3>
    <div className="space-y-6">{children}</div>
  </div>
);

const InputField: React.FC<{ id: string; name: string; label: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; icon: React.ReactNode; type?: string; placeholder?: string }> = ({ id, name, label, value, onChange, icon, type = 'text', placeholder }) => (
  <div>
    <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
    <div className="relative">
      <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">{icon}</span>
      <input
        type={type}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="pl-10 pr-4 py-2.5 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all"
      />
    </div>
  </div>
);

// --- Main Component ---
export default function ProfileForm() {
  const { token } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [municipalities, setMunicipalities] = useState<Municipality[]>([]);

  // State for Eventos Caracterizacion Modal
  const [isEventosModalOpen, setIsEventosModalOpen] = useState(false);
  const [eventosCaracterizacionData, setEventosCaracterizacionData] = useState<CaracterizacionEmpresaEventos | null>(null);

  // State for Agroturismo Caracterizacion Modal
  const [isAgroModalOpen, setIsAgroModalOpen] = useState(false);
  const [agroCaracterizacionData, setAgroCaracterizacionData] = useState<CaracterizacionAgroturismo | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/profile/prestador/`, {
        headers: { Authorization: `Token ${token}` },
      });
      setProfile(response.data);
    } catch {
      setError('No se pudo cargar el perfil. Por favor, intente de nuevo.');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchProfile();
    const fetchDepartments = async () => {
        try {
            const data = await getDepartments();
            setDepartments(data);
        } catch (error) {
            console.error("Failed to fetch departments", error);
        }
    };
    fetchDepartments();
  }, [fetchProfile]);

  useEffect(() => {
    if (profile?.department) {
        const fetchMunicipalities = async () => {
            try {
                const data = await getMunicipalitiesByDepartment(profile.department);
                setMunicipalities(data);
            } catch (error) {
                console.error("Failed to fetch municipalities", error);
            }
        };
        fetchMunicipalities();
    }
  }, [profile?.department]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    if (!profile) return;
    const { name, value } = e.target;

    if (name === 'department' || name === 'municipality') {
      setProfile({ ...profile, [name]: value ? parseInt(value, 10) : null });
    } else {
      setProfile({ ...profile, [name]: value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await axios.put(`${API_BASE_URL}/profile/prestador/`, profile, {
        headers: { Authorization: `Token ${token}` },
      });
      setSuccess('¡Perfil actualizado con éxito!');
      setTimeout(() => setSuccess(null), 5000);
    } catch {
      setError('Error al guardar el perfil. Por favor, verifique los datos.');
    } finally {
      setIsSaving(false);
    }
  };

  // Eventos Modal Handlers
  const handleOpenEventosModal = async () => {
    if (!profile) return;
    const data = await getCaracterizacionByPrestadorId(profile.id);
    setEventosCaracterizacionData(data);
    setIsEventosModalOpen(true);
  };

  const handleEventosSubmit = async (formData: FormData) => {
    if (!profile) return;
    try {
      if (eventosCaracterizacionData) {
        await updateCaracterizacion(eventosCaracterizacionData.id, formData);
      } else {
        formData.append('prestador', String(profile.id));
        await createCaracterizacion(formData);
      }
      setSuccess('¡Caracterización de Eventos guardada con éxito!');
      setTimeout(() => setSuccess(null), 5000);
      handleCloseModal();
    } catch (err) {
      setError('Error al guardar la caracterización de eventos.');
    }
  };

  // Agroturismo Modal Handlers
  const handleOpenAgroModal = async () => {
    if (!profile) return;
    const data = await getAgroturismoCaracterizacionByPrestadorId(profile.id);
    setAgroCaracterizacionData(data);
    setIsAgroModalOpen(true);
  };

  const handleAgroSubmit = async (formData: CaracterizacionAgroturismo) => {
    if (!profile) return;
    try {
      const dataToSubmit = { ...formData, prestador: profile.id };
      if (agroCaracterizacionData) {
        await updateAgroturismoCaracterizacion(agroCaracterizacionData.id, dataToSubmit);
      } else {
        await createAgroturismoCaracterizacion(dataToSubmit);
      }
      setSuccess('¡Caracterización de Agroturismo guardada con éxito!');
      setTimeout(() => setSuccess(null), 5000);
      handleCloseModal();
    } catch (err) {
      setError('Error al guardar la caracterización de agroturismo.');
    }
  };

  // Generic Close Modal
  const handleCloseModal = () => {
    setIsEventosModalOpen(false);
    setEventosCaracterizacionData(null);
    setIsAgroModalOpen(false);
    setAgroCaracterizacionData(null);
  };

  if (isLoading) return <div className="flex justify-center items-center p-8"><FiLoader className="animate-spin h-8 w-8 text-blue-600" /> <p className="ml-4">Cargando perfil...</p></div>;
  if (error && !profile) return <p className="text-red-500 text-center p-8">{error}</p>;
  if (!profile) return <p className="text-center p-8">No se encontró un perfil asociado a esta cuenta.</p>;

  return (
    <form onSubmit={handleSubmit} className="space-y-8 font-sans">
      <div className={`p-4 rounded-lg flex items-center gap-4 ${profile.aprobado ? 'bg-green-50 text-green-800' : 'bg-yellow-50 text-yellow-800'}`}>
        {profile.aprobado ? <FiCheckCircle className="h-6 w-6"/> : <FiAlertCircle className="h-6 w-6"/>}
        <div>
          <p className="font-bold">Estado: {profile.aprobado ? 'Aprobado' : 'Pendiente de Aprobación'}</p>
          <p className="text-sm">Categoría: {profile.categoria_nombre || 'No asignada'}</p>
        </div>
      </div>

      <FormSection title="Información Principal">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <InputField id="nombre_negocio" name="nombre_negocio" label="Nombre del Negocio" value={profile.nombre_negocio} onChange={handleChange} icon={<FiUser />} placeholder="Ej: Hotel Paraíso"/>
          <InputField id="telefono" name="telefono" label="Teléfono de Contacto" value={profile.telefono} onChange={handleChange} icon={<FiPhone />} placeholder="Ej: 3001234567"/>
          <InputField id="email_contacto" name="email_contacto" label="Email de Contacto" value={profile.email_contacto} onChange={handleChange} icon={<FiMail />} type="email" placeholder="Ej: contacto@hotelparaiso.com"/>
          <InputField id="direccion" name="direccion" label="Dirección" value={profile.direccion || ''} onChange={handleChange} icon={<FiMapPin />} placeholder="Ej: Calle 5 # 4-32"/>
          <div>
            <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">Departamento</label>
            <select id="department" name="department" value={profile.department || ''} onChange={handleChange} className="pl-10 pr-4 py-2.5 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all">
              <option value="">Seleccione un departamento</option>
              {departments.map(dep => <option key={dep.id} value={dep.id}>{dep.name}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="municipality" className="block text-sm font-medium text-gray-700 mb-1">Municipio</label>
            <select id="municipality" name="municipality" value={profile.municipality || ''} onChange={handleChange} disabled={!profile.department} className="pl-10 pr-4 py-2.5 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all disabled:bg-gray-200">
              <option value="">Seleccione un municipio</option>
              {municipalities.map(mun => <option key={mun.id} value={mun.id}>{mun.name}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label htmlFor="descripcion" className="block text-sm font-medium text-gray-700 mb-1">Descripción del Negocio</label>
          <textarea name="descripcion" id="descripcion" value={profile.descripcion} onChange={handleChange} rows={5} className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all" placeholder="Describe tu negocio, servicios y lo que te hace especial..."></textarea>
        </div>
      </FormSection>

      <FormSection title="Redes Sociales y Promociones">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <InputField id="red_social_facebook" name="red_social_facebook" label="Facebook (URL)" value={profile.red_social_facebook} onChange={handleChange} icon={<FiLink />} type="url" placeholder="https://facebook.com/..."/>
          <InputField id="red_social_instagram" name="red_social_instagram" label="Instagram (URL)" value={profile.red_social_instagram} onChange={handleChange} icon={<FiLink />} type="url" placeholder="https://instagram.com/..."/>
          <InputField id="red_social_whatsapp" name="red_social_whatsapp" label="WhatsApp" value={profile.red_social_whatsapp} onChange={handleChange} icon={<FaWhatsapp />} placeholder="Ej: 3001234567"/>
        </div>
        <div>
          <label htmlFor="promociones_ofertas" className="block text-sm font-medium text-gray-700 mb-1">Promociones y Ofertas Especiales</label>
          <textarea name="promociones_ofertas" id="promociones_ofertas" value={profile.promociones_ofertas} onChange={handleChange} rows={3} className="block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm transition-all" placeholder="Describe tus ofertas actuales..."></textarea>
        </div>
      </FormSection>

      {profile.categoria_nombre === 'Hotel' && (
        <FormSection title="Reporte de Ocupación (Exclusivo para Hoteles)">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <InputField id="reporte_ocupacion_nacional" name="reporte_ocupacion_nacional" label="Ocupación Nacional (%)" value={String(profile.reporte_ocupacion_nacional)} onChange={handleChange} icon={<FiTag />} type="number" />
            <InputField id="reporte_ocupacion_internacional" name="reporte_ocupacion_internacional" label="Ocupación Internacional (%)" value={String(profile.reporte_ocupacion_internacional)} onChange={handleChange} icon={<FiTag />} type="number" />
          </div>
        </FormSection>
      )}

      {profile.categoria_nombre === 'Agencias de Eventos' && (
        <FormSection title="Caracterización Específica">
          <p className="text-sm text-gray-600 mb-4">
            Complete el formulario de caracterización para que su perfil como agencia de eventos esté completo.
          </p>
          <button
            type="button"
            onClick={handleOpenEventosModal}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-purple-600 hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all"
          >
            <FiFileText className="h-5 w-5" />
            Gestionar Caracterización de Eventos
          </button>
        </FormSection>
      )}

      {profile.categoria_nombre === 'Agroturismo' && (
        <FormSection title="Caracterización Específica de Agroturismo">
          <p className="text-sm text-gray-600 mb-4">
            Complete el formulario de caracterización para que su perfil como operador de agroturismo esté completo.
          </p>
          <button
            type="button"
            onClick={handleOpenAgroModal}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all"
          >
            <FiFileText className="h-5 w-5" />
            Gestionar Caracterización de Agroturismo
          </button>
        </FormSection>
      )}

      <div className="bg-white p-6 rounded-xl shadow-md mt-8">
        <div className="flex flex-col sm:flex-row items-center justify-end gap-4">
            {success && <p className="text-green-600 font-semibold text-sm">{success}</p>}
            {error && <p className="text-red-600 font-semibold text-sm">{error}</p>}
            <button
            type="submit"
            disabled={isSaving}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 transition-all transform hover:scale-105"
            >
            {isSaving ? <FiLoader className="animate-spin h-5 w-5" /> : <FiSave className="h-5 w-5" />}
            {isSaving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
        </div>
      </div>

      <ImageGalleryManager initialImages={profile.galeria_imagenes} onUpdate={fetchProfile} />
      <DocumentManager initialDocuments={profile.documentos_legalizacion} onUpdate={fetchProfile} />
      <FeedbackProveedor />

      {isEventosModalOpen && profile && (
         <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex justify-center items-center p-4">
            <div className="bg-gray-50 p-6 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CaracterizacionEventosForm
                    initialData={eventosCaracterizacionData}
                    onSubmit={handleEventosSubmit}
                    onCancel={handleCloseModal}
                    prestadorId={profile.id}
                />
            </div>
        </div>
      )}

      {isAgroModalOpen && profile && (
         <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex justify-center items-center p-4">
            <div className="bg-gray-50 p-6 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CaracterizacionAgroturismoForm
                    initialData={agroCaracterizacionData}
                    onSubmit={handleAgroSubmit}
                    onCancel={handleCloseModal}
                    prestadorId={profile.id}
                />
            </div>
        </div>
      )}
    </form>
  );
}