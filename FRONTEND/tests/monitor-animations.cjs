const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');const assert=require('node:assert/strict');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18080';
const gsapDir=process.env.GSAP_DIST||'/tmp/sgacd-ui-tests/node_modules/gsap/dist';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 try {
  for(const empty of [false,true]){
   const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'no-preference',serviceWorkers:'block'});
   await page.route('**/*',async r=>{
    const u=new URL(r.request().url());
    if(process.env.SGA_MAIN_OVERRIDE && u.pathname.endsWith('/main.js'))return r.fulfill({contentType:'text/javascript',body:fs.readFileSync(process.env.SGA_MAIN_OVERRIDE)});
    if(u.pathname.endsWith('/gsap.min.js'))return r.fulfill({contentType:'text/javascript',body:fs.readFileSync(gsapDir+'/gsap.min.js')});
    if(u.pathname.endsWith('/ScrollTrigger.min.js'))return r.fulfill({contentType:'text/javascript',body:fs.readFileSync(gsapDir+'/ScrollTrigger.min.js')});
    if(u.pathname.endsWith('/public/landing')){await new Promise(resolve=>setTimeout(resolve,1200));return r.fulfill({json:{}})}
    if(u.pathname.endsWith('/public/events'))return r.fulfill(empty?{json:[]}:{status:503,json:{detail:'offline'}});
    if(u.origin!==new URL(base).origin)return r.abort();
    return r.continue();
   });
   await page.goto(base+'/index.html');
   await page.waitForFunction(()=>typeof gsap!=='undefined' && typeof ScrollTrigger!=='undefined');
   await page.waitForSelector('#features-grid .feature-card');
   await page.locator('#monitor-vivo').scrollIntoViewIfNeeded();
   await page.waitForTimeout(1000);
   if(!empty){
    assert.equal(await page.locator('.monitor-card').count(),4);
    const opacity=await page.locator('.monitor-card').evaluateAll(nodes=>nodes.map(n=>Number(getComputedStyle(n).opacity)));
    assert.ok(opacity.every(value=>value>.95),'Monitor cards must be visible before reaching the Modules trigger: '+opacity);
   } else {
    assert.equal(await page.locator('.monitor-card').count(),0);
    const height=(await page.locator('#monitor-grid').boundingBox()).height;
    assert.ok(height<120,'Empty monitor must not reserve card-height whitespace');
   }
   console.log('PASS real GSAP/ScrollTrigger:',empty?'compact empty feed':'all monitor cards visible');
   await page.close();
  }
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
