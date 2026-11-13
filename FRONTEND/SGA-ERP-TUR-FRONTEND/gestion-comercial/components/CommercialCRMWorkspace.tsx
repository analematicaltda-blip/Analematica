'use client';
import {useEffect,useRef} from 'react';
declare global {interface Window {Pool08NativeCRM?:{mount:(access:HTMLElement,host:HTMLElement,base:string)=>()=>void}}}
function loadScript(src:string){return new Promise<void>((resolve,reject)=>{
 const existing=document.querySelector<HTMLScriptElement>(`script[data-crm-src="${src}"]`);
 if(existing?.dataset.ready==='true'){resolve();return;}
 const script=existing||document.createElement('script');
 script.addEventListener('load',()=>{script.dataset.ready='true';resolve();},{once:true});
 script.addEventListener('error',()=>reject(new Error('No se pudo cargar el CRM.')),{once:true});
 if(!existing){script.src=src;script.dataset.crmSrc=src;document.body.append(script);}
});}
export default function CommercialCRMWorkspace({initialWorkspace='contacts'}:{initialWorkspace?:'contacts'|'opportunities'|'pricing'|'quotations'|'analytics'}){
 const access=useRef<HTMLElement>(null),host=useRef<HTMLDivElement>(null);
 useEffect(()=>{let active=true;let dispose:(()=>void)|undefined;
  loadScript('/js/commercial-analytics.js').then(()=>loadScript('/js/commercial-army.js')).then(()=>loadScript('/js/commercial-ads.js')).then(()=>loadScript('/js/commercial-inbox.js')).then(()=>loadScript('/js/commercial-publishing.js')).then(()=>loadScript('/js/commercial-mobile-messages.js')).then(()=>loadScript('/js/commercial-email-campaigns.js')).then(()=>loadScript('/js/commercial-generation.js')).then(()=>loadScript('/js/commercial-library.js')).then(()=>loadScript('/js/commercial-landings.js')).then(()=>loadScript('/js/commercial-after-sales-policy.js')).then(()=>loadScript('/js/commercial-after-sales.js')).then(()=>loadScript('/js/commercial-payments.js')).then(()=>loadScript('/js/commercial-sales.js')).then(()=>loadScript('/js/commercial-quotations.js')).then(()=>loadScript('/js/commercial-pricing.js')).then(()=>loadScript('/js/commercial-opportunities.js')).then(()=>loadScript('/js/commercial-crm.js')).then(()=>loadScript('/js/commercial-crm-native.js')).then(()=>{
   if(active&&access.current&&host.current)dispose=window.Pool08NativeCRM?.mount(access.current,host.current,'/api/v1/mi-negocio/comercial/unified/crm/');
  }).catch(()=>{if(active&&access.current)access.current.textContent='No se pudo cargar el CRM. Recarga la página.';});
  return ()=>{active=false;dispose?.();};
 },[]);
 return <main style={{background:'#071b30',color:'#fff',padding:'1rem'}}><link rel="stylesheet" href="/css/commercial-crm.css"/><h1>CRM y seguimiento comercial</h1><section ref={access} className="pool08-crm" aria-label="Acceso empresarial"><p role="status">Verificando acceso…</p></section><div ref={host} data-workspace={initialWorkspace}/></main>;
}
