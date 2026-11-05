"use client";

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { getPublicaciones, Publicacion } from '@/services/api';
import { FiCalendar } from 'react-icons/fi';

const NoticiaCard = ({ noticia }: { noticia: Publicacion }) => {
  const fallbackImage = "/images/placeholder.png"; // Provide a fallback image path

  return (
    <Link href={`/publicaciones/${noticia.slug}`} legacyBehavior>
      <a className="block bg-white rounded-lg shadow-lg overflow-hidden transform hover:-translate-y-1 transition-all duration-300 group">
        <div className="relative h-56 w-full">
          <Image
            src={noticia.imagen_principal || fallbackImage}
            alt={`Imagen para ${noticia.titulo}`}
            layout="fill"
            objectFit="cover"
            className="group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className="p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-3 h-16 overflow-hidden">{noticia.titulo}</h3>
          <div className="flex items-center text-sm text-gray-500">
            <FiCalendar className="mr-2" />
            <span>{new Date(noticia.fecha_publicacion).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
          </div>
        </div>
      </a>
    </Link>
  );
};

const NoticiasPage = () => {
  const [noticias, setNoticias] = useState<Publicacion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNoticias = async () => {
      setIsLoading(true);
      try {
        const data = await getPublicaciones({ tipo: 'NOTICIA' });
        setNoticias(data || []);
      } catch (err) {
        setError('No se pudieron cargar las noticias. Por favor, intente más tarde.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchNoticias();
  }, []);

  return (
    <div className="bg-gray-50 min-h-screen">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-6 py-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 leading-tight">
            Últimas <span className="text-blue-600">Noticias</span>
          </h1>
          <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
            Manténgase informado sobre los acontecimientos más recientes y relevantes de nuestro municipio.
          </p>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        {isLoading && <p className="text-center text-gray-500">Cargando noticias...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}

        {!isLoading && !error && (
          noticias.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {noticias.map((noticia) => (
                <NoticiaCard key={noticia.id} noticia={noticia} />
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-20">No hay noticias para mostrar en este momento.</p>
          )
        )}
      </main>
    </div>
  );
};

export default NoticiasPage;