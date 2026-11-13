const fs=require('node:fs');
const assert=require('node:assert/strict');
const resolve=name=>require.resolve('@modelcontextprotocol/sdk/'+name,{paths:[process.env.MATRIX_GATEWAY||'/workspace/SGA-CD/matrix-os/packages/gateway']});
const {Client}=require(resolve('client/index.js'));
const {StdioClientTransport}=require(resolve('client/stdio.js'));
const {StreamableHTTPClientTransport}=require(resolve('client/streamableHttp.js'));
const values=Object.fromEntries(fs.readFileSync(process.env.NODE6_ENV,'utf8').split('\n').filter(line=>line.includes('=')).map(line=>{const i=line.indexOf('=');return [line.slice(0,i),line.slice(i+1)]}));
(async()=>{
 const client=new Client({name:'sgacd-matrix-compatibility-check',version:'0.1.0'});
 try{
  await client.connect(new StreamableHTTPClientTransport(new URL((process.env.NODE6_URL||'http://127.0.0.1:8606')+'/mcp'),{requestInit:{headers:{Authorization:'Bearer '+values.NODE6_TOKEN}}}));
  const tools=await client.listTools();assert.equal(tools.tools.length,5);
  const result=await client.callTool({name:'node6_status',arguments:{}});
  assert.equal(JSON.parse(result.content[0].text).node,6);
  console.log('PASS MCP initialize/listTools/callTool with Matrix-installed SDK; no provider call');
 }finally{await client.close()}
 await client.close();
 const bridge=new Client({name:'sgacd-stdio-check',version:'0.1.0'});
 try{await bridge.connect(new StdioClientTransport({command:'python3',args:['BACKEND/tools/node6_mcp_stdio.py','--env-file',process.env.NODE6_ENV]}));assert.equal((await bridge.listTools()).tools.length,5);assert.equal(JSON.parse((await bridge.callTool({name:'node6_status',arguments:{}})).content[0].text).node,6);console.log('PASS MCP stdio bridge with Matrix-installed SDK; credential kept outside client config');}finally{await bridge.close()}
})().catch(error=>{console.error(error.message);process.exit(1)});
