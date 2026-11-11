'use client';
import React,{useEffect,useRef} from 'react';
import '../../../ANALEMATICA-FRONTEND/js/bank-empty-period.js';
declare global {interface Window {SGACDEmptyBankPeriod:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>})=>{destroy:()=>void;clear:()=>void}}}}
const actions:Record<string,string>={bank_sources:'fuentes-conciliacion-bancaria',review_empty_bank_period:'revisar-periodo-bancario-vacio',confirm_empty_bank_period:'confirmar-periodo-bancario-vacio',empty_bank_period_state:'estado-periodo-bancario-vacio'};
export function EmptyBankPeriod({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request);requester.current=request;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDEmptyBankPeriod)return;const controller=window.SGACDEmptyBankPeriod.mount(root.current,{request:async(action,payload,signal)=>{if(!actions[action])throw Error('Acción no admitida.');const read=action==='bank_sources',query=new URLSearchParams({provider_id:providerId});const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+actions[action]+'/?'+query,{signal,...(read?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})});const raw=await response.json();if(!response.ok)throw Error('No se confirmó el período. Recupera la misma revisión.');return raw?.success===true?raw.data:raw;}});return ()=>controller.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Período bancario sin movimientos"/>:null;
}
