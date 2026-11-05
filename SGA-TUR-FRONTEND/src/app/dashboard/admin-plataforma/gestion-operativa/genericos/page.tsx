'use client';

import React, { useEffect, useState } from 'react';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { FiMonitor, FiUser, FiCalendar, FiClock, FiShield } from 'react-icons/fi';
import { ViewState } from '@/components/ui/ViewState';

export default function GlobalSocialMonitoringPage() {
  const [rooms, setRooms] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      const { data } = await api.get('/admin/plataforma/system-audit/social/active-rooms/');
      setRooms(data);
    } catch (e) {
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
           <div className="flex items-center gap-2 text-brand font-bold mb-2 uppercase tracking-widest text-xs">
              <FiMonitor /> Centro de Control Social Vía 3
           </div>
           <h1 className="text-5xl font-black text-slate-900 tracking-tighter uppercase italic">Monitoreo de Video Citas</h1>
           <p className="text-slate-500 font-medium mt-1">Supervisión en tiempo real de salas de encuentro y streaming social.</p>
        </div>
      </div>

      <ViewState isLoading={isLoading}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {rooms.map((room) => (
                <Card key={room.id} className="border-none shadow-sm bg-white rounded-[2.5rem] overflow-hidden group hover:shadow-xl transition-all">
                    <div className="p-8 space-y-6">
                        <div className="flex justify-between items-start">
                            <div className="space-y-1">
                                <Badge className={`text-[9px] font-black uppercase tracking-widest ${room.type === 'private_room' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'}`}>
                                    {room.type.replace('_', ' ')}
                                </Badge>
                                <h4 className="text-xl font-black text-slate-900 truncate max-w-[200px]">{room.title}</h4>
                            </div>
                            {room.adult_only && (
                                <div className="w-8 h-8 bg-red-50 text-red-600 rounded-full flex items-center justify-center font-black text-xs border border-red-100">18+</div>
                            )}
                        </div>

                        <div className="grid grid-cols-2 gap-4 border-y border-slate-50 py-6">
                            <div>
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Participantes</p>
                                <div className="flex items-center gap-2 font-bold text-slate-700">
                                    <FiUser /> {room.members_count}
                                </div>
                            </div>
                            <div>
                                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Tarifa Entrada</p>
                                <div className="flex items-center gap-2 font-bold text-emerald-600">
                                    ${room.entry_fee}
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-between items-center text-[10px] font-medium text-slate-400">
                            <div className="flex items-center gap-1">
                                <FiClock /> Creada {new Date(room.created_at).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1 text-emerald-500 font-bold uppercase">
                                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping" /> EN VIVO
                            </div>
                        </div>
                    </div>
                    <button className="w-full bg-slate-900 text-white py-4 font-black uppercase tracking-widest text-[10px] group-hover:bg-brand transition-colors flex items-center justify-center gap-2">
                        <FiShield /> Auditar Sala
                    </button>
                </Card>
            ))}

            {rooms.length === 0 && (
                <div className="col-span-full py-32 text-center bg-slate-50 rounded-[3rem] border-2 border-dashed border-slate-200">
                    <FiMonitor className="mx-auto text-slate-200 mb-6" size={48} />
                    <p className="font-black text-slate-400 uppercase tracking-widest">No hay video salas activas en este momento</p>
                </div>
            )}
        </div>
      </ViewState>
    </div>
  );
}
