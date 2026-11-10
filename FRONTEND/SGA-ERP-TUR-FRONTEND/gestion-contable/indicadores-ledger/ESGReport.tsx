'use client';
import React,{useEffect,useRef} from 'react';
import '../../../ANALEMATICA-FRONTEND/js/esg-report.js';
declare global {interface Window {SGACDESGReport:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>})=>{destroy:()=>void;clear:()=>void}}}}
const actions:Record<string,string>={esg_report:'reporte-evidencia-esg'};
export function ESGReport({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request);requester.current=request;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDESGReport)return;const controller=window.SGACDESGReport.mount(root.current,{request:async(action,payload,signal)=>{if(!actions[action])throw Error('Acción no admitida.');const query=new URLSearchParams({provider_id:providerId});const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+actions[action]+'/?'+query,{signal,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const raw=await response.json();if(!response.ok)throw Error('Reporte ESG no confirmado. Revisa el período, corte UTC y fuentes.');return raw?.success===true?raw.data:raw;}});return ()=>controller.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Reporte ESG de evidencias"/>:null;
}
