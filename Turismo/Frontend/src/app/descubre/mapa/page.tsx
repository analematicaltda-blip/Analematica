import MapComponent from '@/components/MapComponent';
import React from 'react';

export default function MapaInteractivoPage() {
  return (
    <div className="bg-gray-100 py-12">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Mapa Interactivo del Paraíso
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            Explora todos los atractivos y servicios turísticos en un solo lugar.
          </p>
        </div>

        <div className="bg-white p-4 rounded-xl shadow-lg">
          <MapComponent />
        </div>
      </div>
    </div>
  );
}