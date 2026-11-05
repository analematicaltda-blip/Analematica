'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  FiDollarSign,
  FiVolume2,
  FiTrendingUp,
  FiZap,
  FiLayout,
  FiActivity,
  FiSettings,
  FiFileText,
  FiUsers,
  FiArrowRight,
  FiPlus,
  FiHeart,
  FiSpeaker
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import { useComercialApi } from './hooks/useComercialApi';
import { TraceabilityBanner, TraceabilityInfo } from '@/components/ui/TraceabilityBanner';
 
import { GRCIndicator } from '@/components/ui/GRCIndicator';
 
import { PermissionGuard, usePermissions } from '@/ui/guards/PermissionGuard';
import { auditLogger } from '@/services/auditLogger';
import { ViewState } from '@/components/ui/ViewState';

// Importación de los niveles de clase mundial
import Level1_Communication from './components/Level1_Communication';
import Level2_Responses from './components/Level2_Responses';
import LevelAIStudio from './components/LevelAIStudio';
import LevelFunnels from './components/LevelFunnels';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import Link from 'next/link';

enum CommercialView {
  DASHBOARD = 'dashboard',
  MARKETING = 'marketing',
  SALES_CRM = 'sales_crm',
  AI_STUDIO = 'ai_studio',
  FUNNELS = 'funnels',
  INVOICING = 'invoicing',
  LOYALTY = 'loyalty'
}

