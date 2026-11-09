'use client';
import React,{useEffect,useRef,useState} from 'react';
type Source={reservation_id:string;gross:string;revision:number;review_id:string|null;request_created:boolean};
type Item={item_id:string;net:string;tax:string;tax_category:string;policy_reference:string};
const empty=():Item=>({item_id:crypto.randomUUID(),net:'',tax:'',tax_category:'',policy_reference:''});
export function ReservationBilling({identity,providerId,request}:{identity:string|null;providerId:string;request:(path:string,init?:RequestInit)=>Promise<Response>}){
 const generation=useRef(0);const context=JSON.stringify([identity,providerId]);const current=useRef(context);current.current=context;const pending=useRef<AbortController|null>(null);
 const [sources,setSources]=useState<{context:string;rows:Source[];currency:string;next:string|null}|null>(null);const [selected,setSelected]=useState('');
 const [items,setItems]=useState<Item[]>([]);const [evidence,setEvidence]=useState('');const [first,setFirst]=useState(false);const [second,setSecond]=useState(false);
 const [review,setReview]=useState<{id:string;revision:number;form:string}|null>(null);const [busy,setBusy]=useState(false);const [message,setMessage]=useState('');const [done,setDone]=useState(false);
 const form=JSON.stringify([context,selected,items,evidence]);const liveForm=useRef(form);liveForm.current=form;
 useEffect(()=>{generation.current++;pending.current?.abort();setSources(null);setSelected('');setItems([]);setEvidence('');setFirst(false);setSecond(false);setReview(null);setBusy(false);setMessage('');setDone(false);return ()=>pending.current?.abort();},[context]);
 useEffect(()=>{setFirst(false);setSecond(false);setReview(null);setDone(false);setMessage('');},[form]);
 const visible=sources?.context===context?sources:null;const source=visible?.rows.find(r=>r.reservation_id===selected);
 async function call(action:string,body?:unknown,after?:string){const controller=new AbortController();pending.current?.abort();pending.current=controller;
  const params=new URLSearchParams({provider_id:providerId});if(after)params.set('despues_id',after);
  const response=await request('/api/v1/mi-negocio/contable/contabilidad/cuentas/'+action+'/?'+params.toString(),{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:undefined,body:body?JSON.stringify(body):undefined,signal:controller.signal});
  const raw=await response.json();if(!response.ok)throw Error('No se pudo confirmar. Recarga las reservas y revisa el estado, el total y la revisión vigente.');
  if(controller.signal.aborted||current.current!==context)throw new DOMException('Contexto cambiado.','AbortError');return raw?.success===true?raw.data:raw;
 }
 async function load(after?:string){const task=++generation.current;setBusy(true);setMessage('');setReview(null);setSecond(false);setSelected('');setItems([]);
  try{const d=await call('fuentes-reserva-fiscal',undefined,after);
   if(d.read_only!==true||typeof d.currency!=='string'||!/^[A-Z]{3}$/.test(d.currency)||!Array.isArray(d.sources)||d.sources.length>20||!d.sources.every((r:any)=>typeof r.reservation_id==='string'&&typeof r.gross==='string'&&/^[0-9]{1,16}\.[0-9]{2}$/.test(r.gross)&&Number.isSafeInteger(r.revision)&&r.revision>=0&&typeof r.request_created==='boolean'))throw Error('Respuesta de reservas incompleta.');
   if(current.current===context&&generation.current===task)setSources({context,rows:d.sources,currency:d.currency,next:d.next_after});
  }catch(e){if(current.current===context&&generation.current===task)setMessage(e instanceof Error?e.message:'Consulta no disponible.');}finally{if(current.current===context&&generation.current===task)setBusy(false);}
 }
 async function approve(){if(!source)return;const task=++generation.current;const submitted=form;setBusy(true);setMessage('');
  try{const d=await call('revisar-reserva-fiscal',{reservation_id:selected,items,evidence_digest:evidence,confirmed:first,expected_revision:source.revision});
   if(typeof d.review_id!=='string'||d.revision!==source.revision+1||d.fiscal_accepted!==false||d.ledger_written!==false)throw Error('Revisión incompleta.');
   if(current.current===context&&generation.current===task&&liveForm.current===submitted){setReview({id:d.review_id,revision:d.revision,form:submitted});setSources(old=>old?{...old,rows:old.rows.map(r=>r.reservation_id===selected?{...r,revision:d.revision,review_id:d.review_id}:r)}:old);setMessage('Revisión guardada. Falta la segunda confirmación para crear la solicitud.');}
  }catch(e){if(current.current===context&&generation.current===task)setMessage(e instanceof Error?e.message:'Revisión no disponible.');}finally{if(current.current===context&&generation.current===task)setBusy(false);}
 }
 async function submit(){if(!review||review.form!==form)return;const task=++generation.current;const submitted=form;setBusy(true);setMessage('');
  try{const d=await call('solicitar-factura-reserva',{reservation_id:selected,review_id:review.id,confirmed:second});
   if(d.request_persisted!==true||d.source_authority_verified!==true||d.fiscal_accepted!==false||d.ledger_written!==false)throw Error('Solicitud no confirmada.');
   if(current.current===context&&generation.current===task&&liveForm.current===submitted){setDone(true);setMessage('Solicitud registrada. Aún no es una factura emitida ni aceptada por DIAN.');setSources(old=>old?{...old,rows:old.rows.map(r=>r.reservation_id===selected?{...r,request_created:true}:r)}:old);}
  }catch(e){if(current.current===context&&generation.current===task)setMessage(e instanceof Error?e.message:'Solicitud no disponible.');}finally{if(current.current===context&&generation.current===task)setBusy(false);}
 }
 if(!identity||!providerId)return null;
 const style={background:'#142850',color:'#FFFFFF',border:'1px solid #60A5FA',padding:8,borderRadius:6,maxWidth:'100%'};
 const edit=(index:number,key:keyof Item,value:string)=>setItems(old=>old.map((r,i)=>i===index?{...r,[key]:value}:r));
 return <section aria-label="Facturación de reservas" style={{background:'#0E1B38',color:'#FFFFFF',padding:16,border:'1px solid #60A5FA',borderRadius:8,marginTop:16}}>
 <h2>Facturación de reservas</h2><p>Revisa el desglose de una reserva confirmada y después autoriza su solicitud. El tratamiento tributario declarado requiere revisión contable; este paso no emite una factura.</p>
 <button type="button" style={style} disabled={busy} onClick={()=>load()}>Cargar reservas confirmadas</button>
 {visible&&<><label>Reserva para facturación <select aria-label="Reserva para facturación" style={{...style,width:'100%'}} disabled={busy} value={selected} onChange={e=>{setSelected(e.target.value);setItems([empty()]);setEvidence('');}}><option value="">Seleccionar reserva</option>{visible.rows.map(r=><option key={r.reservation_id} value={r.reservation_id}>{r.reservation_id} · {r.gross} {visible.currency}{r.request_created?' · Solicitud registrada':''}</option>)}</select></label>{visible.rows.length===0&&<p>No hay reservas confirmadas en esta página.</p>}{visible.next&&<button type="button" style={style} disabled={busy} onClick={()=>load(visible.next!)}>Siguientes reservas</button>}</>}
 {source&&<><p>Total de la reserva: {source.gross} {visible?.currency} · Revisión vigente: {source.revision}</p>
 {source.request_created?<p>Esta reserva ya tiene una solicitud; no se creará otra revisión.</p>:<><fieldset disabled={busy||done} style={{border:'1px solid #60A5FA',minWidth:0}}><legend>Desglose revisado</legend>{items.map((r,i)=><div key={r.item_id} style={{display:'flex',flexWrap:'wrap',gap:8,marginBottom:12}}>
 <label>Neto <input aria-label={'Neto '+(i+1)} style={{...style,width:120}} value={r.net} onChange={e=>edit(i,'net',e.target.value)} placeholder="0.00"/></label><label>Impuesto <input aria-label={'Impuesto '+(i+1)} style={{...style,width:120}} value={r.tax} onChange={e=>edit(i,'tax',e.target.value)} placeholder="0.00"/></label>
 <label>Tratamiento <select aria-label={'Tratamiento '+(i+1)} style={style} value={r.tax_category} onChange={e=>edit(i,'tax_category',e.target.value)}><option value="">Seleccionar</option><option value="TAXABLE">Gravado</option><option value="EXEMPT">Exento</option><option value="EXCLUDED">Excluido</option></select></label>
 <label>Referencia de política <input aria-label={'Referencia de política '+(i+1)} style={style} value={r.policy_reference} onChange={e=>edit(i,'policy_reference',e.target.value)}/></label>{items.length>1&&<button type="button" style={style} onClick={()=>setItems(old=>old.filter((_,n)=>n!==i))}>Quitar componente {i+1}</button>}</div>)}
 <button type="button" style={style} disabled={items.length>=100} onClick={()=>setItems(old=>[...old,empty()])}>Añadir componente</button>
 <label>Huella del soporte revisado <input aria-label="Huella del soporte revisado" style={{...style,width:'100%',boxSizing:'border-box'}} value={evidence} onChange={e=>setEvidence(e.target.value)} maxLength={64}/></label>
 <label><input type="checkbox" checked={first} onChange={e=>setFirst(e.target.checked)}/>Confirmo que revisé el total, el desglose y el soporte.</label></fieldset>
 <button type="button" style={style} disabled={busy||!first||done||Boolean(review&&review.form===form)} onClick={approve}>Guardar revisión fiscal</button>
 {review&&review.form===form&&<div><label><input type="checkbox" checked={second} disabled={busy||done} onChange={e=>setSecond(e.target.checked)}/>Autorizo crear la solicitud con esta revisión guardada.</label><button type="button" style={style} disabled={busy||!second||done} onClick={submit}>Crear solicitud de factura</button></div>}</>}
 </>}{message&&<p role="status">{message}</p>}
 </section>;
}
