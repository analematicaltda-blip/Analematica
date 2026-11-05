"use client";

import React, { useState } from 'react';
import Image from 'next/image';
import axios from 'axios';
import { useAuth } from '@/contexts/AuthContext';
import { FiAlertTriangle, FiCheckCircle, FiUploadCloud } from 'react-icons/fi';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Image {
  id: number;
  imagen: string;
  alt_text: string;
}

interface ImageGalleryManagerProps {
  initialImages: Image[];
  onUpdate: () => void; // Función para refrescar los datos del perfil
}

const MAX_IMAGES = 10;
const MIN_IMAGES_RECOMMENDED = 5;

export default function ImageGalleryManager({ initialImages, onUpdate }: ImageGalleryManagerProps) {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [altText, setAltText] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const imageCount = initialImages.length;
  const canUpload = imageCount < MAX_IMAGES;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canUpload) {
      setError(`No se pueden subir más de ${MAX_IMAGES} imágenes.`);
      return;
    }
    if (!file) {
      setError('Por favor, seleccione una imagen para subir.');
      return;
    }
    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('imagen', file);
    formData.append('alt_text', altText);

    try {
      await axios.post(`${API_BASE_URL}/galeria/prestador/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Token ${token}`,
        },
      });
      onUpdate();
      setFile(null);
      setAltText('');
    } catch (err) {
      setError('Error al subir la imagen.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('¿Está seguro de que desea eliminar esta imagen?')) {
      return;
    }
    try {
      await axios.delete(`${API_BASE_URL}/galeria/prestador/${id}/`, {
        headers: { Authorization: `Token ${token}` },
      });
      onUpdate();
    } catch (err) {
      alert('Error al eliminar la imagen.');
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100 mt-8">
      <h3 className="text-xl font-bold text-gray-800 mb-2">Galería de Imágenes</h3>
      <p className="text-sm text-gray-600 mb-4">
        Sube entre {MIN_IMAGES_RECOMMENDED} y {MAX_IMAGES} fotos de alta calidad para mostrar tu negocio.
      </p>

      {imageCount < MIN_IMAGES_RECOMMENDED && (
        <div className="p-3 mb-4 rounded-lg bg-yellow-50 text-yellow-800 flex items-center gap-3">
          <FiAlertTriangle className="h-5 w-5" />
          <p className="text-sm font-medium">
            ¡Te recomendamos subir al menos {MIN_IMAGES_RECOMMENDED} imágenes para tener un perfil más atractivo! ({imageCount}/{MIN_IMAGES_RECOMMENDED})
          </p>
        </div>
      )}

      {!canUpload && (
        <div className="p-3 mb-4 rounded-lg bg-red-50 text-red-800 flex items-center gap-3">
          <FiCheckCircle className="h-5 w-5" />
          <p className="text-sm font-medium">
            ¡Excelente! Has alcanzado el límite de {MAX_IMAGES} imágenes.
          </p>
        </div>
      )}

      {canUpload && (
        <form onSubmit={handleUpload} className="my-4 p-4 border rounded-lg bg-gray-50">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div>
              <label htmlFor="imagen" className="block text-sm font-medium text-gray-700">Nueva Imagen</label>
              <input type="file" name="imagen" id="imagen" accept="image/*" onChange={handleFileChange} className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"/>
            </div>
            <div>
              <label htmlFor="alt_text" className="block text-sm font-medium text-gray-700">Texto Alternativo (Descripción)</label>
              <input type="text" name="alt_text" id="alt_text" value={altText} onChange={(e) => setAltText(e.target.value)} className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" placeholder="Ej: Fachada del hotel" />
            </div>
          </div>
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          <button type="submit" disabled={isUploading || !file} className="mt-4 inline-flex items-center justify-center gap-2 px-6 py-3 border border-transparent shadow-sm text-sm font-semibold rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400 transition-all">
            <FiUploadCloud className="h-5 w-5" />
            {isUploading ? 'Subiendo...' : 'Subir Imagen'}
          </button>
        </form>
      )}

      <div className="grid grid-cols-2 gap-4 mt-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
        {initialImages.map((image) => (
          <div key={image.id} className="relative group aspect-w-1 aspect-h-1 rounded-lg overflow-hidden shadow-md">
            <Image src={image.imagen} alt={image.alt_text} layout="fill" objectFit="cover" className="transition-transform group-hover:scale-110" />
            <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-0 group-hover:bg-opacity-60 transition-opacity">
              <button onClick={() => handleDelete(image.id)} className="px-3 py-1 text-xs font-bold text-white bg-red-600 rounded-full hover:bg-red-700 opacity-0 group-hover:opacity-100 transition-opacity transform scale-90 group-hover:scale-100">
                Eliminar
              </button>
            </div>
          </div>
        ))}
      </div>
      {imageCount === 0 && <p className="text-sm text-gray-500 text-center py-4">No hay imágenes en la galería.</p>}
    </div>
  );
}