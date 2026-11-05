'use client';

import React from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  FiMapPin,
  FiCompass,
  FiCalendar,
  FiUsers,
  FiAward,
  FiEye,
  FiTrendingUp,
  FiGlobe,
  FiExternalLink,
  FiCheckCircle
} from 'react-icons/fi';

export default function TurismoAdminPage() {
  const stats = [
    { title: 'Catálogo de Prestadores', value: '148 Activos', status: 'Verificados en plataforma', icon: FiUsers },
    { title: 'Atractivos & Rutas', value: '32 Publicados', status: 'Cobertura territorial total', icon: FiCompass },
    { title: 'Reservas del Destino', value: '1,240 este mes', status: 'Sincronizadas con ERP', icon: FiCalendar },
    { title: 'Visitantes Registrados', value: '28,450', status: 'Tráfico público portal', icon: FiGlobe },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-[#0a192f] to-[#1e3a8a] text-slate-100 p-6 md:p-10">
      {/* Header Territorial con Paleta Azul Metalizado y Azul Claro */}
      <header className="mb-8 border-b border-sky-400/20 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="h-3 w-3 rounded-full bg-sky-400 animate-ping" />
            <span className="text-xs font-semibold uppercase tracking-wider text-sky-300">
              Panel Administrativo Exclusivo de Turismo
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-sky-200 via-sky-400 to-blue-200 tracking-tight mt-1">
            Gobernanza Territorial y Plataforma de Turismo
          </h1>
          <p className="text-sm text-sky-200/70 mt-1">
            Gestión pública del destino: Directorio de prestadores, experiencias, guías y oferta turística.
          </p>
        </div>

        {/* Runtime info */}
        <div className="flex items-center gap-3">
          <Badge className="bg-sky-500/10 text-sky-300 border border-sky-400/30 px-3 py-1">
            Portal Público: Puerto 3000
          </Badge>
          <Badge className="bg-blue-600/20 text-blue-300 border border-blue-400/30 px-3 py-1">
            API Gateway: Puerto 8000
          </Badge>
        </div>
      </header>

      {/* Tarjetas de Estadísticas Metálicas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((s, i) => (
          <Card key={i} className="bg-slate-900/90 border-sky-500/30 text-slate-100 shadow-lg shadow-sky-950/50 backdrop-blur-md">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-sky-300 uppercase tracking-wide">{s.title}</p>
                  <h3 className="text-2xl font-black text-white mt-1">{s.value}</h3>
                  <p className="text-xs text-sky-200/70 mt-1 flex items-center gap-1">
                    <FiCheckCircle className="text-sky-400" size={12} /> {s.status}
                  </p>
                </div>
                <div className="p-3 bg-sky-500/10 border border-sky-400/30 rounded-2xl text-sky-300">
                  <s.icon size={24} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Áreas de Gobernanza Territorial */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <TurismoAreaCard
          title="Directorio de Prestadores"
          desc="Administración de perfiles públicos, artesanos, guías turísticos y categorizaciones institucionales."
          href="/dashboard/prestadores"
          icon={FiUsers}
          action="Gestionar Directorio"
        />
        <TurismoAreaCard
          title="Atractivos y Circuitos Turísticos"
          desc="Catálogo georreferenciado de senderos ecológicos, balnearios, museos y experiencias culturales."
          href="/dashboard/atractivos"
          icon={FiMapPin}
          action="Administrar Atractivos"
        />
        <TurismoAreaCard
          title="Capacitaciones y Certificaciones"
          desc="Talleres para la comunidad, estándares de servicio y fortalecimiento del tejido turístico regional."
          href="/dashboard/capacitaciones"
          icon={FiAward}
          action="Ver Convocatorias"
        />
      </div>
    </div>
  );
}

function TurismoAreaCard({ title, desc, href, icon: Icon, action }: any) {
  return (
    <Card className="bg-slate-900/90 border-sky-500/30 text-slate-100 flex flex-col justify-between hover:border-sky-400 transition-all duration-300 group">
      <CardContent className="p-6 space-y-4">
        <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-400/30 text-sky-300 flex items-center justify-center">
          <Icon size={24} />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white group-hover:text-sky-300 transition-colors">
            {title}
          </h3>
          <p className="text-sm text-sky-200/70 mt-2 leading-relaxed">
            {desc}
          </p>
        </div>
        <Link
          href={href}
          className="inline-flex items-center gap-2 text-sm font-bold text-sky-400 hover:text-sky-200 pt-2 transition-colors"
        >
          {action} <FiExternalLink size={14} />
        </Link>
      </CardContent>
    </Card>
  );
}
