'use client';
import React,{useEffect,useRef,useState} from 'react';
import type {useErpSession,SecurityEvent} from './useErpSession';
const labels={password_reset:'Contraseña restablecida',recovery_issued:'Códigos de recuperación emitidos',recovery_rotated:'Códigos de recuperación regenerados',recovery_used:'Acceso con código de recuperación'};
export function SecurityHistory({session}:{session:ReturnType<typeof useErpSession>}){
 const [events,setEvents]=useState<SecurityEvent[]>([]);const [error,setError]=useState('');const [loaded,setLoaded]=useState(false);const [busy,setBusy]=useState(false);
 const actor=useRef(session.user?.id);actor.current=session.user?.id;
 useEffect(()=>{setEvents([]);setLoaded(false);setError('');setBusy(false);},[session.user?.id]);
 if(!session.user)return null;
 return <section aria-label="Historial de recuperación"><h2>Historial de recuperación</h2>
  <p>Últimos 20 eventos de recuperación y restablecimiento de contraseña. Este historial no incluye todavía todos los accesos ni los intentos fallidos.</p>
  <button type="button" disabled={busy||session.loading} onClick={async()=>{const current=actor.current;setBusy(true);setError('');try{const rows=await session.securityEvents();if(actor.current===current){setEvents(rows);setLoaded(true);}}catch{if(actor.current===current){setEvents([]);setLoaded(false);setError('No se pudo consultar el historial. Reintenta.');}}finally{if(actor.current===current)setBusy(false);}}}>Consultar mi historial</button>
  {error&&<p role="alert">{error}</p>}
  {loaded&&!events.length&&<p>No hay eventos de recuperación registrados.</p>}
  {events.length>0&&<ul>{events.map(event=><li key={event.id}>{labels[event.kind]} · <time dateTime={event.occurred_at}>{new Date(event.occurred_at).toLocaleString('es-CO',{timeZone:'America/Bogota'})}</time></li>)}</ul>}
 </section>;
}
