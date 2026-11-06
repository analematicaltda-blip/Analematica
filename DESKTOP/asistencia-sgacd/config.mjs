import path from 'node:path';
import {root} from './bridge.mjs';
const runner=path.join(root,'mcp.mjs');
const server={command:'node',args:[runner]};
const kind=process.argv[2]??'vscode';
if(kind==='vscode')console.log(JSON.stringify({servers:{'sgacd-assistance':{type:'stdio',...server}}},null,2));
else if(kind==='claude')console.log(JSON.stringify({mcpServers:{'sgacd-assistance':server}},null,2));
else if(kind==='codex')console.log('[mcp_servers.sgacd_assistance]\ncommand = "node"\nargs = ['+JSON.stringify(runner)+']');
else{console.error('Usa vscode, claude o codex.');process.exitCode=1}
