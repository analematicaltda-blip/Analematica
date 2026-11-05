'use client';

import React from 'react';
import {
  Truck,
  Package,
  MapPin,
  Users,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Clock
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function DeliveryDashboard() {
  const stats = [
    { title: 'Pedidos Hoy', value: '124', icon: Package, color: 'text-blue-600' },
    { title: 'En Ruta', value: '18', icon: Truck, color: 'text-orange-600' },
    { title: 'Entregados', value: '98', icon: CheckCircle, color: 'text-green-600' },
    { title: 'Incidencias', value: '3', icon: AlertTriangle, color: 'text-red-600' },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Gobierno Logístico de Delivery</h1>
        <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-semibold">
          Fase 9: Operación Activa
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow border-t-4 border-t-blue-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium text-gray-500">{stat.title}</CardTitle>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-gray-400">+12% respecto a ayer</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-l-4 border-l-blue-600 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              Estado de la Operación
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { label: 'Tiempo Promedio de Entrega', value: '28 min', trend: 'down' },
                { label: 'Ocupación de Flota', value: '82%', trend: 'up' },
                { label: 'Costo Logístico / Pedido', value: '$4.200', trend: 'stable' },
              ].map((item, i) => (
                <div key={i} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <span className="text-sm font-medium text-gray-600">{item.label}</span>
                  <span className="text-lg font-bold text-gray-900">{item.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-orange-500" />
              Rendimiento por Zona
            </CardTitle>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div className="bg-blue-600 h-4 rounded-full" style={{ width: '85%' }}></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Zona Norte (85%)</span>
                  <span>92 pedidos</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div className="bg-orange-500 h-4 rounded-full" style={{ width: '65%' }}></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Zona Sur (65%)</span>
                  <span>45 pedidos</span>
                </div>
             </div>
          </CardContent>
        </Card>
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-red-500" />
          Monitoreo de Últimas Entregas
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
              <tr>
                <th className="p-3">ID Pedido</th>
                <th className="p-3">Repartidor</th>
                <th className="p-3">Destino</th>
                <th className="p-3">Estado</th>
                <th className="p-3">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              <tr>
                <td className="p-3 font-medium">#DLV-8821</td>
                <td className="p-3">Carlos Ruiz</td>
                <td className="p-3 text-gray-500 text-xs">Calle 10 #45-12</td>
                <td className="p-3">
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">EN RUTA</span>
                </td>
                <td className="p-3">
                  <button className="text-blue-600 hover:underline">Ver Mapa</button>
                </td>
              </tr>
              <tr>
                <td className="p-3 font-medium">#DLV-8820</td>
                <td className="p-3">Maria Lopez</td>
                <td className="p-3 text-gray-500 text-xs">Cra 5 #2-88</td>
                <td className="p-3">
                  <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">ENTREGADO</span>
                </td>
                <td className="p-3">
                  <button className="text-blue-600 hover:underline">Ver Evidencia</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
