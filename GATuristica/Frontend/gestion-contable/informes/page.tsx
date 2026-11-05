'use client';
import React from 'react';
import AnalisisFinancieroChart from './AnalisisFinancieroChart'; // Suponiendo que el gráfico se refactoriza a su propio componente
import LibroMayorReporte from './LibroMayorReporte';
import BalanceComprobacionReporte from './BalanceComprobacionReporte';
import EstadoResultadosReporte from './EstadoResultadosReporte';
import BalanceGeneralReporte from './BalanceGeneralReporte';

import { FiBookOpen, FiActivity, FiPieChart, FiFileText, FiDownload } from 'react-icons/fi';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/Card';

const reports = [
  { title: 'Libro Diario', desc: 'Registros cronológicos de todas las transacciones.', href: '/dashboard/prestador/mi-negocio/gestion-contable/asientos', icon: FiBookOpen, color: 'bg-blue-50 text-blue-600' },
  { title: 'Libro Mayor', desc: 'Movimientos históricos por cuenta contable.', href: '/dashboard/prestador/mi-negocio/gestion-contable/informes/libro-mayor', icon: FiActivity, color: 'bg-green-50 text-green-600' },
  { title: 'Balance General', desc: 'Situación financiera (Activo, Pasivo, Patrimonio).', href: '/dashboard/prestador/mi-negocio/gestion-contable/informes/balance-general', icon: FiPieChart, color: 'bg-purple-50 text-purple-600' },
  { title: 'Estado de Resultados', desc: 'Resumen de ingresos, costos y gastos (P&L).', href: '/dashboard/prestador/mi-negocio/gestion-contable/informes/estado-resultados', icon: FiFileText, color: 'bg-orange-50 text-orange-600' },
  { title: 'Balance de Comprobación', desc: 'Resumen de sumas y saldos para verificación.', href: '#', icon: FiDownload, color: 'bg-slate-50 text-slate-600' },
];

export default function InformesPage() {
  return (
    <div className="space-y-8 py-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Centro de Reportes Financieros</h1>
        <p className="text-slate-500 mt-1">Acceda a la información contable estratégica de su negocio.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => (
          <Link key={report.title} href={report.href}>
            <Card className="border-none shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group bg-white">
              <CardContent className="p-8 space-y-4">
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${report.color} group-hover:scale-110 transition-transform`}>
                  <report.icon size={28} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-800">{report.title}</h3>
                  <p className="text-sm text-slate-500 mt-1 leading-relaxed">{report.desc}</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="bg-slate-900 rounded-3xl p-12 text-white overflow-hidden relative">
         <div className="relative z-10 space-y-4 max-w-lg">
            <h2 className="text-3xl font-black tracking-tight">Análisis Predictivo de Flujo</h2>
            <p className="text-slate-400">Próximamente: SARITA utilizará IA para proyectar su flujo de caja y alertar sobre riesgos de liquidez.</p>
            <div className="pt-4">
               <span className="bg-brand text-white px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest">Fase IA 6.0</span>
            </div>
         </div>
         <div className="absolute right-[-100px] bottom-[-100px] opacity-10">
            <FiActivity size={400} />
         </div>
      </div>
    </div>
  );
}
