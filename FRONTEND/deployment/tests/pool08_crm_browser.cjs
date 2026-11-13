// Actual owned pages, real backend responses via a loopback-only test transport.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../../..');
const targets=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});let checks=0;
 const artifacts=process.env.GC003_BROWSER_OUTPUT||'/tmp/gc003-browser-artifacts';fs.mkdirSync(artifacts,{recursive:true});
 try{for(const target of targets){
  const folder=path.join(root,target.name==='sga-cd'?'FRONTEND/SGA-CD-WEB.git':target.name==='erp-tur'?'FRONTEND/SGA-ERP-TUR-FRONTEND/public':'FRONTEND/ANALEMATICA-FRONTEND');
  const server=http.createServer((req,res)=>{const file=path.resolve(folder,'.'+new URL(req.url,'http://local').pathname);if(!file.startsWith(folder+path.sep)){res.writeHead(404);res.end();return;}try{res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  try{for(const width of [1280,390]){
   console.log('Browser target '+target.name+' '+width);
   const origin='http://127.0.0.1:'+server.address().port;
   let loseNext=true;const createRequests=[],transport=[];
   const ctx=await browser.newContext({viewport:{width,height:1000},serviceWorkers:'block'});const page=await ctx.newPage();page.on('pageerror',e=>console.error('CRM UI error: '+e.message));
   await ctx.addInitScript(({token})=>{localStorage.setItem('accessToken',token);localStorage.setItem('sgacd_cookie_consent','essential_only');localStorage.setItem('userRoles','["admin_empresa"]');localStorage.setItem('userName','Prueba CRM');localStorage.setItem('userId','1');},{token:target.token});
   await page.route('**/*',async route=>{
    const req=route.request(),url=new URL(req.url());
    if(url.pathname.startsWith('/api/')){
     const response=await ctx.request.fetch(target.origin+url.pathname+url.search,{method:req.method(),headers:{...req.headers(),host:'localhost',Authorization:'Bearer '+target.token},data:req.postDataBuffer(),failOnStatusCode:false});
     let code=null;if(response.status()>=400){try{const body=await response.json();code=body.code||body.detail?.code||body.data?.code||null;}catch{}}transport.push({method:req.method(),path:url.pathname,status:response.status(),code});
     if(req.method()==='POST'&&url.pathname.includes('/crm/commands')&&JSON.parse(req.postData()).operation==='create'){createRequests.push(JSON.parse(req.postData()).request_id);if(loseNext){loseNext=false;return route.abort('failed');}}
     return route.fulfill({status:response.status(),headers:{'content-type':'application/json','cache-control':'no-store'},body:await response.body()});
    }
    if(url.pathname.endsWith('/js/config.js'))return route.fulfill({contentType:'text/javascript',body:'window.config={apiBaseUrl:location.origin};'});
    if(url.origin!==origin)return route.abort();return route.continue();
   });
   const url=target.name==='sga-cd'?'/app.html#/admin_empresa/crm-empresa':'/commercial-crm.html';
   await page.goto(origin+url);
   if(target.name!=='sga-cd'){try{await page.locator('[data-company]').selectOption(target.provider);}catch(e){console.error((await page.locator('body').innerText()).slice(0,1000));throw e;}}
   await page.locator('[data-create]').waitFor({state:'attached'});
   await page.locator('details').filter({has:page.locator('[data-create]')}).locator('summary').click();
   const form=page.locator('[data-create]'),name=target.name+' '+width+' '+Date.now();
   await form.locator('[name=name]').fill(name);await form.locator('[name=email]').fill('ui-'+crypto.randomUUID()+'@example.test');
   await form.locator('button').click();
   await page.locator('[data-retry]').waitFor();
   if(width===390){
    await page.reload();if(target.name!=='sga-cd')await page.locator('[data-company]').selectOption(target.provider);
    try{await page.locator('[data-detail] h3').filter({hasText:name}).waitFor();}catch(e){console.error(JSON.stringify({stage:'reload-recovery',target:target.name,width,transport:transport.slice(-14),feedback:await page.locator('[data-feedback]').textContent(),pendingKeys:await page.evaluate(()=>Object.keys(sessionStorage)),detail:await page.locator('[data-detail]').innerText()}));throw e;}assert.equal(createRequests.length,1);
   }else{
    if(target.name==='sga-cd'&&await page.locator('#sga-error-btn').isVisible())await page.locator('#sga-error-btn').click();
    await page.locator('[data-retry]').click();await page.locator('[data-detail] h3').filter({hasText:name}).waitFor();assert.equal(createRequests[0],createRequests[1]);
   }
   checks+=2;
   // A duplicate must be reviewed; this path never auto-merges or inherits consent.
   const sameEmail=await page.locator('[data-edit] [name=email]').inputValue();
   if(!await form.isVisible())await page.locator('details').filter({has:form}).locator('summary').click();
   await form.locator('[name=name]').fill('Coincidente');await form.locator('[name=email]').fill(sameEmail);await form.locator('button').click();
   await page.locator('[data-duplicates]').waitFor({state:'visible'});await page.locator('[data-cancel-review]').click();checks++;
   await page.locator('[data-convert]').click();await page.locator('[data-detail]').getByText(/Cliente · Revisión 2/).waitFor();checks++;
   await page.locator('[data-task] [name=title]').fill('Seguimiento verificado');await page.locator('[data-task] [name=due_at]').fill('2026-12-12T10:00');await page.locator('[data-task] button').click();
   await page.locator('[data-complete]').waitFor();await page.locator('[data-complete]').click();await page.locator('[data-detail]').getByText(/Seguimiento verificado.*Completada/).waitFor();checks++;
   const consent=page.locator('[data-consent]');await consent.locator('[name=expires_at]').fill('2026-12-12T10:00');await consent.locator('[name=evidence_digest]').fill('a'.repeat(64));await consent.locator('[name=granted]').check();await consent.locator('button').click();await page.getByText('EMAIL:MARKETING: Vigente localmente',{exact:true}).waitFor();checks++;
   await page.locator('[data-withdraw] [name=reason]').fill('Solicitud expresa de baja');await page.locator('[data-withdraw] button').click();await page.getByText('EMAIL:MARKETING: Revocado o vencido',{exact:true}).waitFor();checks++;
   await page.locator('[data-history]').click();await page.locator('[data-events] li').last().waitFor();assert.ok(await page.locator('[data-events] li').count()>=6);checks++;
   assert.equal(await page.locator('.pool08-crm').last().evaluate(n=>getComputedStyle(n).color),'rgb(255, 255, 255)');
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'mobile overflow');checks+=2;
   await page.screenshot({path:path.join(artifacts,target.name+'-'+width+'.png'),fullPage:true});
   await page.reload();if(target.name!=='sga-cd')await page.locator('[data-company]').selectOption(target.provider);
   await page.locator('[data-search]').waitFor();await page.locator('[data-search] [name=q]').fill(name);await page.locator('[data-search] button').click();await page.locator('[data-contact]').first().click();await page.getByText('EMAIL:MARKETING: Revocado o vencido',{exact:true}).waitFor();checks++;
   await ctx.close();
  }}finally{await new Promise(r=>server.close(r));}
 }
 fs.writeFileSync(path.join(artifacts,'report.json'),JSON.stringify({checks,targets:targets.map(t=>t.name),actual_http:true,synthetic_customers:true,native_password_mfa_qualified:false,production_ready:false},null,2));console.log(JSON.stringify({checks,passed:true}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1});
