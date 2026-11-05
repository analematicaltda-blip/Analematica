'use client';

import React from 'react';
import { GoogleMap, useJsApiLoader, MarkerF } from '@react-google-maps/api';

const containerStyle = {
  width: '100%',
  height: '400px',
  borderRadius: '0.5rem',
};

const defaultCenter = {
  lat: 4.1426, // Coordenadas de Villavicencio como centro por defecto
  lng: -73.626,
};

interface Location {
    id: string;
    nombre: string;
    lat: number;
    lng: number;
    tipo: string;
    url_detalle: string | null;
}

interface MapaInteractivoProps {
    locations: Location[];
}

const MapaInteractivo = ({ locations }: MapaInteractivoProps) => {
  const { isLoaded } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || "",
  });

  if (!isLoaded) return <div>Cargando mapa...</div>;

  return (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={defaultCenter}
      zoom={10}
    >
      {locations.map((location) => (
        <MarkerF
          key={location.id}
          position={{ lat: location.lat, lng: location.lng }}
          title={location.nombre}
          // Opcional: añadir un InfoWindow al hacer clic
        />
      ))}
    </GoogleMap>
  );
};

export default React.memo(MapaInteractivo);