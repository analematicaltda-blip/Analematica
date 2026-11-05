'use client';

import React, { useState } from 'react';
import { useMiNegocioApi } from '../../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FiRefreshCw, FiCheckCircle, FiAlertCircle, FiShield } from 'react-icons/fi';
import { useAuth } from '@/contexts/AuthContext';

export default function ConciliacionWalletPage() {
  const { user } = useAuth();
  const { getConciliacionWallet, isLoading } = useMiNegocioApi();
  const [result, setResult] = useState<any>(null);

  const handleConciliate = async () => {
    // Necesitamos el provider_id. Lo obtenemos del perfil del usuario si está disponible.
    const providerId = (user as any)?.perfil_prestador?.id;
    if (!providerId) {
      alert("No se pudo identificar el ID del prestador.");
      return;
    }
    const res = await getConciliacionWallet(providerId);
    if (res && res.details) {
      // El resultado viene del SaritaOrchestrator consolidado
      const details = res.details.find((d: any) => d.soldier === 'SoldadoConciliacionWallet');
      setResult(details?.result);
    }
  };

  return (
    <div className="space-y-8 py-8 max-w-3xl mx-auto">
      <div className="text-center space-y-2">
        <div className="w-16 h-16 bg-brand/10 text-brand rounded-full flex items-center justify-center mx-auto mb-4 shadow-inner">
           <FiShield size={32} />
        </div>
        <h1 className="text-4xl font-black text-slate-900 tracking-tight">Conciliación Wallet Soberano</h1>
        <p className="text-slate-500 max-w-md mx-auto">Verifica la integridad de tus saldos digitales contra los registros contables locales.</p>
      </div>

      <div className="flex justify-center">
         <Button
            onClick={handleConciliate}
            disabled={isLoading}
            className="bg-brand hover:bg-brand-light text-white font-black px-12 py-8 rounded-2xl shadow-2xl shadow-brand/30 transition-all hover:scale-105 active:scale-95"
         >
            {isLoading ? <FiRefreshCw className="mr-2 animate-spin" /> : <FiRefreshCw className="mr-2" />}
            Iniciar Verificación de Integridad
         </Button>
      </div>

      {result && (
         <div className="animate-in zoom-in-95 duration-500">
            <Card className={`border-none shadow-2xl ${result.status === 'OK' ? 'bg-green-50' : 'bg-red-50'}`}>
               <CardHeader className="flex flex-row items-center gap-4 p-8">
                  {result.status === 'OK' ? (
                     <FiCheckCircle size={48} className="text-green-500" />
                  ) : (
                     <FiAlertCircle size={48} className="text-red-500" />
                  )}
                  <div>
                     <CardTitle className={`text-2xl font-black ${result.status === 'OK' ? 'text-green-800' : 'text-red-800'}`}>
                        {result.status === 'OK' ? 'Saldos Sincronizados' : 'Discrepancia Detectada'}
                     </CardTitle>
                     <p className={`text-sm font-medium ${result.status === 'OK' ? 'text-green-600' : 'text-red-600'}`}>
                        {result.status === 'OK' ? 'La contabilidad coincide perfectamente con el Wallet.' : 'Se requiere ajuste contable o auditoría de transacciones.'}
                     </p>
                  </div>
               </CardHeader>
               <CardContent className="p-8 pt-0 grid grid-cols-2 gap-8 border-t border-black/5 mt-4">
                  <div className="space-y-1">
                     <p className="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Saldo en Wallet</p>
                     <p className="text-3xl font-mono font-black text-slate-900">${parseFloat(result.wallet_balance).toLocaleString()}</p>
                  </div>
                  <div className="space-y-1">
                     <p className="text-[10px] font-black uppercase text-slate-400 tracking-[0.2em]">Saldo en Libros</p>
                     <p className="text-3xl font-mono font-black text-slate-900">${parseFloat(result.contable_balance).toLocaleString()}</p>
                  </div>
                  <div className="col-span-2 pt-6 flex justify-between items-center border-t border-black/5">
                     <p className="text-sm font-bold text-slate-500 uppercase tracking-widest">Diferencia Neta</p>
                     <p className={`text-2xl font-mono font-black ${result.difference === 0 ? 'text-slate-400' : 'text-red-500'}`}>
                        ${parseFloat(result.difference).toLocaleString()}
                     </p>
                  </div>
               </CardContent>
            </Card>
         </div>
      )}
    </div>
  );
}
