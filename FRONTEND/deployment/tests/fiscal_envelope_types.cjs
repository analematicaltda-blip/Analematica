/* Strict isolated browser SDK types; does not certify complete app builds. */
const path=require('node:path');const deps=process.env.QUOTE_UI_DEPS;if(!deps)throw Error('QUOTE_UI_DEPS required');
const ts=require(path.join(deps,'typescript'));const file=path.resolve(__dirname,'../../shared/accounting/fiscalEnvelope.ts');
const program=ts.createProgram([file],{strict:true,noEmit:true,skipLibCheck:true,target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext,moduleResolution:ts.ModuleResolutionKind.Bundler,types:[]});
const errors=ts.getPreEmitDiagnostics(program).map(d=>ts.flattenDiagnosticMessageText(d.messageText,' '));
console.log(JSON.stringify({scope:'Fiscal browser envelope SDK only',strict:true,errors}));process.exitCode=errors.length?1:0;
