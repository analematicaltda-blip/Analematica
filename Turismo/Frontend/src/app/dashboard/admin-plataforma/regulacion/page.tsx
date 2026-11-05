'use client';

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  FiFileText, FiBook, FiCheckCircle, FiAlertCircle, FiSettings, FiGlobe, FiBriefcase, FiPercent, FiShield
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';
import { toast } from 'react-hot-toast';

export default function RegulacionPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [settings, setSettings] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const { data } = await api.get('/admin/plataforma/system-audit/settings/global/');
      setSettings(data);
    } catch (e) {
      toast.error("Error al cargar configuraciones globales.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateSetting = async (key: string, value: any) => {
    setIsSaving(true);
    try {
      await api.patch('/admin/plataforma/system-audit/settings/global/', { [key]: value });
      toast.success("Configuración actualizada.");
      loadSettings();
    } catch (e) {
      toast.error("No se pudo guardar el cambio.");
    } finally {
      setIsSaving(false);
    }
  };

  const frameworks = [
    {
        id: 'fw-01',
        name: 'EU AI Act (Alineación)',
        scope: 'Internacional',
        status: 'COMPLIANT',
        version: '1.4.2',
        description: 'Estándares de transparencia, explicabilidad y gestión de riesgos para sistemas de IA de alto riesgo.'
    },
    {
        id: 'fw-02',
        name: 'Ley 1581 de 2012 (Habeas Data)',
        scope: 'Nacional (Colombia)',
        status: 'COMPLIANT',
        version: '2.1.0',
        description: 'Protección de datos personales y derechos de los titulares en el tratamiento de información.'
    },
    {
        id: 'fw-03',
        name: 'Decreto Territorial 045',
        scope: 'Local (Puerto Gaitán)',
        status: 'ACTIVE',
        version: '1.0.5',
        description: 'Normativas específicas para la promoción y control del turismo municipal.'
    }
  ];

  return (
    <ViewState isLoading={isLoading}>
      <div className="space-y-10 animate-in fade-in duration-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="bg-brand text-white p-2 rounded-lg">
                        <FiFileText size={24} />
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Configuración Multi-Regulatoria</h1>
                </div>
                <p className="text-slate-500 text-lg font-medium italic">Gestión de marcos legales y parámetros normativos por jurisdicción.</p>
            </div>
            <Button className="bg-brand text-white font-black px-8 py-6 rounded-2xl flex items-center gap-2 uppercase tracking-widest text-xs">
                <FiBook /> Cargar Nueva Norma
            </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
                {/* GLOBAL PARAMETERS (FASE SUPER ADMIN) */}
                <h3 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-2 italic">
                    <FiSettings className="text-brand" /> Parámetros Globales del Sistema
                </h3>
                <Card className="border-none shadow-xl bg-white rounded-[2.5rem] overflow-hidden">
                    <CardContent className="p-10 space-y-8">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center">
                                        <FiPercent />
                                    </div>
                                    <label className="text-sm font-black text-slate-900 uppercase">Comisión Regalos Social</label>
                                </div>
                                <div className="flex gap-2">
                                    <input
                                        type="number"
                                        value={settings?.social_gift_commission_pct || 0}
                                        onChange={(e) => setSettings({...settings, social_gift_commission_pct: e.target.value})}
                                        className="w-full border-2 border-slate-100 rounded-2xl px-6 py-4 font-bold text-xl focus:border-brand transition-all"
                                    />
                                    <Button
                                        onClick={() => handleUpdateSetting('social_gift_commission_pct', settings.social_gift_commission_pct)}
                                        disabled={isSaving}
                                        className="bg-slate-900 text-white font-black px-6 rounded-2xl"
                                    >
                                        FIJAR
                                    </Button>
                                </div>
                                <p className="text-[10px] text-slate-400 font-medium">Porcentaje aplicado a cada premio/regalo en Vía 3.</p>
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center">
                                        <FiShield />
                                    </div>
                                    <label className="text-sm font-black text-slate-900 uppercase">Modo Mantenimiento</label>
                                </div>
                                <div className="flex items-center justify-between bg-slate-50 p-6 rounded-2xl">
                                    <span className="text-xs font-bold text-slate-600 uppercase italic">Estado de Plataforma</span>
                                    <button
                                        onClick={() => handleUpdateSetting('maintenance_mode', !settings?.maintenance_mode)}
                                        className={`w-14 h-8 rounded-full transition-all relative ${settings?.maintenance_mode ? 'bg-red-500' : 'bg-emerald-500'}`}
                                    >
                                        <div className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-all ${settings?.maintenance_mode ? 'right-1' : 'left-1'}`} />
                                    </button>
                                </div>
                                <p className="text-[10px] text-slate-400 font-medium">Bloquea el acceso a todas las interfaces excepto Super Admin.</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <h3 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-2 italic pt-6">
                    <FiGlobe className="text-indigo-500" /> Marcos Legales Activos
                </h3>
                {frameworks.map((fw) => (
                    <Card key={fw.id} className="border-none shadow-sm bg-white overflow-hidden rounded-3xl group">
                        <div className="p-8">
                            <div className="flex justify-between items-start mb-6">
                                <div>
                                    <div className="flex items-center gap-3 mb-2">
                                        <Badge variant="outline" className="font-black text-[9px] uppercase tracking-widest">{fw.scope}</Badge>
                                        <h4 className="text-2xl font-black text-slate-900 uppercase italic">{fw.name}</h4>
                                    </div>
                                    <p className="text-slate-500 text-sm max-w-xl leading-relaxed">
                                        {fw.description}
                                    </p>
                                </div>
                                <div className="text-right">
                                    <Badge className="bg-emerald-500 text-white font-black px-4 py-1 mb-2">VIGENTE</Badge>
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">v{fw.version}</p>
                                </div>
                            </div>
                            <div className="pt-6 border-t border-slate-50 flex justify-between items-center">
                                <div className="flex gap-4">
                                    <Button variant="ghost" size="sm" className="text-indigo-600 font-bold hover:bg-indigo-50 rounded-xl">Ver Mapeo de Reglas</Button>
                                    <Button variant="ghost" size="sm" className="text-slate-400 font-bold hover:bg-slate-50 rounded-xl">Historial de Cambios</Button>
                                </div>
                                <Button size="sm" className="rounded-xl bg-slate-900 text-white font-bold"><FiSettings className="mr-2" /> Ajustar Parámetros</Button>
                            </div>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="space-y-6">
                <h3 className="text-xl font-black text-slate-900 uppercase tracking-widest flex items-center gap-2 italic">
                    <FiBriefcase className="text-amber-500" /> Estado de Alineación
                </h3>
                <Card className="border-none shadow-sm bg-slate-900 text-white p-8 rounded-[2rem] relative overflow-hidden">
                    <div className="absolute -right-10 -top-10 opacity-10">
                        <FiCheckCircle size={200} />
                    </div>
                    <div className="relative z-10 space-y-8">
                        <div>
                            <p className="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] mb-4">Consistencia Normativa</p>
                            <h4 className="text-5xl font-black italic">94.8%</h4>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center text-sm">
                                <span className="font-bold text-slate-400 uppercase tracking-widest">Conflicto de Normas</span>
                                <span className="font-black text-amber-400">0 DETECTADOS</span>
                            </div>
                            <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-emerald-500 w-[95%]" />
                            </div>
                        </div>
                        <div className="pt-6 border-t border-white/10">
                            <p className="text-xs text-slate-400 leading-relaxed italic">
                                "El motor de gobernanza está aplicando las reglas nacionales con precedencia sobre las locales en el dominio financiero."
                            </p>
                        </div>
                    </div>
                </Card>

                <Card className="border-none shadow-sm bg-white p-8 rounded-3xl">
                    <h4 className="text-sm font-black text-slate-900 uppercase tracking-widest mb-6">Próximas Actualizaciones</h4>
                    <div className="space-y-6">
                        <div className="flex gap-4">
                            <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
                                <FiAlertCircle />
                            </div>
                            <div>
                                <p className="text-xs font-black text-slate-900 uppercase">Nueva Directiva IA Act</p>
                                <p className="text-[10px] text-slate-500">Programada: 15/08/2024</p>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
                                <FiBook />
                            </div>
                            <div>
                                <p className="text-xs font-black text-slate-900 uppercase">Revisión de Privacidad Regional</p>
                                <p className="text-[10px] text-slate-500">En Proceso de Análisis</p>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
      </div>
    </ViewState>
  );
}
