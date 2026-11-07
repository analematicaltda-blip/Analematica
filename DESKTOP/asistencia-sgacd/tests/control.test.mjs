import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {verifyGrant,policy} from '../control-client.mjs';
import {MobileDriver} from '../mobile-driver.mjs';
const key=crypto.generateKeyPairSync('ed25519'),config={device_id:'device-test',kind:'desktop',owner_id:1,tenant_id:1,platforms:['meta'],server_public_key:key.publicKey.export({type:'spki',format:'pem'})};
function envelope(change=()=>{}){
 const intent={policy:policy.version,target_kind:'desktop',job_id:'job-test',device_id:config.device_id,owner_id:1,tenant_id:1,platform:'meta',account_label:'principal',operation:'browser_snapshot',arguments:{}};
 const grant={policy:policy.version,device_id:config.device_id,owner_id:1,tenant_id:1,intent_json:JSON.stringify(intent),lease_id:'a'.repeat(48),issued_at:100,expires_at:130};
 grant.digest=crypto.createHash('sha256').update(grant.intent_json).digest('hex');grant.approvals=[1,2].map(stage=>({stage,user_id:1,tenant_id:1,digest:grant.digest}));change(grant);
 const payload=JSON.stringify(grant);return {payload,signature:crypto.sign(null,Buffer.from(payload),key.privateKey).toString('base64')};
}
test('signed permission binds two distinct approval stages, requesting admin and target',()=>{
 assert.equal(verifyGrant(envelope(),config,110).intent.operation,'browser_snapshot');
 for(const change of [g=>g.approvals.pop(),g=>g.approvals[1].stage=1,g=>g.approvals[1].user_id=2,g=>g.device_id='other',g=>g.expires_at=500,g=>g.intent_json+=' '])assert.throws(()=>verifyGrant(envelope(change),config,110));
 assert.throws(()=>verifyGrant(envelope(),config,131));const tampered=envelope();tampered.payload+=' ';assert.throws(()=>verifyGrant(tampered,config,110));
});
test('mobile cannot be pointed at a remote Appium server or selected implicitly',()=>{
 assert.throws(()=>new MobileDriver({kind:'ios',udid:'test-123',appium_url:'http://evil.example:4723/'}));assert.throws(()=>new MobileDriver({kind:'android'}));
});
for(const kind of ['android','ios'])test(kind+' W3C adapter pins UDID, requires fresh screen and refuses changed foreground app',async()=>{
 const calls=[],app=policy.native_apps[kind].meta[0];let source=kind==='android'?'<hierarchy><node class="android.widget.Button" text="Continue" clickable="true"/></hierarchy>':'<AppiumAUT><XCUIElementTypeButton type="XCUIElementTypeButton" label="Continue"/></AppiumAUT>',active=app;
 const transport=async(method,route,body)=>{
  calls.push({method,route,body});if(route==='/session')return {value:{sessionId:'test-session'}};
  if(route.endsWith('/current_package'))return {value:active};
  if(route.endsWith('/execute/sync')&&body.script==='mobile: activeAppInfo')return {value:{bundleId:active}};
  if(route.endsWith('/source'))return {value:source};
  if(route.endsWith('/elements'))return {value:[{'element-6066-11e4-a52e-4f735466cecf':'button-one'}]};
  return {value:null};
 };
 const driver=new MobileDriver({kind,udid:'explicit-device-123'},{transport});
 const intent={platform:'meta',operation:'mobile_snapshot',arguments:{app_id:app}};
 const snap=await driver.run(intent);assert.equal(snap.elements.length,1);assert.equal(calls[0].body.capabilities.alwaysMatch['appium:udid'],'explicit-device-123');
 const tap={...intent,operation:'mobile_tap',arguments:{app_id:app,observation_id:snap.observation_id,ref:'e0'}};
 source=source.replace('Continue','Changed');await assert.rejects(driver.run(tap),/cambió/);assert.equal(calls.filter(c=>c.route.endsWith('/click')).length,0);
 source=source.replace('Changed','Continue');await driver.run(tap);assert.equal(calls.filter(c=>c.route.endsWith('/click')).length,1);await assert.rejects(driver.run(tap),/vencida/);
 active='com.unapproved.app';await assert.rejects(driver.run(intent),/activa cambió/);await driver.close();
});
