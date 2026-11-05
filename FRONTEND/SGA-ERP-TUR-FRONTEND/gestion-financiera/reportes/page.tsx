'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiFileText, FiDownload, FiPieChart, FiTrendingUp, FiActivity } from 'react-icons/fi';

const reports = [
  { title: 'Estado de Resultados (P&L)', desc: 'Resumen de ingresos, costos y gastos acumulados.', icon: FiTrendingUp, color: 'text-green-600 bg-green-50' },
  { title: 'Balance General', desc: 'Situación financiera detallada a la fecha.', icon: FiPieChart, color: 'text-blue-600 bg-blue-50' },
  { title: 'Flujo de Efectivo', desc: 'Movimientos de caja por operación, inversión y financiación.', icon: FiActivity, color: 'text-purple-600 bg-purple-50' },
  { title: 'Ejecución Presupuestal', desc: 'Comparativa entre lo planeado y lo realmente gastado.', icon: FiFileText, color: 'text-amber-600 bg-amber-50' },
];

export default function ReportesFinancierosPage() {
  return (
    <div className="space-y-8 py-8">
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Reportes Financieros</h1>
        <p className="text-slate-500 mt-1">Generación de estados financieros oficiales y documentos de auditoría.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((report) => (
          <Card key={report.title} className="border-none shadow-sm bg-white hover:shadow-xl transition-all duration-300 group">
            <CardContent className="p-10 flex gap-8 items-start">
               <div className={`w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0 ${report.color} group-hover:scale-110 transition-transform`}>
                  <report.icon size={32} />
               </div>
               <div className="flex-1 space-y-4">
                  <div>
                     <h3 className="text-xl font-bold text-slate-800">{report.title}</h3>
                     <p className="text-sm text-slate-500 mt-1 leading-relaxed">{report.desc}</p>
                  </div>
                  <div className="flex gap-2">
                     <Button variant="outline" size="sm" className="font-bold">Vista Previa</Button>
                     <Button className="bg-slate-900 text-white font-black px-6">
                        <FiDownload className="mr-2" /> PDF
                     </Button>
                  </div>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="bg-slate-100 p-12 rounded-[3rem] text-center space-y-4">
         <FiFileText size={48} className="mx-auto text-slate-300" />
         <h2 className="text-2xl font-black text-slate-800">¿Necesita un reporte personalizado?</h2>
         <p className="text-slate-500 max-w-md mx-auto">Solicite a SARITA la generación de tableros específicos para juntas directivas o entidades de control.</p>
         <Button className="bg-brand text-white font-black px-8 py-4 rounded-xl mt-4">Hablar con SARITA Finance</Button>
      </div>
    </div>
  );
}
