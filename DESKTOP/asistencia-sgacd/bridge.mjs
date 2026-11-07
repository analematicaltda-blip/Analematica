import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const exec=promisify(execFile);
export const root=path.dirname(fileURLToPath(import.meta.url));
export const engine=path.resolve(root,'../../BACKEND/SGA-CD-BACKEND/app/services/assistance');
const catalog=JSON.parse(fs.readFileSync(path.join(engine,'catalog.json'),'utf8'));
export const policy=fs.readFileSync(path.join(engine,'policy.txt'),'utf8');
const noArgs={type:'object',properties:{},additionalProperties:false};
export const toolset=[
 {name:'assistance_catalog',description:'Lista guías de Meta Ads, TikTok Ads, Gmail y YouTube. No accede a cuentas.',inputSchema:noArgs},
 {name:'assistance_workflow',description:'Lee los pasos de una guía. El usuario ejecuta las acciones personalmente.',inputSchema:{type:'object',properties:{workflow_id:{type:'string',maxLength:100}},required:['workflow_id'],additionalProperties:false}},
 {name:'assistance_desktop_status',description:'Diagnóstico local de agent-desktop, sin capturar ventanas ni ejecutar acciones.',inputSchema:noArgs},
 {name:'assistance_observe_window',description:'Observación nativa de la única ventana elegida por el operador. Desactivada salvo consentimiento local explícito; no accede al DOM ni hace clic.',inputSchema:noArgs},
].map(tool=>({...tool,annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:tool.name==='assistance_observe_window'}}));
function validate(name,args){
 if(!args||typeof args!=='object'||Array.isArray(args))throw Error('Argumentos no válidos.');
 const allowed=name==='assistance_workflow'?['workflow_id']:[];
 if(Object.keys(args).some(key=>!allowed.includes(key)))throw Error('No se permiten esos parámetros.');
 if(name==='assistance_workflow'&&(typeof args.workflow_id!=='string'||args.workflow_id.length>100))throw Error('Falta workflow_id.');
}
export function redact(value){
 if(typeof value==='string')return value.replace(/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g,'[token omitido]').replace(/\bBearer\s+\S+/gi,'[credencial omitida]').replace(/\b(password|contraseña|clave|access_token|refresh_token|client_secret|api_key|token)\s*[:=]\s*[^\s,;]+/gi,'[credencial omitida]');
 if(Array.isArray(value))return value.slice(0,100).map(redact);
 if(value&&typeof value==='object'){
  if(/password|secure.?text/i.test(String(value.role??value.type??'')))return {role:'protected',text:'[campo protegido omitido]'};
  return Object.fromEntries(Object.entries(value).filter(([key])=>!['state_root','token','password','value'].includes(key.toLowerCase())).slice(0,100).map(([key,item])=>[key,redact(item)]));
 }
 return value;
}
export async function desktop(args, runner=exec){
 const result=await runner(process.execPath,[path.resolve(root,'../agent-desktop-sgacd/run.mjs'),...args],{timeout:6000,maxBuffer:256*1024,windowsHide:true,env:process.env});
 let value;try{value=JSON.parse(result.stdout)}catch{throw Error('El runtime no devolvió un diagnóstico válido.')}
 if(!value.ok)return {ok:false,error:value.error?.code??'desktop_unavailable'};
 return redact(value.data??{});
}
export async function call(name,args={},options={}){
 if(!toolset.some(tool=>tool.name===name))throw Error('Herramienta no permitida. Este conector no ofrece acciones de escritura.');
 validate(name,args);
 if(name==='assistance_catalog')return {version:catalog.version,mode:catalog.mode,notice:catalog.notice,platforms:catalog.platforms,workflows:catalog.workflows.map(({id,title,platform})=>({id,title,platform}))};
 if(name==='assistance_workflow'){
  const flow=catalog.workflows.find(item=>item.id===args.workflow_id);if(!flow)throw Error('Guía no encontrada.');return structuredClone(flow);
 }
 if(name==='assistance_desktop_status')return desktop(['status'],options.runner);
 throw Error('La observación directa fue deshabilitada. Usa el panel de control con dos autorizaciones y un equipo vinculado.');
}
