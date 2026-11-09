/* Strict isolated component check; does not replace a complete Next.js build. */
const path=require('node:path');const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const ts=require(path.join(deps,'typescript'));
const file=path.resolve(__dirname,'../../SGA-ERP-TUR-FRONTEND/gestion-contable/indicadores-ledger/ReservationBilling.tsx');
const program=ts.createProgram([file],{strict:true,noEmit:true,skipLibCheck:true,target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext,moduleResolution:ts.ModuleResolutionKind.Bundler,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true,types:[],baseUrl:path.resolve(deps),paths:{react:['@types/react/index.d.ts'],'react/jsx-runtime':['@types/react/jsx-runtime.d.ts']}});
const errors=ts.getPreEmitDiagnostics(program).map(d=>ts.flattenDiagnosticMessageText(d.messageText,' '));
console.log(JSON.stringify({scope:'ReservationBilling component only',strict:true,errors}));process.exitCode=errors.length?1:0;
