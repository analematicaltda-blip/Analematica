'use client';

import React from 'react';
import { FiHardHat } from 'react-icons/fi';
import { FiActivity } from 'react-icons/fi';

interface PlaceholderContentProps {
  title: string;
  description?: string;
}

export default function PlaceholderContent({
  title,
  description = "Estamos trabajando para traerte esta funcionalidad lo antes posible. Gracias por tu paciencia."
}: PlaceholderContentProps) {
  return (
    <Card className="m-4">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center text-center text-gray-500 py-12">
          <FiHardHat className="w-16 h-16 mb-4 text-yellow-500" />
          <h2 className="text-2xl font-bold mb-2">Módulo en Construcción</h2>
          <p className="max-w-md">{description}</p>
        </div>
      </CardContent>
    </Card>
  );
}