export default function GestionComercialPage() {
  const { token, user } = useAuth();
  const { role, isReadOnly } = usePermissions();
  const [activeView, setActiveView] = useState<CommercialView>(CommercialView.DASHBOARD);
  const { facturas, isLoading: isLoadingFacturas } = useComercialApi();
  const { getClientes, getStatistics, isLoading: isLoadingClientes } = useMiNegocioApi();
  const [clientes, setClientes] = useState<any[]>([]);
  const [statsData, setStatsData] = useState<any>(null);

  const isLoading = isLoadingFacturas || isLoadingClientes;

  useEffect(() => {
    getStatistics().then(res => res && setStatsData(res));
  }, [getStatistics]);

  useEffect(() => {
    if (activeView === CommercialView.LOYALTY) {
      getClientes().then(res => res && setClientes(res.results));
    }
  }, [activeView, getClientes]);

  useEffect(() => {
    auditLogger.log({
      type: 'VIEW_LOAD',
      view: `Gestion Comercial - ${activeView}`,
      userRole: role,
      userEmail: user?.email,
      status: 'OK'
    });
  }, [activeView, role, user]);

  const traceabilityData: Record<CommercialView, TraceabilityInfo> = {
    [CommercialView.DASHBOARD]: {
      source: '/api/dashboard/analytics/',
      model: 'OperationalStats',
      period: 'Mes Actual',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'OK',
      certainty: 'Datos reales - Backend validado'
    },
    [CommercialView.MARKETING]: {
      source: '/api/marketing/campaigns/',
      model: 'Campaign',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'OK',
      certainty: 'Datos reales - Orquestación SARITA'
    },
    [CommercialView.SALES_CRM]: {
      source: '/api/bff/sales/opportunities/',
      model: 'Opportunity',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'OK'
    },
    [CommercialView.AI_STUDIO]: {
      source: '/api/sadi/intent/',
      model: 'SadiSession',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'INFO',
      certainty: 'Motor de Inteligencia Activo'
    },
    [CommercialView.FUNNELS]: {
      source: '/api/bff/funnel-builder/',
      model: 'Funnel',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'OK',
      certainty: 'Datos reales - Motor de Conversión Activo'
    },
    [CommercialView.INVOICING]: {
      source: '/api/v1/mi-negocio/comercial/facturas-venta/',
      model: 'FacturaVenta',
      period: 'Histórico Total',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'OK'
    },
    [CommercialView.LOYALTY]: {
      source: '/api/v1/mi-negocio/comercial/clientes/',
      model: 'Cliente',
      period: 'Últimos 12 meses',
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
      status: 'OK'
    }
  };

  const renderContent = () => {
    switch (activeView) {
      case CommercialView.MARKETING:
        return <Level1_Communication authToken={token!} />;
      case CommercialView.SALES_CRM:
        return <Level2_Responses />;
      case CommercialView.AI_STUDIO:
        return <LevelAIStudio />;
      case CommercialView.FUNNELS:
        return <LevelFunnels authToken={token!} />;
      case CommercialView.LOYALTY:
        return (
          <div className="p-8 space-y-6 animate-in fade-in duration-500">
 
             <TraceabilityBanner info={traceabilityData[CommercialView.LOYALTY]} />
 
             <div className="flex justify-between items-center">
                <h2 className="text-2xl font-black text-slate-900 dark:text-white uppercase italic">Fidelización y Postventa</h2>
             </div>
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="border-none shadow-sm bg-emerald-50 dark:bg-emerald-900/10">
                   <CardContent className="p-6">
                      <p className="text-[10px] font-black text-emerald-600 uppercase tracking-widest mb-1">Clientes Activos</p>
                      <h3 className="text-3xl font-black">{clientes.length}</h3>
                   </CardContent>
                </Card>
                <Card className="border-none shadow-sm bg-brand/5">
                   <CardContent className="p-6">
                      <p className="text-[10px] font-black text-brand uppercase tracking-widest mb-1">Tasa de Recompra</p>
                      <h3 className="text-3xl font-black">12%</h3>
                   </CardContent>
                </Card>
                <Card className="border-none shadow-sm bg-indigo-50 dark:bg-indigo-900/10">
                   <CardContent className="p-6">
                      <p className="text-[10px] font-black text-indigo-600 uppercase tracking-widest mb-1">LTV Promedio</p>
                      <h3 className="text-3xl font-black">$450.00</h3>
                   </CardContent>
                </Card>
             </div>
             <Card className="border-none shadow-sm overflow-hidden">
                <CardContent className="p-0">
                  <Table>
                    <TableHeader className="bg-slate-50 dark:bg-black/20">
                      <TableRow>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest px-8">Cliente</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">Email</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">Estado</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right px-8">Acción</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                        {clientes.map((c: any) => (
                          <TableRow key={c.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                            <TableCell className="font-bold text-slate-700 dark:text-slate-200 px-8">{c.nombre}</TableCell>
                            <TableCell className="text-xs text-slate-500">{c.email}</TableCell>
                            <TableCell>
                               <Badge className="bg-emerald-100 text-emerald-700 text-[8px] font-black uppercase">Activo</Badge>
                            </TableCell>
                            <TableCell className="text-right px-8">
                               <Button variant="ghost" size="sm" className="text-brand">Ver Historial</Button>
                            </TableCell>
                          </TableRow>
                        ))}
                        {clientes.length === 0 && (
                          <TableRow>
                            <TableCell colSpan={4} className="p-20 text-center text-slate-400 uppercase italic tracking-widest text-xs">
                               No se han detectado clientes registrados en el CRM.
                            </TableCell>
                          </TableRow>
                        )}
                    </TableBody>
                  </Table>
                </CardContent>
             </Card>
          </div>
        );
      case CommercialView.INVOICING:
        return (
          <div className="p-8 space-y-6 animate-in fade-in duration-500">
 
             <TraceabilityBanner info={traceabilityData[CommercialView.INVOICING]} />
 
             <div className="flex justify-between items-center">
                <h2 className="text-2xl font-black text-slate-900 dark:text-white uppercase italic">Libro de Ventas y Facturación</h2>
                <PermissionGuard deniedRoles={['Auditor', 'Observador']}>
                  <Link href="/dashboard/prestador/mi-negocio/gestion-comercial/ventas/nueva">
                    <Button className="bg-brand text-white font-black px-6"><FiPlus className="mr-2"/> Emitir Factura</Button>
                  </Link>
                </PermissionGuard>
             </div>
             <Card className="border-none shadow-sm overflow-hidden">
                <CardContent className="p-0">
                  <Table>
                    <TableHeader className="bg-slate-50 dark:bg-black/20">
                      <TableRow>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest px-8">N° Factura</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">Cliente</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest">Fecha</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest text-center">Clasificación</TableHead>
                        <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right px-8">Monto</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {facturas.map((f: any) => (
                        <TableRow key={f.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                          <TableCell className="font-mono text-xs font-black text-brand px-8">{f.number}</TableCell>
                          <TableCell className="font-bold text-slate-700 dark:text-slate-200">{f.cliente_nombre}</TableCell>
                          <TableCell className="text-xs text-slate-500">{new Date(f.issue_date).toLocaleDateString()}</TableCell>
                          <TableCell className="text-center">
                             <Badge variant="outline" className="text-[8px] font-black border-indigo-100 text-indigo-400 uppercase">Dato Financiero</Badge>
                          </TableCell>
                          <TableCell className="text-right font-black text-slate-900 dark:text-white px-8">${parseFloat(f.total).toLocaleString()}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
             </Card>
          </div>
        );
      case CommercialView.DASHBOARD:
      default:
        return (
          <div className="p-8 space-y-10 animate-in fade-in duration-700">
            <TraceabilityBanner info={traceabilityData[CommercialView.DASHBOARD]} />
 
            <GRCIndicator
              moduleName="Gestión Comercial"
              risks={['R1: Dependencias externas']}
              controls={['Backend RBAC', 'Frontend PermissionGuard']}
            />
 
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter uppercase leading-none">Operación y Crecimiento Comercial</h1>
                <p className="text-slate-500 dark:text-slate-400 mt-2 text-lg font-medium italic">Gestión Operativa del Prestador de Servicios Turísticos.</p>
              </div>
              <div className="flex bg-slate-100 dark:bg-brand-deep/30 p-1 rounded-xl">
                 <button className="px-6 py-2 bg-white dark:bg-brand shadow-sm rounded-lg text-sm font-bold text-slate-900 dark:text-white">Snapshot</button>
                 <button className="px-6 py-2 text-sm font-bold text-slate-500 hover:text-slate-700">Historial</button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
               {[
                 { label: 'Ingresos Mes', val: statsData?.ventas_mes ? `$${statsData.ventas_mes.toLocaleString()}` : '$0.00', icon: FiDollarSign, color: 'text-brand' },
                 { label: 'Leads Nuevos', val: statsData?.leads_nuevos || '0', icon: FiUsers, color: 'text-indigo-600' },
                 { label: 'Conversión', val: statsData?.tasa_conversion ? `${statsData.tasa_conversion}%` : '0%', icon: FiZap, color: 'text-amber-500' },
                 { label: 'Tickets Activos', val: statsData?.tickets_activos || '0', icon: FiActivity, color: 'text-emerald-600' },
               ].map((kpi, i) => (
                 <Card key={i} className="border-none shadow-sm bg-white dark:bg-brand-deep/20">
                    <CardContent className="p-8 flex items-center justify-between">
                       <div>
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{kpi.label}</p>
                          <h3 className="text-3xl font-black text-slate-900 dark:text-white">{kpi.val}</h3>
                       </div>
                       <div className={`p-4 rounded-2xl bg-slate-50 dark:bg-black/20 ${kpi.color}`}>
                          <kpi.icon size={24} />
                       </div>
                    </CardContent>
                 </Card>
               ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
               <Card className="border-none shadow-xl bg-slate-900 text-white rounded-[2rem] p-10 overflow-hidden relative group cursor-pointer" onClick={() => setActiveView(CommercialView.FUNNELS)}>
                  <div className="absolute -right-10 -bottom-10 opacity-10 group-hover:scale-110 transition-transform duration-1000">
                     <FiLayout size={250} />
                  </div>
                  <Badge className="bg-brand-light text-brand-deep font-black mb-4">OPTIMIZADOR IA</Badge>
                  <h3 className="text-3xl font-black italic leading-tight">Arquitecto de Embudos</h3>
                  <p className="mt-4 text-slate-400 text-lg">Diseña flujos de conversión automatizados para tus paquetes turísticos.</p>
                  <Button className="mt-10 bg-white text-slate-900 font-black px-8 py-4 rounded-xl">Configurar Ahora</Button>
               </Card>

               <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 rounded-[2rem] p-10 flex flex-col justify-between" onClick={() => setActiveView(CommercialView.MARKETING)}>
                  <div>
                    <FiSpeaker className="text-brand mb-6" size={40} />
                    <h3 className="text-2xl font-black text-slate-900 dark:text-white uppercase tracking-tighter">Marketing Multicanal</h3>
                    <p className="mt-2 text-slate-500">Envía promociones por WhatsApp, Email y Redes Sociales en un solo clic.</p>
                  </div>
                  <div className="mt-10 flex items-center gap-2 text-brand font-black text-xs uppercase tracking-widest cursor-pointer group">
                     Ir al estudio <FiArrowRight className="group-hover:translate-x-2 transition-transform" />
                  </div>
               </Card>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-black transition-colors flex flex-col">
       <ViewState
          isLoading={isLoading}
          loadingMessage="Sincronizando flujo comercial..."
          isEmpty={facturas.length === 0 && activeView === CommercialView.INVOICING}
          emptyMessage="No se han detectado facturas emitidas en este periodo."
       >
       {/* Sub-nav horizontal corporativo */}
       <div className="bg-white dark:bg-brand-deep/10 border-b border-slate-100 dark:border-white/5 flex items-center px-8 gap-8 overflow-x-auto no-scrollbar sticky top-0 z-30 backdrop-blur-md">
          {[
            { id: CommercialView.DASHBOARD, label: 'Resumen', icon: FiActivity },
            { id: CommercialView.MARKETING, label: 'Marketing', icon: FiVolume2 },
            { id: CommercialView.SALES_CRM, label: 'Ventas y CRM', icon: FiTrendingUp },
            { id: CommercialView.AI_STUDIO, label: 'Estudio AI', icon: FiZap },
            { id: CommercialView.FUNNELS, label: 'Arquitecto', icon: FiLayout },
            { id: CommercialView.INVOICING, label: 'Facturación', icon: FiFileText },
            { id: CommercialView.LOYALTY, label: 'Fidelización', icon: FiHeart },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveView(tab.id)}
              className={`py-6 flex items-center gap-2 text-xs font-black uppercase tracking-widest transition-all border-b-2 ${
                activeView === tab.id
                ? 'border-brand text-brand'
                : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-200'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
       </div>

       <div className="flex-1 overflow-y-auto">
          {renderContent()}
       </div>
       </ViewState>
    </div>
  );
}

 
