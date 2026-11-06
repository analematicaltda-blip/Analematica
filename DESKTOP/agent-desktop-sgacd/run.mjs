import fs from 'node:fs';
import {spawn} from 'node:child_process';
import {paths,verifyInstalled,environment,provenance} from './runtime.mjs';
try{
 const p=paths(),installed=verifyInstalled(p),args=process.argv.slice(2);
 if(args[0]==='doctor'){
  console.log(JSON.stringify({platform:p.platform,arch:p.arch,source_commit:provenance.commit,release_version:provenance.release_version,runtime:installed,remote_runtime:Boolean(process.env.CODESPACES||process.env.CODESPACE_NAME||process.env.REMOTE_CONTAINERS),graphical_session_hint:p.platform!=='linux'||Boolean(process.env.DBUS_SESSION_BUS_ADDRESS),note:'El proceso controla el equipo donde se ejecuta. Codespaces no equivale al escritorio del portátil. La respuesta nativa de status determina las capacidades.'},null,2));
 }else{
  if(!installed.ready)throw new Error(installed.reason);
  if(!args.length)throw new Error('Indica doctor, version, status, skills get desktop, skills get platform, mcp o un comando nativo.');
  fs.mkdirSync(p.state,{recursive:true,mode:0o700});
  const child=spawn(p.binary,args,{env:environment(p),stdio:'inherit',shell:false,windowsHide:true});
  child.on('error',()=>{console.error('No se pudo iniciar agent-desktop.');process.exitCode=1;});
  child.on('exit',(code,signal)=>{process.exitCode=code??(signal?1:0);});
  for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>child.kill(signal));
 }
}catch(error){console.error(error.message);process.exitCode=1;}
