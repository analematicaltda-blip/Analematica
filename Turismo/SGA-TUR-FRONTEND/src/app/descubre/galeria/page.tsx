"use client";

import { useState, useEffect } from 'react';
import { getGaleriaMedia, GaleriaItem } from '@/services/api';
import Image from 'next/image';
import Lightbox from "yet-another-react-lightbox";
import "yet-another-react-lightbox/styles.css";
import { FiPlayCircle } from 'react-icons/fi';

const GalleryPage = () => {
  const [items, setItems] = useState<GaleriaItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [index, setIndex] = useState(-1);

  useEffect(() => {
    const fetchMedia = async () => {
      try {
        const media = await getGaleriaMedia();
        setItems(media);
      } catch {
        setError("No se pudo cargar el contenido de la galería.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchMedia();
  }, []);

  const slides = items.map(item => ({
      src: item.tipo === 'video' ? item.thumbnail_url : item.url,
      type: item.tipo,
      width: 1280,
      height: 720,
      title: item.titulo,
      description: item.descripcion,
      youtubeId: item.tipo === 'video' ? new URL(item.url).searchParams.get('v') : undefined
  }));

  if (isLoading) {
    return <div className="text-center py-20">Cargando galería...</div>;
  }

  if (error) {
    return <div className="text-center py-20 text-red-500">{error}</div>;
  }

  return (
    <div className="font-sans bg-gray-50">
        <div className="bg-gray-800 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-5xl font-extrabold">Galería Multimedia</h1>
            <p className="mt-4 text-xl text-gray-300">
              Explora la belleza de nuestro municipio a través de imágenes y videos.
            </p>
          </div>
        </div>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {items.map((item, i) => (
                    <div key={item.id} className="group relative cursor-pointer" onClick={() => setIndex(i)}>
                        <Image
                            src={item.thumbnail_url}
                            alt={item.titulo}
                            width={400}
                            height={400}
                            className="w-full h-full object-cover rounded-lg shadow-md aspect-square transition-transform duration-300 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center rounded-lg">
                            {item.tipo === 'video' && <FiPlayCircle className="text-white text-5xl opacity-0 group-hover:opacity-100 transition-opacity" />}
                        </div>
                    </div>
                ))}
            </div>
        </main>

        <Lightbox
            open={index >= 0}
            close={() => setIndex(-1)}
            slides={slides}
            index={index}
        />
    </div>
  );
};

export default GalleryPage;