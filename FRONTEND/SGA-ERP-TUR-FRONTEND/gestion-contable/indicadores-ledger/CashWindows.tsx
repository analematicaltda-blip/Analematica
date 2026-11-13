'use client';
import React,{useEffect,useRef} from 'react';
import '../runtime/cash-windows.js';
declare global {interface Window {SGACDCashWindows:{mount:(root:HTMLElement,options:{request:(payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>})=>{destroy:()=>void;clear:()=>void}}}}
export function CashWindows({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request);requester.current=request;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDCashWindows)return;const control=window.SGACDCashWindows.mount(root.current,{request:async(payload,signal)=>{const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/backtest-ventanas-caja/?'+new URLSearchParams({provider_id:providerId}),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload),signal});const raw=await response.json();if(!response.ok)throw Error('Evaluación rechazada: revisa continuidad, separación de fechas, datos y permisos.');return raw?.success===true?raw.data:raw;}});return ()=>control.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Evaluación cronológica de caja"/>:null;
}
