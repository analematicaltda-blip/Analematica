'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { getRutaTuristicaBySlug, RutaTuristicaDetalle, PrestadorPublico } from '@/services/api';
import { FiMapPin, FiBriefcase, FiCamera, FiInfo } from 'react-icons/fi';
import 'yet-another-react-lightbox/styles.css';
import Lightbox from 'yet-another-react-lightbox';

// Reutilizamos un componente de tarjeta similar al del directorio de prestadores
function AssociatedCard({ item }: { item: PrestadorPublico }) {
  const isPrestador = 'categoria_nombre' in item;
  const link = isPrestador ? `/prestadores/${item.id}` : `/atractivos/${item.slug}`;

  return (
    <Link href={link} passHref>
      <div className="border rounded-lg shadow-sm hover:shadow-lg transition-shadow flex flex-col h-full cursor-pointer group bg-white">
        <div className="relative w-full h-40 overflow-hidden">
          <Image
            src={item.imagen_principal_url || '/placeholder.png'}
            alt={`Imagen de ${item.nombre_negocio || item.nombre}`}
            layout="fill"
            objectFit="cover"
            className="rounded-t-lg transition-transform duration-300 group-hover:scale-105"
          />
        </div>
        <div className="p-4 flex flex-col flex-grow">
          <h4 className="text-md font-bold text-gray-800">{item.nombre_negocio || item.nombre}</h4>
          {isPrestador && <p className="text-xs text-gray-500 mb-2">{item.categoria_nombre}</p>}
          <div className="mt-auto text-sm text-blue-600 font-semibold flex items-center pt-2">
            Ver Más <FiInfo className="ml-2" />
          </div>
        </div>
      </div>
    </Link>
  );
}

function SkeletonLoader() {
    return (
        <div className="container mx-auto px-4 py-12 animate-pulse">
            <div className="h-10 bg-gray-300 rounded w-2/3 mx-auto mb-4"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2 mx-auto mb-10"></div>
            <div className="h-64 bg-gray-300 rounded-lg mb-8"></div>
            <div className="space-y-4">
                <div className="h-4 bg-gray-300 rounded w-full"></div>
                <div className="h-4 bg-gray-300 rounded w-full"></div>
                <div className="h-4 bg-gray-300 rounded w-5/6"></div>
            </div>
        </div>
    );
}

export default function RutaDetailPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [ruta, setRuta] = useState<RutaTuristicaDetalle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  useEffect(() => {
    if (slug) {
      async function loadRuta() {
        try {
          setLoading(true);
          const fetchedRuta = await getRutaTuristicaBySlug(slug);
          setRuta(fetchedRuta);
          setError(null);
        } catch (err) {
          setError('No se pudo cargar la ruta turística. Es posible que no exista o haya ocurrido un error.');
        } finally {
          setLoading(false);
        }
      }
      loadRuta();
    }
  }, [slug]);

  if (loading) {
    return <SkeletonLoader />;
  }

  if (error) {
    return <div className="text-center py-20 text-red-500">{error}</div>;
  }

  if (!ruta) {
    return <div className="text-center py-20 text-gray-500">No se encontró la ruta turística.</div>;
  }

  const slides = ruta.imagenes.map(img => ({ src: img.imagen }));

  return (
    <div className="bg-gray-50">
      <div className="relative h-80 bg-black">
        <Image
          src={ruta.imagen_principal_url || '/placeholder.png'}
          alt={`Imagen de ${ruta.nombre}`}
          layout="fill"
          objectFit="cover"
          className="opacity-50"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <h1 className="text-4xl lg:text-6xl font-extrabold text-white text-center px-4">{ruta.nombre}</h1>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white p-8 rounded-lg shadow-lg -mt-24 relative z-10">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Descripción de la Ruta</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{ruta.descripcion}</p>

            {ruta.imagenes && ruta.imagenes.length > 0 && (
              <div className="mt-8">
                <button
                  onClick={() => setLightboxOpen(true)}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <FiCamera /> Ver Galería de Fotos
                </button>
                <Lightbox
                  open={lightboxOpen}
                  close={() => setLightboxOpen(false)}
                  slides={slides}
                />
              </div>
            )}
          </div>

          {ruta.atractivos && ruta.atractivos.length > 0 && (
            <div className="mt-12">
              <h3 className="text-3xl font-bold text-gray-800 mb-6 flex items-center"><FiMapPin className="mr-3 text-blue-500" /> Puntos de Interés en la Ruta</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {ruta.atractivos.map(item => <AssociatedCard key={`atractivo-${item.id}`} item={item} />)}
              </div>
            </div>
          )}

          {ruta.prestadores && ruta.prestadores.length > 0 && (
            <div className="mt-12">
              <h3 className="text-3xl font-bold text-gray-800 mb-6 flex items-center"><FiBriefcase className="mr-3 text-green-500" /> Servicios Recomendados</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {ruta.prestadores.map(item => <AssociatedCard key={`prestador-${item.id}`} item={item} />)}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}