'use client';
import React,{useEffect,useRef,useState} from 'react';

type Requester=(path:string,init?:RequestInit)=>Promise<Response>;
type Profit={tenant_id:string;currency:string;start_date:string;end_date:string;revenue:string;expenses:string;net_profit:string;sources:{account_id:string;code:string;type:string;net_amount:string}[];net_margin:{value:string|null;unavailable_reason:string|null}};
type Liquidity={tenant_id:string;currency:string;cutoff_date:string;value:string|null;unavailable_reason:string|null;policy:{revision:number}|null};
const API='/api/v1/mi-negocio/contable/contabilidad/cuentas/';
const reasons:Record<string,string>={REVIEWED_CLASSIFICATION_REQUIRED:'Falta una clasificación contable revisada.',NON_POSITIVE_REVENUE:'El margen no se calcula con ingresos cero o negativos.',NON_POSITIVE_CURRENT_LIABILITIES:'No hay pasivos corrientes positivos para calcular el indicador.',NEGATIVE_ACCOUNT_BALANCE_REQUIRES_REVIEW:'Hay saldos negativos que requieren revisión contable.'};
const decimal=(value:unknown):value is string=>typeof value==='string'&&/^-?\d+\.\d{2,4}$/.test(value);
async function payload(response:Response){
 const raw=await response.json().catch(()=>null);
 if(!response.ok){
  if(response.status===401)throw Error('Tu sesión venció. Inicia sesión nuevamente.');
  if(response.status===403)throw Error('No tienes acceso a esta empresa o su vínculo contable dejó de estar vigente.');
  if(response.status===400)throw Error('Revisa las fechas, la clasificación de cuentas y los saldos pendientes de conciliación.');
  throw Error('No se pudo consultar el libro mayor. Inténtalo nuevamente.');
 }
 return raw?.success===true?raw.data:raw;
}
export function LedgerIndicators({providerId,identity,request,revisionSignal=0}:{providerId:string;identity:string|null;request:Requester;revisionSignal?:number}){
 const today=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Bogota',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
 const [start,setStart]=useState(today.slice(0,8)+'01');const [end,setEnd]=useState(today);
 const [policyRevision,setPolicyRevision]=useState('');
 const [nonce,setNonce]=useState(0);const [busy,setBusy]=useState(false);const [error,setError]=useState('');
 const [result,setResult]=useState<{key:string;profit:Profit;liquidity:Liquidity}|null>(null);
 const requester=useRef(request);requester.current=request;
 const key=JSON.stringify([identity,providerId,start,end,revisionSignal,policyRevision]);
 useEffect(()=>{
  const controller=new AbortController();setResult(null);setError('');setBusy(false);
  if(!identity||!providerId)return ()=>controller.abort();
  if(!/^\d{4}-\d{2}-\d{2}$/.test(start)||!/^\d{4}-\d{2}-\d{2}$/.test(end)||start>end){setError('Selecciona un intervalo de fechas válido.');return ()=>controller.abort();}
  if(policyRevision&&!/^[1-9][0-9]{0,8}$/.test(policyRevision)){setError('La revisión debe ser un entero positivo o dejarse vacía.');return ()=>controller.abort();}
  setBusy(true);
  const query=new URLSearchParams({provider_id:providerId,desde:start,hasta:end});
  const cutoff=new URLSearchParams({provider_id:providerId,fecha_corte:end});
  if(policyRevision)cutoff.set('revision',policyRevision);
  Promise.all([requester.current(API+'rentabilidad/?'+query,{signal:controller.signal}).then(payload),requester.current(API+'liquidez-acida/?'+cutoff,{signal:controller.signal}).then(payload)])
   .then(([profit,liquidity])=>{
    if(controller.signal.aborted)return;
    if(!profit||!liquidity||profit.tenant_id!==liquidity.tenant_id||profit.currency!==liquidity.currency||typeof profit.tenant_id!=='string'||!profit.tenant_id||!/^([A-Z]{3})$/.test(profit.currency)||profit.start_date!==start||profit.end_date!==end||liquidity.cutoff_date!==end||(policyRevision&&liquidity.policy?.revision!==Number(policyRevision))||
      ![profit.revenue,profit.expenses,profit.net_profit].every(decimal)||!profit.net_margin||!(profit.net_margin.value===null||decimal(profit.net_margin.value))||!(liquidity.value===null||decimal(liquidity.value))||!Array.isArray(profit.sources)||
      !profit.sources.every((row:Profit['sources'][number])=>row&&typeof row.code==='string'&&typeof row.type==='string'&&typeof row.account_id==='string'&&decimal(row.net_amount)))throw Error('La respuesta contable está incompleta o no coincide con el periodo solicitado.');
    setResult({key,profit,liquidity});
   }).catch(e=>{if(!controller.signal.aborted)setError(e instanceof Error?e.message:'No se pudo consultar el libro mayor.');})
   .finally(()=>{if(!controller.signal.aborted)setBusy(false);});
  return ()=>controller.abort();
 },[key,nonce]);
 const visible=result?.key===key?result:null;
 return <section aria-label="Indicadores del libro mayor" style={{background:'#0E1B38',color:'#FFFFFF',border:'1px solid #60A5FA',borderRadius:12,padding:20,margin:'20px 0',overflowWrap:'anywhere'}}>
  <style>{`.ledger-indicators input,.ledger-indicators button{background:#142850;color:#fff;border:1px solid #60a5fa;border-radius:6px;padding:10px;max-width:100%;box-sizing:border-box}.ledger-indicators :focus-visible{outline:3px solid #7dd3fc;outline-offset:3px}.ledger-indicators button:disabled{opacity:.6}.ledger-indicators td,.ledger-indicators th{text-align:left;padding:8px;border-bottom:1px solid #60a5fa}`}</style>
  <div className="ledger-indicators">
  <h2>Indicadores del libro mayor</h2><p>Importes contabilizados en moneda base. La liquidez usa la revisión indicada o, si no se indica, la más reciente; no acredita fondos disponibles ni autoriza pagos.</p>
  <form onSubmit={e=>{e.preventDefault();setNonce(n=>n+1);}} style={{display:'flex',flexWrap:'wrap',gap:16,alignItems:'end'}}>
   <label>Desde<br/><input aria-label="Desde" type="date" value={start} onChange={e=>setStart(e.target.value)} required/></label>
   <label>Hasta / corte de liquidez<br/><input aria-label="Hasta" type="date" value={end} onChange={e=>setEnd(e.target.value)} required/></label>
   <label>Revisión de liquidez (opcional)<br/><input aria-label="Revisión de liquidez" inputMode="numeric" maxLength={9} value={policyRevision} onChange={e=>setPolicyRevision(e.target.value)} placeholder="Más reciente"/></label>
   <button disabled={busy||!providerId||!identity} type="submit">Consultar nuevamente</button>
  </form>
  {!identity?<p role="status">Inicia sesión en el ERP.</p>:!providerId?<p role="status">Selecciona una empresa autorizada.</p>:null}
  {busy&&<p role="status">Consultando asientos contabilizados…</p>}{error&&<p role="alert">{error}</p>}
  {visible&&<div aria-live="polite">
   <p>Moneda: <strong>{visible.profit.currency}</strong> · Periodo: {visible.profit.start_date} a {visible.profit.end_date}</p>
   <dl style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:16}}>
    <div><dt>Ingresos</dt><dd>{visible.profit.revenue}</dd></div><div><dt>Gastos</dt><dd>{visible.profit.expenses}</dd></div><div><dt>Resultado neto empresarial</dt><dd>{visible.profit.net_profit}</dd></div>
    <div><dt>Margen neto</dt><dd>{visible.profit.net_margin.value===null?(reasons[visible.profit.net_margin.unavailable_reason||'']||'No calculable; requiere revisión.'):visible.profit.net_margin.value+' %'}</dd></div>
    <div><dt>Liquidez ácida</dt><dd>{visible.liquidity.value===null?(reasons[visible.liquidity.unavailable_reason||'']||'No calculable; requiere revisión.'):visible.liquidity.value+' veces'}</dd></div>
   </dl>
   {visible.liquidity.policy&&<p>Clasificación de liquidez: revisión {visible.liquidity.policy.revision}, declarada por el revisor; requiere validación contable.</p>}
   <details><summary>Cuentas de origen del resultado</summary><div style={{overflowX:'auto'}}><table><caption>Movimientos netos del periodo en {visible.profit.currency}</caption><thead><tr><th scope="col">Cuenta</th><th scope="col">Tipo</th><th scope="col">Importe neto</th></tr></thead><tbody>{visible.profit.sources.map(row=><tr key={row.account_id}><td>{row.code}</td><td>{row.type}</td><td>{row.net_amount}</td></tr>)}</tbody></table></div>{visible.profit.sources.length===0&&<p>No hay movimientos de ingresos o gastos contabilizados en este periodo.</p>}</details>
   <p>Consulta recalculada con los asientos contabilizados actuales hasta el corte económico; no reproduce el informe publicado originalmente en esa fecha.</p>
   <p>RevPAR, GOPPAR y margen por paquete requieren datos operativos y clasificación específica.</p>
  </div>}
  </div>
 </section>;
}
