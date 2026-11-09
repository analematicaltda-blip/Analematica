'use client';
import React,{useEffect,useRef} from 'react';
import '../../../ANALEMATICA-FRONTEND/js/payroll-costs.js';
declare global {interface Window {SGACDPayrollCosts:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>})=>{destroy:()=>void;clear:()=>void}}}}
const actions:Record<string,string>={payroll_sources:'fuentes-nomina-revisada',payroll_cost_sources:'fuentes-costos-operativos-nomina',review_payroll_costs:'revisar-costos-operativos-nomina',record_payroll_costs:'registrar-costos-operativos-nomina',payroll_cost_state:'estado-costos-operativos-nomina'};
export function PayrollCosts({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request);requester.current=request;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDPayrollCosts)return;const controller=window.SGACDPayrollCosts.mount(root.current,{request:async(action,payload,signal)=>{if(!actions[action])throw Error('Acción no admitida.');const read=action==='payroll_sources',query=new URLSearchParams({provider_id:providerId});const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+actions[action]+'/?'+query,{signal,...(read?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})});const raw=await response.json();if(!response.ok)throw Error('No se confirmó la distribución. Recupera la misma nómina.');return raw?.success===true?raw.data:raw;}});return ()=>controller.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Costos de nómina por operación"/>:null;
}
