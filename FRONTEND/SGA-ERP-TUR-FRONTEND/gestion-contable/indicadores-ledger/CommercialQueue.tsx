'use client';
import React,{useEffect,useRef,useState} from 'react';
type Counts={PENDING:number;PROCESSED:number;ERROR:number;OTHER:number};
type Report={company_id:string;transport_counts:{invoice_requests:Counts;reservation_confirmations:Counts}};
function valid(value:any):value is Report {
 const counts=(v:any)=>v&&['PENDING','PROCESSED','ERROR','OTHER'].every(k=>Number.isSafeInteger(v[k])&&v[k]>=0);
 return value&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value.company_id)
  &&value.read_only===true&&value.financial_values_omitted===true&&value.published_by_this_call===false&&value.ledger_written===false
  &&value.fiscal_consumer_available===false&&value.fiscal_receipt_verified===false&&value.fiscal_acceptance==='NOT_VERIFIED'
  &&value.outbox_status_is_fiscal_acceptance===false&&value.blocking_reason==='FISCAL_CONSUMER_NOT_INTEGRATED'
  &&counts(value.transport_counts?.invoice_requests)&&counts(value.transport_counts?.reservation_confirmations);
}
export function CommercialQueue({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const context=JSON.stringify([identity,providerId]);const current=useRef(context);current.current=context;
 const pending=useRef<AbortController|null>(null);const [result,setResult]=useState<{context:string;data:Report}|null>(null);
 const [error,setError]=useState<{context:string;message:string}|null>(null);const [loading,setLoading]=useState<string|null>(null);
 useEffect(()=>{pending.current?.abort();setResult(null);setError(null);setLoading(null);return ()=>pending.current?.abort();},[context]);
 async function load(){
  pending.current?.abort();const controller=new AbortController();pending.current=controller;
  setResult(null);setError(null);setLoading(context);
  try{
   const response=await request('/api/v1/mi-negocio/contable/contabilidad/cuentas/estado-cola-comercial/?provider_id='+encodeURIComponent(providerId),{signal:controller.signal});
   if(!response.ok)throw Error('No se pudo consultar la cola de esta empresa.');
   const raw=await response.json();const data=raw?.success===true?raw.data:raw;if(!valid(data))throw Error('Respuesta incompleta; no se muestran estados sin verificar.');
   if(!controller.signal.aborted&&current.current===context)setResult({context,data});
  }catch(e){if(!controller.signal.aborted&&current.current===context)setError({context,message:e instanceof Error?e.message:'Consulta no disponible.'});}
  finally{if(!controller.signal.aborted&&current.current===context)setLoading(null);}
 }
 if(!identity||!providerId)return null;
 const data=result?.context===context?result.data:null;
 const button={background:'#142850',color:'#FFFFFF',border:'1px solid #60A5FA',padding:10,borderRadius:6};
 return <section aria-label="Cola comercial" style={{background:'#0E1B38',color:'#FFFFFF',border:'1px solid #60A5FA',padding:16,borderRadius:8,marginTop:16}}>
  <h2>Cola comercial</h2><p>Los estados de transporte no certifican facturas aceptadas, pagos ni asientos contables.</p>
  <button type="button" style={button} disabled={loading===context} onClick={load}>{loading===context?'Consultando cola…':'Consultar cola comercial'}</button>
  {error?.context===context&&<p role="alert">{error.message}</p>}
  {data&&<div aria-live="polite"><p>Consumidor fiscal pendiente de integración. Aceptación fiscal no verificada.</p>
   {([['invoice_requests','Solicitudes de factura'],['reservation_confirmations','Confirmaciones de reserva']] as const).map(([key,label])=><div key={key} style={{marginTop:16}}><h3>{label}</h3><dl style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(130px,1fr))',gap:12}}>
    {([['PENDING','Pendientes'],['PROCESSED','Marcadas como procesadas'],['ERROR','Con error'],['OTHER','Otros estados']] as const).map(([state,name])=><div key={state}><dt>{name}</dt><dd style={{margin:0}}>{data.transport_counts[key][state]}</dd></div>)}
   </dl></div>)}
  </div>}
 </section>;
}
