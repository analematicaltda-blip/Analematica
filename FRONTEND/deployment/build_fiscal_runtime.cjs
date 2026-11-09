/* Deterministic browser asset from the canonical TypeScript envelope SDK. */
const fs=require('node:fs'),path=require('node:path');
const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS must identify the pinned development dependencies.');
const esbuild=require(path.join(deps,'esbuild'));if(esbuild.version!=='0.25.11')throw Error('Use esbuild0.25.11 for reproducible runtime bytes.');
const root=path.resolve(__dirname,'..'),src=path.join(root,'shared/accounting/fiscalEnvelope.ts'),out=path.join(root,'ANALEMATICA-FRONTEND/js/fiscal-envelope-runtime.js');
const built=esbuild.buildSync({stdin:{contents:fs.readFileSync(src,'utf8'),sourcefile:'fiscalEnvelope.ts',loader:'ts'},write:false,bundle:true,format:'iife',globalName:'SGACDEnvelopeRuntime',target:'es2022',legalComments:'inline'}).outputFiles[0].text;
const text='/* GENERATED from FRONTEND/shared/accounting/fiscalEnvelope.ts with esbuild0.25.11; rebuild/check with FRONTEND/deployment/build_fiscal_runtime.cjs. */\n(()=>{\n'+built+'\nif(typeof window!=="undefined")window.SGACDFiscalEnvelope=SGACDEnvelopeRuntime;\n})();\n';
if(process.argv.includes('--check')){if(fs.readFileSync(out,'utf8')!==text)throw Error('Fiscal runtime differs from canonical SDK.');console.log('Fiscal runtime matches canonical SDK.');}else fs.writeFileSync(out,text);
