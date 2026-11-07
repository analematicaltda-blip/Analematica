/* Real local central login, read-only resource browsing, no provider calls or telemetry transmission. */
const fs=require('node:fs'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.ASSISTANCE_URL||'https://localhost:8101',account=JSON.parse(fs.readFileSync(process.env.ASSISTANCE_ACCESS_FILE)),views=JSON.parse(fs.readFileSync(process.env.ASSISTANCE_VIEW_FILE)),view=views[process.env.ASSISTANCE_SITE||'analematica'];
const args=['--no-sandbox'];if(process.env.ASSISTANCE_CERT_FILE){const cert=new crypto.X509Certificate(fs.readFileSync(process.env.ASSISTANCE_CERT_FILE));args.push('--ignore-certificate-errors-spki-list='+crypto.createHash('sha256').update(cert.publicKey.export({type:'spki',format:'der'})).digest('base64'));}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args});const errors=[];let token;
 try{
  for(const width of [1440,390,320]){
   const context=await browser.newContext({httpCredentials:view,viewport:{width,height:1000},serviceWorkers:'block'});
   await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
   if(token)await context.addInitScript(value=>localStorage.setItem('accessToken',value),token);
   const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));await page.goto(base+'/resources.html',{waitUntil:'networkidle'});
   if(!token){assert.match(await page.locator('#status').innerText(),/Ingresa con tu cuenta/);const login=await page.evaluate(async credentials=>{const r=await fetch('/api/v1/workspace/corporate/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(credentials)});const data=await r.json();if(r.ok)localStorage.setItem('accessToken',data.access_token);return {status:r.status,token:r.ok?data.access_token:null}},account);assert.equal(login.status,200);token=login.token;await page.reload({waitUntil:'networkidle'});}
   await page.waitForFunction(()=>!document.getElementById('search').disabled);assert.equal(await page.locator('#category option').count(),16);assert.equal(await page.locator('#providers article').count(),102);assert.match(await page.locator('#soc-state').innerText(),/no verificado/);
   await page.selectOption('#category','video');await page.fill('#query','replicate');await page.click('#search');await page.waitForFunction(()=>document.querySelectorAll('#providers article').length===1);assert.match(await page.locator('#providers h3').innerText(),/Replicate/);
   assert.match(await page.locator('#providers article').innerText(),/Sin activar/);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow at '+width);
   // Download is explicit and remains inside the browser process; do not persist audit data.
   const responsePromise=page.waitForResponse(r=>r.url().includes('/security/control-audit-export'));await page.click('#export');const response=await responsePromise;assert.equal(response.status(),200);const bundle=await response.json();assert.equal(bundle.algorithm,'Ed25519');const payload=JSON.parse(bundle.payload);assert.equal(payload.transport,'manual_not_sent');assert(!bundle.payload.includes('confirmation_phrase'));await page.waitForFunction(()=>document.getElementById('export-state').innerText.includes('No se enviaron'));
   await context.close();
  }
  assert.deepEqual(errors,[]);console.log('Resources UI passed at 1440/390/320: real central login, catalog/filtering, unverified SOC state and explicit signed local export. External requests blocked.');
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exitCode=1});
