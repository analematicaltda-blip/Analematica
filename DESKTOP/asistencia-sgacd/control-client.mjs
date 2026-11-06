import fs from 'node:fs';
import path from 'node:path';
import https from 'node:https';
import http from 'node:http';
import crypto from 'node:crypto';
import tls from 'node:tls';
import {engine} from './bridge.mjs';
export const policy=JSON.parse(fs.readFileSync(path.join(engine,'control_policy.json'),'utf8'));
export function request(origin,route,{token,body,caFile,method}={}){
 const base=new URL(origin);
 if(base.username||base.password||base.search||base.hash||base.pathname!=='/'||base.protocol!=='https:')throw Error('El control requiere un origen HTTPS sin rutas ni credenciales.');
 const url=new URL('/api/v1/assistance/control'+route,base),payload=body===undefined?null:Buffer.from(JSON.stringify(body));
 return new Promise((resolve,reject)=>{
  const req=https.request(url,{method:method??(payload?'POST':'GET'),ca:caFile?[...tls.rootCertificates,fs.readFileSync(caFile)]:undefined,headers:{...(token?{Authorization:'Bearer '+token}:{}),...(payload?{'Content-Type':'application/json','Content-Length':payload.length}:{})},timeout:20000},response=>{
   let size=0;const chunks=[];
   response.on('data',chunk=>{size+=chunk.length;if(size>1_000_000){req.destroy(Error('Respuesta demasiado grande.'));return}chunks.push(chunk)});
   response.on('end',()=>{if(response.statusCode>=300){const error=Error('El servidor rechazó la operación ('+response.statusCode+').');error.status=response.statusCode;reject(error);return}try{resolve(JSON.parse(Buffer.concat(chunks)))}catch{reject(Error('Respuesta no válida.'))}});
  });req.on('timeout',()=>req.destroy(Error('Tiempo de conexión agotado. No se reintentó la acción.')));req.on('error',reject);if(payload)req.write(payload);req.end();
 });
}
export function verifyGrant(envelope,config,at=Math.floor(Date.now()/1000)){
 if(!envelope||typeof envelope.payload!=='string'||envelope.payload.length>32000||typeof envelope.signature!=='string')throw Error('Permiso firmado no válido.');
 if(!crypto.verify(null,Buffer.from(envelope.payload),config.server_public_key,Buffer.from(envelope.signature,'base64')))throw Error('Firma de control no válida.');
 const grant=JSON.parse(envelope.payload),intent=JSON.parse(grant.intent_json);
 if(grant.policy!==policy.version||intent.policy!==policy.version||grant.device_id!==config.device_id||intent.device_id!==config.device_id||grant.owner_id!==config.owner_id||grant.tenant_id!==config.tenant_id||intent.owner_id!==config.owner_id||intent.tenant_id!==config.tenant_id)throw Error('El permiso pertenece a otro equipo o usuario.');
 if(!Number.isInteger(grant.issued_at)||!Number.isInteger(grant.expires_at)||grant.issued_at>at+5||grant.expires_at<at||grant.expires_at-grant.issued_at>policy.max_grant_seconds||grant.expires_at<=grant.issued_at)throw Error('Permiso vencido o duración no permitida.');
 if(crypto.createHash('sha256').update(grant.intent_json).digest('hex')!==grant.digest)throw Error('El plan aprobado cambió.');
 const keys=policy.operation_arguments[intent.operation];if(!keys||!intent.arguments||Array.isArray(intent.arguments)||Object.keys(intent.arguments).sort().join('|')!==[...keys].sort().join('|')||Object.values(intent.arguments).some(v=>typeof v!=='string'||v.length>4000||v.includes('\0')))throw Error('Argumentos de operación fuera del contrato autorizado.');
 const count=policy.operations[intent.operation];if(!count||!Array.isArray(grant.approvals)||grant.approvals.length!==count)throw Error('Faltan autorizaciones independientes.');
 grant.approvals.forEach((a,index)=>{if(a.stage!==index+1||a.user_id!==config.owner_id||a.tenant_id!==config.tenant_id||a.digest!==grant.digest)throw Error('Autorizaciones fuera del plan o del solicitante.');});
 if(!config.platforms.includes(intent.platform)||!policy.platform_hosts[intent.platform]||intent.account_label!=='principal'||intent.target_kind!==(config.kind??'desktop'))throw Error('Plataforma, cuenta o tipo de equipo no autorizado.');
 if(intent.operation==='browser_open'||intent.operation==='mobile_open_url'){
  const url=new URL(intent.arguments.url);if(url.protocol!=='https:'||url.username||url.password||(url.port&&url.port!=='443')||!policy.platform_hosts[intent.platform].includes(url.hostname))throw Error('Solo se permiten páginas oficiales aprobadas.');
 }
 if(intent.operation.startsWith('mobile_')){
  const native=policy.native_apps[config.kind]?.[intent.platform]??[],browsers=policy.mobile_browsers[config.kind]??[];
  if(!(intent.operation==='mobile_open_url'?browsers:[...native,...browsers]).includes(intent.arguments.app_id))throw Error('Aplicación nativa no autorizada.');
 }else if(config.kind!=='desktop')throw Error('Operación de escritorio sobre un móvil.');
 if(!/^[a-f0-9]{48}$/.test(grant.lease_id)||typeof intent.job_id!=='string')throw Error('Permiso de una sola ejecución incompleto.');
 return {grant,intent};
}
