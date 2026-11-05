"use client";

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { FiSave, FiLoader, FiCheckCircle, FiAlertCircle, FiFileText } from 'react-icons/fi';
import CaracterizacionArtesanoForm from './CaracterizacionArtesanoForm';
import {
    getArtesanoCaracterizacionByArtesanoId,
    createArtesanoCaracterizacion,
    updateArtesanoCaracterizacion,
    CaracterizacionArtesano,
    ImagenArtesano
} from '@/services/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ArtesanoProfileData {
  id: number;
  nombre_taller: string;
  nombre_artesano: string;
  descripcion: string;
  aprobado: boolean;
  foto_url: string | null;
  galeria_imagenes: ImagenArtesano[];
}

const FormSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
    <h3 className="text-xl font-bold text-gray-800 mb-6">{title}</h3>
    <div className="space-y-6">{children}</div>
  </div>
);

export default function ArtesanoProfileForm() {
  const { token } = useAuth();
  const [profile, setProfile] = useState<Partial<ArtesanoProfileData>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [caracterizacionData, setCaracterizacionData] = useState<CaracterizacionArtesano | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/profile/artesano/`, {
        headers: { Authorization: `Token ${token}` },
      });
      setProfile(response.data);
    } catch {
      setError('No se pudo cargar el perfil de artesano.');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfile(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      await axios.patch(`${API_BASE_URL}/profile/artesano/`, profile, {
        headers: { Authorization: `Token ${token}` },
      });
      setSuccess('¡Perfil actualizado con éxito!');
      setTimeout(() => setSuccess(null), 5000);
    } catch {
      setError('Error al guardar el perfil.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleOpenModal = async () => {
    if (!profile?.id) return;
    const data = await getArtesanoCaracterizacionByArtesanoId(profile.id);
    setCaracterizacionData(data);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setCaracterizacionData(null);
  };

  const handleFormSubmit = async (formData: FormData) => {
    if (!profile?.id) return;
    try {
      if (caracterizacionData) {
        await updateArtesanoCaracterizacion(caracterizacionData.id, formData);
      } else {
        formData.append('artesano', String(profile.id));
        await createArtesanoCaracterizacion(formData);
      }
      setSuccess('Caracterización guardada con éxito.');
      handleCloseModal();
    } catch {
      setError('Error al guardar la caracterización.');
    }
  };

  if (isLoading) return <p>Cargando perfil de artesano...</p>;
  if (error) return <p className="text-red-500">{error}</p>;
  if (!profile) return <p>No se encontró un perfil de artesano.</p>;

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
        <div className={`p-4 rounded-lg flex items-center gap-4 ${profile.aprobado ? 'bg-green-50 text-green-800' : 'bg-yellow-50 text-yellow-800'}`}>
            {profile.aprobado ? <FiCheckCircle className="h-6 w-6"/> : <FiAlertCircle className="h-6 w-6"/>}
            <p className="font-bold">Estado: {profile.aprobado ? 'Aprobado' : 'Pendiente de Aprobación'}</p>
        </div>

        <FormSection title="Información del Taller/Artesano">
            <input name="nombre_taller" value={profile.nombre_taller || ''} onChange={handleChange} placeholder="Nombre del Taller" className="input" />
            <input name="nombre_artesano" value={profile.nombre_artesano || ''} onChange={handleChange} placeholder="Nombre del Artesano" className="input" />
            <textarea name="descripcion" value={profile.descripcion || ''} onChange={handleChange} placeholder="Descripción" className="input w-full" rows={4}></textarea>
        </FormSection>

        <FormSection title="Caracterización Específica del Artesano">
          <p className="text-sm text-gray-600 mb-4">
            Complete el formulario de caracterización para que su perfil como artesano esté completo.
          </p>
          <button
            type="button"
            onClick={handleOpenModal}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-blue-600 hover:bg-blue-700"
          >
            <FiFileText className="h-5 w-5" />
            Gestionar Caracterización
          </button>
        </FormSection>

        <div className="flex justify-end items-center gap-4">
            {success && <p className="text-green-600">{success}</p>}
            <button type="submit" disabled={isSaving} className="btn-primary">
                {isSaving ? <FiLoader className="animate-spin" /> : <FiSave />}
                {isSaving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
        </div>

        {isModalOpen && profile.id && (
            <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center">
                <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                    <CaracterizacionArtesanoForm
                        initialData={caracterizacionData}
                        onSubmit={handleFormSubmit}
                        onCancel={handleCloseModal}
                        artesanoId={profile.id}
                    />
                </div>
            </div>
        )}
    </form>
  );
}