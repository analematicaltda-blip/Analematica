/* Synthetic transport contract in real Chromium; no fiscal-provider validation. */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),http=require('node:http');
const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const esbuild=require(path.join(deps,'esbuild'));
const root=path.resolve(__dirname,'../../..');
(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'commercial-queue-ui-'));let browser,server;
 try{
  const component=path.join(root,'FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/CommercialQueue.tsx');
  const entry=`import React,{useState} from 'react';import {createRoot} from 'react-dom/client';import {CommercialQueue} from ${JSON.stringify(component)};function Harness(){const [p,setP]=useState('company-a');const [u,setU]=useState('1');return <><button onClick={()=>setP(p==='company-a'?'company-b':'company-a')}>Cambiar empresa</button><button onClick={()=>setU(u?'':'1')}>Salir</button><CommercialQueue providerId={p} identity={u||null} request={(path,init)=>fetch(path,init)}/></>};createRoot(document.getElementById('root')).render(<Harness/>);`;
  esbuild.buildSync({stdin:{contents:entry,loader:'tsx',resolveDir:root},bundle:true,nodePaths:[deps],outfile:path.join(temp,'app.js'),define:{'process.env.NODE_ENV':'"production"'}});
  server=http.createServer((req,res)=>{res.setHeader('Content-Type',req.url==='/app.js'?'text/javascript':'text/html');res.end(req.url==='/app.js'?fs.readFileSync(path.join(temp,'app.js')):'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><div id="root"></div><script src="/app.js"></script>');});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH==='playwright'?undefined:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();let mode='normal';const methods=[];
  await page.route('**/api/v1/**',async route=>{
   methods.push(route.request().method());const url=new URL(route.request().url());
   if(url.searchParams.get('provider_id')==='company-b')return route.fulfill({status:403,json:{detail:'Denied'}});
   const counts={PENDING:3,PROCESSED:1,ERROR:0,OTHER:0};
   await route.fulfill({json:{success:true,data:{company_id:'00000000-0000-4000-8000-000000000001',read_only:true,financial_values_omitted:true,published_by_this_call:false,ledger_written:false,fiscal_consumer_available:mode==='malformed',fiscal_receipt_verified:false,fiscal_acceptance:'NOT_VERIFIED',blocking_reason:'FISCAL_CONSUMER_NOT_INTEGRATED',outbox_status_is_fiscal_acceptance:false,transport_counts:{invoice_requests:counts,reservation_confirmations:counts}}}});
  });
  await page.goto('http://127.0.0.1:'+server.address().port);
  const panel=page.getByRole('region',{name:'Cola comercial',exact:true});await panel.getByRole('button').click();
  await panel.getByText('Consumidor fiscal pendiente de integración. Aceptación fiscal no verificada.',{exact:true}).waitFor();
  assert.equal(await panel.getByRole('heading',{name:'Solicitudes de factura',exact:true}).count(),1);
  assert.equal(await panel.evaluate(e=>getComputedStyle(e).color),'rgb(255, 255, 255)');assert.equal(await panel.evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(14, 27, 56)');
  mode='malformed';await panel.getByRole('button').click();await panel.getByRole('alert').waitFor();assert.equal(await panel.getByRole('heading',{name:'Solicitudes de factura',exact:true}).count(),0);
  mode='normal';await panel.getByRole('button').click();await panel.getByRole('heading',{name:'Solicitudes de factura',exact:true}).waitFor();
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.getByText('Cambiar empresa',{exact:true}).click();assert.equal(await panel.getByRole('heading',{name:'Solicitudes de factura',exact:true}).count(),0);
  await panel.getByRole('button').click();await panel.getByRole('alert').waitFor();
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.getByText('Salir',{exact:true}).click();assert.equal(await panel.count(),0);
  assert(methods.length>0&&methods.every(m=>m==='GET'));
  console.log(JSON.stringify({passed:true,scope:'Synthetic Chromium contract',checks:['counts_rendered','fiscal_pending_explicit','malformed_response_rejected','context_change_clears_counts','permission_error','logout_clears_panel','blue_white_identity','mobile_no_overflow','GET_only'],production_ready:false}));
 }finally{if(browser)await browser.close();if(server)await new Promise(resolve=>server.close(resolve));fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
