import test from 'node:test';import assert from 'node:assert/strict';import {runLiveSmoke} from '../scripts/smoke_real_codex.mjs';
test('live smoke is opt-in',async()=>{const r=await runLiveSmoke({env:{}});assert.equal(r.skipped,true);assert.match(r.reason,/SUBAGENT_BROKER_LIVE=1/);});

test('live smoke requires explicit consumer repository binding before Codex probe',async()=>{
  await assert.rejects(
    ()=>runLiveSmoke({env:{SUBAGENT_BROKER_LIVE:'1',SUBAGENT_BROKER_CODEX_PATH:'definitely-missing-codex'}}),
    /SUBAGENT_BROKER_REPO_ROOT.*required/i
  );
});
