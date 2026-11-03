const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
const source=process.env.SGA_SW_FILE || 'SGA-CD-WEB.git/service-worker.js';
(async()=>{
 const listeners={},entries=new Map();let skipped=false,claimed=false,offline=false;
 const key=r=>typeof r==='string'?r:r.url;
 const cache={addAll:async()=>{},put:async(r,v)=>entries.set(key(r),v),match:async r=>entries.get(key(r))};
 const self={location:{origin:'http://localhost'},addEventListener:(n,f)=>listeners[n]=f,skipWaiting:async()=>{skipped=true},clients:{claim:async()=>{claimed=true}}};
 vm.runInNewContext(fs.readFileSync(source,'utf8'),{self,URL,Request,Response,console,caches:{open:async()=>cache,keys:async()=>[],delete:async()=>true,match:async r=>entries.get(key(r))},fetch:async()=>{if(offline)throw Error('Offline');return new Response('fresh',{status:200})}});
 let pending;listeners.install({waitUntil:p=>pending=p});await pending;assert.ok(skipped,'New worker must activate immediately');
 listeners.activate({waitUntil:p=>pending=p});await pending;assert.ok(claimed,'Worker must claim open clients');
 const request=new Request('http://localhost/js/main.js');entries.set(request.url,new Response('stale'));
 let response;listeners.fetch({request,respondWith:p=>response=p});assert.equal(await (await response).text(),'fresh','Scripts must refresh from network');
 offline=true;listeners.fetch({request,respondWith:p=>response=p});assert.equal(await (await response).text(),'fresh','Previously refreshed script remains available offline');
 let intercepted=false;listeners.fetch({request:new Request('http://localhost/api/v1/private'),respondWith:()=>intercepted=true});assert.equal(intercepted,false,'API data must not be cached');
 listeners.fetch({request:new Request('http://localhost/private',{headers:{Authorization:'Bearer fixture'}}),respondWith:()=>intercepted=true});assert.equal(intercepted,false,'Authenticated responses must not be cached');
 console.log('PASS: worker activation, client claim, fresh scripts, offline cache and API/auth exclusion');
})().catch(e=>{console.error(e);process.exit(1)});
