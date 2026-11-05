'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import {
  FiMapPin, FiLayers, FiActivity, FiShield, FiGlobe, FiServer, FiAlertTriangle, FiCheckCircle
} from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';

export default function NodosSoberanosPage() {
  const [isLoading] = useState(false);

  const nodes = [
    {
        id: 'node-col-01',
        name: 'Nodo Nacional Colombia',
        level: 'NACIONAL',
        status: 'ACTIVE',
        jurisdiction: 'Nacional',
        health: 98,
        activeAgentes: 124,
        regulatoryContext: 'Ley 1581 / EU AI Act'
    },
    {
        id: 'node-meta-01',
        name: 'Nodo Departamental Meta',
        level: 'DEPARTAMENTAL',
        status: 'ACTIVE',
        jurisdiction: 'Meta',
        health: 95,
        activeAgentes: 45,
        regulatoryContext: 'Ordenanza 012 / Nacional'
    },
    {
        id: 'node-pg-01',
        name: 'Nodo Municipal Puerto Gaitán',
        level: 'MUNICIPAL',
        status: 'ACTIVE',
        jurisdiction: 'Puerto Gaitán',
        health: 99,
        activeAgentes: 12,
        regulatoryContext: 'Decreto 045 / Departamental'
    },
    {
        id: 'node-vc-01',
        name: 'Nodo Municipal Villavicencio',
        level: 'MUNICIPAL',
        status: 'PAUSED',
        jurisdiction: 'Villavicencio',
        health: 82,
        activeAgentes: 0,
        regulatoryContext: 'Decreto 102 / Auditoría'
    }
  ];

  return (
    <ViewState isLoading={isLoading}>
      <div className="space-y-10 animate-in fade-in duration-700">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-gray-100 pb-8">
            <div>
                <div className="flex items-center gap-3 mb-2">
                    <div className="bg-slate-900 text-white p-2 rounded-lg">
                        <FiGlobe size={24} />
                    </div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tighter uppercase italic">Red de Nodos Soberanos</h1>
                </div>
                <p className="text-slate-500 text-lg font-medium italic">Escalamiento territorial y descentralización de la gobernanza Sarita.</p>
            </div>
            <Button className="bg-slate-900 text-white font-black px-8 py-6 rounded-2xl flex items-center gap-2 uppercase tracking-widest text-xs">
                <FiServer /> Registrar Nuevo Nodo
            </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card className="border-none shadow-sm bg-white p-6">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Nodos Activos</p>
                <h3 className="text-3xl font-black text-slate-900">24</h3>
            </Card>
            <Card className="border-none shadow-sm bg-white p-6">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Cobertura Nacional</p>
                <h3 className="text-3xl font-black text-indigo-600">85%</h3>
            </Card>
            <Card className="border-none shadow-sm bg-white p-6">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Salud Global de Red</p>
                <h3 className="text-3xl font-black text-emerald-600">Optima</h3>
            </Card>
            <Card className="border-none shadow-sm bg-white p-6">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Alertas Sistémicas</p>
                <h3 className="text-3xl font-black text-amber-600">2</h3>
            </Card>
        </div>

        <div className="grid grid-cols-1 gap-6">
            {nodes.map((node) => (
                <Card key={node.id} className="border-none shadow-sm hover:shadow-md transition-all overflow-hidden bg-white rounded-3xl group">
                    <div className="flex flex-col lg:flex-row items-stretch">
                        <div className={`w-2 lg:w-4 ${
                            node.level === 'NACIONAL' ? 'bg-indigo-600' :
                            node.level === 'DEPARTAMENTAL' ? 'bg-brand' : 'bg-slate-200'
                        }`} />
                        <div className="flex-1 p-8">
                            <div className="flex flex-col lg:flex-row justify-between gap-6">
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3">
                                        <Badge variant="outline" className="font-black text-[9px] tracking-widest uppercase">
                                            {node.level}
                                        </Badge>
                                        <h3 className="text-2xl font-black text-slate-900 uppercase italic tracking-tight">{node.name}</h3>
                                        <Badge className={node.status === 'ACTIVE' ? 'bg-emerald-500' : 'bg-amber-500'}>
                                            {node.status}
                                        </Badge>
                                    </div>
                                    <div className="flex flex-wrap gap-6 text-sm text-slate-500 font-medium">
                                        <span className="flex items-center gap-2"><FiMapPin className="text-indigo-500" /> {node.jurisdiction}</span>
                                        <span className="flex items-center gap-2"><FiShield className="text-emerald-500" /> Contexto: {node.regulatoryContext}</span>
                                        <span className="flex items-center gap-2"><FiLayers className="text-slate-400" /> {node.activeAgentes} Agentes Activos</span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-8 border-l border-slate-100 pl-8">
                                    <div className="text-center">
                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Salud</p>
                                        <p className={`text-2xl font-black ${node.health > 90 ? 'text-emerald-500' : 'text-amber-500'}`}>
                                            {node.health}%
                                        </p>
                                    </div>
                                    <div className="flex flex-col gap-2">
                                        <Button variant="outline" size="sm" className="rounded-xl font-bold text-xs">Administrar Nodo</Button>
                                        <Button variant="ghost" size="sm" className="rounded-xl font-bold text-xs text-slate-400">Ver Logs</Button>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-8 pt-8 border-t border-slate-50 grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="bg-slate-50 p-4 rounded-2xl flex items-center gap-4">
                                    <FiActivity className="text-indigo-600" size={24} />
                                    <div>
                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Gobernanza</p>
                                        <p className="text-xs font-bold text-slate-700">KERNEL SINCRONIZADO</p>
                                    </div>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-2xl flex items-center gap-4">
                                    <FiShield className="text-emerald-600" size={24} />
                                    <div>
                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Seguridad</p>
                                        <p className="text-xs font-bold text-slate-700">AES-256 + SHA-256 ACTIVE</p>
                                    </div>
                                </div>
                                <div className="bg-slate-50 p-4 rounded-2xl flex items-center gap-4">
                                    <FiCheckCircle className="text-indigo-400" size={24} />
                                    <div>
                                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Resiliencia</p>
                                        <p className="text-xs font-bold text-slate-700">MODO DEGRADADO OK</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </Card>
            ))}
        </div>
      </div>
    </ViewState>
  );
}
