'use client';
import React,{useEffect,useRef,useState} from 'react';
type Entry={journal_id:string;economic_date:string;hash_version:string;findings:string[]};
type Report={read_only:true;repairs_executed:false;posted_journal_count:number;legacy_journal_count:number;initial_balance_account_count:number;initial_balance_accounts:{account_id:string;code:string}[];initial_balance_sample_truncated:boolean;opening_reconciliation?:{status:string;journal_id?:string};entries:Entry[];next_after:string|null;chain_validation_included:false;full_ledger_certified:false;snapshot_stable_across_pages:false};
const labels:Record<string,string>={
 LINE_LIMIT_REQUIRES_SEPARATE_REVIEW:'El asiento supera el límite de líneas de este diagnóstico.',
 TRANSACTION_BALANCE_OR_LINE_SCOPE_INVALID:'Revisar el balance y la pertenencia empresarial de las líneas.',
 ACCOUNT_CHART_SCOPE_INVALID:'El plan de una cuenta no corresponde a esta empresa.',
 HASH_MISMATCH:'La huella del asiento no coincide; requiere investigación.',
 HASH_VALIDATION_UNAVAILABLE:'No se pudo verificar la huella del asiento.',
 LEGACY_HASH_REVIEW_REQUIRED:'Registro legado: revisar su versión de integridad sin reescribirla.',
 UNKNOWN_HASH_VERSION_REVIEW_REQUIRED:'Versión de integridad no reconocida.',
 LINE_CURRENCY_MISMATCH:'La moneda de una línea no coincide con la cabecera.',
 TRANSACTION_VALUATION_REVIEW_REQUIRED:'Revisar la valoración de la transacción.',
 BASE_VALUATION_REVIEW_REQUIRED:'Revisar el importe registrado en moneda base.',
 SAME_CURRENCY_RATE_REVIEW_REQUIRED:'Revisar la tasa de una operación en la misma moneda.',
 VALUATION_INVALID:'Valoración inválida o incompleta; requiere conciliación.',
 POSTED_TIMESTAMP_MISSING:'Falta la fecha y hora de contabilización.',
 COMPANY_BASE_CURRENCY_REVIEW_REQUIRED:'La moneda base registrada difiere de la configuración actual.'};
