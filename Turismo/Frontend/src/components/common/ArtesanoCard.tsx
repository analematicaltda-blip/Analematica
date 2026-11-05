import React from 'react';
import Image from 'next/image';
import { ArtesanoPublico } from '@/services/api';
import { FaPhone, FaEnvelope, FaInfoCircle, FaFacebook, FaInstagram, FaWhatsapp, FaMapMarkerAlt } from 'react-icons/fa';

interface ArtesanoCardProps {
  artesano: ArtesanoPublico;
  onViewMore: () => void;
}

const ArtesanoCard: React.FC<ArtesanoCardProps> = ({ artesano, onViewMore }) => {
  const hasCoordinates = artesano.latitud && artesano.longitud;

  return (
    <div className="border rounded-lg shadow-md hover:shadow-xl transition-shadow flex flex-col h-full bg-white">
      <div className="relative w-full h-48">
        <Image
          src={artesano.foto_url || '/images/placeholder.png'}
          alt={`Foto de ${artesano.nombre_taller}`}
          fill
          style={{ objectFit: 'cover' }}
          className="rounded-t-lg"
        />
      </div>
      <div className="p-4 flex flex-col flex-grow">
        <h3 className="text-lg font-bold mb-1 truncate">{artesano.nombre_taller}</h3>
        <p className="text-sm text-gray-600 mb-2">{artesano.nombre_artesano}</p>
        <p className="text-xs text-gray-700 flex-grow mb-3 line-clamp-3">{artesano.descripcion || "Sin descripción."}</p>

        <div className="space-y-1 text-sm mb-4">
            {artesano.telefono && <div className="flex items-center"><FaPhone className="mr-2 text-gray-500"/> {artesano.telefono}</div>}
            {artesano.email_contacto && <div className="flex items-center truncate"><FaEnvelope className="mr-2 text-gray-500"/> {artesano.email_contacto}</div>}
        </div>

        <div className="flex items-center space-x-4 mb-4">
            {artesano.red_social_whatsapp && (
                <a href={`https://wa.me/${artesano.red_social_whatsapp.replace(/\\D/g, '')}`} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-green-500" aria-label="WhatsApp">
                    <FaWhatsapp size={22} />
                </a>
            )}
            {artesano.red_social_instagram && (
                <a href={artesano.red_social_instagram} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-pink-500" aria-label="Instagram">
                    <FaInstagram size={22} />
                </a>
            )}
            {artesano.red_social_facebook && (
                <a href={artesano.red_social_facebook} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-blue-600" aria-label="Facebook">
                    <FaFacebook size={22} />
                </a>
            )}
        </div>

        <div className="mt-auto grid grid-cols-1 gap-2">
            <button
                onClick={onViewMore}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors flex items-center justify-center"
            >
                <FaInfoCircle className="mr-2" /> Ver más
            </button>
            {hasCoordinates && (
                <a
                    href={`https://www.google.com/maps/search/?api=1&query=${artesano.latitud},${artesano.longitud}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors flex items-center justify-center text-center"
                >
                    <FaMapMarkerAlt className="mr-2" /> Cómo llegar
                </a>
            )}
        </div>
      </div>
    </div>
  );
};

export default ArtesanoCard;