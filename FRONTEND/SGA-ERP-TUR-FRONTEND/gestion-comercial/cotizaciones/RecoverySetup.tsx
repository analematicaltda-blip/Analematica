'use client';
import React,{useEffect,useState} from 'react';
import type {useErpSession} from './useErpSession';
export function RecoverySetup({session}:{session:ReturnType<typeof useErpSession>}){
 const [password,setPassword]=useState('');const [code,setCode]=useState('');const [codes,setCodes]=useState<string[]>([]);
 useEffect(()=>{setCodes([]);setPassword('');setCode('');},[session.user?.id]);
 useEffect(()=>{const hide=()=>{if(document.hidden){setCodes([]);setPassword('');setCode('');}};document.addEventListener('visibilitychange',hide);return ()=>document.removeEventListener('visibilitychange',hide);},[]);
 useEffect(()=>{if(!codes.length)return;const timer=setTimeout(()=>setCodes([]),60000);return ()=>clearTimeout(timer);},[codes]);
 if(!session.user||!session.issuanceAllowed)return null;
 return <section aria-label="Códigos de recuperación" style={{padding:16,border:'1px solid #60a5fa',borderRadius:12,margin:'24px 0',background:'#0e1b38'}}>
  <h2>Códigos de recuperación</h2>
  <p>Guárdalos fuera de este dispositivo, en un lugar privado. Cada código sirve una sola vez junto con tu contraseña. Emitir un conjunto nuevo invalida todos los anteriores.</p>
  {codes.length?<><p>Se muestran una sola vez y se ocultarán en un minuto o al salir de esta pestaña.</p><ul aria-label="Códigos recién emitidos">{codes.map((item,index)=><li key={index}><code>{item}</code></li>)}</ul><button type="button" onClick={()=>setCodes([])}>Ya los guardé; ocultar códigos</button></>:<form onSubmit={async event=>{event.preventDefault();if(!window.confirm('Se invalidarán todos los códigos anteriores. ¿Emitir un conjunto nuevo?'))return;const pass=password,proof=code;setPassword('');setCode('');try{const value=await session.issueRecovery(pass,proof);if(!document.hidden)setCodes(value);}catch{ /* Session hook presents error; codes cannot be retrieved again. */ }}}>
   <p>Si falla la conexión después de confirmar, la emisión puede haberse completado. Los códigos anteriores podrían quedar invalidados; vuelve a autenticarte con TOTP antes de generar otro conjunto.</p>
   <p>Espera al siguiente código de tu autenticador si acabas de iniciar sesión. El código utilizado para entrar no puede reutilizarse aquí.</p>
   <label>Contraseña para emitir códigos <input type="password" autoComplete="current-password" required maxLength={1024} value={password} disabled={session.loading} onChange={event=>setPassword(event.target.value)}/></label>{' '}
   <label>Código TOTP nuevo <input type="text" inputMode="numeric" autoComplete="one-time-code" required pattern="[0-9]{6}|[0-9]{8}" maxLength={8} value={code} disabled={session.loading} onChange={event=>setCode(event.target.value.replace(/[^0-9]/g,''))}/></label>{' '}
   <button type="submit" disabled={session.loading}>Emitir nuevos códigos</button>
  </form>}
 </section>;
}
