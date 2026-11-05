import React from 'react';

export default function ImageSlider({ images }: { images: string[] }) {
  return (
    <div className="w-full h-64 bg-gray-200 flex items-center justify-center rounded-lg overflow-hidden">
      {images.length > 0 ? (
        <img src={images[0]} alt="Slider" className="object-cover w-full h-full" />
      ) : (
        <span>No hay imágenes disponibles</span>
      )}
    </div>
  );
}
