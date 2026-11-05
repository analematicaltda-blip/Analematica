import React from 'react';
import Image from 'next/image';
import { ArtesanoPublicoDetalle } from '@/services/api';
import { FaPhone, FaEnvelope, FaMapMarkerAlt, FaWhatsapp, FaFacebook, FaInstagram, FaTiktok } from 'react-icons/fa';

interface ArtesanoDetailModalProps {
  artesano: ArtesanoPublicoDetalle;
}

const ArtesanoDetailModal: React.FC<ArtesanoDetailModalProps> = ({ artesano }) => (
  <div>
    {artesano.galeria_imagenes && artesano.galeria_imagenes.length > 0 && (
      <div className="mb-4">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {artesano.galeria_imagenes.slice(0, 6).map((img) => (
            <div key={img.id} className="relative h-32 w-full overflow-hidden rounded-lg shadow-md">
              <Image src={img.imagen} alt={img.alt_text || `Imagen de ${artesano.nombre_taller}`} fill style={{ objectFit: 'cover' }} />
            </div>
          ))}
        </div>
      </div>
    )}
    <p className="text-gray-700 whitespace-pre-wrap mb-4">{artesano.descripcion || 'No hay descripción disponible.'}</p>
    <div className="bg-gray-50 p-4 rounded-lg">
      <h4 className="font-bold text-lg mb-2">Contacto y Ubicación</h4>
      <ul className="space-y-2 text-gray-800">
        {artesano.telefono && <li className="flex items-center"><FaPhone className="mr-2 text-gray-500"/>{artesano.telefono}</li>}
        {artesano.email_contacto && <li className="flex items-center"><FaEnvelope className="mr-2 text-gray-500"/>{artesano.email_contacto}</li>}
        {artesano.red_social_whatsapp && <li className="flex items-center"><FaWhatsapp className="mr-2 text-green-500"/>{artesano.red_social_whatsapp}</li>}
        {artesano.latitud && artesano.longitud && (
            <li>
                <a
                    href={`https://www.google.com/maps/search/?api=1&query=${artesano.latitud},${artesano.longitud}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline flex items-center"
                >
                    <FaMapMarkerAlt className="mr-2"/>Cómo llegar
                </a>
            </li>
        )}
        {artesano.red_social_facebook && <li><a href={artesano.red_social_facebook} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center"><FaFacebook className="mr-2"/>Facebook</a></li>}
        {artesano.red_social_instagram && <li><a href={artesano.red_social_instagram} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center"><FaInstagram className="mr-2"/>Instagram</a></li>}
        {artesano.red_social_tiktok && <li><a href={artesano.red_social_tiktok} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline flex items-center"><FaTiktok className="mr-2"/>TikTok</a></li>}
      </ul>
    </div>
  </div>
);

export default ArtesanoDetailModal;