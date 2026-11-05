import React from 'react';
import Link from 'next/link';

interface PlaceholderContentProps {
  title: string;
  description?: string;
}

const PlaceholderContent: React.FC<PlaceholderContentProps> = ({
  title,
  description = 'El contenido para esta sección estará disponible próximamente. Estamos trabajando para ofrecerte la mejor experiencia.'
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center bg-gray-50 p-8">
      <div className="max-w-2xl">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">{title}</h1>
        <p className="text-lg text-gray-600">
          {description}
        </p>
        <div className="mt-8">
          <Link
            href="/"
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition-colors duration-300"
          >
            Volver a la página de inicio
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PlaceholderContent;