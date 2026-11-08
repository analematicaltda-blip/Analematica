/* Local, explicitly started companion. No inbound port, shell tool or auto approvals. */
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline/promises';
import {root} from './bridge.mjs';
import {request,verifyGrant,validateDispatch} from './control-client.mjs';
import {BrowserDriver} from './browser-driver.mjs';
import {MobileDriver} from './mobile-driver.mjs';

const args=process.argv.slice(2),command=args[0];
const option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1]};
const kind=option('--kind','desktop');if(!['desktop','android','ios'].includes(kind))throw Error('Tipo de dispositivo no válido.');
const runtime=path.join(root,'.runtime');fs.mkdirSync(runtime,{recursive:true,mode:0o700});
const profile=path.resolve(option('--profile',path.join(runtime,'device-'+kind+'.json')));
function writePrivate(file,value){fs.writeFileSync(file,JSON.stringify(value,null,2),{mode:0o600});fs.chmodSync(file,0o600)}
if(command==='pair'){
 if(fs.existsSync(profile))throw Error('Ya existe una vinculación. No se sobrescribió. Revócala desde el panel si necesitas reemplazarla.');
 const origin=option('--backend',''),caFile=option('--ca',undefined),udid=option('--udid',undefined);
 if(kind!=='desktop'&&!udid)throw Error('Para un móvil debes seleccionar explícitamente --udid en su host local.');
 const io=readline.createInterface({input:process.stdin,output:process.stdout});let code;
 try{code=(await io.question('Código de vinculación creado por tu administrador: ')).trim()}finally{io.close()}
 const result=await request(origin,'/claim',{body:{pairing_code:code,name:option('--name','Equipo autorizado'),kind},caFile});
 const config={...result,origin,caFile,udid,appium_url:option('--appium','http://127.0.0.1:4723/'),xcode_org_id:option('--xcode-team',undefined)};
 fs.mkdirSync(path.dirname(profile),{recursive:true,mode:0o700});writePrivate(profile,config);
 console.log('Equipo vinculado. La vinculación no autoriza acciones. Para habilitar el ejecutor local usa run --allow-control.');
}else if(command==='run'){
 if(!args.includes('--allow-control'))throw Error('Falta --allow-control: el operador local debe habilitar expresamente el ejecutor.');
 const config=JSON.parse(fs.readFileSync(profile,'utf8')),directory=path.join(runtime,'device-'+config.device_id);fs.mkdirSync(directory,{recursive:true,mode:0o700});
 const driver=config.kind==='desktop'?new BrowserDriver(directory):new MobileDriver(config);
 const journalFile=path.join(directory,'consumed.json'),journal=fs.existsSync(journalFile)?JSON.parse(fs.readFileSync(journalFile,'utf8')):{};
 let running=true;process.on('SIGINT',()=>{running=false});process.on('SIGTERM',()=>{running=false});
 console.log('Ejecutor habilitado. Espera planes firmados con al menos dos autorizaciones del administrador solicitante. Ctrl+C detiene nuevas acciones.');
 const api=(route,body)=>request(config.origin,route,{body,token:config.device_token,caFile:config.caFile});
 try{
  while(running){
   let queue;try{queue=await api('/device/queue')}catch(error){if(error.status===401||error.status===403)throw Error('La vinculación fue revocada o la cuenta ya no está autorizada.');console.error('Conexión no disponible; no se ejecutó ninguna acción.');await new Promise(r=>setTimeout(r,3000));continue}
   for(const item of queue.jobs??[]){
    if(!running)break;if(!/^[a-f0-9-]{36}$/.test(item.id)||journal[item.id])continue;
    let verified;
    try{const envelope=await api('/device/jobs/'+item.id+'/begin',{});verified=verifyGrant(envelope,config);if(verified.intent.job_id!==item.id)throw Error('La orden firmada no coincide con la cola.')}catch(error){console.error('Permiso de operación rechazado. No se ejecutó.');continue}
    if(!running)break;
    journal[item.id]={lease:verified.grant.lease_id,at:Date.now()};
    const entries=Object.entries(journal).sort((a,b)=>b[1].at-a[1].at).slice(0,2000);for(const key of Object.keys(journal))delete journal[key];Object.assign(journal,Object.fromEntries(entries));
    // Consume before dispatch. Crash/timeout does not replay an external change.
    const temporary=journalFile+'.tmp';writePrivate(temporary,journal);fs.renameSync(temporary,journalFile);
    let outcome='not_delivered',data,authorized=false;
    try{await validateDispatch(verified,lease=>api('/device/jobs/'+item.id+'/checkpoint',{lease_id:lease}));authorized=true}catch{data={notice:'No se confirmó la vigencia antes del despacho. No se ejecutó la acción.',automatic_retry:false}}
    if(authorized){
     try{data=await driver.run(verified.intent);outcome='delivered'}catch(error){outcome='uncertain';data={notice:String(error.message).slice(0,400),automatic_retry:false}}
    }
    try{await api('/device/jobs/'+item.id+'/result',{lease_id:verified.grant.lease_id,outcome,data})}catch{console.error('No se pudo registrar el resultado. Comprueba la plataforma antes de crear otra orden. No se repetirá automáticamente.');}
    console.log('Operación terminada:',outcome,'· el éxito en el proveedor requiere comprobación.');
   }
   if(running)await new Promise(r=>setTimeout(r,2000));
  }
 }finally{await driver.close().catch(()=>{});console.log('Ejecutor detenido. No deshace acciones ya entregadas.');}
}else if(command==='doctor'){
 const result={node:process.version,platform:process.platform,kind,paired:fs.existsSync(profile),needs:kind==='ios'?['Mac con Xcode y firma WebDriverAgent','Appium local y dispositivo confiado']:kind==='android'?['Appium local, Android SDK y Java','USB debugging autorizado y UDID explícito']:['Chrome local y perfil de navegador separado']};
 console.log(JSON.stringify(result,null,2));
}else{console.log('Uso: node device.mjs pair|run|doctor --kind desktop|android|ios [--backend https://...] [--ca certificado] [--udid ID] [--allow-control]');}
