#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${AWESOME_LLM_APPS_REPO_ROOT:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"
UPSTREAM_URL="${AWESOME_LLM_APPS_UPSTREAM_URL:-https://github.com/Shubhamsaboo/awesome-llm-apps.git}"
UPSTREAM_REF="${AWESOME_LLM_APPS_UPSTREAM_REF:-main}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
UP="$TMP/upstream"
STAGE="$TMP/stage"
mkdir -p "$STAGE/vendor" "$STAGE/registry" "$STAGE/skills"

if ! git clone --quiet --depth 1 --branch "$UPSTREAM_REF" "$UPSTREAM_URL" "$UP" 2>/dev/null; then
  git clone --quiet "$UPSTREAM_URL" "$UP"
  git -C "$UP" checkout --quiet "$UPSTREAM_REF"
fi
SHA="$(git -C "$UP" rev-parse HEAD)"
LICENSE="$UP/LICENSE"
if [[ ! -f "$LICENSE" ]] || ! grep -q 'Apache License' "$LICENSE" || ! grep -q 'Version 2.0' "$LICENSE"; then
  echo "unrecognized or missing Apache-2.0 LICENSE" >&2; exit 2
fi

PYTHONPATH="$SCRIPT_DIR" python - "$UP" "$STAGE" "$REPO_ROOT" "$SHA" "$UPSTREAM_REF" "$UPSTREAM_URL" "$SCRIPT_DIR" <<'PY'
from pathlib import Path
import json, shutil, sys
from awesome_llm_apps_mirror import plan_mirror, copy_mirror
from awesome_llm_apps_catalog import build_catalog, build_summary, snapshot_statistics, missing_mandatory_roots
from awesome_llm_apps_skills import load_canonical_skills, project_skills
from build_catalog import validate_supported
up=Path(sys.argv[1]); stage=Path(sys.argv[2]); repo=Path(sys.argv[3]); sha=sys.argv[4]; ref=sys.argv[5]; upstream_url=sys.argv[6]; scripts=Path(sys.argv[7])

schema_path=repo/'registry/awesome-llm-apps/catalog.schema.json'
if not schema_path.exists():
    schema_path=scripts.parents[2]/'registry/awesome-llm-apps/catalog.schema.json'
schema=json.loads(schema_path.read_text())
reg=stage/'registry/awesome-llm-apps'
reg.mkdir(parents=True,exist_ok=True)
# catalog.schema.json is repository-owned source, not generated upstream output.
# Preserve it in the staged registry so atomic replacement cannot delete it.
shutil.copy2(schema_path, reg/'catalog.schema.json')

missing=missing_mandatory_roots(up)
if missing:
    raise RuntimeError('mandatory upstream roots missing: '+', '.join(missing))

mirror=stage/'vendor/shubhamsaboo-awesome-llm-apps'
result=copy_mirror(up,mirror,plan_mirror(up),sha)
provenance={'upstream_repository':'Shubhamsaboo/awesome-llm-apps','upstream_url':upstream_url,'ref':ref,'upstream_commit':sha}
(mirror/'.whitechronos-excluded.json').write_text(json.dumps({**provenance,'excluded':result['excluded']},indent=2,sort_keys=True)+'\n')
(mirror/'.whitechronos-mirror.json').write_text(json.dumps({**provenance,**{k:v for k,v in result.items() if k!='excluded'}},indent=2,sort_keys=True)+'\n')

catalog=build_catalog(up,sha); validate_supported(catalog,schema)
(reg/'catalog.json').write_text(json.dumps(catalog,indent=2,sort_keys=True)+'\n')
(reg/'catalog.summary.json').write_text(json.dumps(build_summary(catalog),indent=2,sort_keys=True)+'\n')

live_skills=repo/'.agents/skills'; live_skills.mkdir(parents=True,exist_ok=True)
prev_path=live_skills/'.awesome-llm-apps-managed.json'
prev=json.loads(prev_path.read_text()) if prev_path.exists() else None
matt_path=live_skills/'.matt-pocock-managed.json'
matt=json.loads(matt_path.read_text()) if matt_path.exists() else None
loaded=load_canonical_skills(up)
prev_names={x['name'] if isinstance(x,dict) else x for x in (prev or {}).get('managed_skills',[])}
matt_names={x['name'] if isinstance(x,dict) else x for x in (matt or {}).get('skills',(matt or {}).get('managed_skills',[]))}
for item in loaded['skills']:
    name=item['name']
    if name in matt_names: raise RuntimeError(f'collision with Matt-managed skill: {name}')
    if (live_skills/name).exists() and name not in prev_names: raise RuntimeError(f'collision with unmanaged skill: {name}')
manifest=project_skills(up,stage/'skills',None,None)
(stage/'skills-manifest.json').write_text(json.dumps({**manifest,'upstream_commit':sha},indent=2,sort_keys=True)+'\n')

lock={
  'upstream_repository':'Shubhamsaboo/awesome-llm-apps','upstream_url':upstream_url,
  'ref':ref, 'commit':sha,'license':'Apache-2.0','schema_version':1,
  'canonical_skill_count':len(loaded['skills']),'canonical_skills':[x['name'] for x in loaded['skills']],
  'catalog_entry_count':len(catalog['entries']),'catalog_by_source_type':build_summary(catalog)['by_source_type'],
  'snapshot_statistics':snapshot_statistics(up),
  'included_files':result['included_files'],'included_bytes':result['included_bytes'],
  'excluded_files':result['excluded_files'],'excluded_bytes':result['excluded_bytes'],
  'inconsistencies':loaded['inconsistencies'],'exclusion_policy_version':1,
}
(stage/'upstream.lock.json').write_text(json.dumps(lock,indent=2,sort_keys=True)+'\n')
PY

# Commit staged outputs to the project only after every generation step succeeds.
rm -rf "$REPO_ROOT/vendor/shubhamsaboo-awesome-llm-apps" "$REPO_ROOT/registry/awesome-llm-apps"
mkdir -p "$REPO_ROOT/vendor" "$REPO_ROOT/registry" "$REPO_ROOT/.agents/skills" "$REPO_ROOT/plugins/awesome-llm-apps-controller"
mv "$STAGE/vendor/shubhamsaboo-awesome-llm-apps" "$REPO_ROOT/vendor/"
mv "$STAGE/registry/awesome-llm-apps" "$REPO_ROOT/registry/"

python - "$REPO_ROOT" "$STAGE" <<'PY'
from pathlib import Path
import json, shutil, sys
repo=Path(sys.argv[1]); stage=Path(sys.argv[2]); live=repo/'.agents/skills'
manifest=json.loads((stage/'skills-manifest.json').read_text())
old_path=live/'.awesome-llm-apps-managed.json'
old=json.loads(old_path.read_text()) if old_path.exists() else {'managed_skills':[]}
old_names={x['name'] if isinstance(x,dict) else x for x in old.get('managed_skills',[])}
new_names={x['name'] for x in manifest.get('managed_skills',[])}
for name in sorted(old_names-new_names):
    p=live/name
    if p.exists(): shutil.rmtree(p)
for item in manifest.get('managed_skills',[]):
    name=item['name']; src=stage/'skills'/name; dst=live/name
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src,dst,symlinks=True)
old_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
PY
mv "$STAGE/upstream.lock.json" "$REPO_ROOT/plugins/awesome-llm-apps-controller/upstream.lock.json"
printf 'UPSTREAM_SHA=%s\n' "$SHA"
