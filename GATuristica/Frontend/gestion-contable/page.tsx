'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi, ChartOfAccount, JournalEntry } from '../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import {
  FiBook,
  FiPlus,
  FiPieChart,
  FiFileText,
  FiTrendingUp,
  FiActivity,
  FiCheckCircle,
  FiAlertTriangle
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

export default function GestionContablePage() {
  const { getChartOfAccounts, getJournalEntries, isLoading } = useMiNegocioApi();
  const [accounts, setAccounts] = useState<ChartOfAccount[]>([]);
  const [entries, setEntries] = useState<JournalEntry[]>([]);

  useEffect(() => {
    const loadData = async () => {
      const [accs, ents] = await Promise.all([
        getChartOfAccounts(),
        getJournalEntries()
      ]);
      if (accs) setAccounts(accs);
      if (ents) setEntries(ents);
    };
    loadData();
  }, [getChartOfAccounts, getJournalEntries]);

  // KPIs Simulados para demo de "Clase Mundial" si no hay datos reales
  const stats = [
    { label: 'Cuentas Activas', value: accounts.length || '0', icon: FiBook, color: 'text-blue-600' },
    { label: 'Asientos del Mes', value: entries.length || '0', icon: FiActivity, color: 'text-green-600' },
    { label: 'Patrimonio Neto', value: '$0.00', icon: FiTrendingUp, color: 'text-indigo-600' },
    { label: 'Estatus Fiscal', value: 'Al día', icon: FiCheckCircle, color: 'text-teal-600' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Disclaimer de Verdad Operativa (F-CF) */}
      <div className="bg-amber-50 border-l-4 border-amber-500 p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <FiAlertTriangle className="h-5 w-5 text-amber-500" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-amber-700 font-bold uppercase tracking-tight">
              ESTADO DEL MÓDULO: INTEGRACIÓN PARCIAL
            </p>
            <p className="text-xs text-amber-600 mt-1">
              La arquitectura contable está en proceso de unificación (Tenant vs ProviderProfile).
              Ciertos reportes pueden no reflejar la totalidad de las operaciones comerciales asíncronas.
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Gestión Contable Sistémica</h1>
          <p className="text-gray-500 mt-1">Control integral del patrimonio y las obligaciones fiscales.</p>
        </div>
        <div className="flex gap-3">
          <Link href="/dashboard/prestador/mi-negocio/gestion-contable/asientos/nuevo">
            <Button className="bg-indigo-600 hover:bg-indigo-700">
              <FiPlus className="mr-2" /> Nuevo Asiento
            </Button>
          </Link>
          <Button variant="outline">
            <FiPieChart className="mr-2" /> Reportes
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <Card key={i} className="border-none shadow-sm bg-white hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-xl bg-gray-50 ${stat.color}`}>
                  <stat.icon size={24} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Plan de Cuentas Resumen */}
        <Card className="lg:col-span-2 shadow-sm border-none">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <FiFileText className="text-indigo-600" /> Plan de Cuentas Maestro
            </CardTitle>
            <Link href="/dashboard/prestador/mi-negocio/gestion-contable/plan-de-cuentas" className="text-sm text-indigo-600 hover:underline">
              Ver todo
            </Link>
          </CardHeader>
          <CardContent>
            {isLoading && accounts.length === 0 ? (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => <div key={i} className="h-10 bg-gray-100 rounded animate-pulse" />)}
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-50/50">
                    <TableHead>Código</TableHead>
                    <TableHead>Nombre de Cuenta</TableHead>
                    <TableHead>Naturaleza</TableHead>
                    <TableHead className="text-right">Saldo</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {accounts.slice(0, 8).map((account) => (
                    <TableRow key={account.code} className="hover:bg-gray-50/50 transition-colors">
                      <TableCell className="font-mono text-xs font-bold text-indigo-600">{account.code}</TableCell>
                      <TableCell className="font-medium">{account.name}</TableCell>
                      <TableCell>
                        <Badge variant={account.nature === 'DEBITO' ? 'default' : 'secondary'} className="text-[10px] uppercase tracking-wider">
                          {account.nature}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-semibold">$0.00</TableCell>
                    </TableRow>
                  ))}
                  {accounts.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-gray-500 italic">
                        No hay cuentas configuradas en el plan maestro.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Últimos Movimientos */}
        <Card className="shadow-sm border-none">
          <CardHeader>
            <CardTitle className="text-lg font-semibold flex items-center gap-2">
              <FiActivity className="text-green-600" /> Actividad Reciente
            </CardTitle>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
               {entries.slice(0, 5).map((entry) => (
                 <div key={entry.id} className="flex flex-col p-3 rounded-lg border border-gray-100 hover:border-indigo-200 transition-colors">
                   <div className="flex justify-between items-start mb-1">
                     <span className="text-xs font-bold text-gray-400">#{entry.id}</span>
                     <span className="text-[10px] text-gray-500 uppercase">{new Date(entry.entry_date).toLocaleDateString()}</span>
                   </div>
                   <p className="text-sm font-medium text-gray-800 line-clamp-1">{entry.description}</p>
                   <div className="mt-2 flex justify-between items-center">
                      <Badge variant="outline" className="text-[9px]">{entry.entry_type}</Badge>
                      <span className="text-sm font-bold text-indigo-600">$0.00</span>
                   </div>
                 </div>
               ))}
               {entries.length === 0 && (
                 <div className="text-center py-12">
                   <FiBook size={40} className="mx-auto text-gray-200 mb-2" />
                   <p className="text-sm text-gray-400">Sin movimientos recientes.</p>
                 </div>
               )}
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

