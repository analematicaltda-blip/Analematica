"use client";

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface SaveButtonProps {
  contentType: 'atractivoturistico' | 'publicacion';
  objectId: number;
}

export default function SaveButton({ contentType, objectId }: SaveButtonProps) {
  const { isAuthenticated, user, isItemSaved, toggleSaveItem, isLoading } = useAuth();

  // El botón solo se muestra para usuarios autenticados con el rol de Turista
  if (!isAuthenticated || !user || user.role !== 'TURISTA') {
    return null;
  }

  const isSaved = isItemSaved(contentType, objectId);

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault(); // Evita la navegación si el botón está dentro de un <Link>
    e.stopPropagation();
    if (!isLoading) {
      toggleSaveItem(contentType, objectId);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className={`absolute top-2 right-2 p-2 rounded-full transition-colors duration-200 ${
        isSaved
          ? 'bg-red-500 text-white'
          : 'bg-white/70 text-gray-700 hover:bg-white'
      }`}
      aria-label={isSaved ? 'Quitar de Mi Viaje' : 'Guardar en Mi Viaje'}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill={isSaved ? 'currentColor' : 'none'}
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M4.318 6.318a4.5 4.5 0 016.364 0L12 7.5l1.318-1.182a4.5 4.5 0 116.364 6.364L12 21.5l-7.682-7.682a4.5 4.5 0 010-6.364z"
        />
      </svg>
    </button>
  );
}