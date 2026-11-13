const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18080';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 try{
  for(const enabled of [false,true]){
   const context=await browser.newContext({serviceWorkers:'block'});
   const errors=[];const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   await context.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(u.pathname.endsWith('/sso/providers'))return r.fulfill({json:{google:enabled,microsoft:enabled}});
    if(u.pathname.endsWith('/start'))return r.fulfill({json:{flow_id:'test-flow',proof:'test-proof',expires_in:10,authorization_url:base+'/test-authorize'}});
    if(u.pathname.endsWith('/sso/result'))return r.fulfill({json:{status:'authenticated',access_token:'test-only-access',refresh_token:'test-only-refresh',user:{id:5,nombre:'Usuario autorizado',roles:['profesor'],inquilino_id:2}}});
    if(u.pathname.endsWith('/app.html')||u.pathname.endsWith('/test-authorize'))return r.fulfill({contentType:'text/html',body:'<!doctype html><title>SSO test</title>'});
    if(u.origin!==new URL(base).origin)return r.abort();return r.continue();
   });
   await page.goto(base+'/login.html');
   const google=page.locator('#google-login-btn');
   if(!enabled){await page.waitForFunction(()=>document.getElementById('login-mensaje').textContent.includes('aún no está habilitado'));assert.ok(await google.isDisabled());assert.ok(await page.locator('#microsoft-login-btn').isDisabled());}
   else{
    await google.waitFor();await page.waitForFunction(()=>!document.getElementById('google-login-btn').disabled);
    await page.locator('#password').fill('test-only-password');
    await google.click();await page.waitForURL('**/app.html');
    assert.equal(await page.evaluate(()=>localStorage.getItem('userRoles')),'["profesor"]');
    assert.equal(await page.evaluate(()=>localStorage.getItem('userId')),'5');
    assert.ok(!page.url().includes('access_token'));
   }
   assert.deepEqual(errors,[]);console.log('PASS OAuth browser',enabled?'shared broker and stored session':'unconfigured providers disabled');
   await context.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
