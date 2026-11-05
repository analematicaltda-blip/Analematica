/* Instagram consent shares owner login, never stores provider tokens in the browser. */
(()=>{
 const $=id=>document.getElementById(id),base='/api/v1/workspace/instagram';
 async function request(path,body,method='GET'){
  const token=localStorage.getItem('accessToken');if(!token)throw Error('Ingresa al panel del dueño.');
  const response=await fetch(base+path,{method,headers:{Authorization:'Bearer '+token,...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{}),cache:'no-store',signal:AbortSignal.timeout(45000)});
  let data={};try{data=await response.json();}catch{}
  if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:'No se completó la operación de Instagram.');return data;
 }
 async function refresh(){const state=await request('/status');if(state.config_id)$('instagram-config-id').value=state.config_id;$('instagram-state').textContent=state.authorized_on_record?'Autorización guardada. '+(state.account.username?'Cuenta comprobada: @'+state.account.username:'Falta comprobar y seleccionar la cuenta profesional.'):'Falta completar la autorización de Instagram.';}
 async function run(button,action){button.disabled=true;try{await action();}catch(error){$('instagram-state').textContent=error.name==='TimeoutError'?'No se confirmó la respuesta del servidor.':error.message;}finally{button.disabled=false;}}
 window.addEventListener('analematica:ready',()=>{
  $('meta-webhook-url').value=location.origin+'/api/v1/workspace/meta/webhooks/receive';
  $('meta-webhook-save').onclick=event=>run(event.currentTarget,async()=>{
   const ids=$('meta-webhook-assets').value.split(',').map(s=>s.trim()).filter(Boolean);
   if(!ids.length||ids.some(id=>!/^\d{1,40}$/.test(id)))throw Error('Introduce identificadores numéricos de tus activos.');
   const bytes=crypto.getRandomValues(new Uint8Array(32));const verifier=Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
   const token=localStorage.getItem('accessToken');
   const response=await fetch('/api/v1/workspace/meta/webhooks/config',{method:'PUT',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify({verify_token:verifier,accepted_ids:ids}),cache:'no-store',signal:AbortSignal.timeout(45000)});
   if(!response.ok)throw Error('No se confirmó la configuración del webhook.');
   $('meta-webhook-token').value=verifier;$('meta-webhook-state').textContent='Verificador guardado cifrado. Copia la URL y este verificador en Meta. Pendiente de verificación externa.';
  });
  $('meta-webhook-copy').onclick=event=>run(event.currentTarget,async()=>{const value=$('meta-webhook-token').value;if(!value)throw Error('Primero genera y guarda el verificador.');await navigator.clipboard.writeText(value);$('meta-webhook-state').textContent='Verificador copiado. Pégalo únicamente en la configuración del webhook de Meta.';});
  $('instagram-callback').value=location.origin+'/api/v1/workspace/instagram/oauth/callback';
  $('instagram-save').onclick=event=>run(event.currentTarget,async()=>{await request('/config',{config_id:$('instagram-config-id').value.trim()},'PUT');$('instagram-state').textContent='Configuración guardada. Registra el retorno de Instagram en Meta y en la aplicación compartida antes de conectar.';});
  $('instagram-refresh').onclick=event=>run(event.currentTarget,refresh);
  $('instagram-authorize').onclick=event=>run(event.currentTarget,async()=>{const data=await request('/oauth/start',{redirect_uri:$('instagram-callback').value},'POST');const url=new URL(data.authorization_url);if(url.origin!=='https://www.facebook.com')throw Error('Destino de autorización no válido.');location.assign(url.href);});
  $('instagram-select').onclick=event=>run(event.currentTarget,async()=>{const id=$('instagram-account-id').value.trim();if(!/^\d{1,40}$/.test(id))throw Error('Introduce el ID de la cuenta de Instagram.');await request('/account',{account_id:id},'PUT');await refresh();});
  const result=new URLSearchParams(location.search).get('instagram');if(result){$('instagram-state').textContent=result==='connected'?'Autorización completada. Consulta la conexión para seleccionar tu cuenta.':'Meta no completó la autorización. Comprueba permisos, configuración y restricciones.';const url=new URL(location.href);url.searchParams.delete('instagram');history.replaceState(null,'',url.pathname+url.search+url.hash);}
 },{once:true});
})();
