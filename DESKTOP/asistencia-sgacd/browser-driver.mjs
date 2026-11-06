import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {policy} from './control-client.mjs';
import {desktop,redact} from './bridge.mjs';

export class BrowserDriver{
 constructor(directory,{chromium,launchOptions={},allowURL}={}){this.directory=directory;this.chromium=chromium;this.launchOptions=launchOptions;this.allowURL=allowURL;this.sessions=new Map();}
 allowed(raw,platform){try{const url=new URL(raw);return this.allowURL?this.allowURL(url,platform):url.protocol==='https:'&&(policy.platform_hosts[platform].includes(url.hostname)||(['gmail','youtube'].includes(platform)&&policy.manual_auth_hosts.includes(url.hostname)));}catch{return false}}
 async session(platform){
  if(this.sessions.has(platform))return this.sessions.get(platform);
  const chromium=this.chromium??(await import('playwright')).chromium;
  const folder=path.join(this.directory,'browser-'+platform);fs.mkdirSync(folder,{recursive:true,mode:0o700});
  const context=await chromium.launchPersistentContext(folder,{channel:'chrome',headless:false,acceptDownloads:false,permissions:[],...this.launchOptions});
  const page=context.pages()[0]??await context.newPage(),state={context,page,refs:new Map(),observation:null,at:0,url:null};
  await context.route('**/*',async route=>{const r=route.request();if(r.isNavigationRequest()&&r.frame()===page.mainFrame()&&!this.allowed(r.url(),platform)){await route.abort();return}await route.continue()});
  context.on('page',popup=>{if(popup!==page)popup.close().catch(()=>{})});
  page.on('framenavigated',frame=>{if(frame===page.mainFrame()){state.refs.clear();state.observation=null;}});
  this.sessions.set(platform,state);return state;
 }
 async guard(state,platform){
  if(!this.allowed(state.page.url(),platform))throw Error('La página actual no es un sitio oficial permitido.');
  const url=new URL(state.page.url());
  if(policy.manual_auth_hosts.includes(url.hostname)||/\/(login|signin|challenge|checkpoint|oauth)(\/|\?|$)/i.test(url.pathname)||await state.page.locator('input[type=password],input[autocomplete=one-time-code],iframe[src*="captcha"],iframe[src*="challenge"]').count())throw Error('Se requiere intervención humana para inicio de sesión, CAPTCHA o verificación.');
 }
 async fingerprint(state){
  const content=await state.page.locator('body').evaluate(el=>({text:el.innerText,fields:Array.from(el.querySelectorAll('input,textarea,select,[contenteditable=true]')).filter(e=>e.type!=='password'&&e.type!=='hidden'&&e.autocomplete!=='one-time-code').map(e=>({type:e.type,value:e.value??e.innerText}))}));
  return crypto.createHash('sha256').update(JSON.stringify(content)).digest('hex');
 }
 async snapshot(state,platform){
  await this.guard(state,platform);state.refs.clear();state.observation=crypto.randomBytes(16).toString('hex');state.at=Date.now();state.url=state.page.url();
  const handles=await state.page.locator('button,a,input,textarea,select,[role=button],[role=textbox],[role=checkbox],[contenteditable=true]').elementHandles(),items=[];
  for(const element of handles){
   if(items.length>=60)break;
   if(!await element.isVisible()&&await element.getAttribute('type')!=='file')continue;
   const metadata=await element.evaluate(el=>({tag:el.tagName.toLowerCase(),type:el.getAttribute('type')??'',name:(el.getAttribute('aria-label')||el.labels?.[0]?.innerText||el.innerText||el.getAttribute('placeholder')||'').trim().slice(0,200),autocomplete:el.getAttribute('autocomplete')??''}));
   if(metadata.type==='password'||/one-time-code/.test(metadata.autocomplete))continue;
   const ref='e'+items.length;state.refs.set(ref,{element,metadata});items.push({ref,...redact(metadata)});
  }
  state.fingerprint=await this.fingerprint(state);
  const review=await state.page.locator('body').evaluate(el=>({visible_text:el.innerText.slice(0,8000),fields:Array.from(el.querySelectorAll('input,textarea,select,[contenteditable=true]')).filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height&&e.type!=='password'&&e.type!=='hidden'&&e.autocomplete!=='one-time-code').slice(0,30).map(e=>({name:e.getAttribute('aria-label')||e.name||e.id||'',content:String(e.value??e.innerText).slice(0,500)}))}));
  const result={review_context:redact(review),content_fingerprint:state.fingerprint,observation_id:state.observation,url:state.url,title:(await state.page.title()).slice(0,200),elements:items,expires_in:120,account_label:'principal',account_identity:'operator_must_verify'};
  // Bound UTF-8 bytes, not JS characters: reports must fit the encrypted API contract.
  while(Buffer.byteLength(JSON.stringify(result))>26000&&result.review_context.visible_text.length>200)result.review_context.visible_text=result.review_context.visible_text.slice(0,Math.floor(result.review_context.visible_text.length/2));
  while(Buffer.byteLength(JSON.stringify(result))>26000&&result.review_context.fields.length)result.review_context.fields.pop();
  while(Buffer.byteLength(JSON.stringify(result))>26000&&result.elements.length)result.elements.pop();
  return result;
 }
 async target(state,args,platform){
  await this.guard(state,platform);
  if(state.observation!==args.observation_id||Date.now()-state.at>120000||state.url!==state.page.url())throw Error('Observación vencida. Solicita otra y autoriza un plan nuevo.');
  if(state.fingerprint!==await this.fingerprint(state))throw Error('El contenido cambió después de la revisión. Solicita una observación nueva.');
  const ref=state.refs.get(args.ref);if(!ref||(!await ref.element.isVisible()&&ref.metadata.type!=='file')||!await ref.element.isEnabled())throw Error('Referencia no válida o elemento cambiado.');
  const current=await ref.element.evaluate(el=>({type:el.getAttribute('type')??'',autocomplete:el.getAttribute('autocomplete')??'',name:(el.getAttribute('aria-label')||el.labels?.[0]?.innerText||el.innerText||el.getAttribute('placeholder')||'').trim().slice(0,200)}));
  if(current.type==='password'||/one-time-code/.test(current.autocomplete)||current.name!==ref.metadata.name)throw Error('El campo es protegido o cambió desde la revisión.');
  return ref;
 }
 async files(){
  const root=path.join(this.directory,'shared');fs.mkdirSync(root,{recursive:true,mode:0o700});const items=[];
  for(const name of fs.readdirSync(root).slice(0,10)){
   const file=path.join(root,name),stat=fs.lstatSync(file);if(!stat.isFile()||stat.isSymbolicLink()||stat.size>64*1024*1024||name.startsWith('.'))continue;
   const hash=crypto.createHash('sha256');for await(const chunk of fs.createReadStream(file))hash.update(chunk);items.push({file:name,size:stat.size,sha256:hash.digest('hex')});
  }return {files:items,root:'private-local-shared-folder-only'};
 }
 async run(intent){
  const operation=intent.operation,args=intent.arguments,platform=intent.platform;
  if(operation==='desktop_status')return desktop(['status']);
  if(operation==='files_list')return this.files();
  const state=await this.session(platform);
  if(operation==='browser_open'){
   if(!this.allowed(args.url,platform))throw Error('URL no autorizada.');
   await state.page.goto(args.url,{waitUntil:'domcontentloaded',timeout:15000});state.refs.clear();return {url:state.page.url(),title:await state.page.title(),notice:'El inicio de sesión y la comprobación de cuenta son manuales.'};
  }
  if(operation==='browser_snapshot')return this.snapshot(state,platform);
  const target=await this.target(state,args,platform);
  // References are consumed before dispatch; uncertain failures are never blindly retried.
  state.refs.clear();state.observation=null;
  if(operation==='browser_fill'){
   if(target.metadata.type==='file')throw Error('Usa una carga de archivo aprobada, no texto en un selector de archivo.');
   await target.element.fill(args.text,{timeout:5000});
  }else if(operation==='browser_click')await target.element.click({timeout:5000});
  else if(operation==='browser_press'){
   if(!['Enter','Tab','Escape','ArrowDown','ArrowUp'].includes(args.key))throw Error('Tecla no permitida.');
   await target.element.press(args.key,{timeout:5000});
  }else if(operation==='browser_upload'){
   if(target.metadata.type!=='file'||args.file!==path.basename(args.file)||args.file.startsWith('.'))throw Error('Archivo no permitido.');
   const root=path.join(this.directory,'shared'),file=path.join(root,args.file),stat=fs.lstatSync(file);
   if(!stat.isFile()||stat.isSymbolicLink()||stat.size>64*1024*1024)throw Error('Archivo ausente, enlazado o demasiado grande.');
   const fd=fs.openSync(file,fs.constants.O_RDONLY|(fs.constants.O_NOFOLLOW??0));let buffer;
   try{const opened=fs.fstatSync(fd);if(!opened.isFile()||opened.size>64*1024*1024||opened.ino!==stat.ino||opened.dev!==stat.dev)throw Error('El archivo cambió.');buffer=fs.readFileSync(fd);}finally{fs.closeSync(fd)}
   if(crypto.createHash('sha256').update(buffer).digest('hex')!==args.sha256)throw Error('El archivo cambió después de la autorización.');
   const types={'.pdf':'application/pdf','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.mp4':'video/mp4','.csv':'text/csv','.txt':'text/plain'};
   await target.element.setInputFiles({name:args.file,mimeType:types[path.extname(args.file).toLowerCase()]??'application/octet-stream',buffer},{timeout:10000});
  }else throw Error('Acción no implementada o no permitida.');
  return {interaction:'delivered',provider_success_verified:false,url:state.page.url()};
 }
 async close(){for(const state of this.sessions.values())await state.context.close();this.sessions.clear();}
}
