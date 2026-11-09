/* Actual Chromium WebCrypto; synthetic bytes/keys; no persistence or upload. */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),os=require('node:os'),assert=require('node:assert/strict');
const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const esbuild=require(path.join(deps,'esbuild'));const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
(async()=>{let server,browser;const temp=fs.mkdtempSync(path.join(os.tmpdir(),'fiscal-crypto-'));
 try{
  esbuild.buildSync({entryPoints:[path.resolve(__dirname,'../../shared/accounting/fiscalEnvelope.ts')],bundle:true,format:'iife',globalName:'FiscalVault',outfile:path.join(temp,'vault.js')});
  server=http.createServer((req,res)=>{res.setHeader('Content-Type',req.url==='/vault.js'?'text/javascript':'text/html');res.end(req.url==='/vault.js'?fs.readFileSync(path.join(temp,'vault.js')):'<!doctype html><script src="/vault.js"></script>');});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH==='playwright'?undefined:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});const page=await browser.newPage();const requests=[];page.on('request',r=>requests.push({url:r.url(),method:r.method()}));await page.goto('http://127.0.0.1:'+server.address().port);
  const result=await page.evaluate(async()=>{
   const V=window.FiscalVault,check=(v,m)=>{if(!v)throw Error(m);};let rejected=0;
   async function reject(work){try{await work();}catch{rejected++;return;}throw Error('Expected authentication or contract rejection.');}
   const generate=()=>crypto.subtle.generateKey({name:'AES-KW',length:256},false,['wrapKey','unwrapKey']);
   const key=await generate(),replacement=await generate(),wrong=await generate();
   const ctx={company_id:'00000000-0000-4000-8000-000000000001',document_id:'00000000-0000-4000-8000-000000000002'};
   const plaintext=new TextEncoder().encode('%PDF-1.7\nSynthetic fiscal evidence secret');
   const first=await V.encryptDocument(plaintext,key,ctx),second=await V.encryptDocument(plaintext,key,ctx);
   check(first.iv!==second.iv&&first.wrapped_key!==second.wrapped_key&&first.ciphertext!==second.ciphertext,'Fresh IV and DEK required.');
   check(!JSON.stringify(first).includes('Synthetic fiscal'),'Plaintext must not appear in envelope.');
   const recovered=await V.decryptDocument(JSON.parse(JSON.stringify(first)),key,ctx);
   check(new TextDecoder().decode(recovered)===new TextDecoder().decode(plaintext),'Roundtrip failed.');recovered.fill(0);
   const flip=s=>(s[0]==='A'?'B':'A')+s.slice(1);
   for(const field of ['ciphertext','iv','wrapped_key'])await reject(()=>V.decryptDocument({...first,[field]:flip(first[field])},key,ctx));
   await reject(()=>V.decryptDocument(first,wrong,ctx));
   await reject(()=>V.decryptDocument(first,key,{...ctx,company_id:'00000000-0000-4000-8000-000000000003'}));
   await reject(()=>V.decryptDocument(first,key,{...ctx,document_id:'00000000-0000-4000-8000-000000000003'}));
   await reject(()=>V.decryptDocument({...first,context:{...ctx,document_id:'00000000-0000-4000-8000-000000000003'}},key,{...ctx,document_id:'00000000-0000-4000-8000-000000000003'}));
   await reject(()=>V.decryptDocument({...first,plaintext:'forbidden'},key,ctx));
   await reject(()=>V.decryptDocument({...first,schema:'unknown'},key,ctx));
   await reject(()=>V.decryptDocument({...first,iv:first.iv+'='},key,ctx));
   const extractable=await crypto.subtle.generateKey({name:'AES-KW',length:256},true,['wrapKey','unwrapKey']);
   await reject(()=>V.encryptDocument(plaintext,extractable,ctx));
   await reject(()=>V.encryptDocument(new Uint8Array(0),key,ctx));
   await reject(()=>V.encryptDocument(new Uint8Array(V.MAX_DOCUMENT_BYTES+1),key,ctx));
   const binary=Uint8Array.from({length:100000},(_,i)=>i%256);
   const packed=await V.encryptDocument(binary,key,ctx);const unpacked=await V.decryptDocument(packed,key,ctx);
   check(unpacked.every((v,i)=>v===binary[i]),'Chunked binary document roundtrip failed.');unpacked.fill(0);
   const rotated=await V.rewrapDocument(first,key,replacement,ctx);
   check(rotated.iv===first.iv&&rotated.ciphertext===first.ciphertext&&rotated.wrapped_key!==first.wrapped_key,'Rewrap must preserve authenticated ciphertext.');
   check(new TextDecoder().decode(await V.decryptDocument(rotated,replacement,ctx))===new TextDecoder().decode(plaintext),'New KEK cannot recover envelope.');
   await reject(()=>V.decryptDocument(rotated,key,ctx));
   await reject(()=>V.rewrapDocument({...first,ciphertext:flip(first.ciphertext)},key,replacement,ctx));
   const known=await crypto.subtle.importKey('raw',Uint8Array.from({length:32},(_,i)=>i),{name:'AES-KW'},false,['wrapKey','unwrapKey']);
   const interop=await V.encryptDocument(plaintext,known,ctx);
   return {_interop:interop,checks:['browser_webcrypto_roundtrip','fresh_dek_and_iv','no_plaintext_in_envelope','tamper_authentication','company_document_aad','strict_schema_and_encoding','key_and_size_bounds','authenticated_kek_rewrap','chunked_binary_document'],rejected_cases:rejected,passed:true};
  });
  const subtle=require('node:crypto').webcrypto.subtle;const envelope=result._interop;
  const known=await subtle.importKey('raw',Uint8Array.from({length:32},(_,i)=>i),{name:'AES-KW'},false,['unwrapKey']);
  const dek=await subtle.unwrapKey('raw',Buffer.from(envelope.wrapped_key,'base64url'),known,'AES-KW',{name:'AES-GCM',length:256},false,['decrypt']);
  const aad=new TextEncoder().encode(JSON.stringify([envelope.schema,envelope.algorithm,envelope.context.company_id,envelope.context.document_id,'fiscal-document']));
  const recovered=await subtle.decrypt({name:'AES-GCM',iv:Buffer.from(envelope.iv,'base64url'),additionalData:aad,tagLength:128},dek,Buffer.from(envelope.ciphertext,'base64url'));
  assert.equal(new TextDecoder().decode(recovered),'%PDF-1.7\nSynthetic fiscal evidence secret');new Uint8Array(recovered).fill(0);delete result._interop;result.checks.push('node_openssl_interoperability');
  assert(requests.every(r=>r.method==='GET'));assert(requests.every(r=>new URL(r.url).origin==='http://127.0.0.1:'+server.address().port));
  console.log(JSON.stringify({...result,network:'Only local test HTML/JS GET requests; no upload or external service',production_ready:false}));
 }finally{if(browser)await browser.close();if(server)await new Promise(resolve=>server.close(resolve));fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
