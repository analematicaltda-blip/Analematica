/* Static capture assets only. Never cache sessions, APIs or authorization. */
'use strict';
const ASSETS={"editor.js": "8632251aa05cb7b5d7c1b8d08018e29a496cebaedde4432ee44e14fc55f33b7d", "index.html": "aa7daf35307f05d8d4ea80ba584e5c1b2dae95582e8c3df5b98dfe083c52bc81", "style.css": "319fd51fbc470baba98e5568e0008b86a4287e83a53f047b4b7edbdbdd9da567", "vault.js": "032e8d38d0ac98af4488ef226e5921bd43d4c1b0392ffd6025ea840093fdcacb"},CACHE='sga-cd-commercial-offline-9482e655afebd7386e37',BASE=new URL('./',self.location.href);
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
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const name of await caches.keys())if(name.startsWith('sga-cd-commercial-offline-')&&name!==CACHE)await caches.delete(name);await self.clients.claim();})()));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);if(event.request.method!=='GET'||url.origin!==BASE.origin||url.search||url.hash)return;
 const name=url.pathname===BASE.pathname?'index.html':url.pathname.startsWith(BASE.pathname)?url.pathname.slice(BASE.pathname.length):null;
 if(!Object.hasOwn(ASSETS,name))return;
 event.respondWith((async()=>{const response=await (await caches.open(CACHE)).match(new URL(name,BASE).href);return response||new Response('Capturador no disponible: reinstala con conexión.',{status:503,headers:{'Content-Type':'text/plain;charset=utf-8'}});})());
});
