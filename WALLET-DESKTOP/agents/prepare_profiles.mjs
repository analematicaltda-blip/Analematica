import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),runtime=path.resolve(here,'../.runtime/army');
const provider=process.env.OPEN_DUET_ENGINE??'';
if(provider&&!/^[a-zA-Z0-9_-]{1,64}$/.test(provider))throw Error('Motor no válido.');
fs.mkdirSync(runtime,{recursive:true,mode:0o700});
for(const role of ['custodio','criptografia','integridad','antiphishing','aprobaciones','conciliacion','continuidad','produccion']) {
 const workspace=path.join(runtime,role);fs.mkdirSync(workspace,{recursive:true,mode:0o700});
 const instructions='Asiste en la billetera con el rol '+role+'. No leas vaults, documentos ni secretos. No apruebes tus propias acciones ni ejecutes pagos. El MCP wallet ofrece solo metadatos/estado. El control de equipos requiere permisos firmados del motor existente y dos autorizaciones del mismo solicitante, o tres cuando corresponda. Las revisiones offline no son autorizaciones financieras. No instales herramientas ni uses shell para suplir permisos. Si no hay un modelo local validado, conserva planificación y reglas locales; no solicites un servicio externo de forma automática.';
 for(const [name,text] of [['AGENTS.md',instructions],['.mcp.json',JSON.stringify({mcpServers:{'wallet-team':{command:'node',args:[path.join(here,'mcp.mjs')]}}},null,2)]]) {
  const file=path.join(workspace,name);if(!fs.existsSync(file))fs.writeFileSync(file,text,{mode:0o600,flag:'wx'});
 }
 const profile=path.join(runtime,role+'.json');
 if(!fs.existsSync(profile))fs.writeFileSync(profile,JSON.stringify({status:provider?'AWAITING_REGISTRATION_AND_OFFLINE_VALIDATION':'AWAITING_LOCAL_ENGINE_CONFIGURATION',engine_support:{planner:'Open Duet',device:'agent-desktop',bridge:'DESKTOP/asistencia-sgacd'},profile:{name:'Wallet · '+role,instructions,provider:provider||null,workspace_path:workspace,approval_mode:'plan',memory_enabled:false,use_helper:false,make_lead:false}},null,2),{mode:0o600,flag:'wx'});
}
console.log('Ocho perfiles limitados preparados; no se registraron ni iniciaron modelos. Verifica un proveedor local antes de conectarlos a Open Duet.');
