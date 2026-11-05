"use client";

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import SaveButton from '@/components/SaveButton';
import Image from 'next/image';
import { ViewState } from '@/components/ui/ViewState';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface Atractivo {
  id: number;
  nombre: string;
  slug: string;
  descripcion: string;
  categoria_color: 'AMARILLO' | 'ROJO' | 'BLANCO';
  imagen_principal_url: string | null;
}

const CategoriaInfo = {
  AMARILLO: { nombre: 'Cultural / Histórico', color: 'bg-yellow-400' },
  ROJO: { nombre: 'Urbano / Parque', color: 'bg-red-500' },
  BLANCO: { nombre: 'Natural', color: 'bg-blue-400' },
  TODOS: { nombre: 'Todos', color: 'bg-gray-500' }
};

function AtractivosContent() {
  const [atractivos, setAtractivos] = useState<Atractivo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const searchParams = useSearchParams();
  const initialCategory = searchParams.get('categoria')?.toUpperCase();
  const [filter, setFilter] = useState<'TODOS' | 'AMARILLO' | 'ROJO' | 'BLANCO'>(() => {
    if (initialCategory && ['AMARILLO', 'ROJO', 'BLANCO'].includes(initialCategory)) {
        return initialCategory as 'AMARILLO' | 'ROJO' | 'BLANCO';
    }
    return 'TODOS';
  });

  useEffect(() => {
    const fetchAtractivos = async () => {
      setIsLoading(true);
      try {
        const params = filter === 'TODOS' ? {} : { categoria: filter };
        const response = await axios.get(`${API_BASE_URL}/atractivos/`, { params });
        setAtractivos(response.data);
      } catch (err) {
        setError('No se pudieron cargar los atractivos. Por favor, intente de nuevo más tarde.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchAtractivos();
  }, [filter]);

  return (
    <div className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Atractivos Turísticos
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            Explora la riqueza cultural, urbana y natural de nuestro paraíso.
          </p>
        </div>

        {/* Filtros */}
        <div className="mt-8 flex justify-center gap-2 flex-wrap">
          {(['TODOS', 'AMARILLO', 'ROJO', 'BLANCO'] as const).map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${filter === cat ? `${CategoriaInfo[cat].color} text-white` : 'bg-white text-gray-700 hover:bg-gray-200'}`}
            >
              {CategoriaInfo[cat].nombre}
            </button>
          ))}
        </div>

        {/* Contenido */}
        <div className="mt-12">
          <ViewState
             isLoading={isLoading}
             loadingMessage="Descubriendo atractivos del paraíso..."
             isEmpty={atractivos.length === 0 && !isLoading}
             emptyMessage="No se han encontrado atractivos turísticos en esta categoría por el momento."
             error={error}
          >
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {atractivos.map((atractivo) => (
                <div key={atractivo.id} className="border rounded-lg shadow-md hover:shadow-xl transition-shadow flex flex-col h-full bg-white">
                    <div className="relative w-full h-48">
                        <Image
                          src={atractivo.imagen_principal_url || '/placeholder.png'}
                          alt={`Imagen de ${atractivo.nombre}`}
                          layout="fill"
                          objectFit="cover"
                          className="rounded-t-lg"
                        />
                        <span className={`absolute bottom-2 left-2 px-2 py-1 text-xs font-bold text-white rounded-full ${CategoriaInfo[atractivo.categoria_color].color}`}>
                            {CategoriaInfo[atractivo.categoria_color].nombre}
                        </span>
                         <SaveButton contentType="atractivoturistico" objectId={atractivo.id} />
                    </div>
                    <div className="p-4 flex flex-col flex-grow">
                        <h3 className="text-lg font-bold mb-1">{atractivo.nombre}</h3>
                        <p className="text-xs text-gray-700 flex-grow mb-3 line-clamp-3">{atractivo.descripcion || "Sin descripción disponible."}</p>
                        <Link href={`/descubre/atractivos/${atractivo.slug}`} className="mt-auto w-full bg-blue-600 text-white px-4 py-2 rounded text-center hover:bg-blue-700 transition-colors">
                            Ver más
                        </Link>
                    </div>
                </div>
              ))}
            </div>
          </ViewState>
        </div>
      </div>
    </div>
  );
}

export default function AtractivosPage() {
  return (
    <Suspense fallback={<div className="py-20 text-center">Cargando filtros...</div>}>
      <AtractivosContent />
    </Suspense>
  );
}