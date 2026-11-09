'use client';
import React,{useEffect,useRef,useState} from 'react';
type Requester=(path:string,init?:RequestInit)=>Promise<Response>;
const API='/api/v1/mi-negocio/contable/contabilidad/cuentas/';
const roles={cash_equivalents:'Efectivo y equivalentes',temporary_investments:'Inversiones temporales',immediate_receivables:'Cuentas por cobrar inmediatas',current_liabilities:'Pasivos corrientes'};
type Role=keyof typeof roles;type Mapping=Record<Role,string[]>;
type Account={id:string;code:string;name:string;type:string;is_active:boolean};
const empty=():Mapping=>({cash_equivalents:[],temporary_investments:[],immediate_receivables:[],current_liabilities:[]});
async function read(response:Response){
 const raw=await response.json().catch(()=>undefined);
 if(!response.ok)throw Error(response.status===403?'No tienes acceso a esta empresa.':'Operación no confirmada. Recarga la clasificación antes de revisarla nuevamente.');
 if(raw===undefined)throw Error('Respuesta incompleta; recarga antes de continuar.');
 return raw?.success===true?raw.data:raw;
}
export function LiquidityReview({providerId,identity,request,onSaved}:{providerId:string;identity:string|null;request:Requester;onSaved:()=>void}){
 const context=JSON.stringify([identity,providerId]);const current=useRef(context);current.current=context;
 const requester=useRef(request);requester.current=request;
 const [loaded,setLoaded]=useState('');const [accounts,setAccounts]=useState<Account[]>([]);const [mapping,setMapping]=useState<Mapping>(empty);
 const [revision,setRevision]=useState(0);const [evidence,setEvidence]=useState('');const [reviewed,setReviewed]=useState(false);const [confirmed,setConfirmed]=useState(false);
 const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [message,setMessage]=useState('');const [reload,setReload]=useState(0);const [uncertain,setUncertain]=useState(false);
 useEffect(()=>{
  const controller=new AbortController();setLoaded('');setAccounts([]);setMapping(empty());setEvidence('');setReviewed(false);setConfirmed(false);setError('');setMessage('');setUncertain(false);setBusy(false);
  if(!identity||!providerId)return ()=>controller.abort();
  setBusy(true);
  (async()=>{
   const policy=await read(await requester.current(API+'clasificacion-liquidez/?'+new URLSearchParams({provider_id:providerId}),{signal:controller.signal}));
   const all:Account[]=[];let next:string|null=API+'?'+new URLSearchParams({provider_id:providerId,page_size:'100'});let pages=0;
   while(next){
    if(++pages>20)throw Error('El catálogo supera el límite de revisión. Solicita un catálogo acotado antes de continuar.');
    const response=await requester.current(next,{signal:controller.signal});const raw=await response.clone().json().catch(()=>null);const body=await read(response);
    const rows=Array.isArray(body)?body:body?.results;
    if(!Array.isArray(rows)||!rows.every(a=>a&&typeof a.id==='string'&&typeof a.code==='string'&&typeof a.name==='string'&&typeof a.type==='string'&&typeof a.is_active==='boolean'))throw Error('Catálogo contable incompleto.');
    all.push(...rows);if(all.length>2000)throw Error('Catálogo demasiado extenso para esta revisión.');
    const link=Array.isArray(body)?raw?.meta?.next:body.next;
    if(link){const url=new URL(link,window.location.origin);if(url.origin!==window.location.origin||url.pathname!==API)throw Error('Paginación fuera del catálogo autorizado.');url.searchParams.set('provider_id',providerId);next=url.pathname+url.search;}else next=null;
   }
   if(new Set(all.map(a=>a.id)).size!==all.length)throw Error('Catálogo repetido o inconsistente.');
   const selected=policy?.mapping||empty();
   if(policy!==null&&(!Number.isInteger(policy?.revision)||policy.revision<1||!policy.mapping))throw Error('Revisión contable incompleta.');
   if(Object.keys(selected).length!==4||!(Object.keys(roles) as Role[]).every(role=>Array.isArray(selected[role])&&selected[role].every((id:unknown)=>typeof id==='string'&&all.some(a=>a.id===id&&a.is_active&&a.type===(role==='current_liabilities'?'LIABILITY':'ASSET')))))throw Error('La clasificación contiene cuentas ausentes o inactivas; requiere conciliación.');
   if(!controller.signal.aborted){setAccounts(all);setMapping(selected);setRevision(policy?.revision||0);setLoaded(context);}
  })().catch(e=>{if(!controller.signal.aborted)setError(e instanceof Error?e.message:'No se pudo cargar la clasificación.');}).finally(()=>{if(!controller.signal.aborted)setBusy(false);});
  return ()=>controller.abort();
 },[context,reload]);
 const ready=loaded===context&&!!identity&&!!providerId&&!busy&&!uncertain;
 function validate(){
  const ids=Object.values(mapping).flat();
  if(new Set(ids).size!==ids.length)throw Error('Una cuenta no puede aparecer en dos grupos.');
  if(!mapping.current_liabilities.length||!(mapping.cash_equivalents.length+mapping.temporary_investments.length+mapping.immediate_receivables.length))throw Error('Selecciona cuentas de activo y de pasivo corriente.');
  if(!/^[0-9a-f]{64}$/.test(evidence))throw Error('Introduce el SHA-256 de la evidencia revisada: 64 caracteres hexadecimales en minúsculas.');
 }
 async function save(){
  if(!ready||!reviewed||!confirmed)return;
  const snapshot=context;setBusy(true);setError('');setMessage('');
  try{
   validate();
   const policy=await read(await requester.current(API+'clasificacion-liquidez/?'+new URLSearchParams({provider_id:providerId}),{method:'POST',body:JSON.stringify({mapping,evidence_digest:evidence,expected_revision:revision,confirmed:true})}));
   if(!policy||policy.revision!==revision+1)throw Error('La revisión guardada no se pudo confirmar. Recarga antes de continuar.');
   if(current.current===snapshot){setMessage('Revisión '+policy.revision+' guardada. Se actualizarán los indicadores.');setReviewed(false);setConfirmed(false);setUncertain(true);onSaved();}
  }catch(e){if(current.current===snapshot){setError(e instanceof Error?e.message:'No confirmado; recarga antes de continuar.');setUncertain(true);}}
  finally{if(current.current===snapshot)setBusy(false);}
 }
 if(!identity||!providerId)return null;
 return <section aria-label="Clasificación de liquidez" style={{background:'#0E1B38',color:'#FFFFFF',padding:20,border:'1px solid #60A5FA',borderRadius:12,marginTop:20}}>
  <h2>Revisión de clasificación de liquidez</h2><p>Esta configuración no mueve dinero. Clasifica únicamente cuentas pertinentes y conserva la evidencia; el hash no certifica su contenido ni la cobertura contable.</p>
  {busy&&<p role="status">Procesando clasificación…</p>}{error&&<p role="alert">{error}</p>}{message&&<p role="status">{message}</p>}
  <button type="button" disabled={busy} onClick={()=>setReload(n=>n+1)}>Recargar clasificación</button>
  {loaded===context&&<form onSubmit={e=>{e.preventDefault();try{validate();setError('');setReviewed(true);setConfirmed(false);}catch(e){setError(e instanceof Error?e.message:'Revisa la clasificación.');}}}>
   <p>Revisión cargada: {revision}. Se creará una revisión nueva; no se edita la historia.</p>
   <fieldset disabled={!ready||reviewed} style={{border:0,padding:0,display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(min(100%,240px),1fr))',gap:16}}>
   {(Object.keys(roles) as Role[]).map(role=><label key={role}>{roles[role]}<select aria-label={roles[role]} multiple size={5} value={mapping[role]} onChange={e=>{setMapping({...mapping,[role]:Array.from(e.target.selectedOptions,o=>o.value)});setConfirmed(false);}} style={{display:'block',width:'100%',background:'#142850',color:'#FFFFFF',border:'1px solid #60A5FA',padding:8}}>
    {accounts.filter(a=>a.is_active&&a.type===(role==='current_liabilities'?'LIABILITY':'ASSET')).map(a=><option key={a.id} value={a.id}>{a.code} · {a.name}</option>)}
   </select></label>)}
   <label>Evidencia revisada (SHA-256)<input aria-label="Evidencia revisada" value={evidence} maxLength={64} onChange={e=>setEvidence(e.target.value)} style={{width:'100%',boxSizing:'border-box',background:'#142850',color:'#FFFFFF',border:'1px solid #60A5FA',padding:10}}/></label>
   </fieldset>
   {!reviewed&&<button type="submit" disabled={!ready}>Revisar selección</button>}
   {reviewed&&<div><h3>Confirmar clasificación</h3><ul>{(Object.keys(roles) as Role[]).map(role=><li key={role}>{roles[role]}: {mapping[role].map(id=>accounts.find(a=>a.id===id)?.code).join(', ')||'Sin cuentas'}</li>)}</ul>
    <p>Evidencia: {evidence}</p><label><input type="checkbox" checked={confirmed} disabled={!ready} onChange={e=>setConfirmed(e.target.checked)}/> He revisado las cuentas, su cobertura y la evidencia.</label>
    <p><button type="button" disabled={!ready||!confirmed} onClick={save}>Guardar revisión</button> <button type="button" disabled={!ready} onClick={()=>{setReviewed(false);setConfirmed(false);}}>Volver a editar</button></p>
   </div>}
  </form>}
  <style>{`[aria-label="Clasificación de liquidez"] button{background:#142850;color:#fff;border:1px solid #60a5fa;padding:10px;margin:8px 0;border-radius:6px}[aria-label="Clasificación de liquidez"] :focus-visible{outline:3px solid #7dd3fc;outline-offset:2px}`}</style>
 </section>;
}
