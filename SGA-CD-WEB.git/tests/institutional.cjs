const{chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const assert=require('node:assert/strict');
const base=process.env.SGA_WEB_URL||'http://127.0.0.1:18200';
const names={admin_empresa:'Administrador de empresa',jefe_area:'Jefe de área',coordinador:'Coordinador',profesional_area:'Profesional de área',tecnico_area:'Técnico de área',profesor:'Profesor / Instructor',jefe_almacen:'Jefe de almacén',almacenista:'Almacenista',jefe_escenarios:'Jefe de escenarios',alumno:'Alumno',padre_acudiente:'Madre, padre o acudiente'};
const management=new Set(['admin_empresa','jefe_area','coordinador','profesional_area','tecnico_area']);
const token='test.'+Buffer.from(JSON.stringify({sub:'1',exp:Math.floor(Date.now()/1000)+3600})).toString('base64url')+'.test';
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox']});let count=0;try{
 async function pageFor(role,plan,width,owner){
  const ctx=await b.newContext({viewport:{width,height:1000},serviceWorkers:'block',reducedMotion:'reduce'});const page=await ctx.newPage();const calls=[],errors=[];page.on('pageerror',error=>errors.push(error.message));const actualRole=owner?'admin_general':role;
  await ctx.addInitScript(({token,role})=>{localStorage.setItem('accessToken',token);localStorage.setItem('userRoles',JSON.stringify([role]));localStorage.setItem('userName','Cuenta real de prueba');localStorage.setItem('userId','1');localStorage.setItem('sgacd_cookie_consent','essential_only')},{token,role:actualRole});
  const company={id:2,name:'Instituto <img src=x> Deportivo y Cultural',municipio:'Bogotá',pais:'Colombia',direccion:'Sede'};
  await page.route('**/*',async route=>{const req=route.request(),url=new URL(req.url());if(url.pathname.includes('/api/')){
   calls.push({path:url.pathname,params:Object.fromEntries(url.searchParams),method:req.method(),body:req.postData()?JSON.parse(req.postData()):null,auth:req.headers().authorization});
   if(url.pathname.endsWith('/workspace/session'))return route.fulfill({json:{user:{id:1,name:'Cuenta real de prueba',roles:[actualRole],tenant_id:2},organization:company.name,scope:owner?'platform':'company',plan:owner?'platform':plan,full_enabled:owner||plan==='full',permissions:Object.fromEntries(['crm','media','publish','inbox'].map(key=>[key,owner||plan==='full'&&management.has(role)])),manage_team:owner||role==='admin_empresa',manage_channels:owner||role==='admin_empresa'}});
   if(url.pathname.includes('/institutional')){
    const path=url.pathname.split('/institutional')[1],isReview=url.searchParams.get('review')==='true',requested=url.searchParams.get('role')||role;
    if(path==='/context'){
     if((isReview&&!owner)||(!isReview&&requested!==actualRole))return route.fulfill({status:403,json:{detail:'Rol no autorizado'}});
     const selected=isReview?(url.searchParams.get('plan')||'basico'):plan;
     return route.fulfill({json:{role:requested,plan:selected,review:isReview,company,permissions:Object.fromEntries(['crm','media','publish','inbox'].map(key=>[key,selected==='full'&&management.has(requested)])),full_enabled:selected==='full'&&management.has(requested),contract:{name:names[requested],role:requested,group:management.has(requested)?'administrativo':'operativo',scope:requested==='admin_empresa'?'empresa':'area',duties:['Funciones originales de su contrato preservadas'],commercial_eligible:selected==='full'&&management.has(requested)}}});
    }
    if(path==='/entities')return route.fulfill({json:{entities:[company]}});
    if(path==='/dashboard'){
     const sport={id:1,name:'Fútbol',vertical:'deporte',students:2,enrollments:3,dropouts:1,active:2},culture={id:2,name:'Guitarra',vertical:'cultura',students:1,enrollments:1,dropouts:0,active:0},filtered=url.searchParams.get('specialty')==='1';
     return route.fulfill({json:{company,scope_label:'Datos reales del alcance autorizado',updated_at:new Date().toISOString(),version:filtered?'filtered':'base',kpis:{students:filtered?2:3,enrollments:filtered?3:4,active_enrollments:2,dropouts:1,sports:1,cultural:filtered?0:1},specialties:filtered?[sport]:[sport,culture],states:{activa:2,retirada:1,sin_clasificar:1},trend:[{month:'2026-09',enrollments:4,dropouts:0},{month:'2026-10',enrollments:0,dropouts:1}],quality:{without_status:1,without_specialty:0,without_date:0},definition:'Personas únicas e inscripciones son medidas distintas; deserción explícita.',slicers:Object.fromEntries(['vertical','specialty','process','teacher','venue','group','gender','age_group','neighborhood','status'].map(key=>[key,key==='specialty'?[{value:'1',label:'Fútbol'},{value:'2',label:'Guitarra'}]:[]]))}});
    }
    if(path==='/catalog')return route.fulfill({json:{counts:{deporte:500,cultura:500},items:[{id:1,name:'Fútbol',vertical:'deporte',category:'Deporte',adopted:true},{id:2,name:'Guitarra',vertical:'cultura',category:'Cultura',adopted:false}],can_edit:!isReview&&role==='admin_empresa'}});
    if(path==='/team'&&req.method()==='GET')return route.fulfill({json:{members:[{id:1,name:'Responsable',roles:['admin_empresa'],group:'administrativo',active:true,areas:['Deportes'],plan,full_administrative:plan==='full'}],creatable_roles:['jefe_area','coordinador'],areas:[{id:1,name:'Deportes'}],plan}});
    if(path==='/team'&&req.method()==='POST')return route.fulfill({status:201,json:{created:true,id:999,username:'new@example.org'}});
    return route.fulfill({json:{saved:true}});
   }
   return route.fulfill({json:[]});
  }
  if(url.origin!==new URL(base).origin){if(url.pathname.endsWith('gsap.min.js'))return route.fulfill({path:(process.env.GSAP_DIST||'/tmp/sgacd-ui-tests/node_modules/gsap/dist')+'/gsap.min.js',contentType:'text/javascript'});return route.abort()}return route.continue()});
  return{ctx,page,calls,errors};
 }
 for(const width of [1440,768,390,320])for(const role of Object.keys(names))for(const plan of ['basico','full']){
  const{ctx,page,calls,errors}=await pageFor(role,plan,width,true);await page.goto(base+'/app.html#/revision/'+role+'/'+plan+'/inicio');await page.waitForSelector('#institutional-company-name');await page.waitForSelector('.institutional-review');if(management.has(role))await page.waitForSelector('.institutional-kpis');
  assert.equal(await page.locator('#institutional-company-name').textContent(),'Instituto <img src=x> Deportivo y Cultural');assert.equal(await page.locator('#institutional-company-name img').count(),0);assert.ok(await page.locator('#app-nav .nav-group').count()>0);
  const premium=await page.locator('#app-nav a[data-view=estudio]').count();assert.equal(premium>0,plan==='full'&&management.has(role),role+' '+plan);
  assert.ok(await page.evaluate(()=>{const area=document.getElementById('content-area');return document.documentElement.scrollWidth<=innerWidth+1&&area.scrollWidth<=area.clientWidth+1}),'overflow '+role+' '+plan+' '+width);
  assert.ok(calls.every(call=>call.method==='GET'),'owner review must never write');assert.deepEqual(errors,[]);await ctx.close();count++;
 }
 for(const role of Object.keys(names))for(const plan of ['basico','full']){
  const{ctx,page,calls,errors}=await pageFor(role,plan,390,false);await page.goto(base+'/app.html#/'+role+'/'+plan+'/inicio');await page.waitForSelector('#institutional-company-name');if(management.has(role))await page.waitForSelector('.institutional-kpis');else await page.waitForSelector('.workspace');
  assert.equal(await page.locator('#app-nav a[data-view=estudio]').count()>0,plan==='full'&&management.has(role));assert.equal(await page.locator('.institutional-review').count(),0);
  if(role==='admin_empresa'&&plan==='full'){
   await page.evaluate(()=>location.hash='#/admin_empresa/full/indicadores-institucionales');await page.waitForSelector('[data-specialty="1"]');await page.locator('[data-specialty="1"]').click();await page.waitForFunction(()=>document.querySelectorAll('.institutional-bar').length===1);assert.ok(calls.some(call=>call.params.specialty==='1'));
   await page.evaluate(()=>location.hash='#/admin_empresa/full/equipo');await page.waitForSelector('#institutional-member',{state:'attached'});await page.locator('summary').first().click();await page.locator('#institutional-member [name=name]').fill('Nuevo coordinador');await page.locator('#institutional-member [name=email]').fill('new@example.org');await page.locator('#institutional-member [name=password]').fill('NeverPersistThis-123');await page.locator('#institutional-member [name=role]').selectOption('coordinador');await page.locator('#institutional-member button').click();await page.waitForFunction(()=>document.querySelector('#workspace-feedback')?.textContent.includes('Cuenta creada'));assert.equal(await page.locator('#institutional-member [name=password]').inputValue(),'');
  }
  assert.deepEqual(errors,[]);await ctx.close();count++;
 }
 {const{ctx,page,calls,errors}=await pageFor('admin_empresa','basico',1440,true);await page.goto(base+'/app.html#/admin_empresa/inicio');await page.waitForSelector('.institutional-kpis');assert.ok(page.url().includes('#/revision/admin_empresa/basico/inicio'));assert.ok(!(await page.locator('body').textContent()).includes('Este panel corresponde a otro rol'));await page.evaluate(()=>location.hash='#/admin_general/paneles');await page.waitForSelector('.institutional-directory');assert.equal(await page.locator('.institutional-directory a').count(),22);await page.evaluate(()=>location.hash='#/admin_general/plan');await page.waitForFunction(()=>document.querySelector('#content-area').textContent.includes('sin contratar'));assert.deepEqual(errors,[]);await ctx.close();count++;}
 console.log('PASS institutional: '+count+' role/plan/viewport flows; 22 owner review links, inherited menus, centered branding, interactive BI, team creation and no owner-review writes.');
}finally{await b.close()}})().catch(error=>{console.error(error);process.exit(1)});
