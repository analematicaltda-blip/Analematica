"use client";

import React, { useState, useEffect, useCallback } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { FiUsers, FiFileText, FiBarChart2, FiAlertCircle, FiBriefcase, FiDownload, FiCheckSquare, FiPieChart } from 'react-icons/fi';
import { getStatistics, StatisticsData } from '@/services/api';
import api from '@/services/api';

// --- Componentes de UI ---

const StatCard = ({
  icon,
  title,
  value,
  details,
  color = 'blue'
}: {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  details?: string;
  color?: string;
}) => {
  const colors = {
    blue: 'from-blue-500 to-indigo-600',
    green: 'from-green-500 to-teal-600',
    purple: 'from-purple-500 to-violet-600',
    red: 'from-red-500 to-orange-600',
  };
  return (
    <div className={`bg-gradient-to-br ${colors[color]} text-white p-5 rounded-lg shadow-md`}>
      <div className="flex items-center">
        <div className="text-3xl mr-4">{icon}</div>
        <div>
          <p className="text-sm font-medium uppercase opacity-90">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
      </div>
      {details && <p className="text-xs opacity-80 mt-2">{details}</p>}
    </div>
  );
};

const ChartContainer = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <div className="bg-white p-6 rounded-lg shadow-md">
    <h3 className="text-lg font-semibold text-gray-700 mb-4">{title}</h3>
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>{children}</ResponsiveContainer>
    </div>
  </div>
);

// --- Dashboard Principal ---

export default function StatisticsDashboard() {
  const [stats, setStats] = useState<StatisticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getStatistics();
      setStats(data);
    } catch {
      setError("No se pudieron cargar las estadísticas.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const handleExport = async () => {
    setIsExporting(true);
    try {
      const response = await api.get('/admin/export-excel/', {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'reporte_turismo.xlsx');
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("No se pudo generar el reporte. Inténtelo de nuevo.");
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) return <p className="text-center py-12">Cargando estadísticas avanzadas...</p>;
  if (error) return <div className="text-center py-12 text-red-500"><FiAlertCircle className="mx-auto h-12 w-12"/><p className="mt-4">{error}</p></div>;
  if (!stats) return <p className="text-center py-12">No hay datos de estadísticas disponibles.</p>;

  const { summary } = stats;

  const userRoleData = Object.entries(summary.usuarios.por_rol).map(([name, value]) => ({ name, value }));
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

  return (
    <div className="bg-gray-100 p-4 sm:p-6 rounded-xl space-y-8">
      <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
        <h2 className="text-3xl font-bold text-gray-800 flex items-center"><FiBarChart2 className="mr-3" />Dashboard de Inteligencia</h2>

        <div className="flex items-center gap-2 bg-white p-2 rounded-lg border">
            <button
              onClick={handleExport}
              disabled={isExporting}
              className="px-4 py-2 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700 transition-colors text-sm disabled:bg-gray-400 flex items-center"
            >
              <FiDownload className="mr-2" />
              {isExporting ? 'Exportando...' : 'Exportar Excel'}
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={<FiUsers />} title="Usuarios Totales" value={summary.usuarios.total} color="blue" />
        <StatCard icon={<FiBriefcase />} title="Prestadores Totales" value={summary.prestadores.total} color="green" />
        <StatCard icon={<FiCheckSquare />} title="Artesanos Totales" value={summary.artesanos.total} color="purple" />
        <StatCard icon={<FiFileText />} title="Publicaciones Totales" value={summary.publicaciones.total} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ChartContainer title="Distribución de Usuarios por Rol">
          <PieChart>
            <Pie data={userRoleData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label>
              {userRoleData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ChartContainer>

        {stats.compliance_analysis && (
          <ChartContainer title="Análisis de Cumplimiento">
             <div className="text-center h-full flex flex-col justify-center">
                <p className="text-lg font-semibold">{stats.compliance_analysis.item_texto}</p>
                <p className="text-3xl font-bold text-green-500 mt-2">{stats.compliance_analysis.distribucion_actual.cumplen} Cumplen</p>
                <p className="text-3xl font-bold text-red-500 mt-1">{stats.compliance_analysis.distribucion_actual.no_cumplen} No Cumplen</p>
            </div>
          </ChartContainer>
        )}

      </div>
    </div>
  );
}