/* Real React + Django WSGI, password authentication and CSRF on synthetic accounts. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {spawn,execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const deps=process.env.QUOTE_UI_DEPS;
if(!deps)throw Error('QUOTE_UI_DEPS must point to an isolated node_modules directory');
const gateway=process.env.QUOTE_GATEWAY==='1';
const mfa=process.env.QUOTE_MFA==='1';
const reset=process.env.QUOTE_RESET==='1';
if(reset&&!mfa)throw Error('Reset fixture requires existing MFA');
const enroll=process.env.QUOTE_ENROLL==='1';
const recovery=process.env.QUOTE_RECOVERY==='1';
const issue=process.env.QUOTE_ISSUE==='1';
if(issue&&(!mfa||recovery))throw Error('Issuance requires MFA and no recovery fixture');
if(recovery&&!mfa)throw Error('Recovery fixture requires MFA');
if(mfa&&enroll)throw Error('Enrollment starts with a factor-free test account');
const dockerEnv={...process.env};for(const name of ['DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'])delete dockerEnv[name];
const docker=(...args)=>execFileSync('docker',['--host=unix:///var/run/docker.sock',...args],{env:dockerEnv,encoding:'utf8'}).trim();
const esbuild=require(path.join(deps,'esbuild'));
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
function totp(secret){
 const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';let value=0,bits=0;const bytes=[];
 for(const char of secret.replace(/=/g,'')){const index=alphabet.indexOf(char.toUpperCase());if(index<0)throw Error('Invalid test enrollment');value=(value<<5)|index;bits+=5;if(bits>=8){bits-=8;bytes.push((value>>>bits)&255);}}
 const counter=Buffer.alloc(8);counter.writeBigUInt64BE(BigInt(Math.floor(Date.now()/30000)));
 const hash=require('node:crypto').createHmac('sha1',Buffer.from(bytes)).update(counter).digest();const offset=hash[hash.length-1]&15;
 return ((hash.readUInt32BE(offset)&0x7fffffff)%1000000).toString().padStart(6,'0');
}
async function stableTotp(secret){const remaining=30000-Date.now()%30000;if(remaining<3000)await new Promise(resolve=>setTimeout(resolve,remaining+100));return totp(secret);}
(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'sgacd-quote-browser-'));
 let server,browser,page,network,container;const diagnostics=[];let bind='127.0.0.1',publicPort;
 try{
  const tsconfig={compilerOptions:{strict:true,noEmit:true,target:'ES2020',module:'ESNext',moduleResolution:'bundler',jsx:'react-jsx',esModuleInterop:true,skipLibCheck:true,baseUrl:root,paths:{react:[path.join(deps,'@types/react/index.d.ts')],'react/*':[path.join(deps,'@types/react/*')]},typeRoots:[path.join(deps,'@types')]},files:[path.join(root,'FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/cotizaciones/page.tsx')]};
  fs.writeFileSync(path.join(temp,'tsconfig.json'),JSON.stringify(tsconfig));
  execFileSync(process.execPath,[path.join(deps,'typescript/bin/tsc'),'-p',path.join(temp,'tsconfig.json')],{stdio:'pipe'});
  await esbuild.build({stdin:{contents:`import React from 'react';import{createRoot}from'react-dom/client';import Workspace from ${JSON.stringify(path.join(root,'FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-comercial/cotizaciones/page.tsx'))};createRoot(document.getElementById('root')).render(<Workspace/>);`,resolveDir:root,loader:'tsx'},bundle:true,outfile:path.join(temp,'bundle.js'),nodePaths:[deps],logLevel:'silent'});
  if(gateway){
   network='sgacd-quote-'+process.pid+'-'+Date.now();docker('network','create',network);
   bind=process.env.QUOTE_BIND||JSON.parse(docker('network','inspect',network))[0].IPAM.Config[0].Gateway;
   publicPort=await new Promise((resolve,reject)=>{const socket=require('node:net').createServer();socket.on('error',reject);socket.listen(0,'127.0.0.1',()=>{const port=socket.address().port;socket.close(()=>resolve(port));});});
  }
  server=spawn(process.env.QUOTE_PYTHON||'python',[path.join(__dirname,'quotation_server.py'),'--assets',temp,'--bind',bind,...(gateway?['--origin','https://127.0.0.1:'+publicPort,'--secure-cookie']:[])],{cwd:root,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'},stdio:['ignore','pipe','pipe']});
  const port=await new Promise((resolve,reject)=>{let output='';let diagnostics='';const timer=setTimeout(()=>reject(Error('Quotation fixture did not start')),30000);server.stderr.on('data',chunk=>{diagnostics=(diagnostics+chunk).slice(-3000);});server.stdout.on('data',chunk=>{output+=chunk;const match=output.match(/READY (\d+)/);if(match){clearTimeout(timer);resolve(Number(match[1]));}});server.on('exit',code=>{clearTimeout(timer);reject(Error('Fixture exited '+code+' '+diagnostics));});});
  let origin='http://127.0.0.1:'+port;let basic;
  if(gateway){
   execFileSync(process.env.QUOTE_PYTHON||'python',[path.join(__dirname,'quotation_gateway.py'),'--directory',temp,'--backend',bind+':'+port],{cwd:root});
   basic=JSON.parse(fs.readFileSync(path.join(temp,'private/preview-access.json'),'utf8')).erp;
   container=docker('run','-d','--rm','--network',network,'--user',String(process.getuid?process.getuid():1000)+':'+String(process.getgid?process.getgid():1000),'--read-only','--cap-drop=ALL','--security-opt','no-new-privileges:true','--tmpfs','/tmp:mode=1777','--tmpfs','/var/cache/nginx:mode=1777','-p','127.0.0.1:'+publicPort+':8442','-v',temp+'/runtime/nginx.conf:/etc/nginx/nginx.conf:ro','-v',temp+'/private:/private:ro','--entrypoint','nginx',(process.env.QUOTE_NGINX_IMAGE||'nginx:alpine@sha256:713fc2ebfd92e8217db451477182ee91944b123d2b1ee9fd5a8c6e91ca6c3a11'),'-g','daemon off;');
   origin='https://127.0.0.1:'+publicPort;
  }
  browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH==='playwright'?undefined:(process.env.CHROMIUM_PATH||'/usr/bin/chromium'),headless:true,args:['--no-sandbox']});
  page=await browser.newPage({timezoneId:'America/Bogota',...(gateway?{ignoreHTTPSErrors:true,httpCredentials:basic}:{})});const errors=[];const external=[];
  page.on("response",response=>{if(response.url().includes("/api/"))diagnostics.push({url:response.url(),status:response.status()});});
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('**/*',route=>{if(!route.request().url().startsWith(origin+'/')){external.push(route.request().url());return route.abort();}return route.continue();});
  if(gateway){let ready=false;for(let attempt=0;attempt<50;attempt++){try{ready=(await page.request.get(origin+'/api/v1/erp-session/',{timeout:1000})).status()===200;}catch{}if(ready)break;await new Promise(resolve=>setTimeout(resolve,100));}assert.ok(ready,'HTTPS gateway did not become ready');}
  await page.goto(origin,{waitUntil:'networkidle'});await page.getByRole('heading',{name:'Cotizaciones · borradores'}).waitFor();
  assert.equal(await page.locator('main').evaluate(el=>getComputedStyle(el).color),'rgb(255, 255, 255)');
  assert.equal(await page.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(6, 11, 23)');
  const credentials=JSON.parse(fs.readFileSync(path.join(temp,'fixture-credentials.json'),'utf8'));
  if(reset){
   await page.getByLabel('Correo verificado',{exact:true}).fill('missing@example.test');
   await page.getByRole('button',{name:'Solicitar enlace de recuperación',exact:true}).click();
   await page.getByText('Si la cuenta tiene un correo verificado habilitado, recibirás instrucciones de recuperación.',{exact:true}).waitFor();
   assert.equal(fs.existsSync(path.join(temp,'private-reset-mail.json')),false);
   await page.getByLabel('Correo verificado',{exact:true}).fill(credentials.email);
   const sent=page.waitForResponse(response=>response.url().endsWith('/password-reset/request/')&&response.status()===202);
   await page.getByRole('button',{name:'Solicitar enlace de recuperación',exact:true}).click();await sent;
   const link=JSON.parse(fs.readFileSync(path.join(temp,'private-reset-mail.json'),'utf8')).link;
   const values=new URLSearchParams(new URL(link).hash.slice(1));
   await page.goto(link,{waitUntil:'networkidle'});
   await page.getByLabel('Contraseña nueva',{exact:true}).waitFor();assert.equal(await page.evaluate(()=>location.hash),'');
   await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
   await page.screenshot({path:path.join(temp,'password-recovery.png'),fullPage:true});
   await page.getByLabel('Contraseña nueva',{exact:true}).fill('123456789012');await page.getByLabel('Repetir contraseña nueva',{exact:true}).fill('123456789012');
   await page.getByRole('button',{name:'Restablecer contraseña',exact:true}).click();
   await page.getByText('La contraseña nueva debe ser larga, no común y diferente de los datos personales.',{exact:true}).waitFor();
   const replacement=require('node:crypto').randomBytes(24).toString('base64url');
   await page.getByLabel('Contraseña nueva',{exact:true}).fill(replacement);await page.getByLabel('Repetir contraseña nueva',{exact:true}).fill(replacement);
   await page.getByRole('button',{name:'Restablecer contraseña',exact:true}).click();
   await page.getByText('Contraseña actualizada. Inicia sesión y completa tu segundo factor.',{exact:true}).waitFor();credentials.password=replacement;
   const current=(await (await page.request.get(origin+'/api/v1/erp-session/')).json()).data;assert.equal(current.authenticated,false);
   const replay=await page.request.post(origin+'/api/v1/erp-session/password-reset/confirm/',{headers:{'X-CSRFToken':current.csrf_token},data:{uid:values.get('reset_uid'),token:values.get('reset_token'),password:replacement+'x'}});assert.equal(replay.status(),400);
  }
  const csrfDenied=await page.request.post(origin+'/api/v1/erp-session/login/',{data:{username:credentials.username,password:credentials.password}});assert.equal(csrfDenied.status(),403);
  await page.getByLabel('Usuario',{exact:true}).fill(credentials.username);
  await page.getByLabel('Contraseña',{exact:true}).fill('synthetic-incorrect-password');
  await page.getByRole('button',{name:'Iniciar sesión',exact:true}).click();await page.getByText('Credenciales no válidas.',{exact:true}).waitFor();
  await page.getByLabel('Contraseña',{exact:true}).fill(credentials.password);
  const accepted=page.waitForResponse(response=>response.url().endsWith('/erp-session/login/')&&response.status()===(mfa?202:200));
  await page.getByRole('button',{name:'Iniciar sesión',exact:true}).click();
  const passwordResult=await (await accepted).json();
  if(mfa){
   assert.equal(passwordResult.data.authenticated,false);assert.equal(passwordResult.data.mfa_required,true);
   await page.getByRole('heading',{name:'Verificación en dos pasos',exact:true}).waitFor();
   assert.equal(await page.getByLabel('Empresa',{exact:true}).isDisabled(),true);
   await page.screenshot({path:path.join(temp,'mfa-prompt.png'),fullPage:true});
   const wrong=((Number(await stableTotp(credentials.totp_secret))+1)%1000000).toString().padStart(6,'0');
   await page.getByLabel('Código de verificación',{exact:true}).fill(wrong);await page.getByRole('button',{name:'Verificar código',exact:true}).click();
   await page.getByText('Código no válido, ya utilizado o desafío vencido.',{exact:false}).waitFor();
   if(recovery){
    await page.getByRole('button',{name:'Usar código de recuperación',exact:true}).click();
    await page.getByLabel('Código de recuperación',{exact:true}).fill(credentials.recovery_code);
    await page.getByRole('button',{name:'Verificar código',exact:true}).click();
   }else{
   await page.getByLabel('Código de verificación',{exact:true}).fill(await stableTotp(credentials.totp_secret));await page.getByRole('button',{name:'Verificar código',exact:true}).click();
   }
  }
  await page.getByRole('button',{name:'Cerrar sesión',exact:true}).waitFor();
  if(mfa){
   const current=await (await page.request.get(origin+'/api/v1/erp-session/')).json();
   const replay=await page.request.post(origin+'/api/v1/erp-session/mfa/',{headers:{'X-CSRFToken':current.data.csrf_token},data:{challenge_id:passwordResult.data.challenge_id,code:totp(credentials.totp_secret)}});
   assert.ok([401,403].includes(replay.status()));
  }
  const cookies=await page.context().cookies();if(gateway){assert.ok(cookies.some(cookie=>cookie.name==='sgacd_erp_tur_session'&&cookie.secure&&cookie.sameSite==='Strict'));assert.ok(cookies.some(cookie=>cookie.name==='sgacd_erp_tur_csrf'&&cookie.secure));assert.equal((await page.request.get(origin+'/api/v1/finance/wallet/accounts/')).status(),503);}assert.ok(cookies.some(cookie=>cookie.name==='sgacd_erp_tur_session'&&cookie.httpOnly&&cookie.path==='/api/'));assert.ok(cookies.some(cookie=>cookie.name==='sgacd_erp_tur_csrf'&&cookie.httpOnly));
  assert.equal(await page.evaluate(()=>localStorage.length),0);
  const company=page.getByLabel('Empresa',{exact:true});await page.waitForFunction(()=>document.querySelector('select')?.options.length>1);
  await company.selectOption({label:'Synthetic company'});
  const customer=page.getByLabel('Cliente',{exact:true});await customer.waitFor();await customer.selectOption({label:'Synthetic buyer'});
  await page.getByLabel('Producto',{exact:true}).selectOption({index:1});await page.getByLabel('Cantidad',{exact:true}).fill('2');
  await page.getByRole('button',{name:'Guardar borrador',exact:true}).click();await page.getByText('Borrador guardado.',{exact:false}).waitFor();
  assert.equal(await page.locator('article').count(),1);assert.match(await page.locator('article').innerText(),/25/);
  const replay=page.waitForResponse(response=>response.url().endsWith('/quotation-drafts/')&&response.request().method()==='POST'&&response.status()===200);await page.getByRole('button',{name:'Guardar borrador',exact:true}).click();await replay;assert.equal(await page.locator('article').count(),1);
  await page.reload();await page.waitForFunction(()=>document.querySelector('select')?.options.length>1);await page.getByLabel('Empresa',{exact:true}).selectOption({label:'Synthetic company'});await page.locator('article').waitFor();assert.equal(await page.locator('article').count(),1);
  page.once('dialog',dialog=>dialog.accept());await page.getByRole('button',{name:'Retirar borrador'}).click();await page.getByText('Estado: Retirado',{exact:false}).waitFor();
  if(enroll){
   await page.getByLabel('Confirmar contraseña',{exact:true}).fill('wrong-password');
   await page.getByRole('button',{name:'Preparar activación',exact:true}).click();
   await page.getByText('Contraseña no válida.',{exact:true}).waitFor();
   await page.getByLabel('Confirmar contraseña',{exact:true}).fill(credentials.password);
   await page.getByRole('button',{name:'Preparar activación',exact:true}).click();
   await page.getByLabel('Clave de configuración',{exact:true}).waitFor();
   assert.equal(await page.getByLabel('Clave de configuración',{exact:true}).getAttribute('type'),'password');
   await page.route('**/erp-session/enrollment/cancel/',route=>route.abort(),{times:1});
   await page.getByRole('button',{name:'Cancelar activación',exact:true}).click();
   await page.getByRole('button',{name:'Reintentar cancelación',exact:true}).waitFor();
   assert.equal(await page.getByLabel('Clave de configuración',{exact:true}).count(),0);
   await page.getByRole('button',{name:'Reintentar cancelación',exact:true}).click();
   await page.getByLabel('Confirmar contraseña',{exact:true}).waitFor();
   await page.getByLabel('Confirmar contraseña',{exact:true}).fill(credentials.password);
   await page.getByRole('button',{name:'Preparar activación',exact:true}).click();
   const key=page.getByLabel('Clave de configuración',{exact:true});await key.waitFor();
   const secret=await key.inputValue();
   const state=await (await page.request.get(origin+'/api/v1/erp-session/')).json();assert.equal(state.data.mfa_enabled,false);
   const wrong=((Number(await stableTotp(secret))+1)%1000000).toString().padStart(6,'0');
   await page.getByLabel('Código de activación',{exact:true}).fill(wrong);
   await page.getByRole('button',{name:'Confirmar activación',exact:true}).click();
   await page.getByText('Código no válido o configuración vencida.',{exact:false}).waitFor();
   await page.getByLabel('Código de activación',{exact:true}).fill(await stableTotp(secret));
   await page.getByRole('button',{name:'Confirmar activación',exact:true}).click();
   await page.getByText('Verificación en dos pasos activa.',{exact:true}).waitFor();
   assert.equal(await key.count(),0);assert.equal(await page.evaluate(()=>localStorage.length),0);
   credentials.totp_secret=secret;
  }
  if(issue){
   // A new TOTP is required after the sign-in counter was consumed.
   await new Promise(resolve=>setTimeout(resolve,30000-Date.now()%30000+150));
   await page.getByLabel('Contraseña para emitir códigos',{exact:true}).fill(credentials.password);
   await page.getByLabel('Código TOTP nuevo',{exact:true}).fill(await stableTotp(credentials.totp_secret));
   page.once('dialog',dialog=>dialog.accept());
   await page.getByRole('button',{name:'Emitir nuevos códigos',exact:true}).click();
   const list=page.getByRole('list',{name:'Códigos recién emitidos',exact:true});await list.waitFor();
   const codes=await list.locator('code').allTextContents();assert.equal(codes.length,10);
   credentials.recovery_code=codes[0];assert.equal(await page.evaluate(()=>localStorage.length),0);
   await page.getByRole('button',{name:'Ya los guardé; ocultar códigos',exact:true}).click();
   assert.equal(await list.count(),0);
   await page.getByRole('button',{name:'Consultar mi historial',exact:true}).click();
   await page.getByText('Códigos de recuperación emitidos ·',{exact:false}).waitFor();
  }
  await page.setViewportSize({width:390,height:844});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
  await page.screenshot({path:path.join(temp,'quotation-mobile.png'),fullPage:true});
  await page.route('**/api/v1/erp-session/logout/',route=>route.abort(),{times:1});
  await page.getByRole('button',{name:'Cerrar sesión',exact:true}).click();
  await page.getByRole('button',{name:'Reintentar cierre de sesión',exact:true}).click();await page.getByText('Inicia sesión en el ERP para consultar tus empresas.').waitFor();assert.equal(await page.locator('article').count(),0);
  if(recovery){
   const initial=await (await page.request.get(origin+'/api/v1/erp-session/')).json();
   const response=await page.request.post(origin+'/api/v1/erp-session/login/',{headers:{'X-CSRFToken':initial.data.csrf_token},data:{username:credentials.username,password:credentials.password}});
   assert.equal(response.status(),202);const pending=(await response.json()).data;
   const replay=await page.request.post(origin+'/api/v1/erp-session/recovery/',{headers:{'X-CSRFToken':pending.csrf_token},data:{challenge_id:pending.challenge_id,code:credentials.recovery_code}});
   assert.ok([401,403].includes(replay.status()));
   const completed=await page.request.post(origin+'/api/v1/erp-session/mfa/',{headers:{'X-CSRFToken':pending.csrf_token},data:{challenge_id:pending.challenge_id,code:await stableTotp(credentials.totp_secret)}});
   assert.equal(completed.status(),200);const current=(await completed.json()).data;
   assert.equal((await page.request.post(origin+'/api/v1/erp-session/logout/',{headers:{'X-CSRFToken':current.csrf_token},data:{}})).status(),200);
  }
  if(issue){
   const initial=(await (await page.request.get(origin+'/api/v1/erp-session/')).json()).data;
   const response=await page.request.post(origin+'/api/v1/erp-session/login/',{headers:{'X-CSRFToken':initial.csrf_token},data:{username:credentials.username,password:credentials.password}});
   assert.equal(response.status(),202);const pending=(await response.json()).data;
   const entered=await page.request.post(origin+'/api/v1/erp-session/recovery/',{headers:{'X-CSRFToken':pending.csrf_token},data:{challenge_id:pending.challenge_id,code:credentials.recovery_code}});
   assert.equal(entered.status(),200);const state=(await entered.json()).data;
   const history=await (await page.request.get(origin+'/api/v1/erp-session/security-events/')).json();
   assert.ok(history.data.events.some(event=>event.kind==='recovery_used'));
   assert.equal((await page.request.post(origin+'/api/v1/erp-session/logout/',{headers:{'X-CSRFToken':state.csrf_token},data:{}})).status(),200);
  }
  const denied=await page.request.get(origin+'/api/v1/mi-negocio/comercial/quotation-drafts/?provider_id=00000000-0000-0000-0000-000000000000');assert.ok([401,403].includes(denied.status()));
  await page.goto(origin+'/?anonymous');await page.getByText('Inicia sesión en el ERP para consultar tus empresas.').waitFor();assert.equal(await page.getByLabel('Empresa',{exact:true}).isDisabled(),true);assert.equal(await page.locator('article').count(),0);
  if(enroll){
   await page.getByLabel('Usuario',{exact:true}).fill(credentials.username);
   await page.getByLabel('Contraseña',{exact:true}).fill(credentials.password);
   await page.getByRole('button',{name:'Iniciar sesión',exact:true}).click();
   await page.getByRole('heading',{name:'Verificación en dos pasos',exact:true}).waitFor();
   // Activation already consumed this counter; wait for a new time step, at most 30 s.
   const remaining=30000-Date.now()%30000;await new Promise(resolve=>setTimeout(resolve,remaining+150));
   await page.getByLabel('Código de verificación',{exact:true}).fill(await stableTotp(credentials.totp_secret));
   await page.getByRole('button',{name:'Verificar código',exact:true}).click();
   await page.getByText('Verificación en dos pasos activa.',{exact:true}).waitFor();
  }
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log(JSON.stringify({passed:true,scope:'Real password authentication, CSRF and Django WSGI on synthetic test accounts',gateway_https:gateway,mfa_totp:mfa,enrollment:enroll,recovery_codes:recovery,issue_codes:issue,password_reset:reset,checks:['password_login',...(reset?['verified_email_reset','unknown_email_response','fragment_removed','weak_password_rejected','reset_replay_rejected','mfa_required_after_reset','recovery_mobile_width']:[]),...(issue?['reauthenticated_issuance','one_time_display','issued_code_login','private_audit_history','recovery_use_audited']:[]),...(recovery?['recovery_code_login','recovery_replay_denied','totp_retained']:[]),...(enroll?['enrollment_password_recheck','masked_key','cancel_failure_retry','pending_not_active','incorrect_activation','verified_activation','enrolled_factor_login']:[]),...(mfa?['password_is_first_factor_only','invalid_totp','valid_totp','challenge_replay']:[]),'bad_password','login_csrf','httponly_session','no_token_storage','create','idempotent_retry','reload_persistence','withdraw','logout_failure_recovery','logout_clears_data','anonymous','mobile_width','sgacd_blue_white_theme','no_external_requests'],screenshot:path.join(temp,'quotation-mobile.png')}));
 }catch(error){console.error(JSON.stringify({diagnostics,body:page?await page.locator("body").innerText():null}));throw error;}finally{if(browser)await browser.close();if(server)server.kill('SIGTERM');if(container){try{docker('stop',container);}catch{}}if(network){try{docker('network','rm',network);}catch{}}}
})().catch(error=>{console.error(error);process.exitCode=1;});
