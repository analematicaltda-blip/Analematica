"use client";

import React, { useState, useEffect, useCallback, FormEvent } from 'react';
import Image from 'next/image';
import { FiPlus, FiEdit, FiTrash2, FiImage } from 'react-icons/fi';
import {
  getPaginasInstitucionalesAdmin,
  createPaginaInstitucional,
  updatePaginaInstitucional,
  deletePaginaInstitucional,
  PaginaInstitucional,
} from '@/services/api';

// --- Componente de Formulario ---
const PageForm = ({
  onSubmit,
  onCancel,
  initialData,
}: {
  onSubmit: (data: FormData) => void;
  onCancel: () => void;
  initialData?: PaginaInstitucional | null;
}) => {
  const [formData, setFormData] = useState({
    nombre: initialData?.nombre || '',
    slug: initialData?.slug || '',
    titulo_banner: initialData?.titulo_banner || '',
    subtitulo_banner: initialData?.subtitulo_banner || '',
    contenido_principal: initialData?.contenido_principal || '',
    programas_proyectos: initialData?.programas_proyectos || '',
    estrategias_apoyo: initialData?.estrategias_apoyo || '',
    politicas_locales: initialData?.politicas_locales || '',
    convenios_asociaciones: initialData?.convenios_asociaciones || '',
    informes_resultados: initialData?.informes_resultados || '',
  });
  const [bannerFile, setBannerFile] = useState<File | null>(null);
  const [bannerPreview, setBannerPreview] = useState<string | null>(initialData?.banner_url || null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const file = e.target.files[0];
      setBannerFile(file);
      setBannerPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const data = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      data.append(key, value);
    });
    if (bannerFile) {
      data.append('banner', bannerFile);
    }
    onSubmit(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50 p-4">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-3xl">
        <h2 className="text-2xl font-bold mb-6">{initialData ? 'Editar' : 'Crear'} Página Institucional</h2>
        <form onSubmit={handleSubmit} className="space-y-4 max-h-[85vh] overflow-y-auto pr-4">
          <input type="text" name="nombre" value={formData.nombre} onChange={handleInputChange} placeholder="Nombre de la Página (interno)" className="w-full px-3 py-2 border rounded-md" required />
          <input type="text" name="slug" value={formData.slug} onChange={handleInputChange} placeholder="Slug para la URL (ej: mi-pagina-nueva)" className="w-full px-3 py-2 border rounded-md" required />
          <hr/>
          <h3 className="font-semibold text-lg">Contenido del Banner</h3>
          <input type="text" name="titulo_banner" value={formData.titulo_banner} onChange={handleInputChange} placeholder="Título del Banner" className="w-full px-3 py-2 border rounded-md" required />
          <input type="text" name="subtitulo_banner" value={formData.subtitulo_banner} onChange={handleInputChange} placeholder="Subtítulo del Banner (opcional)" className="w-full px-3 py-2 border rounded-md" />
          <div>
            <label className="block text-sm font-medium text-gray-700">Imagen del Banner</label>
            <div className="mt-2 flex items-center space-x-4">
              {bannerPreview ? <Image src={bannerPreview} alt="Vista previa" width={160} height={90} className="h-24 w-auto rounded-md object-cover bg-gray-100" /> : <div className="h-24 w-40 bg-gray-100 rounded-md flex items-center justify-center text-gray-400"><FiImage size={32}/></div>}
              <input type="file" accept="image/*" onChange={handleFileChange} className="block text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
            </div>
          </div>
          <hr/>
          <h3 className="font-semibold text-lg">Secciones de Contenido (Secretaría)</h3>
          <textarea name="contenido_principal" value={formData.contenido_principal} onChange={handleInputChange} placeholder="Contenido Principal (Objetivos, funciones, etc.)" rows={5} className="w-full px-3 py-2 border rounded-md" />
          <textarea name="programas_proyectos" value={formData.programas_proyectos} onChange={handleInputChange} placeholder="Programas y Proyectos" rows={5} className="w-full px-3 py-2 border rounded-md" />
          <textarea name="estrategias_apoyo" value={formData.estrategias_apoyo} onChange={handleInputChange} placeholder="Estrategias de Apoyo" rows={5} className="w-full px-3 py-2 border rounded-md" />

          <hr/>
          <h3 className="font-semibold text-lg">Secciones Adicionales (Dirección)</h3>
          <textarea name="politicas_locales" value={formData.politicas_locales} onChange={handleInputChange} placeholder="Políticas Locales de Turismo" rows={5} className="w-full px-3 py-2 border rounded-md" />
          <textarea name="convenios_asociaciones" value={formData.convenios_asociaciones} onChange={handleInputChange} placeholder="Convenios y Asociaciones" rows={5} className="w-full px-3 py-2 border rounded-md" />
          <textarea name="informes_resultados" value={formData.informes_resultados} onChange={handleInputChange} placeholder="Informes de Resultados" rows={5} className="w-full px-3 py-2 border rounded-md" />

          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Guardar Página</button>
          </div>
        </form>
      </div>
    </div>
  );
};


