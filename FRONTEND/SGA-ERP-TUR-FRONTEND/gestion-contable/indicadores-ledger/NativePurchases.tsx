'use client';
import React,{useEffect,useRef} from 'react';
import '../../../ANALEMATICA-FRONTEND/js/native-purchases.js';
declare global {interface Window {SGACDNativePurchases:{mount:(root:HTMLElement,options:{request:(action:string,payload:Record<string,unknown>,signal:AbortSignal)=>Promise<unknown>;onPosted:()=>void})=>{destroy:()=>void;clear:()=>void}}}}
const actions:Record<string,string>={accounts:'cuentas-compras-nativas',native_supplier_sources:'proveedores-compras-nativas',native_purchase_sources:'fuentes-compras-nativas',record_native_supplier:'registrar-proveedor-nativo',record_native_purchase:'registrar-factura-compra-nativa',review_native_purchase:'revisar-compra-nativa',post_native_purchase:'contabilizar-compra-nativa',native_purchase_state:'estado-compra-nativa',review_native_purchase_reversal:'revisar-contrapartida-compra-nativa',reverse_native_purchase:'contrapartida-compra-nativa'};
export function NativePurchases({identity,providerId,request,onPosted}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>;onPosted:()=>void}){
 const root=useRef<HTMLElement|null>(null),requester=useRef(request),callback=useRef(onPosted);requester.current=request;callback.current=onPosted;
 useEffect(()=>{if(!identity||!providerId||!root.current||!window.SGACDNativePurchases)return;
  const controller=window.SGACDNativePurchases.mount(root.current,{onPosted:()=>callback.current(),request:async(action,payload,signal)=>{if(!actions[action])throw Error('Operación de compra no disponible.');const read=action==='accounts',query=new URLSearchParams({provider_id:providerId});if(read)for(const [key,value] of Object.entries(payload))query.set(key,String(value));const response=await requester.current('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+actions[action]+'/?'+query,{signal,...(read?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})});const raw=await response.json();if(!response.ok)throw Object.assign(Error('Compra rechazada. Revisa fuente, política, período y autorizaciones; recupera la misma compra antes de reintentar.'),{status:response.status});return raw?.success===true?raw.data:raw;}});
  return ()=>controller.destroy();
 },[identity,providerId]);
 return identity&&providerId?<section ref={root} aria-label="Compras nativas revisadas"/>:null;
}
