'use client';
import React,{useEffect,useRef} from 'react';
import './panel.js';
declare global {interface Window {SGACDCancellationPolicy:{mount:(root:HTMLElement,options:{providerId:string;request:(operation:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>})=>{destroy:()=>void;clear:()=>void}}}}
export function CancellationPolicyPanel({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request);requester.current=request;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDCancellationPolicy)return;const controller=window.SGACDCancellationPolicy.mount(root.current,{providerId,request:async(operation,payload,signal)=>{if(!['review_wallet_refund_lifecycle','confirm_wallet_refund_lifecycle','wallet_refund_lifecycle_state','wallet_refund_sources','prepare_wallet_refund','wallet_refund_state','review_refund','authorize_refund','refund_state','sources','review_policy','publish_policy','policy_state','bind_policy','review_case','confirm_case','case_state'].includes(operation))throw Error('Operación no disponible.');const r=await requester.current('/api/v1/mi-negocio/comercial/cancellation-policies/'+operation+'/?'+new URLSearchParams({provider_id:providerId}),{signal,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const raw=await r.json();if(!r.ok)throw Error('Política comercial rechazada. Revisa versión, empresa, contrato y autorizaciones.');return raw?.success===true?raw.data:raw;}});return ()=>controller.destroy();},[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Políticas comerciales de devolución"/>:null;
}
