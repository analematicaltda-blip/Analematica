import React from 'react';
import { PrestadorPublico } from '@/services/api';
import PrestadorCard from './PrestadorCard';

interface PrestadorGridProps {
  prestadores: PrestadorPublico[];
}

const PrestadorGrid: React.FC<PrestadorGridProps> = ({ prestadores }) => {
  if (prestadores.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">No se encontraron prestadores de servicios.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {prestadores.map((prestador) => (
        <PrestadorCard key={prestador.id} prestador={prestador} />
      ))}
    </div>
  );
};

export default PrestadorGrid;