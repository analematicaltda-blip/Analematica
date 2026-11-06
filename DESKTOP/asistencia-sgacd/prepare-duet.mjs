import fs from 'node:fs';
import path from 'node:path';
import {root,engine,policy} from './bridge.mjs';
const runtime=path.join(root,'.runtime'),workspace=path.join(runtime,'workspace');
fs.mkdirSync(workspace,{recursive:true,mode:0o700});
fs.writeFileSync(path.join(workspace,'AGENTS.md'),policy+'\nLas guías están en CATALOG.json. El MCP sgacd-assistance solo ofrece guías y observación local opcional. Si no está conectado, usa el catálogo y no ejecutes comandos para suplirlo.\n',{mode:0o600});
fs.copyFileSync(path.join(engine,'catalog.json'),path.join(workspace,'CATALOG.json'));
fs.writeFileSync(path.join(workspace,'.mcp.json'),JSON.stringify({mcpServers:{'sgacd-assistance':{command:'node',args:[path.join(root,'mcp.mjs')]}}},null,2),{mode:0o600});
const profile={name:'Asistente SGA-CD · Plataformas',title:'Meta Ads · TikTok Ads · Gmail · YouTube',
 description:'Asistencia guiada, sin ejecutar acciones externas.',instructions:policy,provider:process.env.OPEN_DUET_ENGINE??'codex',
 workspace_path:workspace,approval_mode:'plan',make_lead:false,memory_enabled:false,recall_enabled:false,memory_upkeep:false,compaction_summary:false,use_helper:false};
fs.writeFileSync(path.join(runtime,'agent-profile.json'),JSON.stringify(profile,null,2),{mode:0o600});
if(process.argv.includes('--register')){
 const raw=process.env.OPEN_DUET_URL??'',token=process.env.OPEN_DUET_TOKEN??'';let url;try{url=new URL(raw)}catch{throw Error('Configura OPEN_DUET_URL con el origen local de tu instancia.')}
 if(url.protocol!=='http:'||!['localhost','127.0.0.1','[::1]'].includes(url.hostname)||url.username||url.password||url.search||url.hash||url.pathname!=='/'||token.length<16||/[\s\x00-\x20\x7f]/.test(token))throw Error('Se requiere un origen loopback y una credencial local válida.');
 const saved=path.join(runtime,'registered-agent.json');
 const request=async(method,suffix,payload)=>{
  const response=await fetch(new URL('/api/v1'+suffix,url),{method,redirect:'error',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:payload?JSON.stringify(payload):undefined,signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw Error('Open Duet rechazó la configuración. No se imprimió su respuesta ni la credencial.');
  return response.json();
 };
 if(fs.existsSync(saved)){
  const state=JSON.parse(fs.readFileSync(saved,'utf8'));if(state.origin!==url.origin||!Number.isSafeInteger(state.id)||state.id<1)throw Error('La instancia local cambió. Revisa la inscripción anterior.');
  const current=await request('GET','/agents/'+state.id);
  if(current.approval_mode!=='plan'||current.memory_enabled!==false||current.workspace_path!==workspace)throw Error('El agente existente cambió. No se sobrescribió su configuración.');
  console.log('El agente de asistencia ya está registrado; no se duplicó.');
 }else{
  const agent=await request('POST','/agents',profile);if(!Number.isSafeInteger(agent.id)||agent.id<1||agent.approval_mode!=='plan'||agent.memory_enabled!==false)throw Error('Open Duet no confirmó el perfil limitado; no se inició ninguna conversación.');
  fs.writeFileSync(saved,JSON.stringify({origin:url.origin,id:agent.id}),{mode:0o600});
  console.log('Agente de asistencia registrado en Open Duet, en modo planificación. No se inició ninguna conversación.');
 }
}else console.log('Perfil y catálogo local preparados. No se conectó Open Duet ni se inició un modelo.');
