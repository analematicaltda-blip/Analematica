import React from 'react';
import { WebLayout, KpiCard, LineChart, DataTable } from '@sarita/shared-ui';

export default function SystemGovernancePage() {
  const systemKPIs = [
    { title: 'Nodos de Red', value: '3/3', trend: 'Estable' },
    { title: 'Tasa de Integridad', value: '100%', trend: 'Verificado' },
    { title: 'Misiones IA Activas', value: '42', trend: '+12%' },
    { title: 'Alertas Globales', value: '0', trend: 'Nominal' }
  ];

  return (
    <WebLayout>
      <div className="mb-12">
        <h1 className="text-4xl font-extrabold text-slate-900 mb-2">Torre de Control del Sistema</h1>
        <p className="text-slate-500 text-lg">Gobernanza Institucional y Supervisión Operativa SARITA v1.0</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        {systemKPIs.map((kpi, i) => <KpiCard key={i} {...kpi} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
          <h2 className="text-2xl font-bold mb-6">Actividad Transaccional Regional</h2>
          <LineChart data={[{name: '00:00', v: 100}, {name: '06:00', v: 450}, {name: '12:00', v: 890}]} dataKey="v" />
        </div>
        <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
          <h2 className="text-2xl font-bold mb-6">Estado de Servicios Críticos</h2>
          <DataTable
            columns={[
              {header: 'Servicio', accessor: 'name'},
              {header: 'Salud', accessor: 'health'},
              {header: 'Latencia', accessor: 'lat'}
            ]}
            data={[
              {name: 'Core API', health: 'Online', lat: '45ms'},
              {name: 'Wallet Engine', health: 'Online', lat: '12ms'},
              {name: 'IA Orchestrator', health: 'Processing', lat: '340ms'}
            ]}
          />
        </div>
      </div>
    </WebLayout>
  );
}
