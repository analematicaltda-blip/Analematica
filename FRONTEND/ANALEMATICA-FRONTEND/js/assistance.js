(()=>{'use strict';
 const $=id=>document.getElementById(id),token=localStorage.getItem('accessToken');
 let catalog=null,current=null,capabilities=null,questionId=null,busy=false;
 const message=text=>{$('message').textContent=text;};
 async function api(path,body){
  const response=await fetch('/api/v1/assistance'+path,{method:body===undefined?'GET':'POST',headers:{Authorization:'Bearer '+token,...(body===undefined?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:JSON.stringify(body),cache:'no-store',signal:AbortSignal.timeout(50000)});
  let value={};try{value=await response.json()}catch{}
  if(response.status===401){message('Tu sesión terminó. Ingresa de nuevo al sistema.');throw Error('Sesión no válida.');}
  if(!response.ok)throw Error(typeof value.detail==='string'?value.detail:'No se pudo completar la consulta.');return value;
 }
 function workflowOptions(){
  $('workflow').replaceChildren(...catalog.workflows.filter(item=>item.platform===$('platform').value).map(item=>new Option(item.title,item.id)));
 }
 function canAdvance(){return !busy&&current?.status==='active'&&[...$('checklist').querySelectorAll('input')].every(box=>box.checked)&&(!current.current_step.requires_confirmation||$('confirm').checked);}
 function render(state){
  current=state;questionId=null;$('check-answer').hidden=true;$('answer').textContent='';$('guide').hidden=false;$('guide-title').textContent=state.title;
  $('progress').textContent=`${state.status==='active'?'Paso '+(state.position+1):'Guía '+(state.status==='completed'?'terminada':'cerrada')} · ${state.total} pasos · revisión ${state.revision}`;
  $('official').href=state.entry_url;$('official').textContent='Abrir la plataforma oficial';
  const step=state.current_step;$('checklist').replaceChildren();$('confirm').checked=false;$('confirm-row').hidden=!step?.requires_confirmation;
  $('step-title').textContent=step?.title??'Progreso registrado';$('instruction').textContent=step?.instruction??'La guía terminó. Los pasos representan tus comprobaciones; no una ejecución automática del asistente.';
  for(const item of step?.checklist??[]){const label=document.createElement('label');label.className='check';const box=document.createElement('input');box.type='checkbox';box.addEventListener('change',()=>$('advance').disabled=!canAdvance());label.append(box,document.createTextNode(item));$('checklist').append(label);}
  $('advance').disabled=!canAdvance();$('close').disabled=state.status!=='active';$('advice').hidden=state.status!=='active';
  $('ask').disabled=capabilities?.open_duet!=='configured_not_live_verified';
 }
 async function history(){
  const value=await api('/sessions');$('sessions').replaceChildren();
  if(!value.sessions.length){const li=document.createElement('li');li.textContent='Todavía no tienes guías guardadas.';$('sessions').append(li);return;}
  for(const item of value.sessions){const li=document.createElement('li'),button=document.createElement('button');button.className='secondary';button.textContent=item.title+' · '+item.position+'/'+item.total;button.addEventListener('click',()=>perform(async()=>render(await api('/sessions/'+item.id))));li.append(button);$('sessions').append(li);}
 }
 async function perform(action){if(busy)return;busy=true;$('advance').disabled=true;try{await action()}catch(error){message(error.message)}finally{busy=false;$('advance').disabled=!canAdvance();}}
 $('platform').addEventListener('change',workflowOptions);
 $('confirm').addEventListener('change',()=>$('advance').disabled=!canAdvance());
 $('start').addEventListener('click',()=>perform(async()=>{render(await api('/sessions',{workflow_id:$('workflow').value}));await history();message('Guía preparada. Empieza por confirmar tu cuenta.');}));
 $('advance').addEventListener('click',()=>perform(async()=>{if(!current)return;render(await api('/sessions/'+current.id+'/advance',{revision:current.revision,step_id:current.current_step.id,checklist_checked:true,confirmed:$('confirm').checked}));await history();message('Paso registrado según tu comprobación.');}));
 $('close').addEventListener('click',()=>perform(async()=>{render(await api('/sessions/'+current.id+'/close',{revision:current.revision}));await history();message('Se cerró solo esta guía. No se cambió ninguna cuenta ni campaña.');}));
 $('ask').addEventListener('click',()=>perform(async()=>{
  if(!$('share').checked)throw Error('Autoriza primero compartir la pregunta y el paso actual.');
  const text=$('question').value.trim();if(text.length<3)throw Error('Escribe una pregunta sobre el paso actual.');
  questionId=crypto.randomUUID();const reply=await api('/sessions/'+current.id+'/advice',{request_id:questionId,question:text,share_with_open_duet:true});
  $('answer').textContent='Consulta enviada a tu Open Duet en modo planificación. Pulsa Consultar respuesta para ver su estado.';$('check-answer').hidden=false;
 }));
 $('check-answer').addEventListener('click',()=>perform(async()=>{const reply=await api('/sessions/'+current.id+'/advice/'+questionId);$('answer').textContent=reply.answer??(reply.status==='running'?'La orientación todavía se está preparando.':reply.status==='uncertain'?'No se pudo confirmar la consulta. Revísala en Open Duet antes de repetirla.':'La consulta terminó sin una respuesta disponible.');if(reply.status!=='running')$('check-answer').hidden=true;}));
 if(!token){message('Ingresa al sistema para usar y guardar tus guías.');const a=document.createElement('a');a.href='login.html';a.textContent=' Iniciar sesión';$('message').append(a);return;}
 (async()=>{try{[catalog,capabilities]=await Promise.all([api('/catalog'),api('/capabilities')]);$('platform').replaceChildren(...Object.entries(catalog.platforms).map(([id,p])=>new Option(p.name,id)));workflowOptions();$('platform').disabled=false;$('workflow').disabled=false;$('start').disabled=false;$('catalog-notice').textContent=catalog.notice;$('ai-state').textContent=capabilities.open_duet==='configured_not_live_verified'?'Tu Open Duet está configurado. La pregunta y el paso se comparten solo si lo autorizas.':'Puedes usar todas las guías. La orientación con Open Duet todavía no está conectada.';await history();message('Elige una tarea para comenzar.');}catch(error){message(error.message)}})();
})();
