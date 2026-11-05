'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { KPICard } from '@/ui/components/data/KPICard';
import { DataTable } from '@/ui/components/data/DataTable';
import { FiPlay, FiCheckCircle, FiFileText, FiUsers, FiSettings, FiGlobe } from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import { useSADI } from '@/hooks/useSADI';

export default function SimulationPage() {
  const [step, setStep] = useState(0);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (msg: string) => setLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev]);

  const { state, responseMessage, sendTextIntent } = useSADI();

  const runStep = async (stepId: number) => {
    switch(stepId) {
      case 1:
        addLog("Iniciando creación de Empresa...");
        await new Promise(r => setTimeout(r, 1000));
        addLog("✅ Empresa 'Sarita Tour Operador' creada con éxito.");
        await sendTextIntent("Crear perfil para operador turístico integral");
        setStep(1);
        break;
      case 2:
        addLog("Contratando empleados y configurando nómina...");
        await new Promise(r => setTimeout(r, 1000));
        addLog("✅ 5 Empleados registrados. Planilla de seguridad social activa.");
        await sendTextIntent("Registrar nómina de marzo");
        setStep(2);
        break;
      case 3:
        addLog("Definiendo catálogo de servicios...");
        await new Promise(r => setTimeout(r, 1000));
        addLog("✅ Paquete 'Aventura Meta' y 'Ruta del Sol' publicados.");
        setStep(3);
        break;
      case 4:
        addLog("Ejecutando campañas de marketing y ventas...");
        await new Promise(r => setTimeout(r, 1000));
        addLog("✅ Venta realizada. Factura #FE-1001 emitida. Inversión: $200. Ingreso: $680.");
        await sendTextIntent("Generar reporte de ventas del día");
        setStep(4);
        break;
      case 5:
        addLog("Cerrando periodo contable y calculando métricas...");
        await new Promise(r => setTimeout(r, 1500));
        addLog("✅ Periodo Q1-2025 cerrado. CAC: $40. LTV Proyectado: $1,200.");
        setStep(5);
        break;
      case 6:
        addLog("Generando estados financieros e inteligencia analítica...");
        await new Promise(r => setTimeout(r, 1000));
        addLog("📈 ROI: 3.4x. Relación LTV/CAC: 30.0 (Escalabilidad Crítica).");
        toast.success("Simulación Analítica Completada");
        setStep(6);
        break;
    }
  };

  return (
    <div className="p-8 space-y-10 bg-[var(--background-main)] min-h-screen text-[var(--text-primary)]">
      <div className="flex justify-between items-center border-b border-[var(--border-default)] pb-8">
        <div>
          <h1 className="text-4xl font-black tracking-tighter uppercase italic">Simulación ERP End-to-End</h1>
          <p className="text-[var(--text-muted)] text-lg">Verificación de flujo de datos transversal (Comercial -{'>'} Operativo -{'>'} Contable).</p>
        </div>
        <Button onClick={() => { setStep(0); setLogs([]); }} variant="outline">Reiniciar Escenario</Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        {/* Step List */}
        <div className="lg:col-span-1 space-y-4">
           {[
             { id: 1, label: 'Crear Entidad Legal', icon: FiSettings },
             { id: 2, label: 'Gestión de Talento (Nómina)', icon: FiUsers },
             { id: 3, label: 'Publicar Inventario Operativo', icon: FiGlobe },
             { id: 4, label: 'Venta y Facturación Automática', icon: FiFileText },
             { id: 5, label: 'Cierre de Ciclo Contable', icon: FiCheckCircle },
             { id: 6, label: 'Dashboard de Resultados', icon: FiPlay },
           ].map((s) => (
             <div
               key={s.id}
               className={`p-6 rounded-2xl border transition-all flex items-center gap-4 ${
                 step >= s.id ? 'bg-[var(--status-success)]/10 border-[var(--status-success)]/30 text-[var(--status-success)]' :
                 step === s.id - 1 ? 'bg-[var(--background-card)] border-[var(--brand-primary)] animate-pulse' :
                 'bg-[var(--background-card)] border-[var(--border-default)] opacity-50'
               }`}
             >
               <s.icon size={20} />
               <span className="font-bold">{s.label}</span>
               {step === s.id - 1 && (
                 <Button size="sm" className="ml-auto" onClick={() => runStep(s.id)}>Ejecutar</Button>
               )}
             </div>
           ))}
        </div>

        {/* Live Logs & Results */}
        <div className="lg:col-span-2 space-y-8">
           <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <KPICard label="Estado Simulación" value={step === 6 ? "COMPLETADO" : `PASO ${step}/6`} icon={FiActivity} className="md:col-span-2" />
              <KPICard label="ROI Proyectado" value={step >= 6 ? "3.4x" : "--"} trend={{ value: 'Real', type: 'up' }} icon={FiZap} />
              <KPICard label="LTV / CAC" value={step >= 6 ? "30.0" : "--"} statusColor="emerald-500" icon={FiTrendingUp} />
           </div>

           <div className="bg-black text-green-400 p-8 rounded-[2rem] font-mono text-sm h-96 overflow-y-auto custom-scrollbar border border-green-900/30">
              <p className="mb-4 text-gray-500">// SARITA System Simulation Kernel v4.0</p>
              {logs.map((log, i) => (
                <p key={i} className="mb-1 leading-relaxed">{log}</p>
              ))}
              {logs.length === 0 && <p className="animate-pulse">Esperando instrucción de arranque...</p>}
           </div>
        </div>
      </div>
    </div>
  );
}

import { FiShield, FiActivity } from 'react-icons/fi';
