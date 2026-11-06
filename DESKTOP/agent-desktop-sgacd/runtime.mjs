import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
export const root=path.dirname(fileURLToPath(import.meta.url));
export const source=path.resolve(root,'../agent-desktop');
export const provenance=JSON.parse(fs.readFileSync(path.join(root,'upstream.json'),'utf8'));
const require=createRequire(import.meta.url);
const platforms=require(path.join(source,'npm/lib/platform.js'));
export function paths(platform=process.platform,arch=process.arch){
 const entry=platforms.resolve(platform,arch);
 if(!entry?.released)throw new Error(`Plataforma no soportada: ${platform}-${arch}`);
 const runtime=path.join(root,'.runtime'),packageDir=path.join(runtime,'package');
 return {runtime,packageDir,state:path.join(runtime,'state'),metadata:path.join(runtime,'installed.json'),binary:path.join(packageDir,'bin',entry.binaryName),helpers:platforms.helperNames(entry).map(name=>path.join(packageDir,'bin',name)),platform,arch};
}
export const digest=file=>createHash('sha256').update(fs.readFileSync(file)).digest('hex');
export function verifyInstalled(p=paths()){
 if(!fs.existsSync(p.metadata))return {ready:false,reason:'Ejecuta node DESKTOP/agent-desktop-sgacd/install.mjs en este equipo.'};
 const installed=JSON.parse(fs.readFileSync(p.metadata,'utf8'));
 if(installed.version!==provenance.release_version||installed.platform!==p.platform||installed.arch!==p.arch)return {ready:false,reason:'El runtime pertenece a otra versión o plataforma.'};
 for(const file of [p.binary,...p.helpers]){
  if(!fs.existsSync(file)||!fs.lstatSync(file).isFile()||installed.hashes[path.basename(file)]!==digest(file))return {ready:false,reason:'El runtime está incompleto o cambió su integridad. Reinstálalo explícitamente con --repair.'};
 }
 return {ready:true,version:installed.version};
}
export function environment(p=paths()){
 // Isolate snapshots and sessions without replacing HOME, USERPROFILE or proxy credentials.
 return {...process.env,AGENT_DESKTOP_HOME:p.state};
}
