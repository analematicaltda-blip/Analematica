'use client';
import React,{useEffect,useRef,useState} from 'react';
type Report={model_version:string;input_digest:string;seed:number;paths:number;observation_end:string;results:{days:number;ending_cash_p05:string;ending_cash_p50:string;ending_cash_p95:string;negative_cash_path_fraction:string}[]};
type Evaluation={days:number;actual_ending_cash:string;predicted_ending_cash_p50:string;actual_minus_predicted:string;absolute_terminal_error:string;empirical_interval_contains_actual:boolean};
type Assessment={evaluations:Evaluation[];mean_absolute_terminal_error_across_horizons:string;outcome_digest:string};
type Display={currency:string;reports:{name:string;report:Report}[];assessment?:Assessment};
const amount=(v:unknown):v is string=>typeof v==='string'&&/^-?\d+\.\d{2}$/.test(v);
function valid(report:Report,seed:number,paths:number,lastDate:string){return report&&report.seed===seed&&report.paths===paths&&report.observation_end===lastDate&&typeof report.model_version==='string'&&typeof report.input_digest==='string'&&Array.isArray(report.results)&&report.results.length===3&&report.results.every((row,i)=>row&&row.days===[30,90,365][i]&&[row.ending_cash_p05,row.ending_cash_p50,row.ending_cash_p95].every(amount)&&typeof row.negative_cash_path_fraction==='string'&&/^(?:0\.\d{6}|1\.000000)$/.test(row.negative_cash_path_fraction));}
export function CashScenarios({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const [opening,setOpening]=useState('');const [observations,setObservations]=useState('');const [seed,setSeed]=useState('42');const [paths,setPaths]=useState('500');
 const [actuals,setActuals]=useState('');
 const [mode,setMode]=useState('base');const [openingDelta,setOpeningDelta]=useState('0.00');const [dailyDelta,setDailyDelta]=useState('0.00');
 const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [output,setOutput]=useState<{key:string;data:Display}|null>(null);
 const key=JSON.stringify([identity,providerId,opening,observations,seed,paths,mode,openingDelta,dailyDelta,actuals]);const current=useRef(key);current.current=key;
 const pending=useRef<AbortController|null>(null);
 useEffect(()=>{pending.current?.abort();setOutput(null);setError('');setBusy(false);return ()=>pending.current?.abort();},[key]);
 async function run(){
  if(busy||!identity||!providerId)return;setOutput(null);setError('');
  const snapshot=key;const controller=new AbortController();pending.current=controller;
  try{
   if(!amount(opening)||opening.startsWith('-'))throw Error('Introduce la caja inicial no negativa con dos decimales.');
   if(!/^\d{1,10}$/.test(seed)||Number(seed)>4294967295||!/^\d{3,4}$/.test(paths)||Number(paths)<100||Number(paths)>2000)throw Error('Revisa la semilla y el número de trayectorias (100 a 2000).');
   const lines=observations.trim().split(/\r?\n/);
   if(lines.length<7||lines.length>366)throw Error('Introduce entre 7 y 366 días consecutivos, incluidos los días de flujo cero.');
   const rows=lines.map(line=>{const parts=line.split(';');if(parts.length!==2||!/^\d{4}-\d{2}-\d{2}$/.test(parts[0].trim())||!amount(parts[1].trim()))throw Error('Usa una línea por día: AAAA-MM-DD;importe con dos decimales.');return {date:parts[0].trim(),net_cash_flow:parts[1].trim()};});
   const scenario={opening_cash:opening,observations:rows,seed:Number(seed),paths:Number(paths)};
   if(mode==='sensitivity'&&(!amount(openingDelta)||!amount(dailyDelta)))throw Error('Los cambios declarados requieren dos decimales.');
   let heldOut:{date:string;net_cash_flow:string}[]=[];
   if(mode==='backtest'){
    const lines=actuals.trim().split(/\r?\n/);
    if(lines.length!==365)throw Error('Introduce exactamente 365 resultados diarios posteriores al entrenamiento.');
    heldOut=lines.map(line=>{const parts=line.split(';');if(parts.length!==2||!/^\d{4}-\d{2}-\d{2}$/.test(parts[0].trim())||!amount(parts[1].trim()))throw Error('Resultados posteriores inválidos: usa AAAA-MM-DD;importe con dos decimales.');return {date:parts[0].trim(),net_cash_flow:parts[1].trim()};});
   }
   setBusy(true);
   const response=await request('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+(mode==='base'?'simulacion-caja':mode==='backtest'?'backtest-caja':'sensibilidad-caja')+'/?'+new URLSearchParams({provider_id:providerId}),{method:'POST',signal:AbortSignal.any([controller.signal,AbortSignal.timeout(20000)]),body:JSON.stringify(mode==='base'?scenario:mode==='backtest'?{scenario,actuals:heldOut}:{scenario,shocks:[{name:'Cambio declarado',opening_cash_delta:openingDelta,daily_net_flow_delta:dailyDelta}]})});
   const raw=await response.json().catch(()=>null);if(!response.ok)throw Error(response.status===403?'No tienes acceso a esta empresa.':'No se pudo simular. Revisa continuidad de fechas, importes y permisos.');
   const body=raw?.success===true?raw.data:raw;
   const reports:{name:string;report:Report}[]=mode==='base'?[{name:'Base',report:body}]:mode==='backtest'?[{name:'Entrenamiento',report:body?.forecast}]:[{name:'Base',report:body?.base},...(Array.isArray(body?.variants)?body.variants.map((v:{name:string;simulation:Report})=>({name:v.name,report:v.simulation})):[])];
   if(!body||body.ledger_written!==false||body.financial_execution!==false||typeof body.currency!=='string'||!/^[A-Z]{3}$/.test(body.currency)||reports.length!==(mode==='sensitivity'?2:1)||!reports.every(r=>typeof r.name==='string'&&valid(r.report,Number(seed),Number(paths),rows[rows.length-1].date)))throw Error('Respuesta de simulación incompleta o inconsistente.');
   let assessment:Assessment|undefined;
   if(mode==='backtest'){
    if(body.holdout_count!==365||body.holdout_start!==heldOut[0].date||body.holdout_end!==heldOut[364].date||!amount(body.mean_absolute_terminal_error_across_horizons)||typeof body.outcome_digest!=='string'||!Array.isArray(body.evaluations)||body.evaluations.length!==3||!body.evaluations.every((r:Evaluation,i:number)=>r&&r.days===[30,90,365][i]&&[r.actual_ending_cash,r.predicted_ending_cash_p50,r.actual_minus_predicted,r.absolute_terminal_error].every(amount)&&typeof r.empirical_interval_contains_actual==='boolean'))throw Error('Evaluación temporal incompleta o inconsistente.');
    assessment={evaluations:body.evaluations,mean_absolute_terminal_error_across_horizons:body.mean_absolute_terminal_error_across_horizons,outcome_digest:body.outcome_digest};
   }
   if(!controller.signal.aborted&&current.current===snapshot)setOutput({key:snapshot,data:{currency:body.currency,reports,assessment}});
  }catch(e){if(!controller.signal.aborted&&current.current===snapshot)setError(e instanceof Error?e.message:'No se pudo generar el escenario.');}
  finally{if(current.current===snapshot)setBusy(false);}
 }
 const visible=output?.key===key?output.data:null;
 if(!identity||!providerId)return null;
 return <section aria-label="Escenarios de caja" className="cash-scenarios" style={{background:'#0E1B38',color:'#FFFFFF',padding:20,border:'1px solid #60A5FA',borderRadius:12,marginTop:20}}>
 <h2>Escenarios de caja</h2><p>Usa datos declarados por ti. No son saldos bancarios verificados, recomendaciones ni autorizaciones de pago. El modelo no incorpora automáticamente temporadas, impuestos o tipo de cambio.</p>
 <form onSubmit={e=>{e.preventDefault();run();}}>
 <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(min(100%,220px),1fr))',gap:16}}>
 <label>Caja inicial<input aria-label="Caja inicial" inputMode="decimal" maxLength={32} value={opening} onChange={e=>setOpening(e.target.value)} required/></label>
 <label>Semilla reproducible<input aria-label="Semilla reproducible" inputMode="numeric" maxLength={10} value={seed} onChange={e=>setSeed(e.target.value)} required/></label>
 <label>Trayectorias<input aria-label="Trayectorias" inputMode="numeric" maxLength={4} value={paths} onChange={e=>setPaths(e.target.value)} required/></label>
 <label>Comparación<select aria-label="Comparación" value={mode} onChange={e=>setMode(e.target.value)}><option value="base">Solo base</option><option value="sensitivity">Base y cambio declarado</option><option value="backtest">Evaluar resultados posteriores</option></select></label>
 </div>
 <label>Flujos diarios declarados<textarea aria-label="Flujos diarios declarados" rows={8} maxLength={24000} value={observations} onChange={e=>setObservations(e.target.value)} placeholder="AAAA-MM-DD;importe (una línea por día, incluidos ceros)" required/></label>
 {mode==='backtest'&&<label>Resultados posteriores (365 días)<textarea aria-label="Resultados posteriores" rows={8} maxLength={24000} value={actuals} onChange={e=>setActuals(e.target.value)} placeholder="AAAA-MM-DD;importe (365 días inmediatamente posteriores al entrenamiento)" required/></label>}
 {mode==='sensitivity'&&<div><label>Cambio en caja inicial<input aria-label="Cambio en caja inicial" inputMode="decimal" maxLength={32} value={openingDelta} onChange={e=>setOpeningDelta(e.target.value)}/></label><label>Cambio diario neto<input aria-label="Cambio diario neto" inputMode="decimal" maxLength={32} value={dailyDelta} onChange={e=>setDailyDelta(e.target.value)}/></label></div>}
 <button disabled={busy} type="submit">{busy?'Simulando…':'Generar escenarios'}</button>
 </form>
 {error&&<p role="alert">{error}</p>}
 {visible&&<div aria-live="polite"><p>Escenarios en {visible.currency}. Percentiles empíricos, no intervalos de confianza calibrados. La fracción de déficit describe las trayectorias simuladas.</p>
 {visible.reports.map(({name,report})=><div key={name}><h3>Escenario: {name}</h3><div style={{overflowX:'auto'}}><table><caption>Caja final simulada · {name} · {visible.currency}</caption><thead><tr><th>Días</th><th>p05</th><th>Mediana p50</th><th>p95</th><th>Fracción con déficit</th></tr></thead><tbody>{report.results.map(row=><tr key={row.days}><td>{row.days}</td><td>{row.ending_cash_p05}</td><td>{row.ending_cash_p50}</td><td>{row.ending_cash_p95}</td><td>{row.negative_cash_path_fraction}</td></tr>)}</tbody></table></div><details><summary>Trazabilidad de supuestos · {name}</summary><p>Modelo: {report.model_version}; semilla: {report.seed}; trayectorias: {report.paths}; último día declarado: {report.observation_end}.</p><p style={{overflowWrap:'anywhere'}}>Digest de entrada: {report.input_digest}</p></details></div>)}
 {visible.assessment&&<div><h3>Evaluación temporal</h3><p>Un solo periodo posterior declarado, con horizontes correlacionados. No certifica precisión ni cobertura estadística.</p><p>Error absoluto medio entre horizontes: {visible.assessment.mean_absolute_terminal_error_across_horizons} {visible.currency}</p><div style={{overflowX:'auto'}}><table><caption>Errores fuera del entrenamiento</caption><thead><tr><th>Días</th><th>Caja posterior</th><th>Mediana simulada</th><th>Posterior menos simulada</th><th>Error absoluto</th><th>Dentro de p05–p95</th></tr></thead><tbody>{visible.assessment.evaluations.map(row=><tr key={row.days}><td>{row.days}</td><td>{row.actual_ending_cash}</td><td>{row.predicted_ending_cash_p50}</td><td>{row.actual_minus_predicted}</td><td>{row.absolute_terminal_error}</td><td>{row.empirical_interval_contains_actual?'Sí':'No'}</td></tr>)}</tbody></table></div><details><summary>Trazabilidad de resultados posteriores</summary><p style={{overflowWrap:'anywhere'}}>Digest de resultados declarados: {visible.assessment.outcome_digest}</p></details></div>}
 </div>}
 <style>{`.cash-scenarios input,.cash-scenarios select,.cash-scenarios textarea{display:block;width:100%;box-sizing:border-box;background:#142850;color:#fff;border:1px solid #60a5fa;padding:10px;margin:6px 0}.cash-scenarios button{background:#142850;color:#fff;border:1px solid #60a5fa;padding:10px;border-radius:6px}.cash-scenarios :focus-visible{outline:3px solid #7dd3fc;outline-offset:2px}.cash-scenarios td,.cash-scenarios th{text-align:left;padding:8px;border-bottom:1px solid #60a5fa}`}</style>
 </section>;
}
