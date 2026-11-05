'use client';
import React from 'react';
import AnalisisFinancieroChart from './AnalisisFinancieroChart'; // Suponiendo que el gráfico se refactoriza a su propio componente
import LibroMayorReporte from './LibroMayorReporte';
import BalanceComprobacionReporte from './BalanceComprobacionReporte';
import EstadoResultadosReporte from './EstadoResultadosReporte';
import BalanceGeneralReporte from './BalanceGeneralReporte';

export default function InformesPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Informes Financieros y Contables</h1>

      {/* Gráfico Principal */}
      <AnalisisFinancieroChart />

      {/* Reportes Detallados */}
      <LibroMayorReporte />
      <BalanceComprobacionReporte />
      <EstadoResultadosReporte />
      <BalanceGeneralReporte />

    </div>
  );
}
