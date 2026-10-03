#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
UP="$TMP/upstream"
PROJ="$TMP/project"
mkdir -p "$UP/agent_skills/skill-a" "$UP/rag_tutorials/demo" "$PROJ/.agents/skills" "$PROJ/registry/awesome-llm-apps" "$PROJ/vendor"
for root in starter_ai_agents advanced_ai_agents always_on_agents voice_ai_agents mcp_ai_agents generative_ui_agents rag_tutorials advanced_llm_apps ai_agent_framework_crash_course agent_skills; do
  mkdir -p "$UP/$root"
  echo tracked > "$UP/$root/.whitechronos-fixture"
done
cat > "$UP/LICENSE" <<'EOF'
Apache License
Version 2.0
EOF
cat > "$UP/README.md" <<'EOF'
# Awesome LLM Apps
### Advanced AI Agents
* [External](https://github.com/example/external-agent) - external
EOF
cat > "$UP/agent_skills/registry.json" <<'EOF'
{"version":1,"skills":[{"name":"skill-a","path":"agent_skills/skill-a","license":"Apache-2.0"}]}
EOF
cat > "$UP/agent_skills/skill-a/SKILL.md" <<'EOF'
---
name: skill-a
description: test
---
EOF
cat > "$UP/rag_tutorials/demo/README.md" <<'EOF'
# Demo RAG
EOF
cat > "$UP/rag_tutorials/demo/requirements.txt" <<'EOF'
openai
EOF
cat > "$UP/evil.sh" <<EOF
#!/usr/bin/env bash
touch "$TMP/SENTINEL_EXECUTED"
EOF
chmod +x "$UP/evil.sh"
printf 'GIF89a' > "$UP/large.gif"
truncate -s $((10*1024*1024+1)) "$UP/large.gif"
git -C "$UP" init -q
git -C "$UP" config user.email test@example.com
git -C "$UP" config user.name test
git -C "$UP" add .
git -C "$UP" commit -qm init
git -C "$UP" branch -M main

echo KEEP > "$PROJ/unrelated.txt"
mkdir -p "$PROJ/plugins/awesome-llm-apps-controller/scripts"
cp "$ROOT/plugins/awesome-llm-apps-controller/scripts/"*.py "$PROJ/plugins/awesome-llm-apps-controller/scripts/" 2>/dev/null || true
cp "$ROOT/plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh" "$PROJ/plugins/awesome-llm-apps-controller/scripts/" 2>/dev/null || true
mkdir -p "$PROJ/registry/awesome-llm-apps"
cp "$ROOT/registry/awesome-llm-apps/catalog.schema.json" "$PROJ/registry/awesome-llm-apps/" 2>/dev/null || true

AWESOME_LLM_APPS_REPO_ROOT="$PROJ" AWESOME_LLM_APPS_UPSTREAM_URL="$UP" AWESOME_LLM_APPS_UPSTREAM_REF=main \
  bash "$ROOT/plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh"

test "$(cat "$PROJ/unrelated.txt")" = KEEP
test ! -e "$TMP/SENTINEL_EXECUTED"
test -f "$PROJ/vendor/shubhamsaboo-awesome-llm-apps/.whitechronos-mirror.json"
test -f "$PROJ/vendor/shubhamsaboo-awesome-llm-apps/.whitechronos-excluded.json"
test -f "$PROJ/registry/awesome-llm-apps/catalog.json"
test -f "$PROJ/registry/awesome-llm-apps/catalog.summary.json"
test -f "$PROJ/.agents/skills/skill-a/SKILL.md"
test -f "$PROJ/.agents/skills/.awesome-llm-apps-managed.json"
test -f "$PROJ/plugins/awesome-llm-apps-controller/upstream.lock.json"
test ! -e "$PROJ/vendor/shubhamsaboo-awesome-llm-apps/.git"
python - <<PY
import json
from pathlib import Path
p=Path('$PROJ')
lock=json.loads((p/'plugins/awesome-llm-apps-controller/upstream.lock.json').read_text())
assert lock['license']=='Apache-2.0'
assert lock['ref']=='main'
assert lock['upstream_url']=='$UP'
assert lock['canonical_skill_count']==1
assert lock['snapshot_statistics']['blobs']==18
assert lock['snapshot_statistics']['skill_md']==1
assert lock['snapshot_statistics']['canonical_skills']==1
assert lock['snapshot_statistics']['readmes']==2
assert lock['snapshot_statistics']['dependency_manifests']==1
assert lock['snapshot_statistics']['dockerfiles']==0
assert lock['snapshot_statistics']['compose_files']==0
assert lock['snapshot_statistics']['code_files']==1
meta=json.loads((p/'vendor/shubhamsaboo-awesome-llm-apps/.whitechronos-mirror.json').read_text())
assert meta['upstream_repository']=='Shubhamsaboo/awesome-llm-apps'
assert meta['upstream_url']=='$UP'
assert meta['ref']=='main'
exc=json.loads((p/'vendor/shubhamsaboo-awesome-llm-apps/.whitechronos-excluded.json').read_text())
assert exc['upstream_repository']=='Shubhamsaboo/awesome-llm-apps'
assert exc['upstream_url']=='$UP'
assert exc['ref']=='main'
assert any(x['path']=='large.gif' and x['reason']=='large_demo_media' for x in exc['excluded'])
cat=json.loads((p/'registry/awesome-llm-apps/catalog.json').read_text())
assert any(e['source_type']=='external_reference' for e in cat['entries'])
PY

# Update upstream; stale source must disappear.
rm "$UP/rag_tutorials/demo/requirements.txt"
echo '# changed' >> "$UP/rag_tutorials/demo/README.md"
git -C "$UP" add -A
git -C "$UP" commit -qm update
AWESOME_LLM_APPS_REPO_ROOT="$PROJ" AWESOME_LLM_APPS_UPSTREAM_URL="$UP" AWESOME_LLM_APPS_UPSTREAM_REF=main \
  bash "$ROOT/plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh"
test ! -e "$PROJ/vendor/shubhamsaboo-awesome-llm-apps/rag_tutorials/demo/requirements.txt"
echo 'SYNC PASS'

# Mandatory upstream root removal must fail closed for human review.
rm -rf "$UP/voice_ai_agents"
git -C "$UP" add -A
git -C "$UP" commit -qm remove-mandatory-root
if AWESOME_LLM_APPS_REPO_ROOT="$PROJ" AWESOME_LLM_APPS_UPSTREAM_URL="$UP" AWESOME_LLM_APPS_UPSTREAM_REF=main \
  bash "$ROOT/plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh"; then
  echo "EXPECTED mandatory-root drift rejection" >&2
  exit 1
fi
