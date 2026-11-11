'use client';
import React,{useEffect,useRef} from 'react';
import '../../../ANALEMATICA-FRONTEND/js/financial-rehearsal.js';
declare global {interface Window {SGACDFinancialRehearsal:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<any>})=>{destroy:()=>void}}}}
const paths:Record<string,string>={context:'identidad-contable',prepare_financial_rehearsal:'preparar-simulacion-financiera',state_financial_rehearsal:'estado-simulacion-financiera',confirm_financial_rehearsal:'confirmar-simulacion-financiera',simulate_financial_rehearsal:'simular-orden-financiera',cancel_financial_rehearsal:'cancelar-simulacion-financiera'};
export function FinancialRehearsal({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request);requester.current=request;
 useEffect(()=>{if(!identity||!providerId||!root.current)return;const c=window.SGACDFinancialRehearsal.mount(root.current,{request:async(action,payload,signal)=>{if(!paths[action])throw Error('Acción no admitida.');const r=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+paths[action]+'/?'+new URLSearchParams({provider_id:providerId}),{signal,...(action==='context'?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})});const raw=await r.json();if(!r.ok)throw Error('Ensayo no confirmado.');return raw?.success===true?raw.data:raw;}});return ()=>c.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Ensayo financiero supervisado"/>:null;
}
