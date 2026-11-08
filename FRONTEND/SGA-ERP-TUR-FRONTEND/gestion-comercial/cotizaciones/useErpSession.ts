'use client';
import {useEffect,useRef,useState} from 'react';
type User={id:number;username:string};
type Challenge={id:string;digits:number;recoveryAvailable:boolean;recoveryDigits:number};
export type SecurityEvent={id:string;kind:'recovery_issued'|'recovery_rotated'|'recovery_used'|'password_reset';occurred_at:string};
export type Enrollment={id:string;secret:string;digits:number;expires_at:string};
type State={password_reset_available:boolean;recovery_issuance_allowed:boolean;recovery_available:boolean;recovery_digits:number;totp_enrollment_allowed:boolean;mfa_enabled:boolean;authenticated:boolean;user:User|null;csrf_token:string;mfa_required:boolean;challenge_id:string|null;mfa_digits:number};
const SESSION='/api/v1/erp-session/';
async function readPayload(response:Response){
 const body=await response.json().catch(()=>null);
 if(!response.ok){
  if(response.status===503)throw new Error('El acceso web ERP no está habilitado en este entorno.');
  if(response.status===429){const seconds=Number(response.headers.get('Retry-After')||60);const minutes=Math.max(1,Math.ceil((Number.isFinite(seconds)?seconds:60)/60));throw new Error(`Demasiados intentos. Espera ${minutes} minuto(s) antes de continuar.`);}
  const detail=body?.errors?.[0]?.message||body?.detail;
  if(typeof detail==='string'&&detail.includes('CSRF'))throw new Error('No se pudo validar la seguridad de la sesión. Recarga la página e inténtalo de nuevo.');
  throw new Error(typeof detail==='string'?detail:'No se pudo validar la sesión.');
 }
 return body?.success===true?body.data:body;
}
async function readState(response:Response):Promise<State>{
 const state=await readPayload(response);
 if(!state||typeof state.authenticated!=='boolean'||typeof state.csrf_token!=='string'||(state.authenticated&&(!state.user||!Number.isInteger(state.user.id))))throw new Error('Respuesta de sesión incompleta.');
 if(state.mfa_required&&(typeof state.challenge_id!=='string'||![6,8].includes(state.mfa_digits)))throw new Error('La verificación requiere revisar su configuración.');
 return state;
}
export function useErpSession(){
 const [issuanceAllowed,setIssuanceAllowed]=useState(false);
 const [resetAvailable,setResetAvailable]=useState(false);
 const [user,setUser]=useState<User|null>(null);
 const [enrollment,setEnrollment]=useState<Enrollment|null>(null);
 const [enrollmentAllowed,setEnrollmentAllowed]=useState(false);
 const [mfaEnabled,setMfaEnabled]=useState(false);
 const [cancelUnconfirmed,setCancelUnconfirmed]=useState(false);
 const [challenge,setChallenge]=useState<Challenge|null>(null);
 const [loading,setLoading]=useState(true);
 const [error,setError]=useState('');
 const [logoutUnconfirmed,setLogoutUnconfirmed]=useState(false);
 const csrf=useRef('');const epoch=useRef(0);
 function apply(state:State){setResetAvailable(Boolean(state.password_reset_available));setIssuanceAllowed(Boolean(state.authenticated&&state.recovery_issuance_allowed));csrf.current=state.csrf_token;setUser(state.authenticated?state.user:null);setEnrollmentAllowed(Boolean(state.authenticated&&state.totp_enrollment_allowed));setMfaEnabled(Boolean(state.authenticated&&state.mfa_enabled));if(!state.authenticated)setEnrollment(null);setChallenge(state.mfa_required&&state.challenge_id?{id:state.challenge_id,digits:state.mfa_digits,recoveryAvailable:state.recovery_available===true,recoveryDigits:state.recovery_digits}:null);}
 async function status(signal?:AbortSignal){return readState(await fetch(SESSION,{cache:'no-store',credentials:'same-origin',mode:'same-origin',redirect:'error',signal}));}
 useEffect(()=>{
  const controller=new AbortController();const generation=++epoch.current;
  status(controller.signal).then(state=>{if(!controller.signal.aborted&&epoch.current===generation)apply(state);}).catch(e=>{if(!controller.signal.aborted)setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
  return ()=>{controller.abort();epoch.current++;};
 },[]);
 useEffect(()=>{
  const hide=()=>{if(document.hidden)setEnrollment(current=>current?{...current,secret:''}:null);};
  document.addEventListener('visibilitychange',hide);
  const timer=setInterval(()=>{setEnrollment(current=>{if(current&&Date.parse(current.expires_at)<=Date.now())return null;return current;});},1000);
  return ()=>{document.removeEventListener('visibilitychange',hide);clearInterval(timer);};
 },[]);
 async function login(username:string,password:string){
  const generation=++epoch.current;setLoading(true);setError('');
  try{
   const initial=await status();
   const result=await readState(await fetch(SESSION+'login/',{method:'POST',credentials:'same-origin',mode:'same-origin',redirect:'error',headers:{'Content-Type':'application/json','X-CSRFToken':initial.csrf_token},body:JSON.stringify({username,password})}));
   if(epoch.current===generation)apply(result);
  }catch(e){if(epoch.current===generation)setError(e instanceof Error?e.message:'No se pudo iniciar sesión.');throw e;}finally{if(epoch.current===generation)setLoading(false);}
 }
 async function verifyCode(code:string,recovery=false){
  if(!challenge)throw new Error('Reinicia el acceso para solicitar otra verificación.');
  const generation=++epoch.current;setLoading(true);setError('');
  try{
   const result=await readState(await fetch(SESSION+(recovery?'recovery/':'mfa/'),{method:'POST',credentials:'same-origin',mode:'same-origin',redirect:'error',headers:{'Content-Type':'application/json','X-CSRFToken':csrf.current},body:JSON.stringify({challenge_id:challenge.id,code})}));
   if(epoch.current===generation)apply(result);
  }catch(e){
   const current=await status().catch(()=>null);
   if(epoch.current===generation){if(current)apply(current);setError(e instanceof Error?e.message:'No se pudo completar la verificación.');}
   throw e;
  }finally{if(epoch.current===generation)setLoading(false);}
 }
 async function logout(){
  const generation=++epoch.current;setUser(null);setChallenge(null);setEnrollment(null);setLoading(true);setError('');
  try{
   const result=await readState(await fetch(SESSION+'logout/',{method:'POST',credentials:'same-origin',mode:'same-origin',redirect:'error',headers:{'Content-Type':'application/json','X-CSRFToken':csrf.current},body:'{}'}));
   if(epoch.current===generation){apply(result);setLogoutUnconfirmed(false);}
  }catch(e){if(epoch.current===generation){setLogoutUnconfirmed(true);setError('No se pudo confirmar el cierre en el servidor. Vuelve a intentarlo antes de dejar el equipo.');}}finally{if(epoch.current===generation)setLoading(false);}
 }
 async function request(path:string,init:RequestInit={}){
  if(!path.startsWith('/api/'))throw new Error('Destino fuera del servicio ERP.');
  const generation=epoch.current;
  const headers=new Headers(init.headers);headers.set('Content-Type','application/json');
  if(!['GET','HEAD','OPTIONS'].includes((init.method||'GET').toUpperCase()))headers.set('X-CSRFToken',csrf.current);
  const response=await fetch(path,{...init,headers,cache:'no-store',credentials:'same-origin',mode:'same-origin',redirect:'error'});
  if(response.status===401||response.status===403){
   const current=await status(init.signal||undefined).catch(()=>null);
   if(epoch.current===generation&&current)apply(current);
  }
  return response;
 }
 async function startEnrollment(password:string){
  const generation=epoch.current;setLoading(true);setError('');setCancelUnconfirmed(false);
  try{
   const value=await readPayload(await request(SESSION+'enrollment/start/',{method:'POST',body:JSON.stringify({password})}));
   if(!value||typeof value.id!=='string'||typeof value.secret!=='string'||![6,8].includes(value.digits)||!Number.isFinite(Date.parse(value.expires_at))||Date.parse(value.expires_at)<=Date.now())throw new Error('La configuración venció o está incompleta. Reinicia el proceso.');
   if(epoch.current===generation)setEnrollment(value);
  }catch(e){if(epoch.current===generation)setError(e instanceof Error?e.message:'No se pudo preparar la verificación.');throw e;}finally{if(epoch.current===generation)setLoading(false);}
 }
 async function confirmEnrollment(code:string){
  if(!enrollment)throw new Error('Inicia una configuración nueva.');
  const generation=epoch.current;setLoading(true);setError('');
  try{
   const value=await readState(await request(SESSION+'enrollment/confirm/',{method:'POST',body:JSON.stringify({id:enrollment.id,code})}));
   if(epoch.current===generation){apply(value);setEnrollment(null);setCancelUnconfirmed(false);}
  }catch(e){if(epoch.current===generation)setError(e instanceof Error?e.message:'No se pudo activar la verificación.');throw e;}finally{if(epoch.current===generation)setLoading(false);}
 }
 async function cancelEnrollment(){
  if(!enrollment)return;
  const generation=epoch.current;setLoading(true);setError('');setEnrollment(current=>current?{...current,secret:''}:null);
  try{
   await readPayload(await request(SESSION+'enrollment/cancel/',{method:'POST',body:JSON.stringify({id:enrollment.id})}));
   if(epoch.current===generation){setEnrollment(null);setCancelUnconfirmed(false);}
  }catch(e){if(epoch.current===generation){setCancelUnconfirmed(true);setError('No se pudo confirmar la cancelación. Reinténtala antes de continuar.');}}finally{if(epoch.current===generation)setLoading(false);}
 }
 async function issueRecovery(password:string,code:string):Promise<string[]>{
  const generation=epoch.current;setLoading(true);setError('');
  try{
   const value=await readPayload(await request(SESSION+'recovery/issue/',{method:'POST',body:JSON.stringify({password,code})}));
   if(!value?.session||!Array.isArray(value.codes)||!value.codes.every((item:unknown)=>typeof item==='string'&&/^[0-9]{8,32}$/.test(item)))throw new Error('Respuesta incompleta. No repitas la emisión sin revisar tu acceso.');
   if(epoch.current!==generation)return [];
   apply(value.session);return value.codes;
  }catch(e){if(epoch.current===generation)setError(e instanceof Error?e.message:'No se pudo emitir. Si falló la red, revisa tu acceso antes de reintentar.');throw e;}finally{if(epoch.current===generation)setLoading(false);}
 }
 async function securityEvents():Promise<SecurityEvent[]>{
  const generation=epoch.current;
  const value=await readPayload(await request(SESSION+'security-events/'));
  if(epoch.current!==generation)return [];
  if(!value||!Array.isArray(value.events)||!value.events.every((item:SecurityEvent)=>typeof item.id==='string'&&['recovery_issued','recovery_rotated','recovery_used','password_reset'].includes(item.kind)&&Number.isFinite(Date.parse(item.occurred_at))))throw new Error('No se pudo verificar el historial.');
  return value.events;
 }
 async function passwordRecovery(path:'request'|'confirm',data:Record<string,string>){
  const initial=await status();csrf.current=initial.csrf_token;
  return readPayload(await request(SESSION+'password-reset/'+path+'/',{method:'POST',body:JSON.stringify(data)}));
 }
 return {resetAvailable,passwordRecovery,securityEvents,issuanceAllowed,issueRecovery,user,challenge,verifyCode,loading,error,logoutUnconfirmed,login,logout,request,enrollment,enrollmentAllowed,mfaEnabled,cancelUnconfirmed,startEnrollment,confirmEnrollment,cancelEnrollment};
}
