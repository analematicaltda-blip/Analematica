"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';
import axios from 'axios';
import Link from 'next/link';
import Image from 'next/image';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const containerStyle = {
  width: '100%',
  height: '80vh',
  borderRadius: '0.5rem',
};

const center = {
  lat: 4.3155,
  lng: -72.0819
};

interface Location {
  id: string;
  nombre: string;
  lat: number;
  lng: number;
  tipo: string;
  url_detalle: string | null;
}

// Mapa de tipos a colores de marcador e iconos
const iconMap: { [key: string]: { icon: string, name: string } } = {
  hotel: { icon: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png', name: 'Hoteles' },
  restaurante: { icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png', name: 'Restaurantes' },
  bar: { icon: 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png', name: 'Bares' },
  discoteca: { icon: 'http://maps.google.com/mapfiles/ms/icons/pink-dot.png', name: 'Discotecas' },
  agencia: { icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png', name: 'Agencias' },
  guia: { icon: 'http://maps.google.com/mapfiles/ms/icons/ltblue-dot.png', name: 'Guías' },
  artesano: { icon: 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png', name: 'Artesanos' },
  atractivo_amarillo: { icon: 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png', name: 'Atractivos Culturales' },
  atractivo_rojo: { icon: 'http://maps.google.com/mapfiles/ms/icons/red-pushpin.png', name: 'Atractivos Urbanos' },
  atractivo_blanco: { icon: 'http://maps.google.com/mapfiles/ms/icons/green-pushpin.png', name: 'Atractivos Naturales' },
  default: { icon: 'http://maps.google.com/mapfiles/ms/icons/grey-dot.png', name: 'Otros' }
};

export default function MapComponent() {
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ""
  });

  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [activeFilters, setActiveFilters] = useState<Set<string>>(new Set(Object.keys(iconMap)));

  useEffect(() => {
    axios.get(`${API_BASE_URL}/locations/`)
      .then(response => setLocations(response.data))
  }, []);

  const handleFilterToggle = (tipo: string) => {
    setActiveFilters(prev => {
      const newFilters = new Set(prev);
      if (newFilters.has(tipo)) {
        newFilters.delete(tipo);
      } else {
        newFilters.add(tipo);
      }
      return newFilters;
    });
  };

  const filteredLocations = useMemo(() =>
    locations.filter(loc => activeFilters.has(loc.tipo) || activeFilters.has(loc.tipo.split('_')[0]) || activeFilters.has('default'))
  , [locations, activeFilters]);

  if (loadError) return <div>Error al cargar el mapa. Verifique la clave de API.</div>;
  if (!isLoaded) return <div className="text-center py-10">Cargando mapa...</div>;

  return (
    <div className="flex flex-col md:flex-row gap-4">
      {/* Panel de Filtros */}
      <div className="md:w-1/4 bg-white p-4 rounded-lg shadow-md">
        <h3 className="font-bold text-lg mb-4">Filtrar por Categoría</h3>
        <div className="space-y-2">
          {Object.entries(iconMap).map(([tipo, { name, icon }]) => (
            <div key={tipo} className="flex items-center">
              <input
                type="checkbox"
                id={`filter-${tipo}`}
                checked={activeFilters.has(tipo)}
                onChange={() => handleFilterToggle(tipo)}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor={`filter-${tipo}`} className="ml-3 flex items-center text-sm text-gray-600">
                <Image src={icon} alt={name} width={16} height={16} className="mr-2" />
                {name}
              </label>
            </div>
          ))}
        </div>
      </div>

      {/* Mapa */}
      <div className="flex-grow">
        <GoogleMap mapContainerStyle={containerStyle} center={center} zoom={13}>
          {filteredLocations.map((loc) => (
            <Marker
              key={loc.id}
              position={{ lat: loc.lat, lng: loc.lng }}
              title={loc.nombre}
              icon={{ url: iconMap[loc.tipo]?.icon || iconMap.default.icon }}
              onClick={() => setSelectedLocation(loc)}
            />
          ))}

          {selectedLocation && (
            <InfoWindow
              position={{ lat: selectedLocation.lat, lng: selectedLocation.lng }}
              onCloseClick={() => setSelectedLocation(null)}
            >
              <div className="p-2">
                <h4 className="font-bold">{selectedLocation.nombre}</h4>
                {selectedLocation.url_detalle ? (
                  <Link href={selectedLocation.url_detalle} className="text-indigo-600 hover:underline text-sm">
                    Ver más detalles
                  </Link>
                ) : (
                  <p className="text-sm text-gray-500">Más información próximamente</p>
                )}
              </div>
            </InfoWindow>
          )}
        </GoogleMap>
      </div>
    </div>
  );
}