/* Public deployment metadata only. Never persist credentials or authorize on load. */
(()=>{
 async function initialize(){
  const status=document.getElementById('meta-setup-status');
  try{
   const response=await fetch('config/meta-public.json',{cache:'no-store'});
   if(!response.ok)throw new Error('No se pudo leer la configuración pública.');
   const config=await response.json();
   if(config.callback_path!=='/api/v1/workspace/ads/meta/oauth/callback')throw new Error('Ruta de retorno no válida.');
   for(const key of ['app_id','user_login_config_id','instagram_system_login_config_id'])if(!/^\d{1,40}$/.test(config[key]))throw new Error('Identificador público no válido.');
   const callback=new URL(config.callback_path,location.origin);
   if(callback.protocol!=='https:'&&!(['localhost','127.0.0.1'].includes(callback.hostname)&&callback.protocol==='http:'))throw new Error('Abre el panel mediante HTTPS para configurar Meta.');
   document.getElementById('meta-callback-detected').value=callback.href;
   status.textContent='Aplicación '+config.app_id+' · Acceso personal '+config.user_login_config_id+' · Instagram (usuario del sistema) '+config.instagram_system_login_config_id+'. Pendiente de autorización real.';
   const form=document.getElementById('meta-app-form');
   // Fill empty fields only; never replace an existing server configuration.
   if(!form.elements.app_id.value){form.elements.app_id.value=config.app_id;form.elements.api_version.value=config.api_version;form.elements.login_config_id.value=config.user_login_config_id;}
   if(!form.elements.redirect_uris.value)form.elements.redirect_uris.value=callback.href;
   document.getElementById('meta-copy-callback').onclick=async()=>{try{await navigator.clipboard.writeText(callback.href);status.textContent='URL de retorno copiada. Regístrala exactamente en Meta. Instagram requiere completar su flujo de usuario del sistema en el backend.';}catch{status.textContent='Selecciona y copia la URL del campo de retorno.';}};
  }catch(error){status.textContent=error.message;}
 }
 window.addEventListener('analematica:ready',initialize,{once:true});
})();
