const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const expectedPending=JSON.parse(fs.readFileSync(path.join(__dirname,'../web/pending.json'),'utf8')).filter(item=>item.status!=='CERRADO');
const {chromium}=require('playwright');
(async()=>{
 let ready=false;for(let attempt=0;attempt<50;attempt++){try{ready=(await fetch('http://127.0.0.1:8556/')).ok;}catch{}if(ready)break;await new Promise(resolve=>setTimeout(resolve,100));}assert.ok(ready,'Local preview not ready');
 const browser=await chromium.launch({headless:true,...(process.env.WALLET_TEST_CHROMIUM?{executablePath:process.env.WALLET_TEST_CHROMIUM}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1180,height:900}});const remote=[];const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',route=>{const host=new URL(route.request().url()).hostname;if(host==='127.0.0.1')return route.continue();remote.push(host);return route.abort();});
 const response=await page.goto('http://127.0.0.1:8556',{waitUntil:'networkidle'});assert.equal(response.status(),200);
 await page.waitForFunction(()=>document.querySelector('#team-count').textContent==='8');
 assert.ok(response.headers()['content-security-policy'].includes("connect-src 'self'"));
 assert.equal(await page.locator('input[type=password]').count(),0);assert.equal(await page.locator('#pending-count').innerText(),String(expectedPending.length));
 await page.getByRole('button',{name:'Equipo',exact:true}).click();assert.equal(await page.locator('#team .card:visible').count(),8);
 await page.getByRole('button',{name:'Pendientes de producción',exact:true}).click();assert.equal(await page.locator('#pending .pending-item:visible').count(),expectedPending.length);
 if(expectedPending.length){await page.getByRole('searchbox').fill(expectedPending[0].id);assert.equal(await page.locator('#pending .pending-item:visible').count(),1);}
 for(const path of ['/private-wallet/workspace.sqlite3','/api/v1/finance/wallet/','/%2e%2e/AGENTS.md'])assert.equal((await page.request.get('http://127.0.0.1:8556'+path)).status(),404);
 await page.getByRole('button',{name:'Resumen',exact:true}).click();await page.screenshot({path:process.env.WALLET_TEST_SCREENSHOT||'/tmp/wallet-preview.png',fullPage:true});
 await page.setViewportSize({width:390,height:844});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
 assert.deepEqual(remote,[]);assert.deepEqual(errors,[]);await browser.close();
 console.log('Browser passed: eight agents, pending register, search, mobile layout, no secret fields or private routes, zero external requests.');
})().catch(error=>{console.error(error.message);process.exit(1)});
