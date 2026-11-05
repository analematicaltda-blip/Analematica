/* Same-origin bridge: no credentials in links or public configuration. */
window.AnaleConnection=(()=>{
 const base='/api/v1/workspace/corporate';
 async function request(path,options={}){
  const headers={'Content-Type':'application/json',...(options.headers||{})};
  if(options.authorized){const token=localStorage.getItem('accessToken');if(!token)throw new Error('Ingresa a la consola privada de Analemática.');headers.Authorization='Bearer '+token;}
  const response=await fetch(base+path,{...options,headers,cache:'no-store',signal:AbortSignal.timeout(15000)});
  let data={};try{data=await response.json()}catch{}
  if(response.status===401&&options.authorized)throw new Error('Tu sesión terminó. Ingresa de nuevo a Analemática.');
  if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo completar la operación. Revisa los campos o inténtalo de nuevo.');return data;
 }
 async function owner(){return request('/session',{authorized:true});}
 return {request,owner};
})();
