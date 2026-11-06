const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const config=JSON.parse(fs.readFileSync('FRONTEND/ANALEMATICA-FRONTEND/config/meta-public.json'));
const source=fs.readFileSync('FRONTEND/ANALEMATICA-FRONTEND/js/meta-setup.js','utf8');
async function test(origin,expected){
 let ready,writes=0;
 const fields=Object.fromEntries(['app_id','api_version','login_config_id','redirect_uris'].map(k=>[k,{value:''}]));
 const nodes={'meta-setup-status':{},'meta-callback-detected':{},'meta-copy-callback':{},'meta-app-form':{elements:fields}};
 vm.runInNewContext(source,{URL,location:{origin},document:{getElementById:k=>nodes[k]},window:{addEventListener:(name,fn)=>{assert.equal(name,'analematica:ready');ready=fn;}},fetch:async()=>({ok:true,json:async()=>config}),navigator:{clipboard:{writeText:async()=>writes++}}});
 assert.equal(fields.app_id.value,''); // No setup before owner authentication.
 await ready();
 if(expected){assert.equal(nodes['meta-callback-detected'].value,origin+config.callback_path);assert.equal(fields.login_config_id.value,config.user_login_config_id);assert.notEqual(fields.login_config_id.value,config.instagram_system_login_config_id);await nodes['meta-copy-callback'].onclick();assert.equal(writes,1);fields.app_id.value='999';await ready();assert.equal(fields.app_id.value,'999');}
 else{assert.match(nodes['meta-setup-status'].textContent,/HTTPS/);assert.equal(fields.app_id.value,'');}
}
(async()=>{await test('https://actual-space-8090.app.github.dev',true);await test('http://evil.example',false);console.log('Meta setup: authenticated initialization, origin validation, separate configs, copy and existing config preservation passed.');})().catch(e=>{console.error(e);process.exit(1);});
