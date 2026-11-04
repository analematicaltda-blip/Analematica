const{chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18200';
const token='test.'+Buffer.from(JSON.stringify({sub:'1',exp:Math.floor(Date.now()/1000)+3600})).toString('base64url')+'.test';
const asset='01234567-1234-4234-9234-012345678901',contact='01234567-1234-4234-9234-012345678902';
const providers={youtube:{label:'YouTube',fields:['client_id','client_secret','refresh_token']},instagram:{label:'Instagram',fields:['account_id','access_token']},facebook:{label:'Facebook',fields:['page_id','access_token']},whatsapp:{label:'WhatsApp',fields:['phone_number_id','access_token']},x:{label:'X',fields:['consumer_key','consumer_secret','access_token','access_secret']},tiktok:{label:'TikTok',fields:['access_token']},gmail:{label:'Gmail',fields:['sender_email','client_id','client_secret','refresh_token']}};
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});let count=0;try{
 for(const width of [1440,768,390,320])for(const role of ['admin_general','admin_empresa','jefe_area','basic']){
  const full=role!=='basic',actualRole=role==='basic'?'admin_empresa':role;const session={user:{id:1,name:'Cuenta de prueba',roles:[actualRole],tenant_id:1},organization:'Empresa de prueba',scope:role==='admin_general'?'platform':'company',full_enabled:full,permissions:{crm:full,media:full,publish:full,inbox:full},manage_team:role!=='jefe_area',manage_channels:role!=='jefe_area'};
  const context=await browser.newContext({viewport:{width,height:1000},timezoneId:'America/Bogota',serviceWorkers:'block',reducedMotion:'reduce'}),page=await context.newPage();const errors=[],calls=[];let rows=[];page.on('pageerror',error=>errors.push(error.message));
  await context.addInitScript(({token,role})=>{localStorage.setItem('accessToken',token);localStorage.setItem('userRoles',JSON.stringify([role]));localStorage.setItem('userName','Cuenta de prueba');localStorage.setItem('userId','1');localStorage.setItem('sgacd_cookie_consent','essential_only')},{token,role:actualRole});
  await page.route('**/*',async route=>{const req=route.request(),url=new URL(req.url());
   if(url.pathname.includes('/api/')){
    if(url.pathname.endsWith('/workspace/session'))return route.fulfill({json:session});
    if(url.pathname.endsWith('/institutional/context'))return route.fulfill({json:{role:actualRole,plan:full?'full':'basico',review:false,company:{id:1,name:session.organization},permissions:session.permissions,full_enabled:full,contract:{name:actualRole,duties:[],commercial_eligible:full}}});
    if(url.pathname.endsWith('/workspace/assets'))return route.fulfill({json:{assets:[{id:asset,title:'Video original',kind:'reel'}]}});
    if(url.pathname.endsWith('/assets/'+asset+'/download'))return route.fulfill({body:Buffer.from('test-video'),contentType:'video/mp4'});
    if(url.pathname.includes('/workspace/campaigns')){
     const path=url.pathname.split('/campaigns')[1],method=req.method(),body=req.postData()?JSON.parse(req.postData()):null;calls.push({path,method,body,headers:req.headers()});
     if(path==='/settings')return route.fulfill({json:{providers,delivery_enabled:true,monthly_sends:{limit:50,used:0},scheduler_recent:true,public_media_ready:false}});
     if(path==='/channels'&&method==='GET')return route.fulfill({json:{channels:Object.keys(providers).map(provider=>({provider,label:'Cuenta '+provider,configured:true}))}});
     if(path==='/contacts'&&method==='GET')return route.fulfill({json:{contacts:[{id:contact,provider:'gmail',address:'one@example.org',name:'Audiencia real de prueba',subscribed:true,consent_source:'Consentimiento de prueba'}]}});
     if(path===''&&method==='GET')return route.fulfill({json:{campaigns:rows}});
     if(path===''&&method==='POST'){rows=[{...body,id:asset,state:'draft',can_reschedule:true,counts:{draft:1},targets:[{id:contact,provider:'gmail',state:'draft'}]}];return route.fulfill({status:201,json:rows[0]})}
     if(path.endsWith('/approve')){rows[0].state='scheduled';rows[0].counts={queued:1};rows[0].targets[0].state='queued';return route.fulfill({json:rows[0]})}
     if(path==='/adaptations')return route.fulfill({json:{id:asset,download_url:'/api/v1/workspace/assets/'+asset+'/download'}});
     return route.fulfill({json:{saved:true,configured:true,verified:false}});
    }
    return route.fulfill({json:[]});
   }
   if(url.origin!==new URL(base).origin){if(url.pathname.endsWith('gsap.min.js'))return route.fulfill({path:(process.env.GSAP_DIST||'/tmp/sgacd-ui-tests/node_modules/gsap/dist')+'/gsap.min.js',contentType:'text/javascript'});return route.abort()}
   return route.continue();
  });
  await page.goto(base+'/app.html#/'+actualRole+'/campanas');
  if(!full){await page.waitForFunction(()=>document.querySelector('.workspace h2')?.textContent==='Acceso no habilitado');assert.equal(calls.length,0);await context.close();count++;continue}
  await page.waitForSelector('#campaign-new');const form=page.locator('#campaign-new');await form.locator('[name=asset_id]').selectOption(asset);await form.locator('[name=title]').fill('Campaña <img src=x onerror=alert(1)>');await form.locator('[name=description]').fill('Video para mi audiencia');await form.locator('[name=provider][value=gmail]').check();await form.locator('details').first().locator('summary').click();await form.locator('[name=contact]').check();await form.locator('button').click();await page.waitForSelector('#campaign-list .campaign-event');
  const create=calls.find(call=>call.method==='POST'&&call.path==='');assert.equal(create.body.timezone,'America/Bogota');assert.match(create.body.scheduled_at,/Z$/);assert.deepEqual(create.body.providers,['gmail']);assert.deepEqual(create.body.contact_ids,[contact]);assert.equal(await page.locator('#campaign-list img').count(),0);
  page.once('dialog',dialog=>dialog.accept());await page.locator('[data-campaign-approve]').click();await page.waitForFunction(()=>document.querySelector('#campaign-list').textContent.includes('Programada'));
  await page.evaluate(role=>location.hash='#/'+role+'/calendario',actualRole);await page.waitForSelector('.campaign-calendar');assert.equal(await page.locator('.campaign-calendar-event').count(),1);
  await page.evaluate(role=>location.hash='#/'+role+'/adaptaciones',actualRole);await page.waitForSelector('#campaign-adapt-asset');await page.locator('#campaign-adapt-asset').selectOption(asset);await page.locator('[data-campaign-adapt=whatsapp]').click();await page.waitForSelector('#campaign-adapt-result a');assert.equal(calls.find(call=>call.path==='/adaptations').body.profile,'whatsapp');
  await page.evaluate(role=>location.hash='#/'+role+'/audiencia',actualRole);await page.waitForSelector('#campaign-audience',{state:'attached'});await page.locator('#campaign-audience summary').count();await page.locator('summary').first().click();await page.locator('[name=addresses]').fill('a@example.org\nb@example.org');await page.locator('[name=consent_source]').fill('Autorización de prueba');await page.locator('[name=consent]').check();await page.locator('#campaign-audience button').click();await page.waitForFunction(()=>document.querySelector('#workspace-feedback')?.textContent.includes('Audiencia guardada'));assert.equal(calls.find(call=>call.path==='/contacts'&&call.method==='POST').body.contacts.length,2);
  await page.evaluate(role=>location.hash='#/'+role+'/canales',actualRole);await page.waitForFunction(()=>document.querySelector('.workspace h2')?.textContent==='Integraciones de la organización');assert.equal(await page.locator('.workspace-grid>section').count(),7);
  if(session.manage_channels){const form=page.locator('[data-campaign-channel=gmail]');await form.locator('..').locator('summary').click();await form.locator('[name=label]').fill('Mi Gmail');for(const key of providers.gmail.fields)await form.locator(`[name=${key}]`).fill(key==='sender_email'?'sender@example.org':'NOT-A-REAL-SECRET');await form.locator('button').click();await page.waitForFunction(()=>document.querySelector('#workspace-feedback')?.textContent.includes('Configuración guardada'));assert.equal(await page.locator('[data-campaign-channel=gmail] [name=client_secret]').inputValue(),'');assert.ok(!(await page.locator('body').textContent()).includes('NOT-A-REAL-SECRET'))}
  assert.ok(await page.evaluate(()=>{const area=document.querySelector('#content-area');return document.documentElement.scrollWidth<=innerWidth+1&&area.scrollWidth<=area.clientWidth+1}),'responsive overflow '+width+' '+role);assert.ok(calls.every(call=>call.headers.authorization==='Bearer '+token));assert.deepEqual(errors,[]);await context.close();count++;
 }
 console.log('PASS campaigns: '+count+' role/viewport flows; 7 channels, bulk drafts/approval, calendar, adaptations, consent import, secret clearing and Basic gate.');
}finally{await browser.close()}})().catch(error=>{console.error(error);process.exit(1)});
