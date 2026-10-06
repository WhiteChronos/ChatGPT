import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
test('repository enables broker without removing existing layers',async()=>{const market=JSON.parse(await fs.readFile(path.join(repo,'.agents/plugins/marketplace.json'),'utf8'));assert.ok(market.plugins.some(p=>p.name==='subagent-broker'&&p.source?.path==='./plugins/subagent-broker'));const toml=await fs.readFile(path.join(repo,'.codex/config.toml'),'utf8');assert.match(toml,/\[agents\][\s\S]*?enabled\s*=\s*true/);assert.doesNotMatch(toml,/multi_agent\s*=\s*true/);for(const name of ['github-arena','superpowers','superpowers-controller','matt-pocock-controller','ecc','ecc-controller','subagent-broker'])assert.ok(toml.includes(name),name+' missing');const agents=await fs.readFile(path.join(repo,'AGENTS.md'),'utf8');assert.match(agents,/native.*broker.*inline/is);assert.match(agents,/never.*prompt persona/is);});

test('broker MCP binds only to explicit consumer repository root',async()=>{
  const server=await fs.readFile(path.join(repo,'plugins','subagent-broker','mcp-server','mcp_server.mjs'),'utf8');
  const readme=await fs.readFile(path.join(repo,'plugins','subagent-broker','README.md'),'utf8');
  assert.match(server,/resolveConfiguredRepoRoot\(process\.env\)/);
  assert.doesNotMatch(server,/discoverRepoRoot\(pluginDir\)/);
  assert.match(readme,/SUBAGENT_BROKER_REPO_ROOT/);
  assert.match(readme,/absolute/i);
  assert.match(readme,/fail/i);
});
