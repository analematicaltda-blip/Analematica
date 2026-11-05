'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  FiGlobe, FiShield, FiCpu, FiAnchor, FiHeart, FiBook,
  FiAward, FiActivity, FiZap, FiTarget, FiStar
} from 'react-icons/fi';
import { httpClient } from '@/services/httpClient';

export default function DoctrinaMetaPage() {
  const [standardData, setStandardData] = useState<Record<string, any> | null>(null);

  useEffect(() => {
    httpClient.get('/admin-plataforma/doctrina/')
      .then(res => setStandardData(res.data))
      .catch(err => console.error(err));
  }, []);

  const metaPoints = [
    {
      title: "1. Soberanía Humana Absoluta",
      desc: "Supremacía del mandato humano sobre cualquier lógica algorítmica. El sistema es un instrumento, no una autoridad.",
      icon: <FiAnchor className="text-emerald-500" />
    },
    {
      title: "2. Trazabilidad Forense",
      desc: "Inmutabilidad absoluta mediante encadenamiento de hashes. Cada decisión tiene un autor y un porqué verificable.",
      icon: <FiShield className="text-indigo-500" />
    },
    {
      title: "3. Reversibilidad (PDA)",
      desc: "Protocolo de Desaceleración Algorítmica: capacidad de congelar y revertir cualquier acción autónoma en milisegundos.",
      icon: <FiZap className="text-amber-500" />
    },
    {
      title: "4. Jurisdicción Estricta",
      desc: "Compartimentación y Anti-Deriva: los agentes no pueden actuar fuera de su dominio institucional asignado.",
      icon: <FiTarget className="text-red-500" />
    },
    {
      title: "5. Neutralidad Institucional",
      desc: "Estabilidad técnica independiente de ciclos políticos. El sistema protege la infraestructura, no la ideología.",
      icon: <FiGlobe className="text-blue-500" />
    },
    {
      title: "6. Transparencia XAI",
      desc: "Cadena de decisión de 5 puntos: Hallazgo, Datos, Regla, Alternativas e Impacto. Prohibida la opacidad técnica.",
      icon: <FiActivity className="text-purple-500" />
    },
    {
      title: "7. Autonomía Regulada",
      desc: "Jerarquía de niveles (L0-L3). La delegación es condicional y revocable por el Núcleo de Gobernanza.",
      icon: <FiCpu className="text-slate-500" />
    },
    {
      title: "8. Bien Público",
      desc: "SARITA es infraestructura civilizatoria. Se prohíbe su privatización o transferencia a intereses particulares.",
      icon: <FiAward className="text-yellow-600" />
    },
    {
      title: "9. Privacidad Soberana",
      desc: "Ética de datos radical. La soberanía de la información pertenece a la institución y al ciudadano, no al procesador.",
      icon: <FiStar className="text-cyan-500" />
    },
    {
      title: "10. Legado Generacional",
      desc: "Preservación del conocimiento y transmisión segura del control sistémico a las futuras generaciones de custodios.",
      icon: <FiBook className="text-slate-700" />
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-1000">
      {/* Doctrine Banner */}
      <div className="bg-slate-900 rounded-[2.5rem] p-12 text-white relative overflow-hidden shadow-2xl">
         <div className="absolute top-0 right-0 w-1/2 h-full opacity-10 pointer-events-none">
            <FiCpu className="w-full h-full transform translate-x-1/4 -translate-y-1/4 rotate-12" />
         </div>
         <div className="relative z-10 max-w-3xl">
            <div className="flex items-center gap-4 mb-6">
                <Badge className="bg-emerald-500 text-white font-black px-4 py-1">DOCTRINA INSTITUCIONAL</Badge>
                <Badge variant="outline" className="text-emerald-400 border-emerald-400 font-bold px-4 py-1">FASE META</Badge>
            </div>
            <h1 className="text-6xl font-black tracking-tighter mb-4 leading-none uppercase italic">
                SARITA <span className="text-emerald-400">Standard</span>
            </h1>
            <p className="text-xl text-slate-300 font-medium leading-relaxed italic">
                &quot;Gobernamos los sistemas para que los humanos sigan gobernando las sociedades. La tecnología más poderosa bajo el mandato de la humanidad.&quot;
            </p>
         </div>
      </div>

      {/* Main Philosophy Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <Card className="border-none shadow-xl bg-white rounded-3xl overflow-hidden group hover:scale-[1.02] transition-transform">
            <CardContent className="p-10 text-center">
                <div className="w-20 h-20 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                    <FiStar size={40} />
                </div>
                <h3 className="text-2xl font-black text-slate-900 uppercase italic mb-4">Soberanía Real</h3>
                <p className="text-slate-500 font-medium leading-relaxed">
                    La autoridad humana es la única fuente de legitimidad para el sistema. Ninguna decisión algorítmica es definitiva sin ratificación soberana.
                </p>
            </CardContent>
         </Card>

         <Card className="border-none shadow-xl bg-white rounded-3xl overflow-hidden group hover:scale-[1.02] transition-transform">
            <CardContent className="p-10 text-center">
                <div className="w-20 h-20 bg-indigo-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                    <FiActivity size={40} />
                </div>
                <h3 className="text-2xl font-black text-slate-900 uppercase italic mb-4">Transparencia XAI</h3>
                <p className="text-slate-500 font-medium leading-relaxed">
                    La opacidad es un riesgo técnico. Todo proceso autónomo debe ser explicable en lenguaje natural y auditable en tiempo real.
                </p>
            </CardContent>
         </Card>

         <Card className="border-none shadow-xl bg-white rounded-3xl overflow-hidden group hover:scale-[1.02] transition-transform">
            <CardContent className="p-10 text-center">
                <div className="w-20 h-20 bg-red-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-red-600 group-hover:bg-red-600 group-hover:text-white transition-colors">
                    <FiHeart size={40} />
                </div>
                <h3 className="text-2xl font-black text-slate-900 uppercase italic mb-4">Ética Civilizatoria</h3>
                <p className="text-slate-500 font-medium leading-relaxed">
                    SARITA no define ideologías; protege la estabilidad sistémica para que la sociedad civil florezca de forma autónoma.
                </p>
            </CardContent>
         </Card>
      </div>

      {/* Meta Points Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
         <Card className="border-none shadow-sm rounded-3xl">
            <CardHeader className="p-8 border-b border-slate-50 bg-slate-50/50">
                <CardTitle className="text-xs font-black uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <FiTarget className="text-emerald-500" /> Pilares del Estándar SARITA
                </CardTitle>
            </CardHeader>
            <CardContent className="p-8">
                <div className="space-y-8">
                    {metaPoints.map((point, i) => (
                        <div key={i} className="flex gap-6 items-start">
                            <div className="p-3 bg-white shadow-md rounded-xl">
                                {point.icon}
                            </div>
                            <div>
                                <h4 className="font-black text-slate-900 uppercase italic text-lg mb-1">{point.title}</h4>
                                <p className="text-slate-500 text-sm font-medium leading-relaxed">{point.desc}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
         </Card>

         <div className="space-y-8">
            <Card className="border-none shadow-sm rounded-3xl bg-slate-900 text-white overflow-hidden relative">
                <CardHeader className="p-8 border-b border-white/5">
                    <CardTitle className="text-[10px] font-black uppercase tracking-[0.3em] text-emerald-400">Prohibiciones Absolutas (Red Lines)</CardTitle>
                </CardHeader>
                <CardContent className="p-8 space-y-6">
                    <div className="flex items-center gap-4 border-l-4 border-red-500 pl-4">
                        <p className="font-black uppercase italic leading-tight">Autonomía total sin capacidad de intervención humana directa.</p>
                    </div>
                    <div className="flex items-center gap-4 border-l-4 border-red-500 pl-4 opacity-80">
                        <p className="font-black uppercase italic leading-tight">Auto-expansión de mandato fuera de los dominios institucionales.</p>
                    </div>
                    <div className="flex items-center gap-4 border-l-4 border-red-500 pl-4 opacity-60">
                        <p className="font-black uppercase italic leading-tight">Uso de lógica algorítmica para sustituir autoridades electas.</p>
                    </div>
                    <div className="flex items-center gap-4 border-l-4 border-red-500 pl-4 opacity-40">
                        <p className="font-black uppercase italic leading-tight">Manipulación de la voluntad humana mediante optimización conductual.</p>
                    </div>
                </CardContent>
            </Card>

            <Card className="border-none shadow-2xl rounded-3xl bg-emerald-600 text-white">
                <CardContent className="p-10">
                    <h3 className="text-3xl font-black uppercase italic mb-6">El Antídoto contra la Deriva</h3>
                    <p className="text-emerald-100 font-medium leading-relaxed mb-8">
                        SARITA institucionaliza la <strong>Limitación Consciente</strong> como la mayor virtud técnica. Un sistema no es mejor por ser más autónomo, sino por ser más gobernado y alineado con los fines civilizatorios.
                    </p>
                    <div className="bg-emerald-700/50 p-6 rounded-2xl border border-white/10">
                        <p className="text-xs font-black uppercase tracking-widest mb-2 text-emerald-300">Estado de Consolidación</p>
                        <p className="text-xl font-bold italic">
                            {standardData ? `${standardData.category}: ${standardData.status}` : 'Infraestructura Civilizatoria: ACTIVA'}
                        </p>
                        {standardData && (
                            <div className="mt-4 pt-4 border-t border-white/10 grid grid-cols-2 gap-4 text-[10px] font-black uppercase">
                                <div>Tratados: {standardData.compliance_metrics.active_treaties}</div>
                                <div>Integridad: {standardData.compliance_metrics.audit_integrity}</div>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
         </div>
      </div>
    </div>
  );
}
