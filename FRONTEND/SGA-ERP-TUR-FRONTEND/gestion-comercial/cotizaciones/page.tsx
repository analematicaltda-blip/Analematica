'use client';

import React, {useEffect, useRef, useState} from 'react';
import {useErpSession} from './useErpSession';
import {PasswordRecovery} from './PasswordRecovery';
import {SecurityHistory} from './SecurityHistory';
import {RecoverySetup} from './RecoverySetup';
import {TotpSetup} from './TotpSetup';

const API='/api/v1/mi-negocio/comercial/';
type Company={provider_id:string;name:string};
type Options={currency:string;customers:{id:number;name:string}[];products:{id:string;name:string;unit_price:string}[];customers_truncated:boolean;products_truncated:boolean};
type Line={product_id:string;quantity:number};
type Draft={id:string;status:string;digest:string;created_at:string;expires_at:string;preview:{currency:string;subtotal:string}};
const initialLine=():Line=>({product_id:'',quantity:1});

function LegacyQuotationWorkspace(){
 const session=useErpSession();
 const {user,challenge,verifyCode,loading:sessionLoading,error:sessionError,logoutUnconfirmed,login,logout,request:sessionRequest}=session;
 const identity=user?String(user.id):null;
 const [mfaCode,setMfaCode]=useState('');const [useRecovery,setUseRecovery]=useState(false);
 const [username,setUsername]=useState('');const [password,setPassword]=useState('');
 const [companies,setCompanies]=useState<Company[]>([]);
 const [provider,setProvider]=useState('');
 const [customer,setCustomer]=useState('');
 const [lines,setLines]=useState<Line[]>([initialLine()]);
 const [options,setOptions]=useState<Options|null>(null);
 const [drafts,setDrafts]=useState<Draft[]>([]);
 const [error,setError]=useState('');
 const [message,setMessage]=useState('');
 const [loading,setLoading]=useState(false);
 const [saving,setSaving]=useState(false);
 const [customerSearch,setCustomerSearch]=useState('');
 const [productSearch,setProductSearch]=useState('');
 const idempotency=useRef('');
 const currentIdentity=useRef(identity);currentIdentity.current=identity;

 async function request(path:string,init:RequestInit={}){
  if(!identity)throw new Error('Inicia sesión en el ERP para continuar.');
  const response=await sessionRequest(API+path,init);
  const body=await response.json().catch(()=>null);
  if(!response.ok){
   if(response.status===503)throw new Error('El servicio aún no está habilitado en este entorno.');
   if(response.status===401)throw new Error('Tu sesión venció. Inicia sesión nuevamente.');
   if(response.status===403)throw new Error('Se requiere el administrador titular y un vínculo empresarial vigente.');
   if(response.status===409)throw new Error('La solicitud cambió o el borrador requiere revisión. Recarga antes de continuar.');
   throw new Error(typeof body?.detail==='string'?body.detail:'No se pudo completar la solicitud. Revisa los datos e inténtalo de nuevo.');
  }
  if(body&&typeof body.success==='boolean'&&Object.prototype.hasOwnProperty.call(body,'data')){
   if(Array.isArray(body.data)&&typeof body.meta?.total==='number')return {results:body.data,count:body.meta.total,next:body.meta.next,previous:body.meta.previous};
   if(body.data&&typeof body.data==='object')return body.data;
   throw new Error('El servidor devolvió una respuesta incompleta.');
  }
  if(!body||typeof body!=='object')throw new Error('El servidor devolvió una respuesta incompleta.');
  return body;
 }
 useEffect(()=>{if(challenge)setError('');setMfaCode('');setUseRecovery(false);},[challenge?.id]);
 useEffect(()=>{
  const controller=new AbortController();
  setCompanies([]);setProvider('');setOptions(null);setDrafts([]);setCustomer('');setLines([initialLine()]);idempotency.current='';setMessage('');setSaving(false);
  if(!identity){setLoading(false);setError('Inicia sesión en el ERP para consultar tus empresas.');return ()=>controller.abort();}
  setLoading(true);setError('');
  request('quotation-options/',{signal:controller.signal}).then(data=>{if(!controller.signal.aborted&&currentIdentity.current===identity)setCompanies(data.companies);}).catch(e=>{if(!controller.signal.aborted)setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  return ()=>controller.abort();
 },[identity]);
 useEffect(()=>{
  const controller=new AbortController();setOptions(null);setDrafts([]);setCustomer('');setLines([initialLine()]);idempotency.current='';setMessage('');
  if(!provider||!identity)return ()=>controller.abort();
  setError('');setLoading(true);
  Promise.all([request(`quotation-options/?provider_id=${encodeURIComponent(provider)}`,{signal:controller.signal}),request(`quotation-drafts/?provider_id=${encodeURIComponent(provider)}`,{signal:controller.signal})]).then(([available,stored])=>{if(!controller.signal.aborted&&currentIdentity.current===identity){setOptions(available);setDrafts(stored.results);}}).catch(e=>{if(!controller.signal.aborted)setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  return ()=>controller.abort();
 },[provider,identity]);
 function edited(){idempotency.current='';setMessage('');}
 async function searchOptions(){
  const identityAtStart=identity;setLoading(true);setError('');
  try{const query=new URLSearchParams({provider_id:provider,customer_search:customerSearch,product_search:productSearch});const found=await request('quotation-options/?'+query);if(currentIdentity.current!==identityAtStart)return;setOptions(found);setCustomer('');setLines([initialLine()]);edited();}
  catch(e){if(currentIdentity.current===identityAtStart)setError(e instanceof Error?e.message:'No se pudo buscar.');}finally{if(currentIdentity.current===identityAtStart)setLoading(false);}
 }
 async function save(event:React.FormEvent){
  event.preventDefault();const identityAtStart=identity;setSaving(true);setError('');setMessage('');
  try{
   if(!idempotency.current)idempotency.current=crypto.randomUUID();
   const saved:Draft=await request('quotation-drafts/',{method:'POST',body:JSON.stringify({provider_id:provider,customer_id:customer,lines,idempotency_key:idempotency.current})});
   if(currentIdentity.current!==identityAtStart)return;
   setDrafts(current=>[saved,...current.filter(item=>item.id!==saved.id)]);
   setMessage(saved.status==='DRAFT'?'Borrador guardado. No se ha realizado ningún cobro ni reserva.':'Esta solicitud corresponde a un borrador vencido o retirado. Inicia una nueva propuesta para preparar otro.');
  }catch(e){if(currentIdentity.current===identityAtStart)setError(e instanceof Error?e.message:'No se pudo guardar.');}finally{if(currentIdentity.current===identityAtStart)setSaving(false);}
 }
 async function withdraw(draft:Draft){
  if(!window.confirm('¿Retirar este borrador? Se conservará el registro y no se realizará ningún movimiento de dinero.'))return;
  const identityAtStart=identity;setSaving(true);setError('');
  try{const result:Draft=await request(`quotation-drafts/${draft.id}/withdraw/`,{method:'POST',body:JSON.stringify({digest:draft.digest})});if(currentIdentity.current!==identityAtStart)return;setDrafts(current=>current.map(item=>item.id===result.id?result:item));setMessage('Borrador retirado; el registro se conserva.');}
  catch(e){if(currentIdentity.current===identityAtStart)setError(e instanceof Error?e.message:'No se pudo retirar.');}finally{if(currentIdentity.current===identityAtStart)setSaving(false);}
 }
 const disabled=loading||saving||sessionLoading;
 const valid=Boolean(identity&&provider&&customer&&options&&lines.every(line=>line.product_id&&Number.isInteger(line.quantity)&&line.quantity>0&&line.quantity<=10000));
 const money=(value:string,currency:string)=>{
  const match=/^(\d+)(?:\.(\d{1,2}))?$/.exec(value);
  if(!match)return `${currency} ${value}`;
  const fraction=(match[2]||'').padEnd(2,'0');
  return new Intl.NumberFormat('es-CO',{style:'currency',currency,minimumFractionDigits:2,maximumFractionDigits:2}).formatToParts(BigInt(match[1])).map(part=>part.type==='fraction'?fraction:part.value).join('');
 };
 return <main className="quotation-workspace" style={{maxWidth:1080,margin:'auto',padding:24,color:'#ffffff'}}>
  <style>{`body:has(.quotation-workspace){margin:0;background:#060b17}.quotation-workspace{font-family:system-ui,sans-serif;line-height:1.5;color:#fff;min-height:100vh;box-sizing:border-box;background:linear-gradient(145deg,#0a1128,#0e1b38 45%,#142850);border:1px solid #1e3a8a;border-radius:16px;box-shadow:0 10px 30px #060b1780}.quotation-workspace h1{line-height:1.2;color:#fff;border-bottom:2px solid #38bdf8;padding-bottom:18px}.quotation-workspace h2,.quotation-workspace legend,.quotation-workspace strong{color:#fff}.quotation-workspace a{color:#fff;text-decoration-color:#7dd3fc;text-underline-offset:5px}.quotation-workspace select,.quotation-workspace input{max-width:100%;box-sizing:border-box;border:1px solid #60a5fa;border-radius:8px;padding:10px;background:#0a1128;color:#fff;font:inherit;color-scheme:dark}.quotation-workspace fieldset{min-inline-size:0;border:1px solid #60a5fa;border-radius:12px;padding:16px;background:#0e1b38}.quotation-workspace label{max-width:100%;min-width:0;display:inline-flex;flex-direction:column;gap:6px;font-weight:600;color:#fff}.quotation-workspace button{font:inherit;padding:10px 15px;border:1px solid #7dd3fc;border-radius:8px;background:linear-gradient(135deg,#1a3262,#2563eb);color:#fff;cursor:pointer;box-shadow:inset 0 1px 0 #7dd3fc40}.quotation-workspace button:disabled{opacity:.65;cursor:default}.quotation-workspace button:focus-visible,.quotation-workspace select:focus-visible,.quotation-workspace input:focus-visible{outline:3px solid #7dd3fc;outline-offset:3px}.quotation-workspace article{background:linear-gradient(135deg,#0e1b38,#142850);color:#fff;border-color:#60a5fa!important}.quotation-workspace [role=alert]{background:#0a1128!important;border-left:4px solid #f87171;color:#fff}.quotation-workspace [role=status]{background:#142850!important;border-left:4px solid #38bdf8;color:#fff}`}</style>
  <a href="/dashboard/prestador/mi-negocio/gestion-comercial">Volver a gestión comercial</a>
  <h1>Cotizaciones · borradores</h1>
  <p>Prepara una propuesta con las tarifas registradas de tu empresa. Los impuestos y la disponibilidad aún no se confirman. Este borrador no es una factura ni una orden de pago.</p>
  {sessionError&&<p role="alert">{sessionError}</p>}
  {logoutUnconfirmed&&<button type="button" disabled={sessionLoading} onClick={()=>logout()}>Reintentar cierre de sesión</button>}
  {!user&&!challenge&&<form aria-label="Acceso ERP" onSubmit={async event=>{event.preventDefault();const secret=password;setPassword('');try{await login(username,secret);}catch{ /* The session hook presents a safe message. */ }}} style={{display:'flex',gap:12,flexWrap:'wrap',margin:'24px 0'}}>
   <label>Usuario <input aria-label="Usuario" required autoComplete="username" maxLength={150} value={username} disabled={sessionLoading} onChange={event=>setUsername(event.target.value)}/></label>
   <label>Contraseña <input aria-label="Contraseña" required type="password" autoComplete="current-password" maxLength={1024} value={password} disabled={sessionLoading} onChange={event=>setPassword(event.target.value)}/></label>
   <button type="submit" disabled={sessionLoading||logoutUnconfirmed}>{sessionLoading?'Validando…':'Iniciar sesión'}</button>
  </form>}
  {challenge&&<section aria-label="Verificación en dos pasos">
   <h2>Verificación en dos pasos</h2><p>Introduce el código actual de tu aplicación de autenticación. El desafío vence en dos minutos.</p>
   <form onSubmit={async event=>{event.preventDefault();const code=mfaCode;setMfaCode('');try{await verifyCode(code,useRecovery);}catch{ /* The session hook presents the result. */ }}} style={{display:'flex',gap:12,flexWrap:'wrap',margin:'24px 0'}}>
    {challenge.recoveryAvailable&&<button type="button" disabled={sessionLoading} onClick={()=>{setUseRecovery(current=>!current);setMfaCode('');}}>{useRecovery?'Usar aplicación de autenticación':'Usar código de recuperación'}</button>}
    {useRecovery&&<p>Introduce uno de los códigos guardados previamente. Se consumirá al entrar; tu factor TOTP permanece activo.</p>}
    <label>{useRecovery?'Código de recuperación':'Código de verificación'} <input aria-label={useRecovery?'Código de recuperación':'Código de verificación'} type="text" inputMode="numeric" autoComplete="one-time-code" pattern={'[0-9]{'+(useRecovery?challenge.recoveryDigits:challenge.digits)+'}'} minLength={(useRecovery?challenge.recoveryDigits:challenge.digits)} maxLength={(useRecovery?challenge.recoveryDigits:challenge.digits)} required value={mfaCode} disabled={sessionLoading} onChange={event=>setMfaCode(event.target.value.replace(/[^0-9]/g,''))}/></label>
    <button type="submit" disabled={sessionLoading}>{sessionLoading?'Verificando…':'Verificar código'}</button>
    <button type="button" disabled={sessionLoading} onClick={()=>logout()}>Cancelar verificación</button>
   </form>
  </section>}
  {user&&<p>Sesión: {user.username}{' '}<button type="button" disabled={disabled} onClick={()=>logout()}>Cerrar sesión</button></p>}
  <TotpSetup session={session}/>
  <RecoverySetup session={session}/>
  <SecurityHistory session={session}/>
  <PasswordRecovery session={session}/>
  {error&&<p role="alert" style={{padding:12,background:'#0a1128'}}>{error}</p>}
  {message&&<p role="status" style={{padding:12,background:'#142850'}}>{message}</p>}
  {loading&&<p role="status">Consultando datos de la empresa…</p>}
  <label>Empresa <select aria-label="Empresa" value={provider} disabled={disabled||!identity} onChange={e=>setProvider(e.target.value)}><option value="">Seleccionar empresa</option>{companies.map(c=><option key={c.provider_id} value={c.provider_id}>{c.name}</option>)}</select></label>
  {identity&&!loading&&companies.length===0&&<p>No hay empresas con un vínculo vigente para tu usuario. La revisión de identidad empresarial debe completarse antes de usar este módulo.</p>}
  {options&&<>
   <section aria-label="Buscar clientes y productos" style={{display:'flex',flexWrap:'wrap',gap:12,marginTop:20}}>
    <label>Buscar cliente <input value={customerSearch} maxLength={100} disabled={disabled} onChange={e=>setCustomerSearch(e.target.value)}/></label>
    <label>Buscar producto <input value={productSearch} maxLength={100} disabled={disabled} onChange={e=>setProductSearch(e.target.value)}/></label>
    <button type="button" disabled={disabled} onClick={searchOptions}>Buscar</button>
   </section>
   {(options.customers_truncated||options.products_truncated)&&<p>Se muestran hasta 100 resultados por lista. Usa la búsqueda para encontrar los demás.</p>}
   <form onSubmit={save} style={{marginTop:20}}>
    <label>Cliente <select aria-label="Cliente" required value={customer} disabled={disabled} onChange={e=>{setCustomer(e.target.value);edited();}}><option value="">Seleccionar cliente</option>{options.customers.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
    {lines.map((line,index)=><fieldset key={index} disabled={disabled} style={{margin:'16px 0',display:'flex',gap:12,flexWrap:'wrap'}}><legend>Servicio o producto {index+1}</legend>
     <label>Producto <select aria-label="Producto" required value={line.product_id} onChange={e=>{setLines(current=>current.map((item,i)=>i===index?{...item,product_id:e.target.value}:item));edited();}}><option value="">Seleccionar producto</option>{options.products.map(p=><option key={p.id} value={p.id}>{p.name} · {money(p.unit_price,options.currency)}</option>)}</select></label>
     <label>Cantidad <input aria-label="Cantidad" type="number" required min={1} max={10000} step={1} value={line.quantity} onChange={e=>{setLines(current=>current.map((item,i)=>i===index?{...item,quantity:Number(e.target.value)}:item));edited();}}/></label>
     {lines.length>1&&<button type="button" onClick={()=>{setLines(current=>current.filter((_,i)=>i!==index));edited();}}>Quitar línea {index+1}</button>}
    </fieldset>)}
    <button type="button" disabled={disabled||lines.length>=50} onClick={()=>{setLines(current=>[...current,initialLine()]);edited();}}>Añadir línea</button>{' '}
    <button type="button" disabled={disabled} onClick={()=>{setCustomer('');setLines([initialLine()]);edited();}}>Nueva propuesta</button>{' '}
    <button type="submit" disabled={disabled||!valid}>{saving?'Guardando…':'Guardar borrador'}</button>
   </form>
  </>}
  <section aria-label="Borradores guardados" style={{marginTop:32}}><h2>Borradores recientes</h2>
   {provider&&!loading&&drafts.length===0&&<p>No hay borradores guardados para esta empresa.</p>}
   {drafts.map(draft=><article key={draft.id} style={{border:'1px solid #cdd5e1',borderRadius:10,padding:16,marginTop:12}}><strong>Subtotal: {money(draft.preview.subtotal,draft.preview.currency)}</strong><p>Estado: {({DRAFT:'Borrador',EXPIRED:'Vencido',WITHDRAWN:'Retirado'} as Record<string,string>)[draft.status]||draft.status} · Vence: {new Date(draft.expires_at).toLocaleString('es-CO')}</p><p>Impuestos pendientes. Sin reserva ni cobro.</p>{draft.status==='DRAFT'&&<button type="button" disabled={disabled} onClick={()=>withdraw(draft)}>Retirar borrador</button>}</article>)}
  </section>
 </main>;
}

export default function QuotationWorkspace(){return <><nav style={{background:"#071b30",color:"white",padding:"1rem"}}><a href="/dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones-dinamicas" style={{color:"#bce3f9"}}>Abrir cotizaciones dinámicas con tarifas revisadas</a></nav><LegacyQuotationWorkspace/></>;}
