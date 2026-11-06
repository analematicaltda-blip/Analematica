import fs from 'node:fs';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {source,provenance} from './runtime.mjs';
let failed=0;
for(const file of provenance.files){
 const target=path.resolve(source,file.path);
 if(!target.startsWith(source+path.sep)){console.error('Ruta de inventario inválida.');process.exit(1);}
 try{
  const stat=fs.lstatSync(target);
  // Git on Windows can materialize an internal compatibility symlink as its text.
  const data=file.mode==='120000'&&stat.isSymbolicLink()?Buffer.from(fs.readlinkSync(target)):fs.readFileSync(target);
  const hash=createHash('sha256').update(data).digest('hex');
  if(hash!==file.sha256){console.error('Contenido distinto:',file.path);failed++;}
 }catch{console.error('Archivo ausente:',file.path);failed++;}
}
if(fs.existsSync(path.join(source,'.git'))){console.error('La copia debe ser código incorporado, sin repositorio Git anidado.');failed++;}
if(!failed)console.log(`${provenance.files.length} entradas de origen verificadas; licencia ${provenance.license}; commit ${provenance.commit}.`);
process.exitCode=failed?1:0;
