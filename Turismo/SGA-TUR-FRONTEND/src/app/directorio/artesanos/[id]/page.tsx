"use client";

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import ImageSlider from '@/components/ImageSlider';
import ResenasSection from '@/components/ResenasSection';
import { getArtesanoById, ArtesanoPublicoDetalle } from '@/services/api';
import { FiPhone, FiMail, FiMapPin, FiFacebook, FiInstagram } from 'react-icons/fi';
import { FaWhatsapp, FaTiktok } from 'react-icons/fa';

const ContactInfo = ({ icon: Icon, text, href, label }: { icon: React.ElementType, text?: string | null, href?: string | null, label?: string }) => {
  if (!text) return null;
  const link = href || (text.startsWith('http') ? text : `tel:${text}`);
  return (
    <a href={link} target="_blank" rel="noopener noreferrer" className="flex items-center text-gray-600 hover:text-blue-600 transition-colors">
      <Icon className="mr-3 h-5 w-5 text-gray-400" />
      <span>{label || text}</span>
    </a>
  );
};

const ArtesanoDetailPage = () => {
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : params.id;
  const [artesano, setArtesano] = useState<ArtesanoPublicoDetalle | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      const fetchArtesano = async () => {
        setIsLoading(true);
        setError(null);
        try {
          const data = await getArtesanoById(Number(id));
          setArtesano(data);
        } catch (err) {
          setError('No se pudo encontrar al artesano. Es posible que el enlace no sea válido.');
        } finally {
          setIsLoading(false);
        }
      };
      fetchArtesano();
    }
  }, [id]);

  const fallbackImage = "/images/placeholder.png";

  if (isLoading) {
    return <div className="text-center py-40">Cargando...</div>;
  }

  if (error) {
    return <div className="text-center py-40 text-red-600">{error}</div>;
  }

  if (!artesano) {
    return <div className="text-center py-40">Artesano no encontrado.</div>;
  }

  const sliderImages = [
    ...(artesano.foto_url
      ? [{ id: 0, imagen: artesano.foto_url, alt_text: 'Foto Principal' }]
      : []),
    ...artesano.galeria_imagenes,
  ];
  if (sliderImages.length === 0) {
      sliderImages.push({ id: -1, imagen: fallbackImage, alt_text: 'Imagen por defecto' });
  }

  return (
    <div className="font-sans bg-gray-50">
      <div className="relative">
          <ImageSlider images={sliderImages} />
          <div className="absolute inset-0 flex flex-col justify-center items-center text-white bg-black bg-opacity-50 p-4">
              <p className="text-lg font-semibold text-blue-300">{artesano.rubro.nombre}</p>
              <h1 className="text-5xl font-extrabold text-center mt-2 shadow-text">{artesano.nombre_taller}</h1>
              <p className="text-xl text-gray-200 mt-2">{artesano.nombre_artesano}</p>
          </div>
      </div>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2">
            <section>
              <h2 className="text-3xl font-bold text-gray-800 border-b-2 border-blue-500 pb-2 mb-4">
                Descripción
              </h2>
              <div className="prose prose-lg max-w-none text-gray-600">
                {artesano.descripcion || 'No hay una descripción disponible.'}
              </div>
            </section>
            <ResenasSection contentType="artesano" objectId={artesano.id} />
          </div>
          <aside className="lg:col-span-1">
            <div className="bg-white p-6 rounded-lg shadow-lg sticky top-24">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Información de Contacto</h3>
              <div className="space-y-4">
                <ContactInfo icon={FiPhone} text={artesano.telefono} href={`tel:${artesano.telefono}`} />
                <ContactInfo icon={FiMail} text={artesano.email_contacto} href={`mailto:${artesano.email_contacto}`} />
                <ContactInfo icon={FaWhatsapp} text={artesano.red_social_whatsapp} href={`https://wa.me/${artesano.red_social_whatsapp?.replace(/\D/g, '')}`} label="WhatsApp" />
                <ContactInfo icon={FiInstagram} text={artesano.red_social_instagram} label="Instagram" />
                <ContactInfo icon={FiFacebook} text={artesano.red_social_facebook} label="Facebook" />
                <ContactInfo icon={FaTiktok} text={artesano.red_social_tiktok} label="TikTok" />
                {artesano.ubicacion_taller && <p className="flex items-center text-gray-600"><FiMapPin className="mr-3 h-5 w-5 text-gray-400" /><span>{artesano.ubicacion_taller}</span></p>}
              </div>
              {artesano.ubicacion_taller && (
                  <div className="mt-6">
                      <a
                          href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(artesano.ubicacion_taller)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors"
                      >
                          <FiMapPin className="mr-2" />
                          Cómo Llegar
                      </a>
                  </div>
              )}
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};

export default ArtesanoDetailPage;