'use client';
import React,{useEffect,useRef,useState} from 'react';
type Reply={company_id:string;intent:string;source:string;data:any};
const money=(v:unknown)=>typeof v==='string'&&/^-?[0-9]{1,18}\.[0-9]{2}$/.test(v);
const count=(v:unknown)=>Number.isSafeInteger(v)&&Number(v)>=0;
export function AccountingQuery({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const [kind,setKind]=useState('profitability');const [since,setSince]=useState(()=>new Date().toISOString().slice(0,7)+'-01');const [until,setUntil]=useState(()=>new Date().toISOString().slice(0,10));
 const context=JSON.stringify([identity,providerId,kind,since,until]);const current=useRef(context);current.current=context;
 const pending=useRef<AbortController|null>(null);const [reply,setReply]=useState<{context:string;value:Reply}|null>(null);const [error,setError]=useState<{context:string;text:string}|null>(null);const [busy,setBusy]=useState<string|null>(null);
 useEffect(()=>{pending.current?.abort();setReply(null);setError(null);setBusy(null);return ()=>pending.current?.abort();},[context]);
 async function ask(){
  pending.current?.abort();const controller=new AbortController();pending.current=controller;setReply(null);setError(null);setBusy(context);
  try{
   const body=kind==='profitability'?{question:'¿Cuál es la rentabilidad de mi empresa?',since,until}:{question:'¿Cómo está la cola de facturación?'};
   const response=await request('/api/v1/mi-negocio/contable/contabilidad/cuentas/consulta-contable/?provider_id='+encodeURIComponent(providerId),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:controller.signal});
   if(!response.ok)throw Error('Consulta no disponible. Revisa la empresa y el intervalo.');
   const raw=await response.json();const value=raw?.success===true?raw.data:raw;const d=value?.data;
   const common=value?.schema==='sgacd-accounting-query-v1'&&value.read_only===true&&value.generated_sql===false&&value.external_model_used===false&&value.ledger_written===false&&value.financial_action_authorized===false&&value.execution==='DETERMINISTIC_ALLOWLIST'&&value.intent===kind&&typeof value.company_id==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value.company_id);
   const profit=kind==='profitability'&&value?.source==='ReportsEngine.get_profitability'&&d?.tenant_id===value?.company_id&&d?.start_date===since&&d?.end_date===until&&typeof d?.currency==='string'&&/^[A-Z]{3}$/.test(d.currency)&&money(d?.revenue)&&money(d?.expenses)&&money(d?.net_profit);
   const queue=kind==='commercial_queue'&&value?.source==='inspect_commercial_outbox'&&d?.company_id===value?.company_id&&d?.fiscal_acceptance==='NOT_VERIFIED'&&d?.fiscal_consumer_available===false&&d?.fiscal_receipt_verified===false&&d?.outbox_status_is_fiscal_acceptance===false&&d?.read_only===true&&['invoice_requests','reservation_confirmations'].every(k=>['PENDING','PROCESSED','ERROR','OTHER'].every(s=>count(d?.transport_counts?.[k]?.[s])));
   if(!common||(!profit&&!queue))throw Error('Respuesta incompatible; no se muestran conclusiones.');
   if(!controller.signal.aborted&&current.current===context)setReply({context,value});
  }catch(e){if(!controller.signal.aborted&&current.current===context)setError({context,text:e instanceof Error?e.message:'Consulta no disponible.'});}
  finally{if(!controller.signal.aborted&&current.current===context)setBusy(null);}
 }
 if(!identity||!providerId)return null;
 const result=reply?.context===context?reply.value:null;
 const field={background:'#142850',color:'#FFFFFF',border:'1px solid #60A5FA',padding:10,borderRadius:6,maxWidth:'100%'};
 return <section aria-label="Consulta contable asistida" style={{background:'#0E1B38',color:'#FFFFFF',border:'1px solid #60A5FA',padding:16,borderRadius:8,marginTop:16}}>
  <h2>Consulta contable asistida</h2><p>Preguntas disponibles de solo lectura. No utiliza un modelo de IA ni autoriza operaciones financieras.</p>
  <div style={{display:'flex',gap:12,flexWrap:'wrap',alignItems:'end'}}><label>Pregunta contable <select aria-label="Pregunta contable" style={field} value={kind} onChange={e=>setKind(e.target.value)}><option value="profitability">¿Cuál es la rentabilidad de mi empresa?</option><option value="commercial_queue">¿Cómo está la cola de facturación?</option></select></label>
  {kind==='profitability'&&<><label>Inicio de consulta <input style={field} aria-label="Inicio de consulta" type="date" value={since} onChange={e=>setSince(e.target.value)}/></label><label>Fin de consulta <input style={field} aria-label="Fin de consulta" type="date" value={until} onChange={e=>setUntil(e.target.value)}/></label></>}
  <button type="button" style={field} disabled={busy===context} onClick={ask}>{busy===context?'Consultando pregunta…':'Consultar pregunta'}</button></div>
  {error?.context===context&&<p role="alert">{error.text}</p>}
  {result&&<div aria-live="polite"><p>Fuente: {result.source}</p>{result.intent==='profitability'?<dl><dt>Ingresos ({result.data.currency})</dt><dd>{result.data.revenue}</dd><dt>Gastos ({result.data.currency})</dt><dd>{result.data.expenses}</dd><dt>Resultado neto ({result.data.currency})</dt><dd>{result.data.net_profit}</dd></dl>:<p>Aceptación fiscal no verificada. Consumidor fiscal pendiente de integración.</p>}</div>}
 </section>;
}
