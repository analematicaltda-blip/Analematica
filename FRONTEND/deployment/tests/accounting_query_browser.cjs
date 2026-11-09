/* Isolated UI contract; synthetic answers do not qualify accounting sources. */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),http=require('node:http');
const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const esbuild=require(path.join(deps,'esbuild'));
(async()=>{const root=path.resolve(__dirname,'../../..'),temp=fs.mkdtempSync(path.join(os.tmpdir(),'query-ui-'));let browser,server;
 try{
  const file=path.join(root,'FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/AccountingQuery.tsx');
  esbuild.buildSync({stdin:{contents:`import React,{useState} from 'react';import {createRoot} from 'react-dom/client';import {AccountingQuery} from ${JSON.stringify(file)};function App(){const [p,P]=useState('a'),[u,U]=useState('1');return <><button onClick={()=>P(p==='a'?'b':'a')}>Empresa</button><button onClick={()=>U('')}>Salir</button><AccountingQuery identity={u||null} providerId={p} request={(p,i)=>fetch(p,i)}/></>};createRoot(document.getElementById('root')).render(<App/>);`,loader:'tsx',resolveDir:root},bundle:true,nodePaths:[deps],outfile:path.join(temp,'app.js'),define:{'process.env.NODE_ENV':'"production"'}});
  server=http.createServer((req,res)=>{res.setHeader('Content-Type',req.url==='/app.js'?'text/javascript':'text/html');res.end(req.url==='/app.js'?fs.readFileSync(path.join(temp,'app.js')):'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><div id="root"></div><script src="/app.js"></script>');});await new Promise(r=>server.listen(0,'127.0.0.1',r));
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH==='playwright'?undefined:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();let malformed=false;const methods=[];
  await page.route('**/api/v1/**',async route=>{
   const req=route.request();methods.push(req.method());if(new URL(req.url()).searchParams.get('provider_id')==='b')return route.fulfill({status:403,json:{detail:'Denied'}});
   const input=req.postDataJSON(),company='00000000-0000-4000-8000-000000000001';
   return route.fulfill({json:{success:true,data:{schema:'sgacd-accounting-query-v1',company_id:company,intent:'profitability',source:'ReportsEngine.get_profitability',execution:'DETERMINISTIC_ALLOWLIST',read_only:true,generated_sql:malformed,external_model_used:false,ledger_written:false,financial_action_authorized:false,data:{tenant_id:company,start_date:input.since,end_date:input.until,currency:'COP',revenue:'100.00',expenses:'40.00',net_profit:'60.00'}}}});
  });
  await page.goto('http://127.0.0.1:'+server.address().port);const panel=page.getByRole('region',{name:'Consulta contable asistida',exact:true});
  await panel.getByRole('button').click();await panel.getByText('60.00',{exact:true}).waitFor();
  assert.equal(await panel.evaluate(e=>getComputedStyle(e).color),'rgb(255, 255, 255)');
  assert.equal(await panel.evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(14, 27, 56)');
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await panel.getByLabel('Inicio de consulta',{exact:true}).fill('2026-01-01');assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  malformed=true;await panel.getByRole('button').click();await panel.getByRole('alert').waitFor();assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  malformed=false;await panel.getByRole('button').click();await panel.getByText('60.00',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Empresa',exact:true}).click();assert.equal(await panel.getByText('60.00',{exact:true}).count(),0);
  await panel.getByRole('button').click();await panel.getByRole('alert').waitFor();
  await page.getByRole('button',{name:'Salir',exact:true}).click();assert.equal(await panel.count(),0);assert(methods.length>0&&methods.every(m=>m==='POST'));
  console.log(JSON.stringify({passed:true,scope:'Synthetic Chromium query UI',checks:['exact_money_and_source_rendered','blue_white_identity','mobile_no_overflow','edited_dates_hide_result','unsafe_contract_rejected','company_change_hides_result','permission_denied','logout_hides_result','POST_query_only'],production_ready:false}));
 }finally{if(browser)await browser.close();if(server)await new Promise(r=>server.close(r));fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
