import React from 'react';
import { FiActivity, FiShield, FiCpu, FiClock, FiCheckCircle, FiXCircle, FiTrendingUp } from 'react-icons/fi';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Decision {
  id: string;
  origin_metric: string;
  metric_value: string;
  evaluated_risk: number;
  suggested_action: {
    intention: string;
    parameters: any;
  };
  governance_status: string;
  agent_id: string;
  created_at: string;
  integrity_hash: string;
}

export default function AIDecisionAuditPage() {
  const [decisions, setDecisions] = React.useState<Decision[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/enterprise-core/proposals/`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
      .then(res => res.json())
      .then(data => {
        setDecisions(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="p-8 bg-slate-950 min-h-screen text-slate-200">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-white uppercase flex items-center gap-4">
              <FiShield className="text-indigo-500" />
              Auditoría de Decisiones IA
            </h1>
            <p className="text-slate-500 mt-2 font-medium">Registro inmutable de la capa de inteligencia autónoma SADI/EOS</p>
          </div>
          <div className="bg-slate-900/50 p-4 rounded-2xl border border-white/5 flex gap-8">
            <div className="text-center">
              <p className="text-[10px] font-black text-slate-500 uppercase">Total Decisiones</p>
              <p className="text-2xl font-bold text-indigo-400">{decisions.length}</p>
            </div>
            <div className="text-center">
              <p className="text-[10px] font-black text-slate-500 uppercase">Riesgo Promedio</p>
              <p className="text-2xl font-bold text-emerald-400">
                {(decisions.reduce((acc, d) => acc + d.evaluated_risk, 0) / (decisions.length || 1)).toFixed(2)}
              </p>
            </div>
          </div>
        </header>

        {loading ? (
          <div className="flex justify-center p-20">
            <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid gap-6">
            {decisions.length === 0 ? (
              <div className="bg-slate-900 border border-dashed border-white/10 rounded-3xl p-20 text-center">
                <FiCpu className="mx-auto text-slate-700 mb-4" size={48} />
                <p className="text-slate-500 font-medium">No hay decisiones registradas en el periodo actual.</p>
              </div>
            ) : (
              decisions.map(d => (
                <div key={d.id} className="bg-slate-900/50 border border-white/5 rounded-[2rem] p-8 hover:bg-slate-900 transition-all group">
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-indigo-500/10 rounded-2xl flex items-center justify-center text-indigo-400">
                        <FiCpu size={24} />
                      </div>
                      <div>
                        <h3 className="font-bold text-xl text-white tracking-tight">{d.suggested_action.intention}</h3>
                        <p className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                          <FiActivity size={12} />
                          Disparado por: {d.origin_metric} ({d.metric_value})
                        </p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                        d.governance_status === 'EXECUTED' ? 'bg-emerald-500/10 text-emerald-500' :
                        d.governance_status === 'PENDING' ? 'bg-amber-500/10 text-amber-500' : 'bg-red-500/10 text-red-500'
                      }`}>
                        {d.governance_status}
                      </span>
                      <p className="text-[10px] text-slate-600 font-mono mt-2">{d.id}</p>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-3 gap-8 mb-8">
                    <div className="bg-slate-950 p-6 rounded-2xl border border-white/5">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Evaluación de Riesgo</p>
                      <div className="flex items-center gap-4">
                        <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-emerald-500 to-red-500"
                            style={{ width: `${d.evaluated_risk * 100}%` }}
                          />
                        </div>
                        <span className="font-bold text-white">{d.evaluated_risk.toFixed(2)}</span>
                      </div>
                    </div>

                    <div className="bg-slate-950 p-6 rounded-2xl border border-white/5">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Agente Originador</p>
                      <p className="font-bold text-indigo-400 flex items-center gap-2">
                        <FiZap size={14} />
                        {d.agent_id}
                      </p>
                    </div>

                    <div className="bg-slate-950 p-6 rounded-2xl border border-white/5">
                      <p className="text-[10px] font-black text-slate-500 uppercase mb-2">Timestamp</p>
                      <p className="font-bold text-slate-300 flex items-center gap-2">
                        <FiClock size={14} />
                        {new Date(d.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="border-t border-white/5 pt-6 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <FiShield className="text-emerald-500/50" size={14} />
                      <span className="text-[10px] font-mono text-slate-600">Integrity Hash: {d.integrity_hash?.substring(0, 32)}...</span>
                    </div>
                    <button className="text-indigo-400 text-xs font-black uppercase tracking-widest hover:text-white transition-colors">
                      Ver Detalles de Ejecución →
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function FiZap({ size, className }: { size?: number, className?: string }) {
  return (
    <svg
      stroke="currentColor"
      fill="none"
      strokeWidth="2"
      viewBox="0 0 24 24"
      strokeLinecap="round"
      strokeLinejoin="round"
      height={size}
      width={size}
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
    </svg>
  );
}
