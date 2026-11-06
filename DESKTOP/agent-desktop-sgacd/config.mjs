import path from 'node:path';
import {root} from './runtime.mjs';
const runner=path.join(root,'run.mjs');
const format=process.argv[2]||'vscode';
if(format==='codex'){
 console.log('[mcp_servers.sgacd_desktop]\ncommand = "node"\nargs = ['+JSON.stringify(runner)+', "mcp"]');
}else if(format==='vscode'){
 console.log(JSON.stringify({servers:{'sgacd-desktop':{type:'stdio',command:'node',args:[runner,'mcp']}}},null,2));
}else{console.error('Usa vscode o codex.');process.exitCode=1;}
