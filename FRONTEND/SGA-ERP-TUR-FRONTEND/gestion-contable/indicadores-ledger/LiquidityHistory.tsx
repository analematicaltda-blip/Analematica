'use client';
import React,{useEffect,useRef,useState} from 'react';
type Revision={id:string;revision:number;reviewer_id:number;created_at:string;evidence_digest:string;digest:string;mapping:Record<string,string[]>};
export function LiquidityHistory({identity,providerId,request,revisionSignal}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>;revisionSignal:number}){
 const [before,setBefore]=useState<number|null>(null);const [reload,setReload]=useState(0);
 const [data,setData]=useState<{key:string;results:Revision[];next_before:number|null}|null>(null);const [error,setError]=useState('');const [busy,setBusy]=useState(false);
 const requester=useRef(request);requester.current=request;
 const key=JSON.stringify([identity,providerId,before,reload,revisionSignal]);
 useEffect(()=>{setBefore(null);},[identity,providerId,revisionSignal]);
 useEffect(()=>{
  const controller=new AbortController();setData(null);setError('');setBusy(false);
  if(!identity||!providerId)return ()=>controller.abort();
  setBusy(true);const query=new URLSearchParams({provider_id:providerId,limite:'20'});if(before!==null)query.set('antes_revision',String(before));
  requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/historial-liquidez/?'+query,{signal:controller.signal}).then(async r=>{
   const raw=await r.json();if(!r.ok)throw Error('No se pudo verificar el historial. Revisa permisos, conexión o integridad.');
   const body=raw?.success===true?raw.data:raw;
   if(!body||body.read_only!==true||!Array.isArray(body.results)||!(body.next_before===null||Number.isInteger(body.next_before)&&body.next_before>0)||!body.results.every((row:Revision)=>row&&typeof row.id==='string'&&Number.isInteger(row.revision)&&row.revision>0&&Number.isInteger(row.reviewer_id)&&typeof row.created_at==='string'&&typeof row.evidence_digest==='string'&&typeof row.digest==='string'&&row.mapping&&Object.values(row.mapping).every(ids=>Array.isArray(ids)&&ids.every(id=>typeof id==='string'))))throw Error('Historial incompleto; no se muestran registros sin validar.');
   if(!controller.signal.aborted)setData({key,results:body.results,next_before:body.next_before});
  }).catch(e=>{if(!controller.signal.aborted)setError(e instanceof Error?e.message:'Historial no disponible.');}).finally(()=>{if(!controller.signal.aborted)setBusy(false);});
  return ()=>controller.abort();
 },[key]);
 const visible=data?.key===key?data:null;
 if(!identity||!providerId)return null;
 return <section aria-label="Historial de liquidez" style={{background:'#0E1B38',color:'#FFFFFF',padding:20,border:'1px solid #60A5FA',borderRadius:12,marginTop:20,overflowWrap:'anywhere'}}>
  <h2>Historial de clasificación de liquidez</h2><p>Solo lectura. El digest local permite comprobar consistencia; no es una firma independiente ni una certificación contable.</p>
  {busy&&<p role="status">Consultando historial…</p>}{error&&<p role="alert">{error}</p>}
  {visible&&visible.results.length===0&&<p>No hay revisiones en esta página.</p>}
  {visible?.results.map(row=><details key={row.id}><summary>Revisión histórica {row.revision} · {row.created_at}</summary><p>Identificador del revisor: {row.reviewer_id}</p><p>Evidencia declarada SHA-256: {row.evidence_digest}</p><p>Digest del registro: {row.digest}</p><ul>{Object.entries(row.mapping).map(([role,ids])=><li key={role}>{role}: {ids.join(', ')||'Sin cuentas'}</li>)}</ul></details>)}
  <p><button type="button" disabled={busy} onClick={()=>{setBefore(null);setReload(n=>n+1);}}>Ver revisiones recientes</button> <button type="button" disabled={busy||!visible?.next_before} onClick={()=>setBefore(visible?.next_before??null)}>Ver revisiones anteriores</button></p>
  <style>{`[aria-label="Historial de liquidez"] button{background:#142850;color:#fff;border:1px solid #60a5fa;padding:10px;border-radius:6px}[aria-label="Historial de liquidez"] :focus-visible{outline:3px solid #7dd3fc;outline-offset:2px}`}</style>
 </section>;
}
