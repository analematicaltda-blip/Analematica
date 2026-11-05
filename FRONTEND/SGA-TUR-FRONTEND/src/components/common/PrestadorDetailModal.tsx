import React from 'react';
import Image from 'next/image';
import { PrestadorPublicoDetalle } from '@/services/api';
import { FaPhone, FaEnvelope, FaMapMarkerAlt, FaWhatsapp, FaFacebook, FaInstagram } from 'react-icons/fa';

interface PrestadorDetailModalProps {
  prestador: PrestadorPublicoDetalle;
}

const PrestadorDetailModal: React.FC<PrestadorDetailModalProps> = ({ prestador }) => {
  return (
    <div>
      {prestador.galeria_imagenes && prestador.galeria_imagenes.length > 0 && (
        <div className="mb-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {prestador.galeria_imagenes.slice(0, 6).map((img) => (
              <div key={img.id} className="relative h-32 w-full overflow-hidden rounded-lg shadow-md">
                <Image src={img.imagen} alt={img.alt_text || `Imagen de ${prestador.nombre_negocio}`} fill style={{ objectFit: 'cover' }} />
              </div>
            ))}
          </div>
        </div>
      )}
      <p className="text-gray-700 whitespace-pre-wrap mb-4">{prestador.descripcion || 'No hay descripción disponible.'}</p>
      {prestador.promociones_ofertas && (
        <div className="mb-4">
          <h4 className="font-bold text-lg mb-2">Promociones y Ofertas</h4>
          <p className="text-gray-700 whitespace-pre-wrap">{prestador.promociones_ofertas}</p>
        </div>
      )}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="font-bold text-lg mb-2">Contacto y Ubicación</h4>
        <ul className="space-y-2 text-gray-800">
          {prestador.telefono && <li className="flex items-center"><FaPhone className="mr-2 text-gray-500"/>{prestador.telefono}</li>}
          {prestador.email_contacto && <li className="flex items-center"><FaEnvelope className="mr-2 text-gray-500"/>{prestador.email_contacto}</li>}
          {prestador.red_social_whatsapp && <li className="flex items-center"><FaWhatsapp className="mr-2 text-green-500"/>{prestador.red_social_whatsapp}</li>}
          {prestador.latitud && prestador.longitud && (
            <li>
              <a
                href={`https://www.google.com/maps/search/?api=1&query=${prestador.latitud},${prestador.longitud}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center"
              >
                <FaMapMarkerAlt className="mr-2"/>Cómo llegar
              </a>
            </li>
          )}
          {prestador.red_social_facebook && <li><a href={prestador.red_social_facebook} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center"><FaFacebook className="mr-2"/>Facebook</a></li>}
          {prestador.red_social_instagram && <li><a href={prestador.red_social_instagram} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center"><FaInstagram className="mr-2"/>Instagram</a></li>}
        </ul>
      </div>
    </div>
  );
};

export default PrestadorDetailModal;