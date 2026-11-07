import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {chromium} from 'playwright';
import {BrowserDriver} from '../browser-driver.mjs';

test('real Chromium: snapshots bind reviewed content, refuse changed recipient, consume references and block password fields',async()=>{
 const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html');res.end('<html><head><title>Isolated control fixture</title></head><body><label>Recipient<input id="recipient" value="reviewed@example.test"></label><button id="send" onclick="this.textContent=\'Delivered\'">Send</button><input type="file" hidden id="file"></body></html>')});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const port=server.address().port,dir=fs.mkdtempSync(path.join(os.tmpdir(),'sgacd-browser-test-'));
 const driver=new BrowserDriver(dir,{chromium,launchOptions:{channel:undefined,executablePath:process.env.CHROMIUM_PATH??(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),headless:true,args:['--no-sandbox']},allowURL:u=>u.hostname==='127.0.0.1'&&u.port===String(port)});
 try{
  await driver.run({platform:'meta',operation:'browser_open',arguments:{url:'http://127.0.0.1:'+port}});
  const snapshot=()=>driver.run({platform:'meta',operation:'browser_snapshot',arguments:{}});
  let snap=await snapshot();assert(Buffer.byteLength(JSON.stringify(snap))<26001);assert.equal(snap.elements.length,3);assert(snap.elements.some(e=>e.type==='file'));
  let button=snap.elements.find(e=>e.name==='Send');const click=()=>driver.run({platform:'meta',operation:'browser_click',arguments:{ref:button.ref,observation_id:snap.observation_id}});
  const state=driver.sessions.get('meta');await state.page.locator('#recipient').fill('changed@example.test');await assert.rejects(click(),/contenido cambió/);assert.equal(await state.page.locator('#send').innerText(),'Send');
  snap=await snapshot();button=snap.elements.find(e=>e.name==='Send');await click();assert.equal(await state.page.locator('#send').innerText(),'Delivered');await assert.rejects(click(),/vencida/);
  fs.mkdirSync(path.join(dir,'shared'));const file=path.join(dir,'shared','approved.txt');fs.writeFileSync(file,'approved bytes');
  const sha256=crypto.createHash('sha256').update('approved bytes').digest('hex');snap=await snapshot();let uploadRef=snap.elements.find(e=>e.type==='file').ref;
  fs.writeFileSync(file,'changed bytes');await assert.rejects(driver.run({platform:'meta',operation:'browser_upload',arguments:{ref:uploadRef,observation_id:snap.observation_id,file:'approved.txt',sha256}}),/archivo cambió/);
  fs.writeFileSync(file,'approved bytes');snap=await snapshot();uploadRef=snap.elements.find(e=>e.type==='file').ref;
  await driver.run({platform:'meta',operation:'browser_upload',arguments:{ref:uploadRef,observation_id:snap.observation_id,file:'approved.txt',sha256}});
  assert.equal(await state.page.locator('#file').evaluate(e=>e.files[0].name),'approved.txt');
  await state.page.locator('#recipient').evaluate(e=>e.type='password');await assert.rejects(snapshot(),/intervención humana/);
 }finally{await driver.close();await new Promise(resolve=>server.close(resolve));fs.rmSync(dir,{recursive:true,force:true});}
});
