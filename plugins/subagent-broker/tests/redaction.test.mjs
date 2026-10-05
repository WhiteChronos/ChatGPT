import test from 'node:test';
import assert from 'node:assert/strict';
import {buildChildEnv,redactText} from '../mcp-server/redaction.mjs';

test('child environment is allowlisted without forwarding raw access tokens',()=>{
  const env=buildChildEnv({
    PATH:'/bin',
    HOME:'/tmp/h',
    LANG:'C',
    CODEX_HOME:'/tmp/codex',
    RANDOM_SECRET:'hide',
    CODEX_ACCESS_TOKEN:'codex-token'
  });
  assert.equal(env.PATH,'/bin');
  assert.equal(env.CODEX_HOME,'/tmp/codex');
  assert.equal('CODEX_ACCESS_TOKEN' in env,false);
  assert.equal('RANDOM_SECRET' in env,false);
});

test('secret values are redacted',()=>{assert.equal(redactText('failed token-123',{MY_TOKEN:'token-123'}),'failed [REDACTED]');});
