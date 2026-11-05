'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { getCategorias, getPrestadores, getPrestadorById, Categoria, PrestadorPublico, PrestadorPublicoDetalle } from '@/services/api';
import useDebounce from '@/hooks/useDebounce';
import Modal from '@/components/Modal';
import PrestadorCard from '@/components/common/PrestadorCard';
import PrestadorDetailModal from '@/components/common/PrestadorDetailModal';
import PrestadorCardSkeleton from '@/components/common/PrestadorCardSkeleton';

import MapaInteractivo from '@/components/common/MapaInteractivo';
import { getLocations, Location } from '@/services/api';

function PrestadoresContent() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [prestadores, setPrestadores] = useState<PrestadorPublico[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedCategoria, setSelectedCategoria] = useState<string | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedPrestador, setSelectedPrestador] = useState<PrestadorPublicoDetalle | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);

  const debouncedSearchTerm = useDebounce(searchTerm, 500);

  useEffect(() => {
    async function loadInitialData() {
      try {
        setLoading(true);
        const [fetchedCategorias, fetchedPrestadores, fetchedLocations] = await Promise.all([
          getCategorias(),
          getPrestadores(),
          getLocations(),
        ]);
        setCategorias(fetchedCategorias.filter(c => c.slug !== 'artesanos'));
        setPrestadores(fetchedPrestadores.filter(p => p.categoria_nombre !== 'Artesanos'));
        setLocations(fetchedLocations);
        setError(null);
      } catch (err) {
        setError('No se pudo cargar la información. Por favor, inténtalo de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    }
    loadInitialData();
  }, []);

  useEffect(() => {
    async function loadPrestadores() {
      try {
        setLoading(true);
        const fetchedPrestadores = await getPrestadores(selectedCategoria, debouncedSearchTerm);
        setPrestadores(fetchedPrestadores.filter(p => p.categoria_nombre !== 'Artesanos'));
        setError(null);
      } catch (err) {
        setError('No se pudo cargar los prestadores. Por favor, inténtalo de nuevo.');
      } finally {
        setLoading(false);
      }
    }
    loadPrestadores();
  }, [selectedCategoria, debouncedSearchTerm]);

  const handleViewMore = async (prestadorId: number) => {
    setIsModalLoading(true);
    try {
      const prestadorDetails = await getPrestadorById(prestadorId);
      setSelectedPrestador(prestadorDetails);
    } catch (error) {
      // Opcional: mostrar un toast o mensaje de error
    } finally {
      setIsModalLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedPrestador(null);
  };

  return (
    <>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-4">Directorio Turístico</h1>

        <div className="w-full max-w-md mx-auto mb-8">
          <input
            type="text"
            placeholder="¿Qué estás buscando? (ej. hotel, restaurante)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap justify-center gap-2 mb-8">
          <button
            onClick={() => setSelectedCategoria(undefined)}
            className={`px-4 py-2 rounded-full text-sm font-semibold ${!selectedCategoria ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
          >
            Todos
          </button>
          {categorias.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategoria(cat.slug)}
              className={`px-4 py-2 rounded-full text-sm font-semibold ${selectedCategoria === cat.slug ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}`}
            >
              {cat.nombre}
            </button>
          ))}
        </div>

        <div className="mb-8">
          <MapaInteractivo locations={locations} />
        </div>

        {error && <p className="text-center text-red-500">{error}</p>}

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {loading ? (
            Array.from({ length: 8 }).map((_, index) => <PrestadorCardSkeleton key={index} />)
          ) : prestadores.length > 0 ? (
            prestadores.map((prestador) => (
              <PrestadorCard
                key={prestador.id}
                prestador={prestador}
                onViewMore={() => handleViewMore(prestador.id)}
              />
            ))
          ) : (
            <p className="text-center col-span-full">
              No se encontraron resultados para tu búsqueda.
            </p>
          )}
        </div>
      </div>

      { (selectedPrestador || isModalLoading) && (
          <Modal title={selectedPrestador?.nombre_negocio || 'Cargando...'} onClose={closeModal}>
            {isModalLoading ? (
                <div className="text-center p-8">Cargando detalles...</div>
            ) : selectedPrestador ? (
                <PrestadorDetailModal prestador={selectedPrestador} />
            ) : null}
          </Modal>
      )}
    </>
  );
}

export default function PrestadoresPage() {
  return (
    <Suspense fallback={<div>Cargando...</div>}>
      <PrestadoresContent />
    </Suspense>
  );
}