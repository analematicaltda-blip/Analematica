/* Direct owner login. No redirect to SGA panels and no credentials in URLs. */
(()=>{
 const form=document.getElementById('owner-login-form'),message=document.getElementById('owner-login-message'),button=form.querySelector('button');
 const prior=sessionStorage.getItem('analematica-login-error');if(prior){message.textContent=prior;sessionStorage.removeItem('analematica-login-error');}
 AnaleConnection.owner().then(()=>location.replace('/admin.html')).catch(()=>{});
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(button.disabled)return;button.disabled=true;message.textContent='Verificando el acceso del dueño…';
  const username=form.elements.username.value.trim(),password=form.elements.password.value;
  try{
   const response=await fetch('/api/v1/workspace/corporate/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({username,password}),cache:'no-store',signal:AbortSignal.timeout(15000)});
   let data={};try{data=await response.json()}catch{}
   if(!response.ok||!data.access_token)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo verificar el ingreso.');
   localStorage.setItem('accessToken',data.access_token);localStorage.setItem('userId',String(data.user.id));localStorage.setItem('userName',data.user.name);localStorage.setItem('userRoles',JSON.stringify(data.user.roles));
   form.elements.password.value='';location.replace('/admin.html');
  }catch(error){form.elements.password.value='';message.textContent=error.name==='TimeoutError'?'El servidor tardó demasiado. Puedes reintentar.':error.message;button.disabled=false;}
 });
})();
