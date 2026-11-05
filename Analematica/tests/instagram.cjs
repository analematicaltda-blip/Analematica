const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.ANALEMATICA_URL||'http://127.0.0.1:18090';
const actor=JSON.parse(fs.readFileSync(process.env.ANALEMATICA_SESSION_FILE));
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH,args:['--no-sandbox']});const errors=[];try{
for(const width of [1440,768,390,320]){
 const context=await browser.newContext({viewport:{width,height:1000},serviceWorkers:'block'});
 await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
 await context.addInitScript(actor=>{localStorage.setItem('accessToken',actor.token);localStorage.setItem('userRoles','["admin_general"]');localStorage.setItem('userId',String(actor.id));localStorage.setItem('userName',actor.name);},actor);
 const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/admin.html#tab-meta-ads');
 await page.waitForSelector('#tab-meta-ads.active');
 await page.waitForFunction(()=>document.getElementById('instagram-callback').value.includes('/instagram/oauth/callback'));
 assert.equal(await page.locator('#instagram-config-id').inputValue(),'1119082880751653');
 assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow '+width);
 assert.equal(await page.locator('#meta-webhook-token').getAttribute('type'),'password');
 const status=page.waitForResponse(r=>r.url().endsWith('/instagram/status'));
 await page.locator('#instagram-refresh').click();assert.equal((await status).status(),200);
 await page.waitForFunction(()=>document.getElementById('instagram-state').textContent.includes('Falta completar'));
 const rejected=page.waitForResponse(r=>r.url().endsWith('/instagram/oauth/start'));
 await page.locator('#instagram-authorize').click();assert.equal((await rejected).status(),409);
 assert.ok(page.url().startsWith(base));
 await context.close();
}
assert.deepEqual(errors,[]);console.log('PASS Instagram panel: 4 widths, owner auth, status, protected consent, masked verifier, no overflow or external requests.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
