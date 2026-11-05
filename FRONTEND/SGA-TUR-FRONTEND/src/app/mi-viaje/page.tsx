"use client";

import React, { useState, useEffect, useCallback } from 'react';
import api from '@/services/api';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { ViewState } from '@/components/ui/ViewState';
import { FiTruck } from 'react-icons/fi';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface SavedItem {
  id: number;
  content_type_name: string;
  content_object: {
    id: number;
    titulo?: string;
    nombre?: string;
    slug: string;
    imagen_principal?: string | null;
  };
}

export default function MiViajePage() {
  const { user, token, isLoading: authLoading, toggleSaveItem } = useAuth();
  const router = useRouter();

  const [savedItems, setSavedItems] = useState<SavedItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSavedItems = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await api.get('/mi-viaje/');
      setSavedItems(response.data.results || response.data);
    } catch (err) {
      setError('No se pudieron cargar tus elementos guardados.');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (!authLoading) {
      if (!user || user.role !== 'TURISTA') {
        router.push('/dashboard/login');
      } else {
        fetchSavedItems();
      }
    }
  }, [user, authLoading, router, fetchSavedItems]);

  const handleRemove = async (item: SavedItem) => {
    try {
        await toggleSaveItem(item.content_type_name, item.content_object.id);
        // Refetch to ensure data consistency
        await fetchSavedItems();
    } catch (error) {
        // The error is already handled in the toggleSaveItem function
    }
  };

  const atractivosGuardados = savedItems.filter(item => item.content_type_name === 'atractivoturistico');
  const eventosGuardados = savedItems.filter(item => item.content_type_name === 'publicacion');

  return (
    <div className="py-12 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Mi Viaje
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            Aquí tienes todos tus lugares y eventos favoritos. ¡Es hora de planificar!
          </p>
        </div>

        <ViewState
           isLoading={authLoading || isLoading}
           loadingMessage="Organizando tu próxima aventura..."
           isEmpty={savedItems.length === 0 && !isLoading}
           emptyMessage="Tu maleta virtual está vacía. Guarda atractivos y eventos para verlos aquí."
           emptyAction={{ label: "Explorar Atractivos", onClick: () => router.push('/descubre/atractivos') }}
           error={error}
        >
          <div className="space-y-12">
            {/* Sección de Monedero - Acceso Rápido */}
            <section className="bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100">
               <div className="bg-gradient-to-r from-indigo-600 to-blue-700 p-8 text-white">
                  <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                     <div>
                        <p className="text-indigo-100 text-sm font-bold uppercase tracking-widest mb-1">Mi Monedero Institucional</p>
                        <h2 className="text-4xl font-black">
                           Infraestructura Financiera Soberana
                        </h2>
                     </div>
                     <div className="flex gap-3">
                        <Link href="/mi-viaje/monedero/cartera" className="bg-white/20 hover:bg-white/30 backdrop-blur-md text-white px-6 py-3 rounded-2xl font-bold transition-all border border-white/10 text-sm">
                           Ver Cartera
                        </Link>
                        <Link href="/mi-viaje/monedero/transferir" className="bg-white text-indigo-600 hover:bg-indigo-50 px-6 py-3 rounded-2xl font-bold transition-all shadow-lg text-sm">
                           Transferir Fondos
                        </Link>
                     </div>
                  </div>
               </div>
            </section>

            {/* Sección de Delivery / Transporte */}
            <section className="bg-indigo-900 rounded-[2.5rem] p-10 text-white shadow-2xl relative overflow-hidden group">
               <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-700">
                  <FiTruck size={140} />
               </div>
               <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-8">
                  <div className="flex-1">
                     <h2 className="text-3xl font-black mb-2 tracking-tight">Logística Institucional</h2>
                     <p className="text-indigo-300 font-medium">Solicite traslados y delivery certificados bajo gobernanza SARITA.</p>
                  </div>
                  <div className="flex flex-wrap justify-center gap-4">
                     <Link href="/mi-viaje/delivery/solicitar" className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-2xl font-bold transition-all shadow-lg">
                        Solicitar Servicio
                     </Link>
                     <Link href="/mi-viaje/delivery/historial" className="bg-white/10 hover:bg-white/20 backdrop-blur-md text-white px-8 py-4 rounded-2xl font-bold transition-all border border-white/10">
                        Mi Historial
                     </Link>
                  </div>
               </div>
            </section>

            {/* Atractivos Guardados */}
            {atractivosGuardados.length > 0 && (
              <section>
                <h2 className="text-2xl font-bold text-indigo-700 mb-6">Mis Atractivos Guardados</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {atractivosGuardados.map(item => (
                    <div key={item.id} className="bg-white rounded-lg shadow-lg overflow-hidden group">
                      <div className="relative h-48 w-full">
                        <Image
                          src={item.content_object.imagen_principal || 'https://via.placeholder.com/400x300'}
                          alt={item.content_object.nombre || 'Imagen de atractivo guardado'}
                          layout="fill"
                          objectFit="cover"
                        />
                        <button onClick={() => handleRemove(item)} className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" /></svg>
                        </button>
                      </div>
                      <div className="p-4">
                        <h3 className="font-bold text-lg">{item.content_object.nombre}</h3>
                        <Link href={`/atractivos/${item.content_object.slug}`} className="text-sm text-indigo-600 hover:underline">Ver detalles</Link>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Eventos Guardados */}
            {eventosGuardados.length > 0 && (
              <section>
                <h2 className="text-2xl font-bold text-indigo-700 mb-6">Mis Eventos Guardados</h2>
                <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
                  {eventosGuardados.map(item => (
                    <div key={item.id} className="flex items-center justify-between border-b pb-2">
                      <div>
                        <h3 className="font-semibold">{item.content_object.titulo}</h3>
                        <Link href={`/publicaciones/${item.content_object.slug}`} className="text-sm text-indigo-600 hover:underline">Ver detalles</Link>
                      </div>
                      <button onClick={() => handleRemove(item)} className="text-red-500 hover:text-red-700">
                        Eliminar
                      </button>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </ViewState>
      </div>
    </div>
  );
}