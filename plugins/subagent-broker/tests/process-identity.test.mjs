import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { readProcessIdentity, terminateProcessGroup } from '../mcp-server/process_identity.mjs';

async function waitForExit(pid, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (!await readProcessIdentity(pid)) return;
    await new Promise(resolve => setTimeout(resolve, 50));
  }
  throw new Error(`process ${pid} did not exit`);
}

test('process identity is available on the current host', async () => {
  const identity = await readProcessIdentity(process.pid);
  assert.equal(identity.pid, process.pid);
  assert.match(identity.start_ticks, /^\d+$/);
});

test('termination contains the complete spawned process tree', async () => {
  const script = "const{spawn}=require('node:child_process');const c=spawn(process.execPath,['-e','setInterval(()=>{},1000)'],{stdio:'ignore'});console.log(c.pid);setInterval(()=>{},1000)";
  const parent = spawn(process.execPath, ['-e', script], {
    detached: process.platform === 'linux',
    stdio: ['ignore', 'pipe', 'ignore'],
  });
  const childPid = await new Promise((resolve, reject) => {
    let output = '';
    parent.stdout.setEncoding('utf8');
    parent.stdout.on('data', chunk => {
      output += chunk;
      const line = output.split(/\r?\n/)[0];
      if (/^\d+$/.test(line)) resolve(Number(line));
    });
    parent.on('error', reject);
  });
  try {
    assert.ok(await readProcessIdentity(parent.pid));
    assert.ok(await readProcessIdentity(childPid));
    await terminateProcessGroup(parent.pid, 'SIGTERM');
    await Promise.all([waitForExit(parent.pid), waitForExit(childPid)]);
  } finally {
    try { process.kill(parent.pid, 'SIGKILL'); } catch {}
    try { process.kill(childPid, 'SIGKILL'); } catch {}
  }
});
