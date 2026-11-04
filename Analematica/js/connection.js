/* Same-origin bridge: no credentials in links or public configuration. */
window.AnaleConnection=(()=>{
 const base='/api/v1/workspace/corporate';
 async function request(path,options={}){
  const headers={'Content-Type':'application/json',...(options.headers||{})};
  if(options.authorized){const token=localStorage.getItem('accessToken');if(!token)throw new Error('Inicia sesión como dueño de SGA-CD.');headers.Authorization='Bearer '+token;}
  const response=await fetch(base+path,{...options,headers,cache:'no-store',signal:AbortSignal.timeout(15000)});
  let data={};try{data=await response.json()}catch{}
  if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo completar la operación. Revisa los campos o inténtalo de nuevo.');return data;
 }
 async function owner(){const token=localStorage.getItem('accessToken');if(!token)throw new Error('Inicia sesión como dueño de SGA-CD.');const r=await fetch('/api/v1/workspace/session',{headers:{Authorization:'Bearer '+token},cache:'no-store',signal:AbortSignal.timeout(15000)});if(!r.ok)throw new Error('La sesión de SGA-CD no está disponible.');const data=await r.json();if(data.scope!=='platform'||!data.user?.roles?.includes('admin_general'))throw new Error('Solo el dueño de SGA-CD administra Analemática.');return data;}
 return {request,owner};
})();