// --- Componente Principal del Gestor ---
export default function PaginaInstitucionalManager() {
  const [paginas, setPaginas] = useState<PaginaInstitucional[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPage, setEditingPage] = useState<PaginaInstitucional | null>(null);

  const fetchPages = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getPaginasInstitucionalesAdmin();
      setPaginas(response.results || []);
    } catch (err) {
      setError("No se pudieron cargar las páginas.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchPages(); }, [fetchPages]);

  const handleOpenModal = (page?: PaginaInstitucional) => {
    setEditingPage(page || null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingPage(null);
  };

  const handleSavePage = async (data: FormData) => {
    setError(null);
    try {
      if (editingPage?.slug) {
        await updatePaginaInstitucional(editingPage.slug, data);
      } else {
        await createPaginaInstitucional(data);
      }
      fetchPages();
      handleCloseModal();
    } catch (err) {
      setError(`Error al guardar la página: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  const handleDeletePage = async (slug: string) => {
    if (!window.confirm("¿Está seguro de que desea eliminar esta página? Esta acción es irreversible.")) return;
    setError(null);
    try {
      await deletePaginaInstitucional(slug);
      fetchPages();
    } catch (err) {
      setError(`Error al eliminar la página: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  if (isLoading) return <p className="text-center py-8">Cargando...</p>;
  if (error) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      {isModalOpen && <PageForm onSubmit={handleSavePage} onCancel={handleCloseModal} initialData={editingPage} />}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Páginas Institucionales</h2>
        <button onClick={() => handleOpenModal()} className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm">
          <FiPlus className="mr-2" />Crear Página
        </button>
      </div>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="divide-y divide-gray-200">
          {paginas.length > 0 ? paginas.map(page => (
            <div key={page.id} className="p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center">
              <div className="flex items-center mb-2 sm:mb-0">
                <Image src={page.banner_url} alt={page.nombre} width={128} height={72} className="h-12 w-20 object-cover rounded-md bg-gray-100" />
                <div className="ml-4">
                  <p className="font-bold text-gray-900">{page.nombre}</p>
                  <p className="text-sm text-gray-500">/{page.slug}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2 self-end sm:self-center">
                <button onClick={() => handleOpenModal(page)} className="p-2 text-gray-500 hover:text-blue-600 rounded-full hover:bg-blue-100 transition-colors"><FiEdit size={16} /></button>
                <button onClick={() => handleDeletePage(page.slug)} className="p-2 text-gray-500 hover:text-red-600 rounded-full hover:bg-red-100 transition-colors"><FiTrash2 size={16} /></button>
              </div>
            </div>
          )) : (
            <p className="text-center text-gray-500 py-12">No hay páginas institucionales creadas.</p>
          )}
        </div>
      </div>
    </div>
  );
}