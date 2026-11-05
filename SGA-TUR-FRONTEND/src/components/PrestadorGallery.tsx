'use client';

import React, { useState, useEffect } from 'react';

interface Image {
  id: string;
  url: string;
  alt: string;
}

const PrestadorGallery = ({ images }: { images: Image[] }) => {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrent((prev) => (prev + 1) % images.length);
    }, 4000);  // 4s per image
    return () => clearInterval(interval);
  }, [images.length]);

  if (images.length === 0) return <div>Sin fotos</div>;

  return (
    <div className="relative w-full h-64 overflow-hidden rounded-lg shadow-lg">
      {images.map((img, idx) => (
        <img
          key={img.id}
          src={img.url}
          alt={img.alt}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ${
            idx === current ? 'opacity-100' : 'opacity-0'
          }`}
        />
      ))}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
        {images.map((_, idx) => (
          <button
            key={idx}
            className={`w-3 h-3 rounded-full ${idx === current ? 'bg-white' : 'bg-white/50'}`}
            onClick={() => setCurrent(idx)}
          />
        ))}
      </div>
    </div>
  );
};

export default PrestadorGallery;

