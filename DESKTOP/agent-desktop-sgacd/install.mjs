import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {paths,source,provenance,verifyInstalled,digest,environment} from './runtime.mjs';
try{
 if(process.argv.slice(2).some(arg=>arg!=='--repair'))throw new Error('Opción desconocida. Usa --repair solo para reinstalar el runtime local.');
 const p=paths();
 if(fs.existsSync(p.metadata)&&!process.argv.includes('--repair')){
  const installed=verifyInstalled(p);if(!installed.ready)throw new Error(installed.reason);
  console.log(`agent-desktop ${installed.version} ya está verificado en este equipo.`);process.exit(0);
 }
 fs.mkdirSync(p.runtime,{recursive:true,mode:0o700});fs.mkdirSync(p.state,{recursive:true,mode:0o700});
 // Only the ignored runtime is replaced; the complete source copy stays untouched.
 fs.rmSync(p.packageDir,{recursive:true,force:true});fs.cpSync(path.join(source,'npm'),p.packageDir,{recursive:true});
 const env=environment(p);delete env.AGENT_DESKTOP_BINARY_PATH;delete env.AGENT_DESKTOP_MACOS_HELPER_PATH;env.AGENT_DESKTOP_SKIP_DOWNLOAD='0';
 const install=spawnSync(process.execPath,[path.join(p.packageDir,'BACKEND/tools/postinstall.js')],{env,stdio:'inherit',timeout:150000,windowsHide:true});
 if(install.error||install.status!==0)throw new Error('No se pudo descargar/verificar el runtime oficial. No se activó el conector.');
 const version=spawnSync(p.binary,['version'],{env,encoding:'utf8',timeout:10000,windowsHide:true});
 if(version.error||version.status!==0)throw new Error('El binario descargado no puede ejecutarse en este sistema.');
 const reply=JSON.parse(version.stdout);
 if(reply.ok!==true||reply.data?.version!==provenance.release_version)throw new Error('La versión del ejecutable no coincide con la copia fijada.');
 const hashes=Object.fromEntries([p.binary,...p.helpers].map(file=>[path.basename(file),digest(file)]));
 fs.writeFileSync(p.metadata,JSON.stringify({version:provenance.release_version,source_commit:provenance.commit,platform:p.platform,arch:p.arch,hashes},null,2)+'\n',{mode:0o600});
 console.log(`Runtime ${provenance.release_version} instalado y verificado. No se abrió ningún puerto ni se actuó sobre el escritorio.`);
}catch(error){console.error(error.message);process.exitCode=1;}
