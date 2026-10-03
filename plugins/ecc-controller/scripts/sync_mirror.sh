#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="${1:-$(git rev-parse --show-toplevel)}"
UPSTREAM_URL="${ECC_UPSTREAM_URL:-https://github.com/affaan-m/ECC.git}"
MIRROR_REL="${ECC_MIRROR_REL:-vendor/affaan-m-ecc}"
MIRROR_DIR="$REPO_ROOT/$MIRROR_REL"
LOCK_FILE="$REPO_ROOT/plugins/ecc-controller/upstream.lock.json"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

git clone --depth 1 "$UPSTREAM_URL" "$TMP_DIR/upstream" >/dev/null 2>&1
UPSTREAM_SHA="$(git -C "$TMP_DIR/upstream" rev-parse HEAD)"
UPSTREAM_VERSION="$(node -e 'const fs=require("fs");const p=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));process.stdout.write(String(p.version||"unknown"));' "$TMP_DIR/upstream/package.json")"
SKILL_COUNT="$(find "$TMP_DIR/upstream/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')"
AGENT_COUNT="$(find "$TMP_DIR/upstream/agents" -mindepth 1 -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
COMMAND_COUNT="$(find "$TMP_DIR/upstream/commands" -mindepth 1 -maxdepth 1 -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"

rm -rf "$MIRROR_DIR"
mkdir -p "$MIRROR_DIR"
cp -a "$TMP_DIR/upstream/." "$MIRROR_DIR/"
rm -rf "$MIRROR_DIR/.git"

python - "$MIRROR_DIR/.whitechronos-mirror.json" "$UPSTREAM_SHA" "$UPSTREAM_VERSION" "$SKILL_COUNT" "$AGENT_COUNT" "$COMMAND_COUNT" <<'PY'
import json, sys
from pathlib import Path
path=Path(sys.argv[1])
data={
  "source":"https://github.com/affaan-m/ECC",
  "ref":"main",
  "commit":sys.argv[2],
  "version":sys.argv[3],
  "skill_count":int(sys.argv[4]),
  "agent_count":int(sys.argv[5]),
  "command_count":int(sys.argv[6]),
  "policy":"read-only byte mirror; runtime uses the upstream-native ECC Codex plugin",
}
path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
PY

if [[ -f "$LOCK_FILE" ]]; then
  python - "$LOCK_FILE" "$UPSTREAM_SHA" "$UPSTREAM_VERSION" "$SKILL_COUNT" "$AGENT_COUNT" "$COMMAND_COUNT" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
data=json.loads(p.read_text(encoding='utf-8'))
up=data.setdefault('upstream', {})
up['observed_sha']=sys.argv[2]
up['observed_version']=sys.argv[3]
up['skill_count']=int(sys.argv[4])
up['agent_count']=int(sys.argv[5])
up['command_count']=int(sys.argv[6])
p.write_text(json.dumps(data, indent=2)+"\n", encoding='utf-8')
PY
fi

printf 'ECC_UPSTREAM_SHA=%s\n' "$UPSTREAM_SHA"
printf 'ECC_UPSTREAM_VERSION=%s\n' "$UPSTREAM_VERSION"
printf 'ECC_SKILL_COUNT=%s\n' "$SKILL_COUNT"
printf 'ECC_AGENT_COUNT=%s\n' "$AGENT_COUNT"
printf 'ECC_COMMAND_COUNT=%s\n' "$COMMAND_COUNT"
