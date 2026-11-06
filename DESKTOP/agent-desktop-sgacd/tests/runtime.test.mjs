import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import {paths,verifyInstalled,environment,digest,provenance,root} from '../runtime.mjs';

test('six platform packages resolve and unsupported platforms fail',()=>{
 for(const platform of ['linux','darwin','win32'])for(const arch of ['x64','arm64']){
  const p=paths(platform,arch);assert.equal(p.platform,platform);assert.ok(p.binary.includes(platform));assert.equal(p.helpers.length,platform==='win32'?0:1);
 }
 assert.throws(()=>paths('android','arm64'),/no soportada/);
});

test('isolated state does not replace user home or network selectors',()=>{
 const p=paths();const env=environment(p);assert.equal(env.HOME,process.env.HOME);assert.equal(env.USERPROFILE,process.env.USERPROFILE);assert.equal(env.HTTPS_PROXY,process.env.HTTPS_PROXY);assert.equal(env.AGENT_DESKTOP_HOME,p.state);
});

test('missing or modified executable/helper fails integrity validation',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sga-desktop-'));
 try{
  const p={platform:'linux',arch:'x64',metadata:path.join(dir,'installed.json'),binary:path.join(dir,'cli'),helpers:[path.join(dir,'helper')]};
  assert.equal(verifyInstalled(p).ready,false);fs.writeFileSync(p.binary,'fake-cli');fs.writeFileSync(p.helpers[0],'fake-helper');
  const metadata={version:provenance.release_version,platform:p.platform,arch:p.arch,hashes:{cli:digest(p.binary),helper:digest(p.helpers[0])}};
  fs.writeFileSync(p.metadata,JSON.stringify(metadata));assert.equal(verifyInstalled(p).ready,true);
  fs.writeFileSync(p.helpers[0],'changed');assert.equal(verifyInstalled(p).ready,false);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});

test('configuration outputs valid local stdio setup with absolute paths',()=>{
 const result=spawnSync(process.execPath,[path.join(root,'config.mjs'),'vscode'],{encoding:'utf8'});assert.equal(result.status,0);
 const server=JSON.parse(result.stdout).servers['sgacd-desktop'];assert.equal(server.type,'stdio');assert.equal(server.command,'node');assert.ok(path.isAbsolute(server.args[0]));assert.equal(server.args[1],'mcp');
 const toml=spawnSync(process.execPath,[path.join(root,'config.mjs'),'codex'],{encoding:'utf8'});assert.equal(toml.status,0);assert.match(toml.stdout,/mcp_servers\.sgacd_desktop/);assert.ok(!toml.stdout.includes('http://'));
});

test('native release reports matching version',{skip:process.env.SGACD_DESKTOP_TEST_NATIVE!=='1'},()=>{
 const r=spawnSync(process.execPath,[path.join(root,'run.mjs'),'version'],{encoding:'utf8'});assert.equal(r.status,0,r.stderr);assert.equal(JSON.parse(r.stdout).data.version,provenance.release_version);
});

test('MCP initializes and lists real desktop tools without actions',{skip:process.env.SGACD_DESKTOP_TEST_NATIVE!=='1',timeout:15000},async()=>{
 const child=spawn(process.execPath,[path.join(root,'run.mjs'),'mcp'],{stdio:['pipe','pipe','pipe']});let buffer='',stderr='';
 child.stderr.on('data',chunk=>{stderr+=chunk});
 try{
  const messages=new Map();const waits=new Map();
  child.stdout.on('data',chunk=>{
   buffer+=chunk;
   while(buffer.includes('\n')){const end=buffer.indexOf('\n');const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line.trim())continue;
    const message=JSON.parse(line);messages.set(message.id,message);waits.get(message.id)?.(message);
   }
  });
  const receive=id=>messages.has(id)?Promise.resolve(messages.get(id)):new Promise((resolve,reject)=>{
   const timer=setTimeout(()=>reject(new Error('MCP response timed out: '+stderr)),8000);
   waits.set(id,message=>{clearTimeout(timer);resolve(message)});
  });
  child.stdin.write(JSON.stringify({jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-06-18',capabilities:{},clientInfo:{name:'sgacd-local-test',version:'1'}}})+'\n');
  const init=await receive(1);assert.ok(init.result.serverInfo);
  child.stdin.write(JSON.stringify({jsonrpc:'2.0',method:'notifications/initialized'})+'\n');
  child.stdin.write(JSON.stringify({jsonrpc:'2.0',id:2,method:'tools/list',params:{}})+'\n');
  const response=await receive(2);const names=new Set(response.result.tools.map(t=>t.name));assert.ok(names.has('desktop_snapshot'));assert.ok(names.has('desktop_click'));assert.ok(names.size>40);
 }finally{child.stdin.end();child.kill();}
});
