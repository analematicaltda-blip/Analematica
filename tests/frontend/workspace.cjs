const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18200';
const roles=['admin_general','admin_empresa','jefe_area','profesional_area','tecnico_area','coordinador','profesor','alumno','padre_acudiente','jefe_almacen','almacenista','jefe_escenarios'];
const token='test.'+Buffer.from(JSON.stringify({sub:'1',exp:Math.floor(Date.now()/1000)+3600})).toString('base64url')+'.test';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});
 let count=0;
 try{
 for(const width of [1440,768,390,320])for(const role of roles){
  const privileged=['admin_general','admin_empresa'].includes(role);const full=privileged||['jefe_area','coordinador','jefe_almacen','almacenista','jefe_escenarios','profesional_area','tecnico_area'].includes(role);
  const session={user:{id:1,name:'Cuenta '+role,roles:[role],tenant_id:1},organization:role==='admin_general'?'SGA-CD · Plataforma':'Empresa de prueba',scope:role==='admin_general'?'platform':'company',plan:full?'full':'basico',full_enabled:full,permissions:{crm:full,media:full,publish:full,inbox:full},manage_team:privileged,manage_channels:privileged};
  const page=await browser.newPage({viewport:{width,height:950},serviceWorkers:'block',reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));const requests=[];
  await page.addInitScript(({token,role})=>{localStorage.setItem('accessToken',token);localStorage.setItem('userRoles',JSON.stringify([role]));localStorage.setItem('userId','1');localStorage.setItem('userName','Cuenta '+role);localStorage.setItem('sgacd_cookie_consent','essential_only')},{token,role});
  await page.route('**/*',async r=>{
   const url=new URL(r.request().url());
   if(url.pathname.includes('/api/v1/workspace')){
    requests.push({url:url.pathname,headers:r.request().headers(),body:r.request().postData()});
    const path=url.pathname.split('/workspace')[1];let json={};
    if(path==='/session')json=session;
    else if(path==='/team')json={members:[{id:2,name:'Miembro de prueba',roles:['jefe_area'],active:true,delegable:true,permissions:{crm:false,media:false,publish:false,inbox:false}}],full_enabled:full};
    else if(path==='/studio/status')json={gemini_key_configured:false};
    else if(path==='/studio/script')json={text:'Guion validado mediante API interna'};
    else if(path==='/studio/reel')json={id:'asset',download_url:'/api/v1/workspace/assets/asset/download'};
    else if(path.endsWith('/download'))return r.fulfill({body:Buffer.from('test-video-placeholder'),contentType:'video/mp4'});
    else if(path==='/crm/leads')json={leads:[]};
    else if(path==='/assets')json={assets:[]};
    else if(path==='/inbox/status')json={channels:[],message:'Pendiente de autorización'};
    return r.fulfill({json});
   }
   if(url.pathname.includes('/api/'))return r.fulfill({json:[]});
   if(url.origin!==new URL(base).origin){if(url.pathname.endsWith('gsap.min.js'))return r.fulfill({path:(process.env.GSAP_DIST||'/tmp/sgacd-ui-tests/node_modules/gsap/dist')+'/gsap.min.js',contentType:'text/javascript'});return r.abort()}
   return r.continue();
  });
  await page.goto(base+'/app.html#/'+role+'/inicio');await page.waitForSelector('.workspace-summary');
  assert.equal(await page.locator('.workspace-eyebrow').textContent(),await page.evaluate(role=>SGAWorkspace.roles[role],role));
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'page overflow '+role+' '+width);
  if(width<=768){await page.waitForFunction(()=>document.querySelector('#app-sidebar').getBoundingClientRect().right<=1);await page.locator('#mobile-hamburger-btn').click();assert.equal(await page.locator('#app-sidebar').evaluate(e=>e.inert),false)}
  assert.equal(await page.locator('#app-nav .nav-submenu:not([hidden])').count(),0,'menus initially collapsed');
  await page.locator('#app-nav .nav-group-title').first().click();assert.equal(await page.locator('#app-nav .nav-group-title').first().getAttribute('aria-expanded'),'true');
  await page.locator('#workspace-nav-search').fill('Inicio');assert.ok(await page.locator('#app-nav a[data-view="inicio"]:visible').count());
  await page.locator('#workspace-nav-search').fill('');
  await page.evaluate(role=>location.hash='#/'+role+'/estudio',role);
  if(full){await page.waitForSelector('#ws-script');await page.locator('#ws-prompt').fill('Prueba local');await page.locator('#ws-script').click();await page.waitForFunction(()=>document.querySelector('#ws-script-output')?.textContent.includes('Guion validado'));
   const call=requests.find(item=>item.url.endsWith('/studio/script'));assert.equal(call.headers.authorization,'Bearer '+token);assert.ok(!call.body.includes('NODE6_TOKEN'));
  }else{await page.waitForFunction(()=>document.querySelector('.workspace h2')?.textContent==='Acceso no habilitado');assert.ok(!requests.some(item=>item.url.endsWith('/studio/script')))}
  await page.evaluate(()=>location.hash='#/otro_rol/inicio'); // invalid route cannot elevate
  await page.evaluate(role=>location.hash='#/'+(role==='admin_general'?'admin_empresa':'admin_general')+'/inicio',role);
  await page.waitForFunction(()=>document.querySelector('.workspace h2')?.textContent==='Este panel corresponde a otro rol');
  assert.deepEqual(errors,[]);await page.close();count++;
 }
 console.log('PASS workspaces: '+count+' role/viewport combinations, accordion, mobile drawer, JWT proxy, plan and role gates');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
