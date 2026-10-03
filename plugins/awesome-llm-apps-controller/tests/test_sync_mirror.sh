#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
SYNC="$PLUGIN_ROOT/scripts/sync_mirror.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
UP="$TMP/upstream"
HOST="$TMP/host"
OUTSIDE="$TMP/outside.txt"
SENTINEL="$TMP/upstream-ran.txt"
mkdir -p "$UP" "$HOST/registry/awesome-llm-apps" "$HOST/.agents/skills/unrelated"
cp "$PLUGIN_ROOT/../../registry/awesome-llm-apps/catalog.schema.json" "$HOST/registry/awesome-llm-apps/catalog.schema.json"
printf 'keep\n' > "$HOST/keep.txt"
printf '%s\n' '---' 'name: unrelated' '---' > "$HOST/.agents/skills/unrelated/SKILL.md"
printf '{"skills":[]}' > "$HOST/.agents/skills/.matt-pocock-managed.json"
printf 'outside\n' > "$OUTSIDE"

git -C "$UP" init -q -b main
git -C "$UP" config user.name test
git -C "$UP" config user.email test@example.com
mkdir -p "$UP/agent_skills/commit-archaeologist" "$UP/agent_skills/dependency-doctor" "$UP/agent_skills/first-reader"
mkdir -p "$UP/starter_ai_agents/demo/skills/local" "$UP/src" "$UP/dist" "$UP/media" "$UP/links"
printf 'Apache License\nVersion 2.0\n' > "$UP/LICENSE"
cat > "$UP/README.md" <<'EOF'
# Fake Awesome

### Advanced AI Agents
- [External Useful](https://github.com/example/external-agent)
EOF
cat > "$UP/agent_skills/registry.json" <<'EOF'
{"version":1,"skills":[
 {"name":"commit-archaeologist","path":"agent_skills/commit-archaeologist","license":"Apache-2.0"},
 {"name":"dependency-doctor","path":"agent_skills/dependency-doctor","license":"Apache-2.0"},
 {"name":"first-reader","path":"agent_skills/first-reader","license":""}
]}
EOF
printf '%s\n' '---' 'name: commit-archaeologist' '---' > "$UP/agent_skills/commit-archaeologist/SKILL.md"
printf '%s\n' '---' 'name: first-reader' '---' > "$UP/agent_skills/first-reader/SKILL.md"
printf '# Demo\n' > "$UP/starter_ai_agents/demo/README.md"
printf '%s\n' '---' 'name: local' '---' > "$UP/starter_ai_agents/demo/skills/local/SKILL.md"
printf 'print("v1")\n' > "$UP/src/app.py"
printf 'generated\n' > "$UP/dist/generated.txt"
truncate -s $((10*1024*1024+1)) "$UP/media/demo.gif"
ln -s '../../../outside.txt' "$UP/links/escape"
cat > "$UP/danger.sh" <<EOF
#!/usr/bin/env bash
touch "$SENTINEL"
EOF
chmod +x "$UP/danger.sh"
git -C "$UP" add .
git -C "$UP" commit -qm 'v1'
SHA1="$(git -C "$UP" rev-parse HEAD)"

AWESOME_LLM_APPS_REPO_ROOT="$HOST" \
AWESOME_LLM_APPS_UPSTREAM_URL="file://$UP" \
AWESOME_LLM_APPS_UPSTREAM_REF=main \
bash "$SYNC"

test "$(cat "$HOST/keep.txt")" = keep
test ! -e "$HOST/vendor/shubhamsaboo-awesome-llm-apps/.git"
test -f "$HOST/vendor/shubhamsaboo-awesome-llm-apps/src/app.py"
test ! -e "$HOST/vendor/shubhamsaboo-awesome-llm-apps/dist/generated.txt"
test ! -e "$SENTINEL"
test -f "$HOST/registry/awesome-llm-apps/.whitechronos-excluded.json"
test -f "$HOST/registry/awesome-llm-apps/catalog.json"
test -f "$HOST/registry/awesome-llm-apps/catalog.summary.json"
test -f "$HOST/.agents/skills/commit-archaeologist/SKILL.md"
test -f "$HOST/.agents/skills/first-reader/SKILL.md"
test ! -e "$HOST/.agents/skills/dependency-doctor"
test -f "$HOST/.agents/skills/unrelated/SKILL.md"
test -f "$HOST/.agents/skills/.awesome-llm-apps-managed.json"
test -f "$HOST/plugins/awesome-llm-apps-controller/upstream.lock.json"

python3 - "$HOST" "$SHA1" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1]); sha=sys.argv[2]
cat=json.loads((root/'registry/awesome-llm-apps/catalog.json').read_text())
sum_=json.loads((root/'registry/awesome-llm-apps/catalog.summary.json').read_text())
exc=json.loads((root/'registry/awesome-llm-apps/.whitechronos-excluded.json').read_text())
lock=json.loads((root/'plugins/awesome-llm-apps-controller/upstream.lock.json').read_text())
assert cat['schema_version']==1 and cat['upstream_commit']==sha
assert sum_['total_entries']==len(cat['entries'])
assert any(e['source_type']=='external_reference' for e in cat['entries'])
assert any(x['reason']=='large_demo_media' for x in exc['excluded'])
assert any(x['reason'].startswith('excluded_directory:dist') for x in exc['excluded'])
assert any(x['reason']=='unsafe_symlink' for x in exc['excluded'])
assert lock['upstream']['commit']==sha
assert lock['upstream']['license']=='Apache-2.0'
assert lock['catalog']['schema_version']==1
assert lock['mirror']['exclusion_policy_version']==1
assert lock['counts']['excluded']==len(exc['excluded'])
PY

rm "$UP/src/app.py"
printf 'print("v2")\n' > "$UP/src/new.py"
git -C "$UP" add -A
git -C "$UP" commit -qm 'v2'
SHA2="$(git -C "$UP" rev-parse HEAD)"

AWESOME_LLM_APPS_REPO_ROOT="$HOST" \
AWESOME_LLM_APPS_UPSTREAM_URL="file://$UP" \
AWESOME_LLM_APPS_UPSTREAM_REF=main \
bash "$SYNC"

test ! -e "$HOST/vendor/shubhamsaboo-awesome-llm-apps/src/app.py"
test -f "$HOST/vendor/shubhamsaboo-awesome-llm-apps/src/new.py"
test ! -e "$SENTINEL"
python3 - "$HOST" "$SHA2" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1]); sha=sys.argv[2]
lock=json.loads((root/'plugins/awesome-llm-apps-controller/upstream.lock.json').read_text())
assert lock['upstream']['commit']==sha
cat=json.loads((root/'registry/awesome-llm-apps/catalog.json').read_text())
assert cat['upstream_commit']==sha
PY

echo 'PASS: Awesome LLM Apps sync behavior'
