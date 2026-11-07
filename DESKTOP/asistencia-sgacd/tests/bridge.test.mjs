import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {call,root,toolset,redact} from '../bridge.mjs';

test('guides share one catalog and never advertise action tools',async()=>{
 const catalog=await call('assistance_catalog');assert.equal(catalog.workflows.length,42);assert.equal(catalog.mode,'guidance_only');
 const flow=await call('assistance_workflow',{workflow_id:'gmail.send'});assert.equal(flow.steps.length,6);assert.equal(flow.steps[4].risk,'send');assert.equal(flow.steps[4].requires_confirmation,true);
 assert.equal(toolset.length,4);assert.ok(toolset.every(t=>t.annotations.readOnlyHint));
 await assert.rejects(call('desktop_click',{ref:'anything'}),/no permitida/);
 await assert.rejects(call('assistance_desktop_status',{command:'click'}),/parámetros/);
});

test('observation is disabled unless the local operator selects a window',async()=>{
 let spawned=false;const runner=async()=>{spawned=true;throw Error('must not run')};
 await assert.rejects(call('assistance_observe_window',{}, {environ:{},runner}),/deshabilitada/);
 await assert.rejects(call('assistance_observe_window',{}, {environ:{ASISTENCIA_ALLOW_OBSERVE:'1',ASISTENCIA_WINDOW_ID:'1; rm -rf'},runner}),/deshabilitada/);
 assert.equal(spawned,false);
});

test('legacy observation flags cannot bypass the approval control plane',async()=>{
 let called=false;
 await assert.rejects(call('assistance_observe_window',{}, {environ:{ASISTENCIA_ALLOW_OBSERVE:'1',ASISTENCIA_WINDOW_ID:'1234'},runner:async()=>{called=true}}),/dos autorizaciones/);
 assert.equal(called,false);
 const value=redact({role:'password',value:'private'});assert.ok(!JSON.stringify(value).includes('private'));
});

test('MCP initializes, lists bounded tools and refuses write calls',()=>{
 const requests=[{jsonrpc:'2.0',id:1,method:'initialize',params:{protocolVersion:'2025-06-18',capabilities:{},clientInfo:{name:'test',version:'1'}}},{jsonrpc:'2.0',method:'notifications/initialized'},{jsonrpc:'2.0',id:2,method:'tools/list'},{jsonrpc:'2.0',id:3,method:'tools/call',params:{name:'desktop_click',arguments:{ref:'anything'}}},{jsonrpc:'2.0',id:4,method:'tools/call',params:{name:'assistance_workflow',arguments:{workflow_id:'meta.campaign'}}}];
 const result=spawnSync(process.execPath,[path.join(root,'mcp.mjs')],{input:requests.map(x=>JSON.stringify(x)).join('\n')+'\n',encoding:'utf8',timeout:8000});assert.equal(result.status,0,result.stderr);
 const replies=result.stdout.trim().split('\n').map(line=>JSON.parse(line));assert.equal(replies.length,4);assert.equal(replies[1].result.tools.length,4);assert.equal(replies[2].result.isError,true);assert.equal(replies[3].result.isError,false);
});

test('Open Duet profile uses plan mode and no automatic memory or raw desktop tools',()=>{
 const result=spawnSync(process.execPath,[path.join(root,'prepare-duet.mjs')],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);
 const profile=JSON.parse(fs.readFileSync(path.join(root,'.runtime/agent-profile.json'),'utf8'));
 assert.equal(profile.approval_mode,'plan');assert.equal(profile.make_lead,false);assert.equal(profile.memory_enabled,false);assert.equal(profile.use_helper,false);
 const config=JSON.parse(fs.readFileSync(path.join(profile.workspace_path,'.mcp.json'),'utf8'));assert.deepEqual(Object.keys(config.mcpServers),['sgacd-assistance']);assert.ok(config.mcpServers['sgacd-assistance'].args[0].endsWith('asistencia-sgacd/mcp.mjs'));
});

test('vendored source matches pinned provenance',()=>{
 const result=spawnSync(process.execPath,[path.join(root,'verify-source.mjs')],{encoding:'utf8'});assert.equal(result.status,0,result.stderr);assert.match(result.stdout,/1172 archivos/);
});

test('real native status can be queried without observing a window',{skip:process.env.SGACD_ASSISTANCE_TEST_NATIVE!=='1'},async()=>{
 const result=await call('assistance_desktop_status');assert.equal(result.platform,process.platform==='win32'?'windows':process.platform==='darwin'?'macos':'linux');assert.equal(result.version,'1.2.0');assert.ok(result.permissions);assert.ok(!result.state_root);
});
