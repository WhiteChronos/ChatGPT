#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/scripts/sync_mirror.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
UP="$TMP/upstream"
ROOT="$TMP/root"
mkdir -p "$UP" "$ROOT/plugins/ecc-controller" "$ROOT/unrelated"
git -C "$UP" init -q
git -C "$UP" config user.name test
git -C "$UP" config user.email test@example.com
mkdir -p "$UP/skills/one" "$UP/skills/two" "$UP/agents" "$UP/commands" "$UP/.codex-plugin" "$UP/hooks"
printf '{"version":"9.9.9"}\n' > "$UP/package.json"
printf 'MIT test\n' > "$UP/LICENSE"
printf '%s\n' '---' 'name: one' 'description: one' '---' '# One' > "$UP/skills/one/SKILL.md"
printf '%s\n' '---' 'name: two' 'description: two' '---' '# Two' > "$UP/skills/two/SKILL.md"
printf '# agent\n' > "$UP/agents/reviewer.md"
printf '# command\n' > "$UP/commands/review.md"
printf '{"name":"ecc","version":"9.9.9"}\n' > "$UP/.codex-plugin/plugin.json"
printf '{}\n' > "$UP/hooks/codex-hooks.json"
printf 'keep\n' > "$ROOT/unrelated/file.txt"
ln -s LICENSE "$UP/LICENSE-LINK"
git -C "$UP" add .
git -C "$UP" commit -qm initial
cat > "$ROOT/plugins/ecc-controller/upstream.lock.json" <<'JSON'
{"upstream":{"repository":"affaan-m/ECC","ref":"main","observed_sha":"old","observed_version":"0.0.0","license":"MIT"}}
JSON
ECC_UPSTREAM_URL="$UP" "$SCRIPT" "$ROOT"
[[ -f "$ROOT/vendor/affaan-m-ecc/skills/one/SKILL.md" ]]
[[ -f "$ROOT/vendor/affaan-m-ecc/skills/two/SKILL.md" ]]
[[ -f "$ROOT/vendor/affaan-m-ecc/agents/reviewer.md" ]]
[[ -f "$ROOT/vendor/affaan-m-ecc/commands/review.md" ]]
[[ -f "$ROOT/vendor/affaan-m-ecc/.codex-plugin/plugin.json" ]]
[[ -f "$ROOT/vendor/affaan-m-ecc/hooks/codex-hooks.json" ]]
[[ ! -e "$ROOT/vendor/affaan-m-ecc/.git" ]]
[[ -L "$ROOT/vendor/affaan-m-ecc/LICENSE-LINK" ]]
[[ "$(cat "$ROOT/unrelated/file.txt")" == "keep" ]]
python - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root=Path(sys.argv[1])
mirror=json.loads((root/'vendor/affaan-m-ecc/.whitechronos-mirror.json').read_text())
assert mirror['version']=='9.9.9'
assert mirror['skill_count']==2
assert mirror['agent_count']==1
assert mirror['command_count']==1
assert len(mirror['commit'])==40
lock=json.loads((root/'plugins/ecc-controller/upstream.lock.json').read_text())
assert lock['upstream']['observed_version']=='9.9.9'
assert lock['upstream']['skill_count']==2
assert lock['upstream']['agent_count']==1
assert lock['upstream']['command_count']==1
assert len(lock['upstream']['observed_sha'])==40
PY
rm -rf "$UP/skills/two"
mkdir -p "$UP/skills/three"
printf '%s\n' '---' 'name: three' 'description: three' '---' '# Three' > "$UP/skills/three/SKILL.md"
git -C "$UP" add -A
git -C "$UP" commit -qm update
ECC_UPSTREAM_URL="$UP" "$SCRIPT" "$ROOT"
[[ ! -e "$ROOT/vendor/affaan-m-ecc/skills/two" ]]
[[ -f "$ROOT/vendor/affaan-m-ecc/skills/three/SKILL.md" ]]
echo 'PASS: ECC mirror sync behavior'
