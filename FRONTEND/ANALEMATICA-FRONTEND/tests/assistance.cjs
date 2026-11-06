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
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args});let token,sessionId;const errors=[];
 try{
  for(const width of [1440,390,320]){
   const context=await browser.newContext({httpCredentials:view,viewport:{width,height:1000},serviceWorkers:'block'});
   await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
   if(token)await context.addInitScript(value=>localStorage.setItem('accessToken',value),token);
   const page=await context.newPage();page.on('pageerror',error=>errors.push(error.message));
   await page.goto(base+'/assistance.html',{waitUntil:'networkidle'});
   if(!token){
    assert.match(await page.locator('#message').innerText(),/Ingresa al sistema/);
    const result=await page.evaluate(async account=>{const r=await fetch('/api/v1/workspace/corporate/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(account)});const data=await r.json();if(r.ok)localStorage.setItem('accessToken',data.access_token);return {status:r.status,token:r.ok?data.access_token:null};},credentials);
    assert.equal(result.status,200);token=result.token;await page.reload({waitUntil:'networkidle'});
   }
   await page.waitForFunction(()=>!document.getElementById('start').disabled);
   assert.equal(await page.locator('#platform option').count(),4);
   await page.selectOption('#platform','meta');await page.selectOption('#workflow','meta.campaign');
   if(!sessionId){
    const pending=page.waitForResponse(r=>r.url().endsWith('/api/v1/assistance/sessions')&&r.request().method()==='POST');
    await page.click('#start');sessionId=(await(await pending).json()).id;
   }else{await page.locator('#sessions button').filter({hasText:'Crear campaña'}).first().click();}
   await page.waitForSelector('#guide:not([hidden])');assert.match(await page.locator('#progress').innerText(),/Paso 1/);
   assert.equal(await page.locator('#advance').isDisabled(),true);assert.equal(await page.locator('#ask').isDisabled(),true);
   assert.ok((await page.locator('#official').getAttribute('href')).startsWith('https://business.facebook.com/'));
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow at '+width);
   if(process.env.ASSISTANCE_SCREENSHOT_DIR){fs.mkdirSync(process.env.ASSISTANCE_SCREENSHOT_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.ASSISTANCE_SCREENSHOT_DIR,'assistance-'+width+'.png'),fullPage:true});}
   await context.close();
  }
  assert.deepEqual(errors,[]);console.log('Assistance UI passed at 1440, 390 and 320px: real login, private persisted guide, required checklist and no external calls.');
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exitCode=1});
