import React from 'react';

export default function ResenasSection({ entityId, entityType }: { entityId: number, entityType: string }) {
  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Reseñas</h2>
      <p className="text-gray-600 italic">Próximamente: Sistema de reseñas para {entityType}.</p>
    </div>
  );
}
