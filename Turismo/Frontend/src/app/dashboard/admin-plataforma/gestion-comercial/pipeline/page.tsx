"use client";

import React, { useState, useEffect } from 'react';
import {
  Users,
  ArrowRight,
  TrendingUp,
  DollarSign,
  CheckCircle2,
  XCircle,
  MoreVertical,
  Plus
} from 'lucide-react';

interface Lead {
  id: string;
  company_name: string;
  contact_email: string;
  status: string;
  score: number;
  industry: string;
  estimated_size: number;
  created_at: string;
}

const STAGES = [
  { id: 'NEW', name: 'Nuevos', color: 'bg-blue-50' },
  { id: 'CONTACTED', name: 'Contactados', color: 'bg-indigo-50' },
  { id: 'QUALIFIED', name: 'Calificados', color: 'bg-purple-50' },
  { id: 'PROPOSAL_SENT', name: 'Propuesta', color: 'bg-yellow-50' },
  { id: 'NEGOTIATION', name: 'Negociación', color: 'bg-orange-50' },
  { id: 'CONVERTED', name: 'Convertidos', color: 'bg-green-50' },
  { id: 'LOST', name: 'Perdidos', color: 'bg-red-50' },
];

export default function PipelinePage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await fetch('/api/commercial-engine/leads/');
      const data = await response.json();
      setLeads(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching leads:', error);
      setLoading(false);
    }
  };

  const handleMove = async (leadId: string, newStatus: string) => {
    try {
      await fetch(`/api/commercial-engine/leads/${leadId}/transition/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      fetchLeads();
    } catch (error) {
      console.error('Error transitioning lead:', error);
    }
  };

  if (loading) return <div className="p-8 text-center">Cargando Pipeline...</div>;

  return (
    <div className="flex flex-col h-full bg-gray-50 min-h-screen">
      <header className="bg-white border-b p-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <TrendingUp className="text-blue-600" />
            Pipeline Comercial SaaS
          </h1>
          <p className="text-gray-500">Gestión autónoma de leads y conversiones</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition">
          <Plus size={20} />
          Nuevo Lead
        </button>
      </header>

      <main className="p-6 overflow-x-auto flex-1">
        <div className="flex gap-4 min-w-max h-full">
          {STAGES.map(stage => (
            <div key={stage.id} className={`w-80 rounded-xl ${stage.color} flex flex-col border shadow-sm`}>
              <div className="p-4 border-b flex justify-between items-center">
                <h2 className="font-semibold text-gray-700 flex items-center gap-2">
                  {stage.name}
                  <span className="bg-white px-2 py-0.5 rounded-full text-xs border text-gray-400">
                    {leads.filter(l => l.status === stage.id).length}
                  </span>
                </h2>
                <MoreVertical size={16} className="text-gray-400 cursor-pointer" />
              </div>

              <div className="p-3 flex-1 space-y-3 overflow-y-auto max-h-[calc(100vh-250px)]">
                {leads.filter(l => l.status === stage.id).map(lead => (
                  <div key={lead.id} className="bg-white p-4 rounded-lg shadow-sm border hover:border-blue-400 transition cursor-pointer group relative">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium text-gray-800">{lead.company_name}</h3>
                      <div className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${lead.score > 50 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                        {lead.score} pts
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mb-4">{lead.contact_email}</p>

                    <div className="flex justify-between items-center text-[10px] text-gray-400">
                      <span className="flex items-center gap-1">
                        <Users size={12} />
                        {lead.estimated_size} emp.
                      </span>
                      <span>{new Date(lead.created_at).toLocaleDateString()}</span>
                    </div>

                    {/* Quick Move Tools */}
                    <div className="hidden group-hover:flex absolute right-2 bottom-12 bg-white border rounded shadow-lg p-1 z-10 gap-1">
                      {STAGES.filter(s => s.id !== stage.id).slice(0, 3).map(s => (
                        <button
                          key={s.id}
                          onClick={() => handleMove(lead.id, s.id)}
                          className="p-1 hover:bg-blue-50 text-blue-600 rounded transition"
                          title={`Mover a ${s.name}`}
                        >
                          <ArrowRight size={14} />
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
