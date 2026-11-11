#!/usr/bin/env node
import readline from 'node:readline';

const SERVER_NAME = 'github-arena';
const SERVER_VERSION = '1.1.0';
const RUBRIC = { correctness: 30, completeness: 25, robustness: 20, specificity: 15, clarity: 10 };
const REASONING = ['first-principles','inversion','analogy','adversarial','constraint-first','worked-example','socratic','contrarian','systems-thinking','decomposition','working-backwards','probabilistic','dialectical','evidence-first','expert-panel'];
const WORKFLOWS = ['draft-critique-rewrite','outline-first','test-first','research-then-synthesise','three-drafts','requirements-checklist','iterative-deepening','build-then-break','smallest-version-first','options-matrix','open-questions-first','write-then-restructure'];
const STRATEGIES = ['simplest','maximal-rigour','user-empathy','edge-cases-first','speed','defensive','clarity','completeness','fewest-moving-parts','explicit-trade-offs','built-to-last','concrete-specifics'];

function hashSeed(value) {
  const s = String(value);
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function rngFrom(seed) {
  let a = hashSeed(seed) || 1;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function clampN(n) { return Math.max(1, Math.min(Number.isFinite(Number(n)) ? Math.trunc(Number(n)) : 1, 2160)); }
function plan(n) {
  n = clampN(n);
  const sizes = [n];
  while (sizes.at(-1) > 1) sizes.push(Math.ceil(sizes.at(-1) / 2));
  const matches = sizes.slice(0, -1).reduce((a, x) => a + Math.floor(x / 2), 0);
  return { strategies: n, rounds: sizes.length - 1, alive_per_round: sizes, upstream_equivalent_calls: n + 5 * matches, mode: n > 16 ? 'full' : n > 4 ? 'review' : 'micro' };
}
function cards(n, seed) {
  n = clampN(n);
  const all = [];
  for (const r of REASONING) for (const w of WORKFLOWS) for (const s of STRATEGIES) all.push([r, w, s]);
  const rnd = rngFrom(seed);
  for (let i = all.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [all[i], all[j]] = [all[j], all[i]]; }
  return { seed: String(seed), cards: all.slice(0, n).map((c, i) => ({ id: `a${String(i + 1).padStart(3, '0')}`, reasoning: c[0], workflow: c[1], strategy: c[2] })) };
}
function checklist(highImpact = false, github = false) {
  const checks = ['evidence-first', 'constraint-first', 'edge-cases-first', 'built-to-last'];
  if (github) checks.push('read AGENTS.md and repository instructions', 'verify repository, branch and target path from current state', 'verify result after mutation', 'preserve provenance and licensing');
  return { mode: highImpact ? 'review' : 'micro', checks, rubric: RUBRIC };
}
const tools = [
  { name: 'arena_plan', description: 'Plan an Arena review or tournament size and return rounds and workload estimates. Read-only; does not run agents.', inputSchema: { type: 'object', properties: { agents: { type: 'integer', minimum: 1, maximum: 2160, default: 16 } }, additionalProperties: false }, annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false } },
  { name: 'arena_cards', description: 'Generate deterministic Arena strategy cards combining reasoning mode, workflow, and strategy. Read-only.', inputSchema: { type: 'object', properties: { agents: { type: 'integer', minimum: 1, maximum: 2160, default: 4 }, seed: { default: 7 } }, additionalProperties: false }, annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false } },
  { name: 'arena_rubric', description: 'Return the GitHub Arena scoring rubric used to compare candidate solutions. Read-only.', inputSchema: { type: 'object', properties: {}, additionalProperties: false }, annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false } },
  { name: 'arena_review_checklist', description: 'Return the required Arena review checklist. Set github=true for GitHub work and high_impact=true for complex or risky work. Read-only.', inputSchema: { type: 'object', properties: { high_impact: { type: 'boolean', default: false }, github: { type: 'boolean', default: false } }, additionalProperties: false }, annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false } }
];
function toolResult(data) { return { content: [{ type: 'text', text: JSON.stringify(data, null, 2) }], structuredContent: data, isError: false }; }
function handle(req) {
  const { method, id } = req;
  if (method === 'initialize') {
    const requested = req.params?.protocolVersion ?? '2025-11-25';
    const supported = new Set(['2025-11-25', '2025-06-18', '2024-11-05']);
    return { jsonrpc: '2.0', id, result: { protocolVersion: supported.has(requested) ? requested : '2025-11-25', capabilities: { tools: { listChanged: false } }, serverInfo: { name: SERVER_NAME, version: SERVER_VERSION }, instructions: 'Use Arena tools for structured quality review. Use the GitHub connector separately for repository reads and writes.' } };
  }
  if (method === 'notifications/initialized' || method === 'notifications/cancelled') return null;
  if (method === 'ping') return { jsonrpc: '2.0', id, result: {} };
  if (method === 'tools/list') return { jsonrpc: '2.0', id, result: { tools } };
  if (method === 'tools/call') {
    const name = req.params?.name;
    const args = req.params?.arguments ?? {};
    try {
      let data;
      if (name === 'arena_plan') data = plan(args.agents ?? 16);
      else if (name === 'arena_cards') data = cards(args.agents ?? 4, args.seed ?? 7);
      else if (name === 'arena_rubric') data = { rubric: RUBRIC, formula: '(correctness*30 + completeness*25 + robustness*20 + specificity*15 + clarity*10) / 10' };
      else if (name === 'arena_review_checklist') data = checklist(Boolean(args.high_impact), Boolean(args.github));
      else throw new Error(`unknown tool: ${name}`);
      return { jsonrpc: '2.0', id, result: toolResult(data) };
    } catch (e) {
      return { jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: String(e?.message ?? e) }], isError: true } };
    }
  }
  return id === undefined ? null : { jsonrpc: '2.0', id, error: { code: -32601, message: 'Method not found' } };
}
const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on('line', line => {
  if (!line.trim()) return;
  try {
    const response = handle(JSON.parse(line));
    if (response) process.stdout.write(JSON.stringify(response) + '\n');
  } catch (e) {
    process.stdout.write(JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32700, message: String(e?.message ?? e) } }) + '\n');
  }
});
