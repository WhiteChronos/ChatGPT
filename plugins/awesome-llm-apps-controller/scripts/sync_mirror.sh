#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="${AWESOME_LLM_APPS_REPO_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd -P)}"
URL="${AWESOME_LLM_APPS_UPSTREAM_URL:-https://github.com/Shubhamsaboo/awesome-llm-apps.git}"
REF="${AWESOME_LLM_APPS_UPSTREAM_REF:-main}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
UPSTREAM="$TMP/upstream"
STAGE="$TMP/stage"
mkdir -p "$STAGE"

if ! git clone -q --depth 1 --branch "$REF" "$URL" "$UPSTREAM" 2>/dev/null; then
  rm -rf "$UPSTREAM"
  git clone -q --depth 1 "$URL" "$UPSTREAM"
  git -C "$UPSTREAM" fetch -q --depth 1 origin "$REF"
  git -C "$UPSTREAM" checkout -q --detach FETCH_HEAD
fi

LICENSE_FILE="$UPSTREAM/LICENSE"
if [[ ! -f "$LICENSE_FILE" ]] || ! grep -q 'Apache License' "$LICENSE_FILE" || ! grep -q 'Version 2.0' "$LICENSE_FILE"; then
  echo 'upstream root LICENSE is not verified Apache-2.0' >&2
  exit 2
fi
UPSTREAM_SHA="$(git -C "$UPSTREAM" rev-parse HEAD)"
export AWESOME_LLM_APPS_UPSTREAM_COMMIT="$UPSTREAM_SHA"

MIRROR_STAGE="$STAGE/vendor/shubhamsaboo-awesome-llm-apps"
REGISTRY_STAGE="$STAGE/registry/awesome-llm-apps"
SKILLS_STAGE="$STAGE/skills"
LOCK_STAGE="$STAGE/upstream.lock.json"
mkdir -p "$MIRROR_STAGE" "$REGISTRY_STAGE" "$SKILLS_STAGE"

SCHEMA_SOURCE="$REPO_ROOT/registry/awesome-llm-apps/catalog.schema.json"
if [[ ! -f "$SCHEMA_SOURCE" ]]; then
  echo "missing catalog schema: $SCHEMA_SOURCE" >&2
  exit 3
fi
cp "$SCHEMA_SOURCE" "$REGISTRY_STAGE/catalog.schema.json"

if [[ -d "$REPO_ROOT/.agents/skills" ]]; then
  cp -a "$REPO_ROOT/.agents/skills/." "$SKILLS_STAGE/"
fi

PYTHONPATH="$SCRIPT_DIR" "$PYTHON_BIN" - "$UPSTREAM" "$MIRROR_STAGE" "$REGISTRY_STAGE/.whitechronos-excluded.json" <<'PY'
import json, os, pathlib, sys
from awesome_llm_apps_mirror import copy_mirror, plan_mirror
root=pathlib.Path(sys.argv[1]); dest=pathlib.Path(sys.argv[2]); out=pathlib.Path(sys.argv[3])
plan=plan_mirror(root)
report=copy_mirror(root,dest,plan)
payload={
  'schema_version':1,
  'upstream_commit':os.environ['AWESOME_LLM_APPS_UPSTREAM_COMMIT'],
  'exclusion_policy_version':1,
  'excluded':report['excluded'],
}
out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
PY

"$PYTHON_BIN" "$SCRIPT_DIR/build_catalog.py" \
  --root "$UPSTREAM" \
  --commit "$UPSTREAM_SHA" \
  --catalog "$REGISTRY_STAGE/catalog.json" \
  --summary "$REGISTRY_STAGE/catalog.summary.json" \
  --schema "$REGISTRY_STAGE/catalog.schema.json"

PYTHONPATH="$SCRIPT_DIR" "$PYTHON_BIN" - "$UPSTREAM" "$SKILLS_STAGE" "$REPO_ROOT" <<'PY'
import json, pathlib, sys
from awesome_llm_apps_skills import project_skills
root=pathlib.Path(sys.argv[1]); dest=pathlib.Path(sys.argv[2]); repo=pathlib.Path(sys.argv[3])
def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError: return None
previous=load(repo/'.agents/skills/.awesome-llm-apps-managed.json')
matt=load(repo/'.agents/skills/.matt-pocock-managed.json')
project_skills(root,dest,previous,matt)
PY

"$PYTHON_BIN" - "$REGISTRY_STAGE" "$SKILLS_STAGE" "$LOCK_STAGE" "$URL" "$REF" "$UPSTREAM_SHA" "$MIRROR_STAGE" <<'PY'
import json, pathlib, sys
registry=pathlib.Path(sys.argv[1]); skills=pathlib.Path(sys.argv[2]); out=pathlib.Path(sys.argv[3])
url,ref,sha=sys.argv[4:7]; mirror=pathlib.Path(sys.argv[7])
cat=json.loads((registry/'catalog.json').read_text(encoding='utf-8'))
summary=json.loads((registry/'catalog.summary.json').read_text(encoding='utf-8'))
excluded=json.loads((registry/'.whitechronos-excluded.json').read_text(encoding='utf-8'))
manifest=json.loads((skills/'.awesome-llm-apps-managed.json').read_text(encoding='utf-8'))
mirrored=sum(1 for p in mirror.rglob('*') if p.is_file() or p.is_symlink())
lock={
  'upstream':{'repository':'Shubhamsaboo/awesome-llm-apps','url':url,'ref':ref,'commit':sha,'license':'Apache-2.0'},
  'catalog':{'schema_version':cat['schema_version']},
  'mirror':{'path':'vendor/shubhamsaboo-awesome-llm-apps','exclusion_policy_version':excluded['exclusion_policy_version']},
  'counts':{
    'catalog_entries':len(cat['entries']),
    'excluded':len(excluded['excluded']),
    'mirrored_files':mirrored,
    'projected_skills':len(manifest['skills']),
    'skill_inconsistencies':len(manifest['inconsistencies']),
  },
  'summary':summary,
}
out.write_text(json.dumps(lock,indent=2,sort_keys=True)+'\n',encoding='utf-8')
PY

replace_dir() {
  local staged="$1" target="$2" parent tmp_target
  parent="$(dirname "$target")"
  mkdir -p "$parent"
  tmp_target="$parent/.replace-$(basename "$target")-$$"
  rm -rf "$tmp_target"
  mv "$staged" "$tmp_target"
  rm -rf "$target"
  mv "$tmp_target" "$target"
}

replace_dir "$MIRROR_STAGE" "$REPO_ROOT/vendor/shubhamsaboo-awesome-llm-apps"
replace_dir "$REGISTRY_STAGE" "$REPO_ROOT/registry/awesome-llm-apps"
replace_dir "$SKILLS_STAGE" "$REPO_ROOT/.agents/skills"
mkdir -p "$REPO_ROOT/plugins/awesome-llm-apps-controller"
mv "$LOCK_STAGE" "$REPO_ROOT/plugins/awesome-llm-apps-controller/upstream.lock.json"

echo "UPSTREAM_SHA=$UPSTREAM_SHA"
echo "UPSTREAM_REF=$REF"
echo "UPSTREAM_URL=$URL"
