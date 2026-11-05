'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import api from '@/services/api';
import { FiFileText, FiCheckCircle, FiClock, FiArrowRight } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { useAuth } from '@/contexts/AuthContext';

export default function CharacterizationSelectionPage() {
  const [forms, setForms] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    api.get('/formularios/').then(res => {
      setForms(res.data.results || []);
      setLoading(false);
    });
  }, []);

  // Determinar qué formulario le corresponde basado en su rol y perfil
  // Para la demo, mostramos todos los públicos
  const availableForms = forms.filter(f => f.es_publico);

  if (loading) return <div className="p-10 text-center animate-pulse">Consultando catastro institucional...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-10 animate-in fade-in duration-700">
      <header>
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Caracterización Técnica</h1>
        <p className="text-slate-500 text-lg mt-2 font-medium italic border-l-4 border-orange-500 pl-6">
           Obligación normativa según la Dirección de Turismo de Puerto Gaitán.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {availableForms.map((form) => (
          <Card key={form.id} className="group border-none shadow-sm hover:shadow-2xl transition-all rounded-[2.5rem] bg-white overflow-hidden">
            <CardContent className="p-10 flex flex-col h-full">
               <div className="w-14 h-14 bg-orange-50 text-orange-500 rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 transition-transform">
                  <FiFileText size={28} />
               </div>
               <h3 className="text-xl font-bold text-slate-900 mb-4">{form.titulo}</h3>
               <p className="text-slate-500 text-sm mb-10 flex-1">{form.descripcion}</p>

               <div className="pt-8 border-t border-slate-50 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-black text-slate-400 uppercase">
                     <FiClock /> 30 días restantes
                  </div>
                  <Button
                    onClick={() => window.location.href = `/dashboard/formularios/${form.id}`}
                    className="bg-slate-900 text-white font-black rounded-xl text-[10px] tracking-widest uppercase px-6"
                  >
                     Diligenciar <FiArrowRight className="ml-2" />
                  </Button>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <section className="bg-slate-900 rounded-[3rem] p-12 text-white relative overflow-hidden">
         <div className="absolute right-0 top-0 p-12 opacity-10">
            <FiCheckCircle size={200} />
         </div>
         <div className="max-w-2xl relative z-10">
            <h2 className="text-3xl font-black mb-6 uppercase italic">¿Por qué es importante?</h2>
            <p className="text-slate-300 font-medium leading-relaxed">
               La caracterización permite a la Secretaría de Turismo evaluar la calidad de la oferta local.
               Los prestadores caracterizados obtienen una <strong>mayor puntuación (Score)</strong>, lo que los posiciona de primero en el Directorio Turístico Inteligente y los habilita para participar en programas de incentivos gubernamentales.
            </p>
         </div>
      </section>
    </div>
  );
}
