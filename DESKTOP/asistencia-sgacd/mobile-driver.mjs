import http from 'node:http';
import crypto from 'node:crypto';
import {XMLParser} from 'fast-xml-parser';
import {policy} from './control-client.mjs';
import {redact} from './bridge.mjs';
const ELEMENT='element-6066-11e4-a52e-4f735466cecf';

export class MobileDriver{
 constructor(config,{transport}={}){
  this.config=config;this.kind=config.kind;this.transport=transport;this.sessionId=null;this.app=null;this.refs=new Map();this.observation=null;
  const u=new URL(config.appium_url??'http://127.0.0.1:4723/');
  if(u.protocol!=='http:'||!['127.0.0.1','localhost','[::1]'].includes(u.hostname)||u.username||u.password||u.search||u.hash||u.pathname!=='/')throw Error('Appium solo se conecta al servidor local, nunca a una URL del plan.');
  if(!['android','ios'].includes(this.kind)||!config.udid||!(/^[A-Za-z0-9._:-]{4,128}$/).test(config.udid))throw Error('Falta el identificador local explícito del móvil. No se elige un teléfono automáticamente.');
  this.origin=u;
 }
 async request(method,route,body){
  if(this.transport)return this.transport(method,route,body);
  return new Promise((resolve,reject)=>{
   const payload=body===undefined?null:Buffer.from(JSON.stringify(body));const req=http.request(new URL(route,this.origin),{method,headers:payload?{'Content-Type':'application/json','Content-Length':payload.length}:{},timeout:25000},res=>{
    let size=0;const chunks=[];res.on('data',chunk=>{size+=chunk.length;if(size>2_000_000){req.destroy(Error('Respuesta Appium demasiado grande.'));return}chunks.push(chunk)});
    res.on('end',()=>{try{const value=JSON.parse(Buffer.concat(chunks));if(res.statusCode>=300||value.value?.error)throw Error('Appium rechazó la operación; revisa el dispositivo y la configuración local.');resolve(value)}catch(error){reject(error)}});
   });req.on('error',reject);req.on('timeout',()=>req.destroy(Error('Appium no confirmó la operación. No se reintentó.')));if(payload)req.write(payload);req.end();
  });
 }
 async rpc(method,suffix,body){return (await this.request(method,'/session/'+encodeURIComponent(this.sessionId)+suffix,body)).value;}
 async ensure(app){
  if(this.sessionId&&this.app===app)return;
  if(this.sessionId)await this.close();
  const browser=policy.mobile_browsers[this.kind].includes(app);this.browser=browser;
  const caps={'platformName':this.kind==='android'?'Android':'iOS','appium:automationName':this.kind==='android'?'UiAutomator2':'XCUITest','appium:udid':this.config.udid,'appium:noReset':true,'appium:newCommandTimeout':120};
  if(browser)caps.browserName=this.kind==='android'?'Chrome':'Safari';
  else if(this.kind==='android')caps['appium:appPackage']=app;
  else caps['appium:bundleId']=app;
  if(this.kind==='android'){caps['appium:skipUnlock']=true;caps['appium:autoGrantPermissions']=false;caps['appium:dontStopAppOnReset']=true;}
  else{caps['appium:shouldTerminateApp']=false;if(this.config.xcode_org_id){caps['appium:xcodeOrgId']=this.config.xcode_org_id;caps['appium:xcodeSigningId']='iPhone Developer';}}
  const response=await this.request('POST','/session',{capabilities:{alwaysMatch:caps,firstMatch:[{}]}});
  const id=response.value?.sessionId??response.sessionId;if(typeof id!=='string'||!(/^[A-Za-z0-9-]{1,100}$/).test(id))throw Error('Appium no devolvió una sesión válida.');
  this.sessionId=id;this.app=app;this.refs.clear();this.observation=null;
 }
 async guard(intent){
  if(this.browser){
   const current=await this.rpc('GET','/url');const u=new URL(current);
   if(u.protocol!=='https:'||!policy.platform_hosts[intent.platform].includes(u.hostname))throw Error('El navegador móvil no está en un dominio oficial autorizado. Inicia sesión manualmente si corresponde.');
   return;
  }
  const active=this.kind==='android'?await this.rpc('GET','/appium/device/current_package'):(await this.rpc('POST','/execute/sync',{script:'mobile: activeAppInfo',args:[{}]}))?.bundleId;
  if(active!==intent.arguments.app_id)throw Error('La aplicación activa cambió. No se controla otra app ni la pantalla de bloqueo.');
 }
 async fingerprint(){
  const source=this.browser?await this.rpc('POST','/execute/sync',{script:"return JSON.stringify({url:location.href,text:document.body.innerText,fields:Array.from(document.querySelectorAll('input,textarea,select')).filter(e=>e.type!=='password'&&e.type!=='hidden'&&e.autocomplete!=='one-time-code').map(e=>[e.type,e.value])});",args:[]}):await this.rpc('GET','/source');
  return crypto.createHash('sha256').update(String(source)).digest('hex');
 }
 async snapshot(intent){
  await this.guard(intent);this.refs.clear();const items=[];
  this.observation=crypto.randomBytes(16).toString('hex');this.at=Date.now();
  if(this.browser){
   const data=await this.rpc('POST','/execute/sync',{script:"return Array.from(document.querySelectorAll('button,a,input,textarea,select,[role=button],[role=textbox]')).filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height&&e.type!=='password'&&e.autocomplete!=='one-time-code').slice(0,40).map(e=>({element:e,name:(e.getAttribute('aria-label')||e.innerText||e.placeholder||'').slice(0,200),type:e.type||e.tagName}));",args:[]});
   for(const item of data??[]){const id=item.element?.[ELEMENT];if(!id)continue;const ref='e'+items.length;this.refs.set(ref,{id,type:item.type});items.push({ref,name:redact(item.name),type:item.type});}
  }else{
   const source=await this.rpc('GET','/source');if(typeof source!=='string'||source.length>1_500_000||/<!DOCTYPE|<!ENTITY/i.test(source))throw Error('Fuente móvil no válida.');
   if(/SecureTextField|password="true"|verification.?code|código de verificación|recaptcha|one.time.code/i.test(source))return {state:'manual_auth_required',notice:'Credenciales, CAPTCHA y verificación se resuelven personalmente en el dispositivo.'};
   const tree=new XMLParser({ignoreAttributes:false,processEntities:false}).parse(source),candidates=[];
   function walk(object,prefix=''){
    if(!object||typeof object!=='object')return;
    for(const [tag,value] of Object.entries(object)){
     if(tag.startsWith('@_')||tag==='#text'||!(/^[A-Za-z_][A-Za-z0-9_.-]*$/).test(tag))continue;
     const nodes=Array.isArray(value)?value:[value];nodes.forEach((node,index)=>{if(!node||typeof node!=='object')return;const xpath=prefix+'/'+tag+'['+(index+1)+']';
      const type=String(node['@_class']??node['@_type']??tag),name=String(node['@_content-desc']??node['@_label']??node['@_text']??node['@_name']??'').slice(0,200);
      if((node['@_clickable']==='true'||node['@_focusable']==='true'||/Button|TextField|TextView|Switch|CheckBox|Link/.test(type))&&!/SecureTextField/.test(type)&&node['@_password']!=='true')candidates.push({xpath,type,name});
      walk(node,xpath);
     });
    }
   }walk(tree);
   for(const candidate of candidates.slice(0,24)){
    const found=await this.rpc('POST','/elements',{using:'xpath',value:candidate.xpath});if(!Array.isArray(found)||found.length!==1)continue;
    const id=found[0][ELEMENT]??found[0].ELEMENT;if(!id)continue;const ref='e'+items.length;this.refs.set(ref,{id,type:candidate.type});items.push({ref,name:redact(candidate.name),type:candidate.type});
   }
  }
  this.observedFingerprint=await this.fingerprint();
  return {content_fingerprint:this.observedFingerprint,review_context:{visible_elements:items},observation_id:this.observation,elements:items,app_id:this.app,expires_in:120,account_identity:'operator_must_verify'};
 }
 async run(intent){
  const {operation,arguments:args,platform}=intent,allowed=[...(policy.native_apps[this.kind]?.[platform]??[]),...policy.mobile_browsers[this.kind]];
  if(!allowed.includes(args.app_id))throw Error('Aplicación fuera del alcance.');
  await this.ensure(args.app_id);
  if(operation==='mobile_launch'){await this.guard(intent);return {app_id:args.app_id,opened:true,account_identity:'operator_must_verify'};}
  if(operation==='mobile_open_url'){
   const u=new URL(args.url);if(!this.browser||u.protocol!=='https:'||!policy.platform_hosts[platform].includes(u.hostname))throw Error('Navegación móvil no autorizada.');
   await this.rpc('POST','/url',{url:args.url});return {navigation:'delivered',provider_success_verified:false};
  }
  if(operation==='mobile_snapshot')return this.snapshot(intent);
  await this.guard(intent);
  if(args.observation_id!==this.observation||Date.now()-this.at>120000)throw Error('Observación móvil vencida. Revisa una nueva antes de autorizar.');
  if(this.observedFingerprint!==await this.fingerprint())throw Error('La pantalla móvil cambió. Revisa y autoriza una observación nueva.');
  const target=this.refs.get(args.ref);
  if(operation!=='mobile_swipe'&&(!target||/SecureTextField|password/i.test(target.type)))throw Error('Referencia móvil no válida o campo protegido.');
  this.refs.clear();this.observation=null;
  if(operation==='mobile_tap')await this.rpc('POST','/element/'+encodeURIComponent(target.id)+'/click',{});
  else if(operation==='mobile_type'){
   if(!/TextField|EditText|TextView|textarea|text|email|search/i.test(target.type))throw Error('La referencia no es un campo de texto.');
   const type=await this.rpc('GET','/element/'+encodeURIComponent(target.id)+'/attribute/'+(this.kind==='android'?'password':this.browser?'type':'type'));
   if(type===true||type==='true'||/password|SecureTextField/i.test(String(type)))throw Error('Campo protegido: requiere intervención manual.');
   await this.rpc('POST','/element/'+encodeURIComponent(target.id)+'/value',{text:args.text});
  }else if(operation==='mobile_swipe'){
   if(!['up','down','left','right'].includes(args.direction))throw Error('Dirección no permitida.');
   const rect=this.kind==='android'?await this.rpc('GET','/window/rect'):null;
   await this.rpc('POST','/execute/sync',{script:this.kind==='android'?'mobile: swipeGesture':'mobile: swipe',args:[this.kind==='android'?{left:Math.round(rect.width*0.15),top:Math.round(rect.height*0.2),width:Math.round(rect.width*0.7),height:Math.round(rect.height*0.6),direction:args.direction,percent:0.5}:{direction:args.direction}]});
  }else throw Error('Operación nativa no permitida.');
  return {interaction:'delivered',provider_success_verified:false};
 }
 async close(){if(this.sessionId)await this.request('DELETE','/session/'+encodeURIComponent(this.sessionId));this.sessionId=null;this.refs.clear();}
}
