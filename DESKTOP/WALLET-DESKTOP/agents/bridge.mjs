import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {call as assistance} from '../../asistencia-sgacd/bridge.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const registry=()=>JSON.parse(fs.readFileSync(path.join(root,'BACKEND/WALLET-BACKEND/offline/src/sgacd_wallet_offline/production_pending.json'),'utf8'));
export const tools=[
 {name:'wallet_team',description:'Funciones del equipo local. No lee datos de usuarios.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
 {name:'wallet_production_pending',description:'Pendientes de producción versionados. No acredita validaciones reales.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
 {name:'wallet_control_policy',description:'Condiciones del motor de control existente, sin emitir ni ejecutar permisos.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
 {name:'wallet_desktop_status',description:'Estado local del runtime, sin capturar pantallas ni controlar ventanas.',inputSchema:{type:'object',properties:{},additionalProperties:false}},
].map(t=>({...t,annotations:{readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false}}));
export async function call(name,args={},options={}) {
 if(!args||typeof args!=='object'||Array.isArray(args)||Object.keys(args).length||!tools.some(t=>t.name===name))throw Error('Herramienta o argumentos no permitidos.');
 if(name==='wallet_team')return {mode:'offline_rules_and_gated_planning',engines:['Open Duet','agent-desktop'],roles:['custodio','criptografia','integridad','antiphishing','aprobaciones','conciliacion','continuidad','produccion'],can_approve:false,can_execute_payments:false};
 if(name==='wallet_production_pending')return registry();
 if(name==='wallet_control_policy'){
  const policy=JSON.parse(fs.readFileSync(path.join(root,'BACKEND/SGA-CD-BACKEND/app/services/assistance/control_policy.json'),'utf8'));
  return {policy:policy.version,minimum_human_approvals:2,impact_actions_may_require:3,actor:'same_requesting_administrator',requires_signed_server_grant:true,offline_control_grants_implemented:false,wallet_payment_tools:[],device_connection_assumed:false};
 }
 return assistance('assistance_desktop_status',{},options);
}
