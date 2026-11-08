'use client';
import React,{useEffect,useState} from 'react';
import type {useErpSession} from './useErpSession';
export function PasswordRecovery({session}:{session:ReturnType<typeof useErpSession>}){
 const [link,setLink]=useState<{uid:string;token:string}|null>(null);const [email,setEmail]=useState('');const [password,setPassword]=useState('');const [confirm,setConfirm]=useState('');const [busy,setBusy]=useState(false);const [message,setMessage]=useState('');const [error,setError]=useState('');
 useEffect(()=>{
  const read=()=>{
   const fragment=new URLSearchParams(window.location.hash.slice(1));const uid=fragment.get('reset_uid'),token=fragment.get('reset_token');
   if(uid||token){
    setLink(null);setMessage('');setError('');
    if(uid&&token&&uid.length<=64&&token.length<=128)setLink({uid,token});else setError('El enlace está incompleto. Solicita uno nuevo.');
    window.history.replaceState(null,'',window.location.pathname+window.location.search);
   }
  };
  read();window.addEventListener('hashchange',read);
  const hide=()=>{if(document.hidden){setPassword('');setConfirm('');}};document.addEventListener('visibilitychange',hide);
  return ()=>{window.removeEventListener('hashchange',read);document.removeEventListener('visibilitychange',hide);};
 },[]);
 useEffect(()=>{if(session.user){setLink(null);setPassword('');setConfirm('');}},[session.user?.id]);
 if(session.user||session.challenge||!session.resetAvailable)return null;
 return <section aria-label="Recuperar contraseña" style={{padding:16,margin:'24px 0',border:'1px solid #60a5fa',borderRadius:12,background:'#0e1b38'}}>
  <h2>Recuperar contraseña</h2><p>Restablecer la contraseña conserva tus factores y códigos de recuperación. No permite saltar la verificación en dos pasos.</p>
  {message&&<p role="status">{message}</p>}{error&&<p role="alert">{error}</p>}
  <form onSubmit={async event=>{event.preventDefault();if(link&&password!==confirm){setError('Las contraseñas no coinciden.');return;}const current=link,secret=password;setPassword('');setConfirm('');setBusy(true);setError('');setMessage('');try{if(current){await session.passwordRecovery('confirm',{uid:current.uid,token:current.token,password:secret});setLink(null);setMessage('Contraseña actualizada. Inicia sesión y completa tu segundo factor.');}else{const result=await session.passwordRecovery('request',{email});setMessage(result.message);setEmail('');}}catch(e){setError(e instanceof Error?e.message:'No se pudo completar la recuperación.');}finally{setBusy(false);}}}>
   {link?<><label>Contraseña nueva <input type="password" autoComplete="new-password" minLength={12} maxLength={1024} required value={password} disabled={busy} onChange={e=>setPassword(e.target.value)}/></label>{' '}<label>Repetir contraseña nueva <input type="password" autoComplete="new-password" minLength={12} maxLength={1024} required value={confirm} disabled={busy} onChange={e=>setConfirm(e.target.value)}/></label></>:<label>Correo verificado <input type="email" autoComplete="email" maxLength={254} required value={email} disabled={busy} onChange={e=>setEmail(e.target.value)}/></label>}{' '}
   <button type="submit" disabled={busy||session.loading}>{link?'Restablecer contraseña':'Solicitar enlace de recuperación'}</button>
  </form>
 </section>;
}
