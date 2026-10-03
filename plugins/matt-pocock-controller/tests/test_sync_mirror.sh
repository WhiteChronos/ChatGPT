#!/usr/bin/env bash
set -euo pipefail

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/sync_mirror.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

UP="$TMP/upstream"
ROOT="$TMP/root"
mkdir -p "$UP" "$ROOT/plugins/matt-pocock-controller" "$ROOT/.agents/skills/keep-me"

git -C "$UP" init -q
git -C "$UP" config user.name test
git -C "$UP" config user.email test@example.com
mkdir -p "$UP/skills/engineering/tdd/agents" \
         "$UP/skills/engineering/setup-matt-pocock-skills/agents" \
         "$UP/skills/productivity/grilling/agents" \
         "$UP/skills/deprecated/old"
printf '{"version":"9.9.9"}\n' > "$UP/package.json"
printf 'MIT test\n' > "$UP/LICENSE"
printf '%s\n' '---' 'name: tdd' 'description: test tdd' '---' '# TDD' > "$UP/skills/engineering/tdd/SKILL.md"
printf 'interface:\n  display_name: "TDD"\n  short_description: "TDD"\n' > "$UP/skills/engineering/tdd/agents/openai.yaml"
printf '%s\n' '---' 'name: setup-matt-pocock-skills' 'description: setup' '---' '# Setup' > "$UP/skills/engineering/setup-matt-pocock-skills/SKILL.md"
printf 'interface:\n  display_name: "Setup"\n  short_description: "Setup"\npolicy:\n  allow_implicit_invocation: false\n' > "$UP/skills/engineering/setup-matt-pocock-skills/agents/openai.yaml"
printf '%s\n' '---' 'name: grilling' 'description: grill' '---' '# Grill' > "$UP/skills/productivity/grilling/SKILL.md"
printf 'interface:\n  display_name: "Grilling"\n  short_description: "Grilling"\n' > "$UP/skills/productivity/grilling/agents/openai.yaml"
printf '%s\n' '---' 'name: old' 'description: old' '---' '# Old' > "$UP/skills/deprecated/old/SKILL.md"
git -C "$UP" add .
git -C "$UP" commit -qm initial

cat > "$ROOT/plugins/matt-pocock-controller/upstream.lock.json" <<'JSON'
{
  "upstream": {
    "repository": "mattpocock/skills",
    "ref": "main",
    "observed_sha": "old",
    "observed_version": "0.0.0",
    "license": "MIT"
  }
}
JSON
printf 'keep\n' > "$ROOT/.agents/skills/keep-me/SKILL.md"

MATT_POCOCK_UPSTREAM_URL="$UP" "$SCRIPT" "$ROOT"

[[ -f "$ROOT/vendor/mattpocock-skills/skills/deprecated/old/SKILL.md" ]]
[[ -f "$ROOT/.agents/skills/tdd/SKILL.md" ]]
[[ -f "$ROOT/.agents/skills/setup-matt-pocock-skills/SKILL.md" ]]
[[ -f "$ROOT/.agents/skills/grilling/SKILL.md" ]]
[[ ! -e "$ROOT/.agents/skills/old" ]]
[[ -f "$ROOT/.agents/skills/keep-me/SKILL.md" ]]

python - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1])
managed=json.loads((root/'.agents/skills/.matt-pocock-managed.json').read_text())
assert managed['version']=='9.9.9'
assert managed['skills']==['grilling','setup-matt-pocock-skills','tdd']
lock=json.loads((root/'plugins/matt-pocock-controller/upstream.lock.json').read_text())
assert lock['upstream']['observed_version']=='9.9.9'
assert len(lock['upstream']['observed_sha'])==40
mirror=json.loads((root/'vendor/mattpocock-skills/.whitechronos-mirror.json').read_text())
assert mirror['stable_skill_count']==3
PY

rm -rf "$UP/skills/engineering/tdd"
mkdir -p "$UP/skills/engineering/new-skill/agents"
printf '%s\n' '---' 'name: new-skill' 'description: new' '---' '# New' > "$UP/skills/engineering/new-skill/SKILL.md"
printf 'interface:\n  display_name: "New"\n  short_description: "New"\n' > "$UP/skills/engineering/new-skill/agents/openai.yaml"
git -C "$UP" add -A
git -C "$UP" commit -qm update
MATT_POCOCK_UPSTREAM_URL="$UP" "$SCRIPT" "$ROOT"
[[ ! -e "$ROOT/.agents/skills/tdd" ]]
[[ -f "$ROOT/.agents/skills/new-skill/SKILL.md" ]]
[[ -f "$ROOT/.agents/skills/keep-me/SKILL.md" ]]

COLLIDE="$TMP/collide"
mkdir -p "$COLLIDE/plugins/matt-pocock-controller" "$COLLIDE/.agents/skills/new-skill"
printf 'mine\n' > "$COLLIDE/.agents/skills/new-skill/SKILL.md"
cp "$ROOT/plugins/matt-pocock-controller/upstream.lock.json" "$COLLIDE/plugins/matt-pocock-controller/upstream.lock.json"
if MATT_POCOCK_UPSTREAM_URL="$UP" "$SCRIPT" "$COLLIDE" >/dev/null 2>&1; then
  echo "expected collision failure" >&2
  exit 1
fi

echo "PASS: sync mirror behavior"
