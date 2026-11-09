'use client';
import React,{useEffect,useRef,useState} from 'react';
import {useErpSession} from '../../gestion-comercial/cotizaciones/useErpSession';
import {LedgerIndicators} from './LedgerIndicators';
import {LiquidityReview} from './LiquidityReview';
import {LiquidityHistory} from './LiquidityHistory';
import {CashScenarios} from './CashScenarios';
import {RemediationPanel} from './RemediationPanel';
import {BankComparison} from './BankComparison';
import {TaxReconciliation} from './TaxReconciliation';
import {NativePurchases} from './NativePurchases';
import {PayrollCosts} from './PayrollCosts';
import {ReservationRecognition} from './ReservationRecognition';
import {ReservationBilling} from './ReservationBilling';
import {AccountingQuery} from './AccountingQuery';
import {CommercialQueue} from './CommercialQueue';
import {ReconciliationDiagnostic} from './ReconciliationDiagnostic';
export default function LedgerWorkspace(){
 const session=useErpSession();const identity=session.user?String(session.user.id):null;
 const [companies,setCompanies]=useState<{provider_id:string;name:string}[]>([]);const [provider,setProvider]=useState('');const [error,setError]=useState('');
 const requester=useRef(session.request);requester.current=session.request;
 const [companyIdentity,setCompanyIdentity]=useState<string|null>(null);
 useEffect(()=>{
  const controller=new AbortController();setCompanies([]);setProvider('');setCompanyIdentity(null);setError('');
  if(!identity)return ()=>controller.abort();
  requester.current('/api/v1/mi-negocio/comercial/quotation-options/',{signal:controller.signal}).then(async r=>{
   const raw=await r.json();if(!r.ok)throw Error('No se pudieron consultar las empresas autorizadas.');
   const body=raw?.success===true?raw.data:raw;
   if(!Array.isArray(body?.companies)||!body.companies.every((c:{provider_id:string;name:string})=>typeof c.provider_id==='string'&&typeof c.name==='string'))throw Error('Respuesta de empresas incompleta.');
   if(!controller.signal.aborted){setCompanies(body.companies);setCompanyIdentity(identity);}
  }).catch(()=>{if(!controller.signal.aborted)setError('No se pudieron consultar las empresas autorizadas.');});
  return ()=>controller.abort();
 },[identity]);
 const [revisionSignal,setRevisionSignal]=useState(0);
 const authorized=identity!==null&&companyIdentity===identity;
 return <main style={{background:'#0A1128',color:'#FFFFFF',minHeight:'100vh',padding:20}}>
  <h1>Consulta contable empresarial</h1>
  {(session.user||session.logoutUnconfirmed)&&<div style={{display:'flex',gap:16,flexWrap:'wrap',alignItems:'center'}}>
   {session.user&&<p>Sesión: {session.user.username}</p>}
   <button type="button" disabled={session.loading} onClick={()=>session.logout()} style={{background:'#142850',color:'#FFFFFF',border:'1px solid #60A5FA',padding:10,borderRadius:6}}>{session.logoutUnconfirmed?'Reintentar cierre de sesión':'Cerrar sesión'}</button>
  </div>}
  {!session.user&&<p>Inicia sesión mediante el <a style={{color:'#FFFFFF'}} href="/dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones">acceso seguro del ERP</a> y regresa a esta consulta.</p>}
  {(session.error||error)&&<p role="alert">{session.error||error}</p>}
  <label>Empresa autorizada <select aria-label="Empresa autorizada" disabled={!authorized} value={authorized?provider:''} onChange={e=>setProvider(e.target.value)} style={{background:'#142850',color:'#FFFFFF',padding:10,border:'1px solid #60A5FA',maxWidth:'100%'}}>
   <option value="">Seleccionar empresa</option>{authorized&&companies.map(c=><option key={c.provider_id} value={c.provider_id}>{c.name}</option>)}
  </select></label>
  <RemediationPanel key={'remediation:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request} onPosted={()=>setRevisionSignal(n=>n+1)}/>
  <BankComparison key={'bank:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <TaxReconciliation key={'tax:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <ReservationRecognition key={'reservation-recognition:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request} onPosted={()=>setRevisionSignal(n=>n+1)}/>
  <ReservationBilling key={'reservation-billing:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <AccountingQuery key={'accounting-query:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <PayrollCosts identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <NativePurchases identity={identity} providerId={authorized?provider:''} request={session.request} onPosted={()=>setRevisionSignal(n=>n+1)}/>
  <CommercialQueue key={'commercial-queue:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <LedgerIndicators identity={identity} providerId={authorized?provider:''} request={session.request} revisionSignal={revisionSignal}/>
  <LiquidityReview identity={identity} providerId={authorized?provider:''} request={session.request} onSaved={()=>setRevisionSignal(n=>n+1)}/>
  <LiquidityHistory identity={identity} providerId={authorized?provider:''} request={session.request} revisionSignal={revisionSignal}/>
  <CashScenarios key={JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
  <ReconciliationDiagnostic key={'reconciliation:'+JSON.stringify([identity,authorized?provider:''])} identity={identity} providerId={authorized?provider:''} request={session.request}/>
 </main>;
}
