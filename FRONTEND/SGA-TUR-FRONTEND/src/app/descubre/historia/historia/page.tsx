"use client";

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { getHechosHistoricos, HechoHistorico } from '@/services/api';
import { FiCalendar } from 'react-icons/fi';

const TimelineItem = ({ hecho }: { hecho: HechoHistorico }) => (
  <div className={`flex items-center w-full my-6 md:my-0`}>
    <div className="hidden md:flex w-5/12"></div>
    <div className="hidden md:flex justify-center w-1/12">
      <div className="w-1 h-full bg-gray-300"></div>
      <div className="absolute w-6 h-6 rounded-full bg-blue-600 z-10 text-white flex items-center justify-center">
        <FiCalendar size={14} />
      </div>
    </div>
    <div className={`w-full md:w-5/12 px-4 py-6`}>
      <div className="bg-white p-6 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300 border-l-4 border-blue-600">
        {hecho.imagen_url && (
          <div className="mb-4 rounded-md overflow-hidden">
            <Image src={hecho.imagen_url} alt={`Ilustración de ${hecho.titulo}`} width={400} height={225} className="w-full h-auto object-cover" />
          </div>
        )}
        <p className="text-blue-600 font-bold text-2xl mb-2">{hecho.ano}</p>
        <h3 className="text-xl font-bold text-gray-800 mb-3">{hecho.titulo}</h3>
        <p className="text-gray-600 leading-relaxed">{hecho.descripcion}</p>
      </div>
    </div>
  </div>
);

const HistoriaPage = () => {
  const [hechos, setHechos] = useState<HechoHistorico[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistoria = async () => {
      setIsLoading(true);
      try {
        const data = await getHechosHistoricos(true); // true to fetch only public
        setHechos(data.sort((a, b) => a.ano - b.ano)); // Asegurar orden ascendente
      } catch (err) {
        setError('No se pudo cargar la historia del municipio. Por favor, intente más tarde.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistoria();
  }, []);

  return (
    <div className="bg-gray-50 min-h-screen">
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-6 py-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 leading-tight">
            Nuestra <span className="text-blue-600">Historia</span>
          </h1>
          <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
            Un recorrido a través de los años que han forjado la identidad y el progreso de nuestro municipio.
          </p>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12">
        {isLoading && <p className="text-center text-gray-500">Cargando la línea de tiempo...</p>}
        {error && <p className="text-center text-red-500">{error}</p>}

        {!isLoading && !error && (
          <div className="relative wrap overflow-hidden h-full">
            {/* La línea vertical para escritorio */}
            <div className="hidden md:block border-2-2 absolute border-opacity-20 border-gray-700 h-full border" style={{ left: '50%' }}></div>

            {hechos.map((hecho) => (
              <TimelineItem key={hecho.id} hecho={hecho} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default HistoriaPage;