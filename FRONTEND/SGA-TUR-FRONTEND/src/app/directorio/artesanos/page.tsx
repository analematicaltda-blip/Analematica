"use client";

import React, { useState, useEffect, Suspense } from 'react';
import { getArtesanos, getArtesanoById, getRubrosArtesano, ArtesanoPublico, ArtesanoPublicoDetalle, RubroArtesano } from '@/services/api';
import useDebounce from '@/hooks/useDebounce';
import Modal from '@/components/Modal';
import ArtesanoCard from '@/components/common/ArtesanoCard';
import ArtesanoDetailModal from '@/components/common/ArtesanoDetailModal';
import PrestadorCardSkeleton from '@/components/common/PrestadorCardSkeleton'; // Reutilizamos el esqueleto de prestador por simplicidad
import { FaTag } from 'react-icons/fa';
import { FiSearch } from 'react-icons/fi';

const ArtesanosContent = () => {
  const [artesanos, setArtesanos] = useState<ArtesanoPublico[]>([]);
  const [rubros, setRubros] = useState<RubroArtesano[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRubro, setSelectedRubro] = useState('');

  const [selectedArtesano, setSelectedArtesano] = useState<ArtesanoPublicoDetalle | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);

  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [rubrosData, artesanosData] = await Promise.all([
          getRubrosArtesano(),
          getArtesanos(selectedRubro, debouncedSearchTerm)
        ]);
        setRubros(rubrosData);
        setArtesanos(artesanosData);
      } catch (err) {
        setError('Error al cargar los datos. Por favor, inténtelo más tarde.');
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [selectedRubro, debouncedSearchTerm]);

  const handleViewMore = async (artesanoId: number) => {
    setIsModalLoading(true);
    try {
      const artesanoDetails = await getArtesanoById(artesanoId);
      setSelectedArtesano(artesanoDetails);
    } catch (error) {
      setError('No se pudieron cargar los detalles del artesano.');
    } finally {
      setIsModalLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedArtesano(null);
  };

  return (
    <>
      <div className="bg-gray-50 min-h-screen">
        <header className="bg-white shadow-sm">
          <div className="container mx-auto px-6 py-12 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-800">
              Directorio de <span className="text-blue-600">Artesanos</span>
            </h1>
            <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
              Descubre el talento y la creatividad de los artesanos de nuestro municipio.
            </p>
          </div>
        </header>

        <main className="container mx-auto px-6 py-10">
          <div className="bg-white p-6 rounded-xl shadow-md mb-10 sticky top-4 z-10">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="relative">
                <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por nombre de taller o artesano..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="relative">
                <FaTag className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                <select
                  value={selectedRubro}
                  onChange={(e) => setSelectedRubro(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
                >
                  <option value="">Todos los Rubros</option>
                  {rubros.map(rubro => (
                    <option key={rubro.id} value={rubro.slug}>{rubro.nombre}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {error && <div className="text-center py-20"><p className="text-red-500">{error}</p></div>}

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
            {isLoading ? (
              Array.from({ length: 8 }).map((_, index) => <PrestadorCardSkeleton key={index} />)
            ) : artesanos.length > 0 ? (
              artesanos.map((artesano) => (
                <ArtesanoCard key={artesano.id} artesano={artesano} onViewMore={() => handleViewMore(artesano.id)} />
              ))
            ) : (
              <div className="text-center py-20 col-span-full">
                <p className="text-xl text-gray-500">No se encontraron artesanos que coincidan con su búsqueda.</p>
              </div>
            )}
          </div>
        </main>
      </div>

      {(selectedArtesano || isModalLoading) && (
        <Modal title={selectedArtesano?.nombre_taller || 'Cargando...'} onClose={closeModal}>
          {isModalLoading ? (
              <div className="text-center p-8">Cargando detalles...</div>
          ) : selectedArtesano ? (
              <ArtesanoDetailModal artesano={selectedArtesano} />
          ) : null}
        </Modal>
      )}
    </>
  );
};

export default function ArtesanosPage() {
    return (
        <Suspense fallback={<div className="text-center py-20">Cargando directorio...</div>}>
            <ArtesanosContent />
        </Suspense>
    )
}