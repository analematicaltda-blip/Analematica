'use client';

'use client';

import React from 'react';
import Image from 'next/image';

interface FloatingAgentIconProps {
  onClick: () => void;
  isAgentSpeaking: boolean;
}

export default function FloatingAgentIcon({ onClick, isAgentSpeaking }: FloatingAgentIconProps) {
  // Clases base para el botón
  const baseClasses = "fixed bottom-8 right-8 z-50 h-20 w-20 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 ease-in-out transform focus:outline-none focus:ring-4 focus:ring-teal-300";

  // Clases condicionales para las animaciones
  const animationClasses = "animate-glowing-guacamaya hover:scale-110";
  const speakingClasses = isAgentSpeaking ? "animate-vibrating" : "";

  return (
    <button
      onClick={onClick}
      className={`${baseClasses} ${animationClasses} ${speakingClasses}`}
      aria-label="Abrir asistente turístico"
      style={{ backgroundColor: 'transparent' }} // El fondo lo dará la imagen o un contenedor interno si es necesario
    >
      <Image
        src="/guacamaya.svg"
        alt="Asistente Turístico Guacamaya"
        width={80}
        height={80}
        className="object-contain rounded-full"
      />
    </button>
  );
}