import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {root} from './bridge.mjs';
const manifest=JSON.parse(fs.readFileSync(path.join(root,'open-duet-upstream.json'),'utf8'));
const source=path.resolve(root,manifest.source_copy);
if(fs.existsSync(path.join(source,'.git')))throw Error('La copia no debe contener metadatos .git.');
for(const item of manifest.files){
 const file=path.resolve(source,item.path);if(!file.startsWith(source+path.sep))throw Error('Ruta no permitida.');
 const data=item.mode==='120000'?Buffer.from(fs.readlinkSync(file)):fs.readFileSync(file);
 if(crypto.createHash('sha256').update(data).digest('hex')!==item.sha256)throw Error('La copia cambió: '+item.path);
}
console.log(`${manifest.files.length} archivos de Open Duet verificados; ${manifest.license}; ${manifest.commit}.`);