const count=(value:unknown):value is number=>Number.isSafeInteger(value)&&Number(value)>=0;
const uuid=(value:unknown):value is string=>typeof value==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value);
export function ReconciliationDiagnostic({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const context=JSON.stringify([identity,providerId]);const current=useRef(context);current.current=context;
 const pending=useRef<AbortController|null>(null);const [report,setReport]=useState<{context:string;data:Report}|null>(null);const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 useEffect(()=>{setReport(null);setError('');setBusy(false);return ()=>pending.current?.abort();},[context]);
 async function load(after:string|null){
  if(busy||!identity||!providerId)return;
  pending.current?.abort();const controller=new AbortController();pending.current=controller;const snapshot=context;
  setReport(null);setError('');setBusy(true);
  try{
   const query=new URLSearchParams({provider_id:providerId,limite:'10'});if(after)query.set('despues_id',after);
   const response=await request('/api/v1/mi-negocio/contable/contabilidad/cuentas/diagnostico-conciliacion/?'+query,{signal:AbortSignal.any([controller.signal,AbortSignal.timeout(20000)])});
   if(!response.ok)throw Error(response.status===403?'No tienes acceso a este diagnóstico empresarial.':'No se pudo consultar el diagnóstico. Revisa la sesión, el cursor y la conexión.');
   const raw=await response.json();const body=raw?.success===true?raw.data:raw;
   if(!body||body.read_only!==true||body.repairs_executed!==false||body.chain_validation_included!==false||body.full_ledger_certified!==false||body.snapshot_stable_across_pages!==false||![body.posted_journal_count,body.legacy_journal_count,body.initial_balance_account_count].every(count)||!Array.isArray(body.initial_balance_accounts)||body.initial_balance_accounts.length>10||!body.initial_balance_accounts.every((row:{account_id:string;code:string})=>row&&uuid(row.account_id)&&typeof row.code==='string')||typeof body.initial_balance_sample_truncated!=='boolean'||!Array.isArray(body.entries)||body.entries.length>10||!(body.next_after===null||uuid(body.next_after))||!body.entries.every((row:Entry)=>row&&uuid(row.journal_id)&&typeof row.economic_date==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(row.economic_date)&&typeof row.hash_version==='string'&&Array.isArray(row.findings)&&row.findings.every(code=>typeof code==='string')))throw Error('Diagnóstico incompleto; no se muestran conclusiones sin validar.');
   if(!controller.signal.aborted&&current.current===snapshot)setReport({context:snapshot,data:body});
  }catch(e){if(!controller.signal.aborted&&current.current===snapshot)setError(e instanceof Error?e.message:'Diagnóstico temporalmente no disponible.');}
  finally{if(current.current===snapshot)setBusy(false);}
 }
 const visible=report?.context===context?report.data:null;
 if(!identity||!providerId)return null;
 return <section aria-label="Diagnóstico de conciliación" className="reconciliation-diagnostic" style={{background:'#0E1B38',color:'#FFFFFF',padding:20,border:'1px solid #60A5FA',borderRadius:12,marginTop:20,overflowWrap:'anywhere'}}>
  <h2>Diagnóstico de conciliación</h2><p>Solo lectura. Los hallazgos requieren revisión contable; no se modifican saldos, hashes ni registros. Cada consulta cubre una página y no certifica toda la cadena.</p>
  <button type="button" disabled={busy} onClick={()=>load(null)}>Consultar diagnóstico</button>
  {busy&&<p role="status">Revisando la página solicitada…</p>}{error&&<p role="alert">{error}</p>}
  {visible&&<div aria-live="polite">
   <dl><dt>Asientos contabilizados de la empresa</dt><dd>{visible.posted_journal_count}</dd><dt>Versión anterior o no verificada</dt><dd>{visible.legacy_journal_count}</dd><dt>Cuentas con saldo inicial original</dt><dd>{visible.initial_balance_account_count}</dd></dl>
   <p>{visible.opening_reconciliation?.status==='RECONCILED_PRESERVED_REFERENCE'?'Apertura registrada y comprobada; los saldos originales se conservan como referencia.':visible.opening_reconciliation?.status==='NO_LEGACY_BALANCES'?'No se detectan saldos iniciales legados.':visible.opening_reconciliation?.status==='REQUIRES_REVIEW'?'Los saldos iniciales o su evidencia requieren conciliación.':'La comprobación de apertura no está incluida en este diagnóstico.'}</p>
   {visible.initial_balance_accounts.length>0&&<details><summary>Cuentas con saldo inicial original</summary><ul>{visible.initial_balance_accounts.map(row=><li key={row.account_id}>Cuenta {row.code} · {row.account_id}</li>)}</ul>{visible.initial_balance_sample_truncated&&<p>Solo se muestra una muestra de cuentas; consulta el inventario completo mediante el procedimiento autorizado.</p>}</details>}
   {visible.entries.length===0?<p>No hay asientos en esta página.</p>:visible.entries.every(row=>row.findings.length===0)&&<p>Sin hallazgos en esta página; no certifica el libro completo.</p>}
   <div style={{overflowX:'auto'}}><table><caption>Hallazgos de la página de asientos</caption><thead><tr><th>Asiento</th><th>Fecha económica</th><th>Revisión requerida</th></tr></thead><tbody>{visible.entries.map(row=><tr key={row.journal_id}><td style={{overflowWrap:'anywhere'}}>{row.journal_id}</td><td>{row.economic_date}</td><td>{row.findings.length?<ul>{row.findings.map(code=><li key={code}><span>{labels[code]||'Hallazgo pendiente de clasificación.'}</span><details><summary>Código de revisión</summary>{code}</details></li>)}</ul>:'Sin hallazgos en esta revisión limitada'}</td></tr>)}</tbody></table></div>
   <p>Las páginas no comparten una instantánea estable. Si se contabilizan operaciones durante la revisión, repite el recorrido en una ventana estable.</p>
   <button type="button" disabled={busy||!visible.next_after} onClick={()=>load(visible.next_after)}>Consultar siguiente página</button>
  </div>}
  <style>{`.reconciliation-diagnostic button{background:#142850;color:#fff;border:1px solid #60a5fa;padding:10px;border-radius:6px}.reconciliation-diagnostic :focus-visible{outline:3px solid #7dd3fc;outline-offset:2px}.reconciliation-diagnostic td,.reconciliation-diagnostic th{text-align:left;padding:8px;border-bottom:1px solid #60a5fa}`}</style>
 </section>;
}
