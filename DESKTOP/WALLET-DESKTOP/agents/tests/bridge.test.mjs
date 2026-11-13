import test from 'node:test';
import assert from 'node:assert/strict';
import {call,tools} from '../bridge.mjs';
test('eight wallet soldiers share gated engine policy without payment tools',async()=>{
 const team=await call('wallet_team');assert.equal(team.roles.length,8);assert.equal(team.can_approve,false);assert.equal(team.can_execute_payments,false);assert.ok(team.engines.includes('Open Duet'));
 const policy=await call('wallet_control_policy');assert.equal(policy.minimum_human_approvals,2);assert.equal(policy.requires_signed_server_grant,true);assert.deepEqual(policy.wallet_payment_tools,[]);
});
test('no generic commands, wallet approvals or injected arguments',async()=>{
 for(const name of ['wallet_pay','approve','execute','shell','assistance_observe_window'])await assert.rejects(call(name,{}));
 await assert.rejects(call('wallet_team',{command:'unsafe'}));assert.ok(tools.every(t=>t.annotations.readOnlyHint));
});
test('metadata pending register does not claim production readiness',async()=>{
 const result=await call('wallet_production_pending');assert.equal(result.production_enabled,false);assert.ok(result.items.length>=18);assert.ok(result.items.every(x=>x.acceptance&&x.evidence));
});
test('desktop diagnostic reuses existing fixed runtime bridge',async()=>{
 const runner=async(file,args)=>{assert.ok(args[0].endsWith('DESKTOP/agent-desktop-sgacd/run.mjs'));assert.deepEqual(args.slice(1),['status']);return {stdout:JSON.stringify({ok:true,data:{ready:false}})};};
 assert.deepEqual(await call('wallet_desktop_status',{}, {runner}),{ready:false});
});
