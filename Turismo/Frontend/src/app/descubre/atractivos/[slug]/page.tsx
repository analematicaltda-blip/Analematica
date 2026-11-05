"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'next/navigation';
import Slider from 'react-slick';
import Image from 'next/image';
import Link from 'next/link';
import { FiHome, FiCoffee } from 'react-icons/fi';

// Importar los estilos del carrusel
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Imagen {
  id: number;
  imagen: string;
  alt_text: string;
}

interface AtractivoDetalle {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  como_llegar: string;
  ubicacion_mapa: string;
  categoria_color: string;
  categoria_color_display: string;
  imagenes: Imagen[];
}

export default function AtractivoDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [atractivo, setAtractivo] = useState<AtractivoDetalle | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (slug) {
      const fetchAtractivo = async () => {
        setIsLoading(true);
        try {
          const response = await axios.get(`${API_BASE_URL}/atractivos/${slug}/`);
          setAtractivo(response.data);
        } catch (err) {
          setError('No se pudo encontrar el atractivo turístico.');
        } finally {
          setIsLoading(false);
        }
      };
      fetchAtractivo();
    }
  }, [slug]);

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 3000,
    adaptiveHeight: true,
  };

  if (isLoading) {
    return <div className="text-center py-20">Cargando atractivo...</div>;
  }

  if (error) {
    return <div className="text-center py-20 text-red-500">{error}</div>;
  }

  if (!atractivo) {
    return null;
  }

  return (
    <div className="bg-white">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Slider de Imágenes */}
        <div className="mb-8 rounded-lg overflow-hidden shadow-lg">
          {atractivo.imagenes && atractivo.imagenes.length > 0 ? (
            <Slider {...sliderSettings}>
              {atractivo.imagenes.map(img => (
                <div key={img.id} className="relative w-full h-96">
                  <Image
                    src={img.imagen}
                    alt={img.alt_text || atractivo.nombre}
                    layout="fill"
                    objectFit="cover"
                  />
                </div>
              ))}
            </Slider>
          ) : (
            <div className="w-full h-96 bg-gray-200 flex items-center justify-center">
              <p className="text-gray-500">No hay imágenes disponibles</p>
            </div>
          )}
        </div>

        {/* Contenido del Atractivo */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2">
            <span className="text-sm font-semibold text-indigo-600 uppercase">{atractivo.categoria_color_display}</span>
            <h1 className="mt-2 text-4xl font-extrabold text-gray-900 tracking-tight">
              {atractivo.nombre}
            </h1>

            <div className="mt-6 prose prose-lg text-gray-700 max-w-none">
              <h2 className="font-bold text-xl text-gray-800 border-b pb-2 mb-4">Descripción</h2>
              <p>{atractivo.descripcion}</p>

              <h2 className="mt-8 font-bold text-xl text-gray-800 border-b pb-2 mb-4">¿Cómo Llegar?</h2>
              <p>{atractivo.como_llegar}</p>
            </div>
          </div>

          {/* Mapa de Ubicación y Servicios Cercanos */}
          <div className="md:col-span-1">
            <div className="bg-gray-50 p-6 rounded-lg shadow-md sticky top-24 space-y-6">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Ubicación</h3>
                {atractivo.ubicacion_mapa ? (
                   <div className="mt-4 h-64 bg-gray-300 rounded-md flex items-center justify-center overflow-hidden">
                      <iframe
                        width="100%"
                        height="100%"
                        frameBorder="0" style={{ border: 0 }}
                        src={`https://www.google.com/maps/embed/v1/place?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY}&q=${atractivo.ubicacion_mapa}`}
                        allowFullScreen
                      ></iframe>
                   </div>
                ) : (
                  <p className="mt-4 text-gray-600">Ubicación no especificada.</p>
                )}
              </div>

              <div>
                 <h3 className="text-lg font-bold text-gray-900 border-b pb-2 mb-4">Servicios Cercanos</h3>
                 <p className="text-sm text-slate-500 italic mb-4">Encuentra los mejores lugares cerca de {atractivo.nombre}.</p>
                 <div className="space-y-4">
                    <Link href="/directorio/prestadores?cat=hoteles" className="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-indigo-300 transition-all shadow-sm group">
                       <div className="w-10 h-10 bg-indigo-50 text-indigo-500 rounded-lg flex items-center justify-center group-hover:bg-indigo-500 group-hover:text-white transition-colors">
                          <FiHome />
                       </div>
                       <span className="font-bold text-slate-700">Hoteles</span>
                    </Link>
                    <Link href="/directorio/prestadores?cat=restaurantes" className="flex items-center gap-3 p-3 bg-white rounded-xl border border-slate-100 hover:border-indigo-300 transition-all shadow-sm group">
                       <div className="w-10 h-10 bg-emerald-50 text-emerald-500 rounded-lg flex items-center justify-center group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                          <FiCoffee />
                       </div>
                       <span className="font-bold text-slate-700">Restaurantes</span>
                    </Link>
                 </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}