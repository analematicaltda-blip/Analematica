/* Browser contract fixture: synthetic API and content, no live model or login. */
const assert=require('node:assert/strict'),fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');let draft=null,exported=0;
(async()=>{
 const server=http.createServer(async(req,res)=>{
  if(req.url.startsWith('/api/')){
   res.setHeader('Content-Type','application/json');if(req.headers.authorization!=='Bearer content-ui-fixture'){res.writeHead(401);res.end('{}');return}
   let body='';for await(const chunk of req)body+=chunk;const input=body?JSON.parse(body):{};
   if(req.url.endsWith('/generate')){res.writeHead(503);res.end(JSON.stringify({detail:'Ollama no está habilitado'}));return}
   if(req.url.endsWith('/drafts')&&req.method==='GET'){res.end(JSON.stringify({drafts:draft?[draft]:[]}));return}
   if(req.url.endsWith('/drafts')&&req.method==='POST')draft={id:'fixture-private',revision:1,status:'draft',digest:'a'.repeat(64),content:input,source:{provider:'human'},publication_enabled:false};
   else if(req.url.endsWith('/review')){assert.equal(input.accuracy_rights_privacy_checked,true);draft={...draft,revision:draft.revision+1,status:'reviewed'}}
   else if(req.url.endsWith('/export')){assert.equal(draft.status,'reviewed');exported++}
   else if(req.method==='PUT'){assert.equal(input.revision,draft.revision);draft={...draft,content:input,revision:draft.revision+1,status:'draft'}}
   res.end(JSON.stringify(draft));return;
  }
  const files={'/content.html':'text/html','/js/content.js':'text/javascript','/css/assistance.css':'text/css','/css/content.css':'text/css'};
  if(!files[req.url]){res.writeHead(404);res.end();return}res.setHeader('Content-Type',files[req.url]);res.end(fs.readFileSync(path.join(root,req.url)));
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),args:['--no-sandbox']});const errors=[];
 try{for(const width of [1440,390,320]){
  draft=null;const context=await browser.newContext({viewport:{width,height:900},acceptDownloads:true});const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto(origin+'/content.html');assert.equal(await page.locator('#save').isDisabled(),true);
  await page.evaluate(()=>localStorage.setItem('accessToken','content-ui-fixture'));await page.reload();await page.waitForFunction(()=>document.getElementById('status').textContent.includes('disponible'));
  await page.locator('#brief').fill('Servicio confirmado');await page.locator('#text').fill('<script>alert("test")</script> Texto de prueba');await page.locator('#save').click();
  await page.waitForFunction(()=>document.getElementById('version').textContent.includes('Versión 1'));assert.equal(await page.locator('#export').isDisabled(),true);
  await page.locator('#checked').check();await page.locator('#review').click();await page.waitForFunction(()=>!document.getElementById('export').disabled);
  const download=page.waitForEvent('download');await page.locator('#export').click();await download;
  await page.locator('#text').fill('Texto editado');assert.equal(await page.locator('#export').isDisabled(),true);await page.locator('#save').click();await page.waitForFunction(()=>document.getElementById('version').textContent.includes('Versión 3'));
  assert.equal(await page.locator('#export').isDisabled(),true);assert.equal(await page.locator('body').evaluate(el=>getComputedStyle(el).color),'rgb(255, 255, 255)');
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'overflow '+width);
  await page.locator('#new').click();await page.locator('#brief').fill('Texto sin proveedor');await page.locator('#generate').click();await page.waitForFunction(()=>document.getElementById('status').textContent.includes('Ollama no está habilitado'));
  await context.close();
 }assert.equal(exported,3);assert.deepEqual(errors,[]);console.log('Content UI: create/review/export/edit, unavailable provider, white text and no overflow at 1440/390/320; synthetic API fixture.');}
 finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(e=>{console.error(e);process.exitCode=1});
