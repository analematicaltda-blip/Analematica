"use client";

import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Users,
  BarChart3,
  PieChart,
  ArrowUpRight,
  RefreshCw,
  Activity
} from 'lucide-react';

interface KPIs {
  MRR?: number;
  ARR?: number;
  CONVERSION_RATE?: number;
}

export default function HoldingKPIDashboard() {
  const [kpis, setKpis] = useState<KPIs>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchKPIs();
  }, []);

  const fetchKPIs = async () => {
    try {
      const response = await fetch('/api/commercial-engine/kpis/latest/');
      const data = await response.json();
      setKpis(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      setLoading(false);
    }
  };

  const formatCurrency = (val: number = 0) => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0
    }).format(val);
  };

  if (loading) return <div className="p-8 text-center">Analizando métricas de Holding...</div>;

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <Activity className="text-blue-600" />
            Dashboard Estratégico - Sarita Holding
          </h1>
          <p className="text-gray-500 text-sm">Monitoreo de ingresos recurrentes y conversión SaaS</p>
        </div>
        <button
          onClick={() => { setLoading(true); fetchKPIs(); }}
          className="bg-white border p-2 rounded-lg hover:bg-gray-100 transition shadow-sm"
        >
          <RefreshCw size={20} className="text-gray-600" />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-blue-100 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
            <DollarSign size={80} />
          </div>
          <p className="text-sm font-medium text-gray-400 mb-1">Monthly Recurring Revenue (MRR)</p>
          <h3 className="text-3xl font-bold text-gray-800 mb-2">{formatCurrency(kpis.MRR)}</h3>
          <div className="flex items-center text-xs text-green-600 font-medium">
            <ArrowUpRight size={14} />
            <span>+12.5% vs mes anterior</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-purple-100 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
            <TrendingUp size={80} />
          </div>
          <p className="text-sm font-medium text-gray-400 mb-1">Annual Recurring Revenue (ARR)</p>
          <h3 className="text-3xl font-bold text-gray-800 mb-2">{formatCurrency(kpis.ARR)}</h3>
          <div className="flex items-center text-xs text-blue-600 font-medium">
            <span>Proyección a 12 meses</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-green-100 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition">
            <Users size={80} />
          </div>
          <p className="text-sm font-medium text-gray-400 mb-1">Tasa de Conversión</p>
          <h3 className="text-3xl font-bold text-gray-800 mb-2">{kpis.CONVERSION_RATE}%</h3>
          <div className="flex items-center text-xs text-green-600 font-medium">
            <ArrowUpRight size={14} />
            <span>+2.1% Lead-to-Customer</span>
          </div>
        </div>
      </div>

      {/* Insights Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border">
          <h4 className="font-bold text-gray-800 mb-6 flex items-center gap-2">
            <BarChart3 size={18} className="text-blue-500" />
            Crecimiento de Suscripciones
          </h4>
          <div className="h-64 bg-gray-50 rounded-xl border border-dashed flex items-center justify-center">
             <p className="text-gray-400 text-sm italic">[Gráfico de Crecimiento Temporal]</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border">
          <h4 className="font-bold text-gray-800 mb-6 flex items-center gap-2">
            <PieChart size={18} className="text-purple-500" />
            Distribución por Plan
          </h4>
          <div className="h-64 bg-gray-50 rounded-xl border border-dashed flex items-center justify-center">
             <p className="text-gray-400 text-sm italic">[Gráfico de Torta de Planes]</p>
          </div>
        </div>
      </div>
    </div>
  );
}
