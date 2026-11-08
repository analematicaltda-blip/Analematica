'use client';
import React,{useEffect,useState} from 'react';
import type {useErpSession} from './useErpSession';

export function TotpSetup({session}:{session:ReturnType<typeof useErpSession>}){
 const [password,setPassword]=useState('');const [code,setCode]=useState('');const [show,setShow]=useState(false);
 useEffect(()=>{setPassword('');setCode('');setShow(false);},[session.enrollment?.id,session.user?.id]);
 useEffect(()=>{const hide=()=>{if(document.hidden){setPassword('');setCode('');setShow(false);}};document.addEventListener('visibilitychange',hide);return ()=>document.removeEventListener('visibilitychange',hide);},[]);
 if(!session.user)return null;
 if(session.mfaEnabled)return <section aria-label="Seguridad del acceso"><h2>Seguridad del acceso</h2><p role="status">Verificación en dos pasos activa.</p></section>;
 if(!session.enrollmentAllowed)return null;
 const pending=session.enrollment;
 return <section aria-label="Activar verificación en dos pasos" style={{padding:16,margin:'24px 0',border:'1px solid #60a5fa',borderRadius:12,background:'#0e1b38'}}>
  <h2>Activar verificación en dos pasos</h2>
  {!pending?<form onSubmit={async event=>{event.preventDefault();const secret=password;setPassword('');try{await session.startEnrollment(secret);}catch{ /* Safe message is shown by the session hook. */ }}}>
   <p>Añade un código de tu aplicación de autenticación para proteger los próximos accesos. Confirma tu contraseña para comenzar.</p>
   <label>Confirmar contraseña <input aria-label="Confirmar contraseña" type="password" required autoComplete="current-password" maxLength={1024} value={password} disabled={session.loading} onChange={event=>setPassword(event.target.value)}/></label>{' '}
   <button type="submit" disabled={session.loading}>Preparar activación</button>
  </form>:<>
   <p>En tu aplicación de autenticación, añade una cuenta por clave manual. Selecciona códigos de {pending.digits} dígitos basados en tiempo, con período de 30 segundos.</p>
   <p>Esta clave permite generar tus códigos. No la compartas ni la guardes en documentos o capturas. Se ocultará al salir de esta pantalla.</p>
   {pending.secret?<><label>Clave de configuración <input aria-label="Clave de configuración" type={show?'text':'password'} readOnly autoComplete="off" spellCheck={false} value={pending.secret}/></label>{' '}<button type="button" disabled={session.loading} onClick={()=>setShow(current=>!current)}>{show?'Ocultar clave':'Mostrar clave'}</button></>:<p>La clave está oculta. Si ya configuraste tu aplicación, introduce el código. En otro caso, cancela y vuelve a comenzar.</p>}
   <form onSubmit={async event=>{event.preventDefault();const proof=code;setCode('');try{await session.confirmEnrollment(proof);}catch{ /* Safe message is shown by the session hook. */ }}} style={{marginTop:18}}>
    <label>Código de activación <input aria-label="Código de activación" type="text" inputMode="numeric" autoComplete="one-time-code" required minLength={pending.digits} maxLength={pending.digits} pattern={'[0-9]{'+pending.digits+'}'} value={code} disabled={session.loading||session.cancelUnconfirmed} onChange={event=>setCode(event.target.value.replace(/[^0-9]/g,''))}/></label>{' '}
    <button type="submit" disabled={session.loading||session.cancelUnconfirmed}>Confirmar activación</button>{' '}
    <button type="button" disabled={session.loading} onClick={()=>session.cancelEnrollment()}>{session.cancelUnconfirmed?'Reintentar cancelación':'Cancelar activación'}</button>
   </form>
   <p>La configuración vence en dos minutos. El factor solo quedará activo después de confirmar un código correcto.</p>
  </>}
 </section>;
}
