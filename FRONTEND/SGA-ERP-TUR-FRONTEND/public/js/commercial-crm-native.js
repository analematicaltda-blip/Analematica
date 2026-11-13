/* Native company session. SGA-CD credentials are deliberately not used here. */
window.Pool08NativeCRM={mount(access,host,base){
 if(host._crmDispose)return host._crmDispose;
 let csrf='',dispose=null,disposed=false,closing=false;const lifetime=new AbortController();
 host.addEventListener('crm-busy',event=>{const select=access.querySelector('[data-company]');if(select)select.disabled=Boolean(event.detail);},{signal:lifetime.signal});
 async function request(path,options={}){
  const headers=new Headers(options.headers);if(options.method&&options.method!=='GET')headers.set('X-CSRFToken',csrf);
  return fetch(base+path,{...options,signal:options.signal||lifetime.signal,headers,cache:'no-store',credentials:'same-origin',mode:'same-origin',redirect:'error'});
 }
 async function read(path,body){
  const response=await request(path,{...(body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})});
  const raw=await response.json().catch(()=>({})),data=raw.success===true?raw.data:raw;
  if(disposed)throw new DOMException('Disposed','AbortError');
  if(!response.ok){const error=new Error(response.status===503?'La sesión nativa requiere habilitación en el servidor.':'No se pudo validar el acceso a este sistema.');error.status=response.status;throw error;}
  return data;
 }
 const message=text=>{if(disposed)return;access.replaceChildren();const p=document.createElement('p');p.textContent=text;p.setAttribute('role','status');access.append(p);};
 async function companies(){
  const state=await read('session/status/');csrf=state.csrf_token;
  const result=await read('companies/');
  access.innerHTML='<label>Empresa<select data-company><option value="">Selecciona una empresa</option></select></label><button type="button" data-logout>Cerrar sesión nativa</button>';
  const select=access.querySelector('[data-company]');
  for(const company of result.companies){const option=document.createElement('option');option.value=company.provider_id;option.textContent=company.name;select.append(option);}
  if(!result.companies.length){const empty=document.createElement('p');empty.setAttribute('role','status');empty.textContent='Tu cuenta no tiene acceso CRM vigente a una empresa verificada.';access.append(empty);select.disabled=true;}
  select.onchange=()=>{if(disposed||closing||select.disabled)return;dispose?.();dispose=null;host.replaceChildren();if(select.value)dispose=window.Pool08CRM.mount(host,{request,provider:select.value,native:true});};
  const logout=access.querySelector('[data-logout]');if(logout)logout.onclick=async()=>{if(closing||disposed)return;closing=true;logout.disabled=true;select.disabled=true;dispose?.();dispose=null;host.replaceChildren();try{const state=await read('session/status/');csrf=state.csrf_token;await read('session/logout/',{});await login();}catch(e){if(disposed)return;message('No se pudo confirmar el cierre de sesión. Reintenta antes de dejar el equipo.');const retry=document.createElement('button');retry.textContent='Reintentar cierre';retry.onclick=logout.onclick;access.append(retry);}finally{closing=false;logout.disabled=false;}};
 }
 async function login(){
  const state=await read('session/status/');csrf=state.csrf_token;
  if(state.authenticated){await companies();return;}
  access.innerHTML='<h3>Acceso propio de este sistema</h3><p>Los cargos de otros sistemas no cambian tus permisos aquí.</p><form><label>Usuario<input name="username" required autocomplete="username" maxlength="150"></label><label>Contraseña<input name="password" type="password" required autocomplete="current-password"></label><button>Ingresar</button></form><p role="status" data-status></p>';
  access.querySelector('form').onsubmit=async event=>{
   event.preventDefault();const form=event.target,button=form.querySelector('button');if(form.dataset.busy)return;form.dataset.busy='true';button.disabled=true;form.setAttribute('aria-busy','true');
   try{const result=await read('session/login/',Object.fromEntries(new FormData(form)));csrf=result.csrf_token;
    if(result.mfa_required){mfa(result);return;}
    if(!result.authenticated)throw new Error('Acceso no confirmado.');await companies();
   }catch(e){if(!disposed)access.querySelector('[data-status]')?.replaceChildren(document.createTextNode(e.message));}finally{form.elements.password.value='';form.dataset.busy='';form.setAttribute('aria-busy','false');button.disabled=false;}
  };
 }
 function mfa(state){
  access.innerHTML='<h3>Verificación de acceso</h3><form><label>Código de autenticación<input name="code" required inputmode="numeric" autocomplete="one-time-code"></label><label><input name="recovery" type="checkbox">Usar código de recuperación</label><button>Verificar</button></form><p role="status" data-status></p>';
  access.querySelector('form').onsubmit=async event=>{event.preventDefault();const form=event.target;if(form.dataset.busy)return;form.dataset.busy='true';form.setAttribute('aria-busy','true');form.querySelector('button').disabled=true;try{const result=await read('session/'+(form.elements.recovery.checked?'recovery/':'mfa/'),{challenge_id:state.challenge_id,code:form.elements.code.value});csrf=result.csrf_token;if(result.authenticated)await companies();else throw new Error('Verificación no completada.');}catch(e){if(!disposed)access.querySelector('[data-status]')?.replaceChildren(document.createTextNode(e.message));}finally{form.elements.code.value='';form.dataset.busy='';form.setAttribute('aria-busy','false');form.querySelector('button').disabled=false;}};
 }
 function start(){if(disposed)return;message('Verificando acceso propio del sistema…');companies().catch(async e=>{if(disposed)return;if(e.status===401||e.status===403){try{await login();}catch(error){showRetry(error.message);}}else showRetry(e.message);});}
 function showRetry(text){if(disposed)return;message(text);const retry=document.createElement('button');retry.textContent='Reintentar acceso';retry.onclick=()=>{retry.disabled=true;start();};access.append(retry);}
 start();
 const cleanup=()=>{if(disposed)return;disposed=true;lifetime.abort();dispose?.();dispose=null;host._crmDispose=null;access.replaceChildren();host.replaceChildren();};
 host._crmDispose=cleanup;return cleanup;
}};
{const host=document.getElementById('crm-host'),access=document.getElementById('crm-access');if(host&&access)window.Pool08NativeCRM.mount(access,host,host.dataset.crmBase||document.body.dataset.crmBase);}
