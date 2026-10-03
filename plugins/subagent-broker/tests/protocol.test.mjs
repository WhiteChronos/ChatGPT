import test from 'node:test';
import assert from 'node:assert/strict';
import {AGENT_STATES,TERMINAL_STATES,canTransition,assertTransition,validateSpawnArgs,validateWaitArgs} from '../mcp-server/protocol.mjs';

test('lifecycle states and terminal states are exact',()=>{
  assert.deepEqual([...AGENT_STATES],['QUEUED','SPAWNING','RUNNING','COMPLETED','FAILED','TIMED_OUT','CANCEL_REQUESTED','CANCELLED','ORPHANED']);
  assert.deepEqual([...TERMINAL_STATES],['COMPLETED','FAILED','TIMED_OUT','CANCELLED','ORPHANED']);
});
test('followup is the only completed-to-spawning transition',()=>{
  assert.equal(canTransition('QUEUED','SPAWNING'),true);
  assert.equal(canTransition('RUNNING','COMPLETED'),true);
  assert.equal(canTransition('COMPLETED','SPAWNING'),false);
  assert.doesNotThrow(()=>assertTransition('COMPLETED','SPAWNING','followup'));
  assert.throws(()=>assertTransition('FAILED','SPAWNING','followup'));
});
test('spawn validation is strict and bounded',()=>{
  const v=validateSpawnArgs({task:'do one thing',role:'implementer',workspace_mode:'worktree_write'});
  assert.equal(v.timeout_seconds,1800); assert.equal(v.priority,'normal');
  assert.throws(()=>validateSpawnArgs({task:'x',role:'implementer',workspace_mode:'worktree_write',command:'rm -rf /'}),/unknown field/i);
  assert.throws(()=>validateSpawnArgs({task:'x',role:'bogus',workspace_mode:'read_only'}),/role/i);
});
test('wait validation enforces bounds',()=>{
  assert.equal(validateWaitArgs({agent_id:'sa_abc',timeout_ms:1000}).timeout_ms,1000);
  assert.throws(()=>validateWaitArgs({agent_id:'sa_abc',timeout_ms:999}),/timeout/i);
  assert.throws(()=>validateWaitArgs({agent_id:'sa_abc',timeout_ms:600001}),/timeout/i);
});
