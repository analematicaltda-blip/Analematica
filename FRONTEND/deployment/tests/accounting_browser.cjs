/* UI contract tests with synthetic API responses; not real-account integration. */
const assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),http=require('node:http');
const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');const esbuild=require(path.join(deps,'esbuild'));
const root=path.resolve(__dirname,'../../..');
(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ledger-ui-'));let server,browser;
 try{
  const component=path.join(root,'FRONTEND/SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/LedgerIndicators.tsx');
  const entry=`import React,{useState} from 'react';import {createRoot} from 'react-dom/client';import {LedgerIndicators} from ${JSON.stringify(component)};import {ReconciliationDiagnostic} from ${JSON.stringify(path.join(path.dirname(component),'ReconciliationDiagnostic.tsx'))};function Harness(){const [p,setP]=useState('company-a');const [u,setU]=useState('1');return <><button onClick={()=>setP(p==='company-a'?'company-b':'company-a')}>Cambiar empresa</button><button onClick={()=>setU(u?'':'1')}>Salir</button><LedgerIndicators providerId={p} identity={u||null} request={(path,init)=>fetch(path,init)}/><ReconciliationDiagnostic providerId={p} identity={u||null} request={(path,init)=>fetch(path,init)}/></>};createRoot(document.getElementById('root')).render(<Harness/>);`;
  esbuild.buildSync({stdin:{contents:entry,loader:'tsx',resolveDir:root},bundle:true,nodePaths:[deps],outfile:path.join(temp,'app.js'),define:{'process.env.NODE_ENV':'"production"'}});
  server=http.createServer((req,res)=>{res.setHeader('Content-Type',req.url==='/app.js'?'text/javascript':'text/html');res.end(req.url==='/app.js'?fs.readFileSync(path.join(temp,'app.js')):'<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><div id="root"></div><script src="/app.js"></script>');});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const port=server.address().port;
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH==='playwright'?undefined:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();let mode='normal';const methods=[];
  await page.route('**/api/v1/**',async route=>{
   const req=route.request();methods.push(req.method());const url=new URL(req.url());
   if(url.searchParams.get('provider_id')==='company-b'){await new Promise(r=>setTimeout(r,200));return route.fulfill({status:403,json:{detail:'Denied'}});}
   if(url.pathname.includes('diagnostico-conciliacion')){
    const next=url.searchParams.has('despues_id');
    return route.fulfill({json:{read_only:true,repairs_executed:mode==='malformed',posted_journal_count:2,legacy_journal_count:1,initial_balance_account_count:1,
     initial_balance_accounts:[{account_id:'00000000-0000-4000-8000-000000000010',code:'1105'}],initial_balance_sample_truncated:false,
     entries:[{journal_id:next?'00000000-0000-4000-8000-000000000002':'00000000-0000-4000-8000-000000000001',economic_date:'2026-11-08',hash_version:next?'legacy':'v2',findings:[next?'LEGACY_HASH_REVIEW_REQUIRED':'HASH_MISMATCH']}],
     next_after:next?null:'00000000-0000-4000-8000-000000000001',chain_validation_included:false,full_ledger_certified:false,snapshot_stable_across_pages:false}});
   }
   const end=url.searchParams.get('hasta')||url.searchParams.get('fecha_corte');
   if(url.pathname.includes('rentabilidad')){
    const report={tenant_id:'tenant-a',currency:'COP',start_date:url.searchParams.get('desde'),end_date:end,revenue:'100.00',expenses:'40.00',net_profit:'60.00',sources:[{account_id:'revenue',code:'4105',type:'REVENUE',net_amount:'100.00'}],net_margin:{value:'60.0000',unavailable_reason:null}};
    if(mode==='malformed')report.revenue=100;
    return route.fulfill({json:report});
   }
   return route.fulfill({json:{tenant_id:'tenant-a',currency:'COP',cutoff_date:end,value:mode==='missing'?null:'2.0000',unavailable_reason:mode==='missing'?'REVIEWED_CLASSIFICATION_REQUIRED':null,policy:mode==='missing'?null:{revision:1}}});
  });
  await page.goto('http://127.0.0.1:'+port);await page.getByText('60.0000 %',{exact:true}).waitFor();await page.getByText('2.0000 veces',{exact:true}).waitFor();
  const panel=page.getByRole('region',{name:'Indicadores del libro mayor'});
  assert.equal(await panel.evaluate(e=>getComputedStyle(e).color),'rgb(255, 255, 255)');assert.equal(await panel.evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(14, 27, 56)');
  await page.getByText('Cambiar empresa',{exact:true}).click();assert.equal(await page.getByText('60.0000 %',{exact:true}).count(),0);await page.getByRole('alert').waitFor();
  await page.getByText('Cambiar empresa',{exact:true}).click();await page.getByText('60.0000 %',{exact:true}).waitFor();
  mode='missing';await page.getByRole('button',{name:'Consultar nuevamente'}).click();await page.getByText('Falta una clasificación contable revisada.',{exact:true}).waitFor();
  mode='malformed';await page.getByRole('button',{name:'Consultar nuevamente'}).click();await page.getByRole('alert').waitFor();assert.equal(await page.getByText('60.0000 %',{exact:true}).count(),0);
  mode='normal';await page.getByRole('button',{name:'Consultar nuevamente'}).click();await page.getByText('60.0000 %',{exact:true}).waitFor();
  await page.getByLabel('Desde',{exact:true}).fill('2099-12-31');await page.getByRole('alert').waitFor();assert.equal(await page.getByText('60.0000 %',{exact:true}).count(),0);
  await page.getByText('Salir',{exact:true}).click();await page.getByText('Inicia sesión en el ERP.',{exact:true}).waitFor();
  await page.getByText('Salir',{exact:true}).click();
  const diagnostic=page.getByRole('region',{name:'Diagnóstico de conciliación',exact:true});
  await diagnostic.getByRole('button',{name:'Consultar diagnóstico',exact:true}).click();
  await diagnostic.getByText('La huella del asiento no coincide; requiere investigación.',{exact:true}).waitFor();
  await diagnostic.getByText('Cuentas con saldo inicial pendiente de conciliación',{exact:true}).click();
  await diagnostic.getByText('Cuenta 1105 · 00000000-0000-4000-8000-000000000010',{exact:true}).waitFor();
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await diagnostic.getByRole('button',{name:'Consultar siguiente página',exact:true}).click();
  await diagnostic.getByText('Registro legado: revisar su versión de integridad sin reescribirla.',{exact:true}).waitFor();
  assert.equal(await diagnostic.getByText('La huella del asiento no coincide; requiere investigación.',{exact:true}).count(),0);
  mode='malformed';await diagnostic.getByRole('button',{name:'Consultar diagnóstico',exact:true}).click();
  await diagnostic.getByText('Diagnóstico incompleto; no se muestran conclusiones sin validar.',{exact:true}).waitFor();
  assert.equal(await diagnostic.getByRole('table').count(),0);
  await page.getByText('Salir',{exact:true}).click();assert.equal(await page.getByRole('region',{name:'Diagnóstico de conciliación',exact:true}).count(),0);
  await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  assert(methods.length>0&&methods.every(m=>m==='GET'));
  const admin=fs.readFileSync(path.join(root,'FRONTEND/ANALEMATICA-FRONTEND/admin.html'),'utf8');
  const section=await page.evaluate(html=>{const template=document.createElement('template');template.innerHTML=html;return template.content.querySelector('#tab-contable')?.outerHTML||'';},admin);
  for(const id of ['contableSumasStatus','contablePrecierreStatus','contableStarStatus','contableConciliacionStatus','contableDepreciacionStatus','contableChecklistStatus']){
   assert(new RegExp('id="'+id+'"[^>]*>PENDIENTE DE VERIFICACIÓN<').test(section));
  }
  assert(!section.includes('CONCILIADO 100%'));
  assert(/id="auditLedgerStatus"[^>]*>PENDIENTE DE VERIFICACIÓN</.test(admin));
  console.log(JSON.stringify({scope:'Synthetic browser/API contract; no live accounts or production',checks:['decimal_values','company_switch_clears_values','permission_error','missing_classification','malformed_payload_rejected','invalid_dates','logout_clears_values','white_text_blue_surface','mobile_no_overflow','GET_only','analematica_no_unverified_status','diagnostic_findings_and_opening_accounts','diagnostic_next_page','diagnostic_rejects_mutating_payload','diagnostic_logout_clears_view'],passed:true,production_ready:false}));
 }finally{if(browser)await browser.close();if(server)await new Promise(resolve=>server.close(resolve));fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
