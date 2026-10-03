#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(git rev-parse --show-toplevel)}"
UPSTREAM_URL="${MATT_POCOCK_UPSTREAM_URL:-https://github.com/mattpocock/skills.git}"
MIRROR_REL="${MATT_POCOCK_MIRROR_REL:-vendor/mattpocock-skills}"
MIRROR_DIR="$REPO_ROOT/$MIRROR_REL"
SKILLS_DIR="$REPO_ROOT/.agents/skills"
MANAGED_FILE="$SKILLS_DIR/.matt-pocock-managed.json"
LOCK_FILE="$REPO_ROOT/plugins/matt-pocock-controller/upstream.lock.json"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

git clone --depth 1 "$UPSTREAM_URL" "$TMP_DIR/upstream" >/dev/null 2>&1
UPSTREAM_SHA="$(git -C "$TMP_DIR/upstream" rev-parse HEAD)"
UPSTREAM_VERSION="$(node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); process.stdout.write(String(p.version||"unknown"));' "$TMP_DIR/upstream/package.json")"

mapfile -t CURRENT_SKILLS < <(
  find "$TMP_DIR/upstream/skills/engineering" "$TMP_DIR/upstream/skills/productivity" \
    -mindepth 1 -maxdepth 1 -type d -print0 \
    | while IFS= read -r -d '' d; do
        if [[ -f "$d/SKILL.md" ]]; then basename "$d"; fi
      done \
    | LC_ALL=C sort -u
)

mapfile -t PREVIOUS_SKILLS < <(
  if [[ -f "$MANAGED_FILE" ]]; then
    python - "$MANAGED_FILE" <<'PY'
import json, sys
for name in json.load(open(sys.argv[1], encoding='utf-8')).get('skills', []):
    print(name)
PY
  fi
)

mkdir -p "$SKILLS_DIR"

for name in "${CURRENT_SKILLS[@]}"; do
  dest="$SKILLS_DIR/$name"
  if [[ -e "$dest" ]]; then
    managed=false
    for prev in "${PREVIOUS_SKILLS[@]}"; do
      if [[ "$prev" == "$name" ]]; then managed=true; break; fi
    done
    if [[ "$managed" != true ]]; then
      echo "Refusing to overwrite unmanaged skill: $dest" >&2
      exit 3
    fi
  fi
done

rm -rf "$MIRROR_DIR"
mkdir -p "$MIRROR_DIR"
cp -a "$TMP_DIR/upstream/." "$MIRROR_DIR/"
rm -rf "$MIRROR_DIR/.git"

for name in "${PREVIOUS_SKILLS[@]}"; do
  rm -rf "$SKILLS_DIR/$name"
done

for name in "${CURRENT_SKILLS[@]}"; do
  src=""
  if [[ -d "$TMP_DIR/upstream/skills/engineering/$name" ]]; then
    src="$TMP_DIR/upstream/skills/engineering/$name"
  elif [[ -d "$TMP_DIR/upstream/skills/productivity/$name" ]]; then
    src="$TMP_DIR/upstream/skills/productivity/$name"
  else
    echo "Managed skill source not found: $name" >&2
    exit 4
  fi
  cp -a "$src" "$SKILLS_DIR/$name"
done

python - "$MANAGED_FILE" "$UPSTREAM_SHA" "$UPSTREAM_VERSION" "${CURRENT_SKILLS[@]}" <<'PY'
import json, sys
from pathlib import Path
path=Path(sys.argv[1])
data={
  "source":"https://github.com/mattpocock/skills",
  "ref":"main",
  "commit":sys.argv[2],
  "version":sys.argv[3],
  "policy":"project-scoped stable skills copied from upstream; in-progress/deprecated remain mirror-only",
  "skills":sorted(sys.argv[4:]),
}
path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
PY

python - "$MIRROR_DIR/.whitechronos-mirror.json" "$UPSTREAM_SHA" "$UPSTREAM_VERSION" "${#CURRENT_SKILLS[@]}" <<'PY'
import json, sys
from pathlib import Path
path=Path(sys.argv[1])
data={
  "source":"https://github.com/mattpocock/skills",
  "ref":"main",
  "commit":sys.argv[2],
  "version":sys.argv[3],
  "stable_skill_count":int(sys.argv[4]),
  "policy":"read-only byte mirror; stable Engineering/Productivity skills are projected into .agents/skills",
}
path.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
PY

if [[ -f "$LOCK_FILE" ]]; then
  python - "$LOCK_FILE" "$UPSTREAM_SHA" "$UPSTREAM_VERSION" "${#CURRENT_SKILLS[@]}" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
data=json.loads(p.read_text(encoding='utf-8'))
data.setdefault('upstream', {})['observed_sha']=sys.argv[2]
data['upstream']['observed_version']=sys.argv[3]
data['upstream']['stable_skill_count']=int(sys.argv[4])
p.write_text(json.dumps(data, indent=2)+"\n", encoding='utf-8')
PY
fi

printf 'MATT_POCOCK_UPSTREAM_SHA=%s\n' "$UPSTREAM_SHA"
printf 'MATT_POCOCK_UPSTREAM_VERSION=%s\n' "$UPSTREAM_VERSION"
printf 'MATT_POCOCK_STABLE_SKILL_COUNT=%s\n' "${#CURRENT_SKILLS[@]}"
