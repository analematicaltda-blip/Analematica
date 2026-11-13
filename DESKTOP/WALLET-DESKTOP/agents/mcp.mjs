import readline from 'node:readline';
import {tools,call} from './bridge.mjs';
const input=readline.createInterface({input:process.stdin});
for await(const line of input) {
 let message;
 try {
  if(line.length>8192)throw Error();message=JSON.parse(line);
  if(message.id===undefined)continue;
  let result;
  if(message.method==='initialize')result={protocolVersion:'2024-11-05',serverInfo:{name:'sgacd-wallet-team',version:'0.1.0'},capabilities:{tools:{}}};
  else if(message.method==='tools/list')result={tools};
  else if(message.method==='tools/call')result={content:[{type:'text',text:JSON.stringify(await call(message.params?.name,message.params?.arguments??{}))}]};
  else throw Error();
  process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:message.id,result})+'\n');
 }catch{if(message?.id!==undefined)process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:message.id,error:{code:-32602,message:'Solicitud no permitida o runtime no disponible. No se ejecutó una acción financiera.'}})+'\n');}
}
