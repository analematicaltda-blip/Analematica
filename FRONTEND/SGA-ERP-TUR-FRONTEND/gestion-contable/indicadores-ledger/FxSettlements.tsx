'use client';
import React,{useEffect,useRef} from 'react';
import '../runtime/fx-settlements.js';
declare global {interface Window {SGACDFxSettlements:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>;onPosted:()=>void})=>{destroy:()=>void;clear:()=>void}}}}
const actions:Record<string,string>={fx_settlement_catalog:'catalogo-liquidacion-divisas',review_fx_settlement:'revisar-liquidacion-divisas',post_fx_settlement:'contabilizar-liquidacion-divisas',fx_settlement_state:'estado-liquidacion-divisas',fx_settlement_request_state:'consultar-solicitud-liquidacion-divisas'};
export function FxSettlements({identity,providerId,request,onPosted}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>;onPosted:()=>void}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request),posted=useRef(onPosted);requester.current=request;posted.current=onPosted;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDFxSettlements)return;const c=window.SGACDFxSettlements.mount(root.current,{onPosted:()=>posted.current(),request:async(action,payload,signal)=>{if(!actions[action])throw Error('Acción no admitida.');const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+actions[action]+'/?'+new URLSearchParams({provider_id:providerId}),{signal,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const raw=await response.json();if(!response.ok)throw Error('Liquidación no confirmada; recupera la misma solicitud.');return raw?.success===true?raw.data:raw;}});return ()=>c.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Liquidación de moneda extranjera"/>:null;
}
