/* Local integration smoke: real SGA login, no mocks and no external platform calls. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const base=process.env.ASSISTANCE_URL||'https://localhost:8101';
const credentials=JSON.parse(fs.readFileSync(process.env.ASSISTANCE_ACCESS_FILE));
const preview=JSON.parse(fs.readFileSync(process.env.ASSISTANCE_VIEW_FILE));
const view=preview[process.env.ASSISTANCE_SITE||'analematica'];
const args=['--no-sandbox'];
if(process.env.ASSISTANCE_CERT_FILE){const cert=new crypto.X509Certificate(fs.readFileSync(process.env.ASSISTANCE_CERT_FILE));args.push('--ignore-certificate-errors-spki-list='+crypto.createHash('sha256').update(cert.publicKey.export({type:'spki',format:'der'})).digest('base64'));}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args});const errors=[];
 try{
  for(const width of [1440,390,320]){
   const context=await browser.newContext({httpCredentials:view,viewport:{width,height:1000},serviceWorkers:'block'});
   await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
   const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));await page.goto(base+'/control.html',{waitUntil:'networkidle'});
   assert.match(await page.locator('#status').innerText(),/Ingresa con tu cuenta/);
   const login=await page.evaluate(async account=>{const r=await fetch('/api/v1/workspace/corporate/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(account)});const data=await r.json();if(r.ok)localStorage.setItem('accessToken',data.access_token);return r.status;},credentials);assert.equal(login,200);
   await page.reload({waitUntil:'networkidle'});await page.waitForFunction(()=>!document.getElementById('pair').disabled);await page.click('#pair');await page.waitForFunction(()=>document.getElementById('pair-code').innerText.includes('vence'));
   const device=await page.evaluate(async()=>{const code=document.getElementById('pair-code').innerText.split(' ')[0];const r=await fetch('/api/v1/assistance/control/claim',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pairing_code:code,name:'Isolated UI test — no executor',kind:'desktop'})});const d=await r.json();return {status:r.status,id:d.device_id};});assert.equal(device.status,201);
   await page.click('#refresh');await page.waitForSelector('#device option[value="'+device.id+'"]',{state:'attached'});await page.selectOption('#device',device.id);await page.selectOption('#operation','desktop_status');await page.fill('#purpose','Prueba local de revisión; no ejecutar');await page.click('#propose');await page.waitForFunction(()=>document.getElementById('job-state').innerText.includes('0/2'));
   for(const stage of [1,2]){const phrase=await page.locator('#expected').innerText();await page.fill('#phrase',phrase);await page.click('#authorize');await page.waitForFunction(n=>document.getElementById('job-state').innerText.includes(n+'/2'),stage);}
   assert.match(await page.locator('#job-state').innerText(),/approved/);await page.click('#stop');await page.waitForFunction(()=>document.getElementById('job-state').innerText.includes('cancelled'));await page.click('#revoke');await page.waitForFunction(()=>document.getElementById('status').innerText.includes('revocado'));
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow at '+width);await context.close();
  }
  assert.deepEqual(errors,[]);console.log('Control UI passed at 1440, 390 and 320px: central login, pairing, separate same-admin approvals, stop and revoke; no executor/provider actions.');
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exitCode=1});
