'use client';
import React,{useEffect,useRef} from 'react';
import '../../../ANALEMATICA-FRONTEND/js/opening-chunks.js';
declare global {interface Window {SGACDOpeningChunks:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>;onPosted:()=>void})=>{destroy:()=>void;clear:()=>void}}}}
const actions:Record<string,string>={opening_chunks_sources:'fuentes-apertura-ampliada',review_opening_chunks:'revisar-apertura-ampliada',apply_opening_chunks:'aplicar-apertura-ampliada',opening_chunks_state:'estado-apertura-ampliada'};
export function OpeningChunks({identity,providerId,request,onPosted}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>;onPosted:()=>void}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request),posted=useRef(onPosted);requester.current=request;posted.current=onPosted;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDOpeningChunks)return;const c=window.SGACDOpeningChunks.mount(root.current,{onPosted:()=>posted.current(),request:async(action,payload,signal)=>{if(!actions[action])throw Error('Acción no admitida.');const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+actions[action]+'/?'+new URLSearchParams({provider_id:providerId}),{signal,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const raw=await response.json();if(!response.ok)throw Error('Apertura no confirmada. Recupera el estado de la empresa.');return raw?.success===true?raw.data:raw;}});return ()=>c.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Apertura ampliada del libro"/>:null;
}
