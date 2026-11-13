"""Build the same narrowly scoped offline capture shell for both web origins."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def install_assets(destination,source=None,prefix="sgacd-offline-capture"):
    destination=Path(destination)
    if destination.is_symlink():raise ValueError('Offline destination cannot be a symlink.')
    destination.mkdir(parents=True,exist_ok=True)
    destination.chmod(0o755)
    source=Path(source) if source else ROOT/'FRONTEND/ANALEMATICA-FRONTEND/contabilidad-offline'
    commercial=(source/'vault.js').is_file()
    assets={name:(source/name).read_bytes() for name in ['index.html','style.css' if commercial else 'editor.css','editor.js']}
    assets['vault.js']=(source/'vault.js' if commercial else ROOT/'FRONTEND/ANALEMATICA-FRONTEND/js/accounting-offline.js').read_bytes()
    manifest={name:hashlib.sha256(body).hexdigest() for name,body in assets.items()}
    version=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()[:20]
    worker="""/* Static capture assets only. Never cache sessions, APIs or authorization. */
'use strict';
const ASSETS=MANIFEST,CACHE='sgacd-offline-capture-VERSION',BASE=new URL('./',self.location.href);
self.addEventListener('install',event=>event.waitUntil((async()=>{
 const entries=await Promise.all(Object.entries(ASSETS).map(async([name,digest])=>{
  const url=new URL(name,BASE),response=await fetch(url,{credentials:'omit',cache:'no-store',redirect:'error'});
  const type=response.headers.get('Content-Type')||'',control=response.headers.get('Cache-Control')||'';
  if(!response.ok||response.type==='opaque'||/private|no-store/i.test(control)||!type.startsWith(name.endsWith('.html')?'text/html':name.endsWith('.css')?'text/css':'text/javascript')&&!type.startsWith(name.endsWith('.js')?'application/javascript':'never'))throw Error('Nonpublic capture asset');
  const bytes=await response.clone().arrayBuffer();if(bytes.byteLength>131072)throw Error('Asset too large');
  const actual=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
  if(actual!==digest)throw Error('Capture asset integrity mismatch');return [url.href,response];
 }));const cache=await caches.open(CACHE);for(const [url,response] of entries)await cache.put(url,response);
})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const name of await caches.keys())if(name.startsWith('sgacd-offline-capture-')&&name!==CACHE)await caches.delete(name);await self.clients.claim();})()));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);if(event.request.method!=='GET'||url.origin!==BASE.origin||url.search||url.hash)return;
 const name=url.pathname===BASE.pathname?'index.html':url.pathname.startsWith(BASE.pathname)?url.pathname.slice(BASE.pathname.length):null;
 if(!Object.hasOwn(ASSETS,name))return;
 event.respondWith((async()=>{const response=await (await caches.open(CACHE)).match(new URL(name,BASE).href);return response||new Response('Capturador no disponible: reinstala con conexión.',{status:503,headers:{'Content-Type':'text/plain;charset=utf-8'}});})());
});
""".replace('MANIFEST',json.dumps(manifest,sort_keys=True)).replace('VERSION',version).replace('sgacd-offline-capture',prefix)
    assets['worker.js']=worker.encode()
    for name,body in assets.items():
        path=destination/name
        if path.is_symlink():raise ValueError('Offline asset cannot overwrite a symlink.')
        path.write_bytes(body)
        path.chmod(0o644)
    return {'version':version,'assets':manifest,'scope':'/commercial-offline/' if commercial else '/contabilidad-offline/','api_cached':False}
