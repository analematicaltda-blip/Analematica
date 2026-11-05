'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { getRutasTuristicas, RutaTuristica } from '@/services/api';
import { FiMap } from 'react-icons/fi';

// Componente para la tarjeta de una ruta turística
function RutaCard({ ruta }: { ruta: RutaTuristica }) {
  return (
    <Link href={`/descubre/rutas-turisticas/${ruta.slug}`} passHref>
      <div className="border rounded-lg shadow-md hover:shadow-xl transition-shadow flex flex-col h-full cursor-pointer group">
        <div className="relative w-full h-48 overflow-hidden">
          <Image
            src={ruta.imagen_principal_url || '/placeholder.png'}
            alt={`Imagen de ${ruta.nombre}`}
            layout="fill"
            objectFit="cover"
            className="rounded-t-lg transition-transform duration-300 group-hover:scale-110"
          />
        </div>
        <div className="p-4 flex flex-col flex-grow">
          <h3 className="text-xl font-bold mb-2 text-gray-800 group-hover:text-blue-600 transition-colors">{ruta.nombre}</h3>
          <p className="text-sm text-gray-600 flex-grow mb-4 line-clamp-3">{ruta.descripcion}</p>
          <div className="mt-auto text-blue-600 font-semibold flex items-center">
            Ver Ruta <FiMap className="ml-2" />
          </div>
        </div>
      </div>
    </Link>
  );
}

// Componente de esqueleto para la tarjeta
function RutaCardSkeleton() {
  return (
    <div className="border rounded-lg shadow-md animate-pulse">
      <div className="w-full h-48 bg-gray-300 rounded-t-lg"></div>
      <div className="p-4">
        <div className="h-6 bg-gray-300 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-300 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-300 rounded w-5/6"></div>
      </div>
    </div>
  );
}

// Componente principal de la página
export default function RutasTuristicasPage() {
  const [rutas, setRutas] = useState<RutaTuristica[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRutas() {
      try {
        setLoading(true);
        const fetchedRutas = await getRutasTuristicas();
        setRutas(fetchedRutas);
        setError(null);
      } catch (err) {
        setError('No se pudieron cargar las rutas turísticas. Por favor, inténtalo de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    }
    loadRutas();
  }, []);

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900">Nuestras Rutas Turísticas</h1>
        <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-600">
          Descubre los recorridos que hemos diseñado para que vivas una experiencia inolvidable.
        </p>
      </div>

      {error && <p className="text-center text-red-500">{error}</p>}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
        {loading ? (
          Array.from({ length: 6 }).map((_, index) => <RutaCardSkeleton key={index} />)
        ) : rutas.length > 0 ? (
          rutas.map((ruta) => (
            <RutaCard key={ruta.id} ruta={ruta} />
          ))
        ) : (
          <p className="text-center col-span-full text-gray-500">
            Actualmente no hay rutas turísticas disponibles. Vuelve a consultar pronto.
          </p>
        )}
      </div>
    </div>
  );
}