/* Deferred transport deliberately ignores AbortSignal; no real account data. */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),http=require('node:http');
const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),esbuild=require(path.join(deps,'esbuild'));
(async()=>{const root=path.resolve(__dirname,'../../..'),temp=fs.mkdtempSync(path.join(os.tmpdir(),'query-races-'));let browser,server;
 try{
  const component=path.join(root,'FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/AccountingQuery.tsx');
  esbuild.buildSync({stdin:{contents:`import React,{useState} from 'react';import {createRoot} from 'react-dom/client';import {AccountingQuery} from ${JSON.stringify(component)};function App(){const [p,P]=useState('a'),[u,U]=useState('1');return <><button onClick={()=>P(p==='a'?'b':'a')}>Empresa</button><button onClick={()=>U(u?'':'1')}>Sesion</button><AccountingQuery identity={u||null} providerId={p} request={(path,init)=>{const {signal,...rest}=init||{};return fetch(path,rest)}}/></>};createRoot(document.getElementById('root')).render(<App/>);`,loader:'tsx',resolveDir:root},bundle:true,nodePaths:[deps],outfile:path.join(temp,'app.js'),define:{'process.env.NODE_ENV':'"production"'}});
  server=http.createServer((req,res)=>{res.setHeader('Content-Type',req.url==='/app.js'?'text/javascript':'text/html');res.end(req.url==='/app.js'?fs.readFileSync(path.join(temp,'app.js')):'<!doctype html><div id="root"></div><script src="/app.js"></script>');});await new Promise(r=>server.listen(0,'127.0.0.1',r));
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH==='playwright'?undefined:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();let hold=false,release,started;let fail=false;
  await page.route('**/api/v1/**',async route=>{
   const body=route.request().postDataJSON();const error=fail;
   if(hold){hold=false;started();await new Promise(r=>release=r);}
   if(error)return route.fulfill({status:403,json:{detail:'Denied'}});
   const company='00000000-0000-4000-8000-000000000001';
   await route.fulfill({json:{schema:'sgacd-accounting-query-v1',company_id:company,intent:'profitability',source:'ReportsEngine.get_profitability',execution:'DETERMINISTIC_ALLOWLIST',read_only:true,generated_sql:false,external_model_used:false,ledger_written:false,financial_action_authorized:false,data:{tenant_id:company,start_date:body.since,end_date:body.until,currency:'COP',revenue:'100.00',expenses:'40.00',net_profit:'60.00'}}});
  });
  await page.goto('http://127.0.0.1:'+server.address().port);
  const panel=page.getByRole('region',{name:'Consulta contable asistida',exact:true});
  async function begin(){hold=true;const waiting=new Promise(r=>started=r);await panel.getByRole('button').click();await waiting;}
  async function finish(){const response=page.waitForResponse(r=>r.url().includes('consulta-contable'));release();await response;await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));}
  const empresa=page.getByRole('button',{name:'Empresa',exact:true});
  await begin();await empresa.click();await empresa.click();assert(await panel.getByRole('button').isEnabled());await finish();assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  await panel.getByRole('button').click();await panel.getByText('60.00',{exact:true}).waitFor();await empresa.click();await empresa.click();assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  fail=true;await begin();fail=false;await empresa.click();await empresa.click();await finish();assert.equal(await panel.getByRole('alert').count(),0);
  const since=panel.getByLabel('Inicio de consulta',{exact:true});const original=await since.inputValue();
  await begin();await since.fill('2025-01-01');await since.fill(original);assert(await panel.getByRole('button').isEnabled());await finish();assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  await begin();await page.getByRole('button',{name:'Sesion',exact:true}).click();assert.equal(await panel.count(),0);await finish();await page.getByRole('button',{name:'Sesion',exact:true}).click();assert(await panel.getByRole('button').isEnabled());assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  await panel.getByRole('button').click();await panel.getByText('60.00',{exact:true}).waitFor();
  console.log(JSON.stringify({passed:true,scope:'Synthetic deferred Chromium transport ignoring AbortSignal',checks:['A_B_A_busy_reset','late_success_ignored','old_result_not_resurrected','late_permission_error_ignored','date_roundtrip_clears_pending','logout_pending_ignored','same_identity_reentry_usable','fresh_query_succeeds'],production_ready:false}));
 }finally{if(browser)await browser.close();if(server)await new Promise(r=>server.close(r));fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
