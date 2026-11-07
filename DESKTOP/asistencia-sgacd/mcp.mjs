import readline from 'node:readline';
import {call,toolset} from './bridge.mjs';
const send=value=>process.stdout.write(JSON.stringify(value)+'\n');
const MAX=128*1024;
async function handle(message){
 if(!message||message.jsonrpc!=='2.0'||typeof message.method!=='string')return {jsonrpc:'2.0',id:message?.id??null,error:{code:-32600,message:'Invalid request'}};
 if(!Object.hasOwn(message,'id'))return;
 const result=value=>({jsonrpc:'2.0',id:message.id,result:value});
 if(message.method==='initialize')return result({protocolVersion:'2025-06-18',capabilities:{tools:{}},serverInfo:{name:'sgacd-platform-assistance',version:'1.0.0'},instructions:'Guías y observación opcional. Ninguna herramienta envía, publica o modifica cuentas.'});
 if(message.method==='ping')return result({});
 if(message.method==='tools/list')return result({tools:toolset});
 if(message.method==='tools/call'){
  try{
   const value=await call(message.params?.name,message.params?.arguments??{});
   let text=JSON.stringify(value);if(text.length>32000)text=JSON.stringify({truncated:true,excerpt:text.slice(0,30000)});
   return result({content:[{type:'text',text}],isError:false});
  }catch(error){
   // Native process diagnostics can include titles or paths; never echo child stderr.
   const message=error.code||error.killed?'No se pudo completar la observación local. Revisa los permisos en el equipo.':String(error.message).slice(0,300);
   return result({content:[{type:'text',text:message}],isError:true});
  }
 }
 return {jsonrpc:'2.0',id:message.id,error:{code:-32601,message:'Method not found'}};
}
const lines=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
// Serialize calls so a client cannot spawn an unbounded number of native processes.
for await(const line of lines){
 if(line.length>MAX){send({jsonrpc:'2.0',id:null,error:{code:-32600,message:'Request too large'}});continue}
 try{const response=await handle(JSON.parse(line));if(response)send(response)}catch{send({jsonrpc:'2.0',id:null,error:{code:-32700,message:'Parse error'}})}
}
