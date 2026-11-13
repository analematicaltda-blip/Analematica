'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import {
  FiBook,
  FiDollarSign,
  FiUsers,
  FiShield,
  FiShoppingBag,
  FiLayers,
  FiActivity,
  FiCheckCircle,
  FiAlertTriangle,
  FiTrendingUp,
  FiFileText,
  FiSettings,
  FiExternalLink,
  FiServer
} from 'react-icons/fi';

export default function ErpAdminPage() {
  const [activeTab, setActiveTab] = useState<'resumen' | 'contabilidad' | 'telemetria'>('resumen');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-[#0f1d38] to-[#1e3a8a] text-slate-100 p-6 md:p-10">
      {/* Header Corporativo Metálico */}
      <header className="mb-8 border-b border-sky-500/20 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="h-3 w-3 rounded-full bg-sky-400 animate-ping" />
            <span className="text-xs font-semibold uppercase tracking-wider text-sky-300">
              Panel Administrativo Exclusivo ERP
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-sky-200 via-sky-400 to-blue-200 tracking-tight mt-1">
            GATuristica Enterprise Console
          </h1>
          <p className="text-sm text-sky-200/70 mt-1">
            Gobernanza empresarial privada: Contabilidad PUC, Facturación DIAN, Nómina Electrónica y POS.
          </p>
        </div>

        {/* Indicadores de Entorno y Runtime */}
        <div className="flex items-center gap-3">
          <Badge className="bg-sky-500/10 text-sky-300 border border-sky-400/30 px-3 py-1">
            Puerto ERP: 8001 / 8000
          </Badge>
          <Badge className="bg-blue-600/20 text-blue-300 border border-blue-400/30 px-3 py-1">
            Tenant: Aislado Multi-inquilino
          </Badge>
        </div>
      </header>

      {/* Navegación por Pestañas */}
      <div className="flex gap-2 border-b border-sky-500/20 pb-4 mb-8 overflow-x-auto">
        <button
          onClick={() => setActiveTab('resumen')}
          className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-200 ${
            activeTab === 'resumen'
              ? 'bg-sky-500 text-slate-950 shadow-lg shadow-sky-500/30'
              : 'text-sky-200/70 hover:bg-sky-950/40 hover:text-sky-200'
          }`}
        >
          Resumen Ejecutivo
        </button>
        <button
          onClick={() => setActiveTab('contabilidad')}
          className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-200 ${
            activeTab === 'contabilidad'
              ? 'bg-sky-500 text-slate-950 shadow-lg shadow-sky-500/30'
              : 'text-sky-200/70 hover:bg-sky-950/40 hover:text-sky-200'
          }`}
        >
          Auditoría y Módulo Contable
        </button>
        <button
          onClick={() => setActiveTab('telemetria')}
          className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all duration-200 ${
            activeTab === 'telemetria'
              ? 'bg-sky-500 text-slate-950 shadow-lg shadow-sky-500/30'
              : 'text-sky-200/70 hover:bg-sky-950/40 hover:text-sky-200'
          }`}
        >
          Telemetría y Sockets
        </button>
      </div>

      {/* Contenido según pestaña */}
      {activeTab === 'resumen' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Tarjetas de Métricas Metálicas */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Libro Mayor / PUC"
              value="100% Cuadrado"
              status="Partida doble validada"
              icon={FiBook}
            />
            <MetricCard
              title="Ventas & POS"
              value="$12,850,000 COP"
              status="Facturación DIAN al día"
              icon={FiDollarSign}
            />
            <MetricCard
              title="Nómina Electrónica"
              value="24 Empleados"
              status="Causaciones vigentes"
              icon={FiUsers}
            />
            <MetricCard
              title="Tesorería y Monedero"
              value="$4,320,000 COP"
              status="Conciliación bancaria activa"
              icon={FiShield}
            />
          </div>

          {/* Accesos a los Dominios del ERP */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <DomainCard
              title="Gestión Contable Integral"
              desc="Plan de cuentas PUC, libro diario, libro mayor, balance general y estado de resultados."
              href="/dashboard/prestador/mi-negocio/gestion-contable"
              icon={FiLayers}
              actionText="Entrar al Módulo Contable"
            />
            <DomainCard
              title="Punto de Venta (POS) & DIAN"
              desc="Emisión de tickets de caja, causación automática de ventas y sincronización fiscal."
              href="/dashboard/prestador/mi-negocio/pos"
              icon={FiShoppingBag}
              actionText="Gestionar Facturación"
            />
            <DomainCard
              title="Gestión Operativa y SG-SST"
              desc="Control de tareas operativas, inventario logístico y protocolos de seguridad física."
              href="/dashboard/prestador/mi-negocio/gestion-operativa"
              icon={FiActivity}
              actionText="Revisar Operaciones"
            />
          </div>
        </div>
      )}

      {activeTab === 'contabilidad' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <Card className="bg-slate-900/80 border-sky-500/30 text-slate-100 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="text-xl text-sky-200 flex items-center gap-2">
                <FiCheckCircle className="text-sky-400" /> Diagnóstico de Inconsistencias y Plan Maestro de Contabilidad
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-sky-100/80">
              <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-400/20 space-y-2">
                <h4 className="font-bold text-sky-300">1. Exposición de Endpoints de Asientos Contables:</h4>
                <p>
                  Enrutar formalmente <code>/api/v1/mi-negocio/contable/asientos/</code> en el <code>DefaultRouter</code> de Django para garantizar el registro y consulta inmutable de partidas dobles desde clientes y agentes.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-400/20 space-y-2">
                <h4 className="font-bold text-sky-300">2. Motor de Conciliación Bancaria Automático (Skills):</h4>
                <p>
                  Integración de reglas heurísticas basadas en <code>BACKEND/skills-contabilidad/shared/bank-sync</code> y <code>Conta-Skills</code> para auto-casar extractos con movimientos de pasarela.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-400/20 space-y-2">
                <h4 className="font-bold text-sky-300">3. Pipeline de Cierre Mensual y Liquidación Impositiva:</h4>
                <p>
                  Validación automática de balance, depreciación mensual de activos y liquidación de retenciones/IVA según lineamientos de <code>month-end-close</code> y <code>tax-prep</code>.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'telemetria' && (
        <div className="space-y-6 animate-in fade-in duration-300">
          <Card className="bg-slate-900/80 border-sky-500/30 text-slate-100 backdrop-blur-md">
            <CardHeader>
              <CardTitle className="text-xl text-sky-200 flex items-center gap-2">
                <FiServer className="text-sky-400" /> Estado de Servicios y Conectividad
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-sky-500/20">
                  <span className="text-xs text-sky-300 uppercase font-semibold">Backend Gateway</span>
                  <div className="text-lg font-bold text-white mt-1">Puerto 8000 / Django DRF</div>
                  <p className="text-xs text-sky-200/60 mt-1">Rutas: <code>/api/v1/mi-negocio/</code></p>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-sky-500/20">
                  <span className="text-xs text-sky-300 uppercase font-semibold">Frontend ERP</span>
                  <div className="text-lg font-bold text-white mt-1">Puerto 3001 / Next.js</div>
                  <p className="text-xs text-sky-200/60 mt-1">Modo: Desacoplado Independiente</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, status, icon: Icon }: any) {
  return (
    <Card className="bg-slate-900/90 border-sky-500/30 text-slate-100 shadow-lg shadow-sky-950/50 backdrop-blur-md">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-sky-300 uppercase tracking-wide">{title}</p>
            <h3 className="text-2xl font-black text-white mt-1">{value}</h3>
            <p className="text-xs text-sky-200/70 mt-1 flex items-center gap-1">
              <FiCheckCircle className="text-sky-400" size={12} /> {status}
            </p>
          </div>
          <div className="p-3 bg-sky-500/10 border border-sky-400/30 rounded-2xl text-sky-300">
            <Icon size={24} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function DomainCard({ title, desc, href, icon: Icon, actionText }: any) {
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
          {actionText} <FiExternalLink size={14} />
        </Link>
      </CardContent>
    </Card>
  );
}
