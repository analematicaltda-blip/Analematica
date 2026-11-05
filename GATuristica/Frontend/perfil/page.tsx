'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useForm } from 'react-hook-form';
import api from '@/services/api';
import FormField from '@/components/ui/FormField';
import { toast } from 'react-toastify';
import { FiCheckCircle, FiSearch, FiLayers } from 'react-icons/fi';

export default function PerfilPrestadorPage() {
  const [profile, setProfile] = useState<any>(null);
  const [subclassOptions, setSubclassOptions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const { register, handleSubmit, reset, watch } = useForm();

  const currentRnt = watch('rnt_number');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get('/v1/providers/tourism-providers/me/');
        setProfile(res.data);
        reset(res.data);

        // Cargar opciones de subclasificación basadas en el tipo
        if (res.data.provider_type) {
             const subclassRes = await api.get(`/formularios/?nombre=Subclasificación - ${res.data.provider_type}`);
             // Extraemos las opciones de la primera pregunta del formulario de subclasificación
             const formId = subclassRes.data.results?.[0]?.id;
             if (formId) {
                 const detail = await api.get(`/formularios/${formId}/`);
                 const options = detail.data.preguntas?.[0]?.opciones?.map((o: any) => o.texto_opcion) || [];
                 setSubclassOptions(options);
             }
        }
        setLoading(false);
      } catch (e) {
        toast.error("Error al cargar perfil.");
      }
    };
    fetchData();
  }, [reset]);

  const onSubmit = async (data: any) => {
    try {
      await api.patch(`/v1/providers/tourism-providers/${profile.id}/`, data);
      toast.success("Perfil actualizado y sincronizado.");
    } catch (e) {
      toast.error("Error al guardar cambios.");
    }
  };

  const handleRntVerify = async () => {
      if (!currentRnt) return;
      try {
          // Dispara sync en el backend
          await api.post(`/v1/providers/tourism-providers/${profile.id}/sync_rnt/`);
          toast.success("Información verificada con el RNT estatal.");
          window.location.reload();
      } catch (e) {
          toast.error("No se pudo validar el RNT.");
      }
  }

  if (loading) return <div className="p-10 text-center animate-pulse">Sincronizando con RNT Estatal...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-10 animate-in fade-in duration-700">
      <header>
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Identidad Corporativa</h1>
        <p className="text-slate-500 font-medium mt-2">Gestiona tu clasificación y cumplimiento legal en la Triple Vía.</p>
      </header>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        <Card className="border-none shadow-xl rounded-[2.5rem] overflow-hidden">
          <CardHeader className="bg-slate-900 p-8 text-white">
            <CardTitle className="flex items-center gap-3 italic">
              <FiCheckCircle className="text-emerald-400" /> Registro Nacional de Turismo (RNT)
            </CardTitle>
          </CardHeader>
          <CardContent className="p-10 space-y-6">
             <div className="flex gap-4 items-end">
                <div className="flex-1">
                   <FormField
                     name="rnt_number"
                     label="Número de RNT"
                     register={register}
                     placeholder="Ej: 12345"
                   />
                </div>
                <Button
                  type="button"
                  onClick={handleRntVerify}
                  className="bg-indigo-600 text-white font-black h-12 px-6 rounded-xl hover:bg-indigo-700 transition-all flex items-center gap-2"
                >
                   <FiSearch /> Verificar en Estado
                </Button>
             </div>
             {profile.rnt_validated ? (
                 <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl text-emerald-700 text-xs font-bold flex items-center gap-2">
                    <FiCheckCircle /> INFORMACIÓN VALIDADA POR MINCIT - ÚLTIMA SYNC: {new Date(profile.rnt_last_sync).toLocaleString()}
                 </div>
             ) : (
                 <div className="bg-amber-50 border border-amber-100 p-4 rounded-xl text-amber-700 text-xs font-bold">
                    PENDIENTE DE VALIDACIÓN ESTATAL
                 </div>
             )}
          </CardContent>
        </Card>

        <Card className="border-none shadow-xl rounded-[2.5rem] overflow-hidden">
          <CardHeader className="bg-white border-b border-slate-50 p-8">
            <CardTitle className="text-slate-900 flex items-center gap-3">
              <FiLayers className="text-indigo-600" /> Sub-clasificación Especializada
            </CardTitle>
          </CardHeader>
          <CardContent className="p-10 space-y-6">
             <div>
                <label className="block text-xs font-black uppercase text-slate-400 tracking-widest mb-3">Variante de {profile.provider_type}</label>
                <select
                  {...register('sub_classification')}
                  className="w-full bg-slate-50 border-none px-6 py-4 rounded-2xl text-lg font-bold text-slate-800 focus:ring-2 focus:ring-indigo-500 transition-all"
                >
                   <option value="">Seleccione una variante...</option>
                   {subclassOptions.map(opt => (
                       <option key={opt} value={opt}>{opt}</option>
                   ))}
                </select>
                <p className="text-sm text-slate-400 mt-4 font-medium italic">
                   Escoge la sub-clasificación que mejor describa tu concepto. Esto mejorará tu posicionamiento en el directorio inteligente de SARITA.
                </p>
             </div>
          </CardContent>
        </Card>

        <div className="flex justify-end pt-4">
           <Button type="submit" className="bg-slate-900 hover:bg-slate-800 text-white font-black uppercase tracking-[0.2em] px-12 py-6 rounded-3xl shadow-2xl shadow-slate-200">
              Guardar Cambios Identitarios
           </Button>
        </div>
      </form>
    </div>
  );
}
