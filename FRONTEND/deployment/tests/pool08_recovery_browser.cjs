/* Actual owned browser code with controlled transport faults; no backend/provider acceptance. */
const {chromium}=require('playwright'),assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs');
const root=path.resolve(__dirname,'../../..');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});let checks=0;try{
for(const [system,folder] of [['sga-cd','FRONTEND/SGA-CD-WEB.git'],['erp-tur','FRONTEND/SGA-ERP-TUR-FRONTEND/public'],['analematica','FRONTEND/ANALEMATICA-FRONTEND']]){
 for(const kind of ['landing','library']){
 const page=await browser.newPage({viewport:{width:390,height:1000}});await page.route('http://127.0.0.1:49321/**',r=>r.fulfill({contentType:'text/html',body:'<!doctype html><main id="root"></main>'}));await page.goto('http://127.0.0.1:49321');await page.addScriptTag({path:path.join(root,folder,'js/commercial-'+(kind==='landing'?'landings':'library')+'.js')});
 await page.evaluate(({system,kind})=>{
  const state=window.testState={posts:0,receipts:0,failRead:false,failReceiptRead:false,requestIds:[],provider:'provider-A'};
  const landing={id:'landing-A',code:'demo-page',revision:1,status:'DRAFT',published_version:null,versions:[{number:1,content:{brand:'Marca',title:'Propuesta',description:'Servicios',template:'SERVICIOS',blocks:[{kind:'HERO',heading:'Bienvenidos',body:'Texto',url:'',label:''}]}}]};
  const library={id:'library-A',title:'Original privado',revision:1,status:'PRIVATE',published_version:null,versions:[{number:1,title:'Original privado',brand:{name:'Marca',tagline:'Lema',template:'SQUARE'},rights:{holder:'Titular',license:'OWNED',reference:'Declaración sintética',public_web:true,valid_until:null},original_sha256:'a'.repeat(64),delivery_sha256:'b'.repeat(64),media:{kind:'IMAGE'}}]};
  const result=()=>kind==='landing'?{landing_id:landing.id,revision:landing.revision}:{item_id:library.id,revision:library.revision};
  window.mountTest=provider=>{state.provider=provider;document.querySelector('#root').replaceChildren();return (kind==='landing'?Pool08Landings:Pool08Library).mount(document.querySelector('#root'),{context:{system,tenant_ref:'company-A',actor_ref:'actor-A',company_name:'Marca'},native:system!=='sga-cd',provider,request:async(p,o={})=>{
   let value;if(p==='landing-commands'||p==='library-commands'){state.posts++;const b=JSON.parse(o.body);state.requestIds.push(b.request_id);if(state.failBeforeCommitOnce){state.failBeforeCommitOnce=false;throw Error('Solicitud sin acuse sintética');}if(kind==='landing')landing.revision++;else library.revision++;state.failRead=true;value=result();}
   else if(p.includes('-receipts/')){state.receipts++;state.failReceiptRead=true;value=result();}
   else if(p==='landings/'+landing.id||p==='library/'+library.id){if(state.failRead||state.failReceiptRead){state.failRead=false;state.failReceiptRead=false;throw Error('Interrupción sintética al cargar el resultado');}value=kind==='landing'?landing:library;}
   else if(p.startsWith('landings?'))value={pages:[landing],next_offset:null};
   else if(p.startsWith('library?'))value={items:[library],usage:{originals:1,max_originals:200,bytes:100,max_bytes:10000},next_offset:null};
   else if(p.startsWith('prices?'))value={items:[],next_offset:null};else throw Error('Unexpected request '+p);
   return new Response(JSON.stringify(value),{status:200,headers:{'Content-Type':'application/json'}});
  }});};window.disposeTest=window.mountTest('provider-A');
 },{system,kind});
 const prefix=kind==='landing'?'landing':'library';await page.locator('[data-'+prefix+'-list] button').first().click();
 if(kind==='landing'){await page.locator('[data-landing-form] [name=title]').fill('Nueva versión');await page.locator('[data-landing-form] button').filter({hasText:'Guardar nueva versión'}).click();}
 else{await page.locator('[data-library-form] [name=title]').fill('Nueva versión');await page.locator('[data-library-revise]').click();}
 await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Interrupción sintética'}).waitFor();
 assert.equal(await page.evaluate(()=>Object.keys(sessionStorage).length),1,'Receipt reference must survive committed operation followed by read failure');checks++;
 // Retrying a confirmed command must only reload its result, without another POST.
 await page.locator('[data-'+prefix+'-retry]').click();await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Resultado confirmado'}).waitFor();assert.equal(await page.evaluate(()=>testState.posts),1);assert.equal(await page.evaluate(()=>Object.keys(sessionStorage).length),0);checks+=2;
 // After remount, a different command cannot replace an unresolved UUID; an exact retry reuses it.
 await page.evaluate(()=>{testState.failBeforeCommitOnce=true;});
 async function revise(title){await page.locator('[data-'+prefix+'-form] [name=title]').fill(title);await page.locator(kind==='landing'?'[data-landing-form] button':'[data-library-revise]').filter({hasText:kind==='landing'?'Guardar nueva versión':'Guardar derechos'}).click();}
 await revise('Reintento exacto');await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Solicitud sin acuse sintética'}).waitFor();
 await page.evaluate(()=>{window.disposeTest();window.disposeTest=window.mountTest('provider-A');});await page.locator('[data-'+prefix+'-list] button').first().click();await revise('Otra intención');await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Hay otro envío pendiente.'}).waitFor();assert.equal(await page.evaluate(()=>testState.posts),2);checks++;
 await revise('Reintento exacto');await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Interrupción sintética'}).waitFor();assert.equal(await page.evaluate(()=>testState.requestIds[1]===testState.requestIds[2]),true);checks++;
 await page.locator('[data-'+prefix+'-retry]').click();await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Resultado confirmado'}).waitFor();assert.equal(await page.evaluate(()=>testState.posts),3);checks++;
 // A failed recovery read must also preserve the hint and reset busy controls.
 // Provider-scoped recovery keys are checked with isolated remounts; no real token stored.
 await page.evaluate(({system,kind})=>{sessionStorage.clear();sessionStorage.setItem('pool08-'+kind+':'+system+':company-A:provider-A:actor-A',JSON.stringify({request_id:'pending-A'}));window.disposeTest();window.disposeTest=window.mountTest('provider-B');},{system,kind});
 await page.locator('[data-'+prefix+'-recover]').click();await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Sin petición pendiente.'}).waitFor();assert.equal(await page.evaluate(()=>testState.receipts),0,'Other provider must not consume a pending receipt');checks++;
 await page.evaluate(()=>{window.disposeTest();window.disposeTest=window.mountTest('provider-A');});await page.locator('[data-'+prefix+'-recover]').click();await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Interrupción sintética'}).waitFor();assert.equal(await page.evaluate(()=>Object.keys(sessionStorage).length),1);assert.equal(await page.locator('[data-'+prefix+'-recover]').isEnabled(),true);checks+=2;
 await page.locator('[data-'+prefix+'-retry]').click();await page.locator(kind==='landing'?'[data-landing-feedback]':'[data-library-status]').filter({hasText:'Resultado confirmado'}).waitFor();assert.equal(await page.evaluate(()=>Object.keys(sessionStorage).length),0);checks++;
 await page.close();
 }
}
const report={passed:true,checks,systems:3,controlled_transport:true,backend_acceptance:false};const out=process.env.GC_RECOVERY_BROWSER_OUTPUT||'/tmp/gc-recovery-browser-artifacts';fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}})().catch(e=>{console.error(e.stack);process.exitCode=1;});
