/* Static capture assets only. Never cache sessions, APIs or authorization. */
'use strict';
const ASSETS={"editor.js": "471e8aeb36b5c842f00bd8e00a1661c2ed7d9cc44aed28984d9b28630d9b5b2b", "index.html": "aa7daf35307f05d8d4ea80ba584e5c1b2dae95582e8c3df5b98dfe083c52bc81", "style.css": "319fd51fbc470baba98e5568e0008b86a4287e83a53f047b4b7edbdbdd9da567", "vault.js": "19fe92d06223aaee9b02f650d8539258dc44b7d48a9cac5d36be774f8499f0af"},CACHE='analematica-commercial-offline-910514e21bf6d6532892',BASE=new URL('./',self.location.href);
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
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const name of await caches.keys())if(name.startsWith('analematica-commercial-offline-')&&name!==CACHE)await caches.delete(name);await self.clients.claim();})()));
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);if(event.request.method!=='GET'||url.origin!==BASE.origin||url.search||url.hash)return;
 const name=url.pathname===BASE.pathname?'index.html':url.pathname.startsWith(BASE.pathname)?url.pathname.slice(BASE.pathname.length):null;
 if(!Object.hasOwn(ASSETS,name))return;
 event.respondWith((async()=>{const response=await (await caches.open(CACHE)).match(new URL(name,BASE).href);return response||new Response('Capturador no disponible: reinstala con conexión.',{status:503,headers:{'Content-Type':'text/plain;charset=utf-8'}});})());
});
