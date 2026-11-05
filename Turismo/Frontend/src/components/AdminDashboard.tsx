"use client";
import React from 'react';
import StatisticsDashboard from './StatisticsDashboard';
import { FiBarChart2 } from 'react-icons/fi';

/**
 * Componente principal del panel de administración.
 * Con la nueva navegación en el Sidebar, este componente ahora actúa como
 * la página de inicio o "home" del dashboard, mostrando un resumen
 * o las estadísticas principales.
 */
export default function AdminDashboard() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 font-sans">
      <div className="flex flex-wrap items-center justify-between mb-8 gap-4">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <FiBarChart2 className="mr-3" />
          Dashboard Principal
        </h1>
      </div>
      <div className="bg-white p-4 sm:p-6 rounded-2xl shadow-lg">
        {/* El contenido por defecto del dashboard ahora son las estadísticas */}
        <StatisticsDashboard />
      </div>
    </div>
  );
}