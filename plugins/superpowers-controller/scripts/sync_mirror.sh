#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-$(git rev-parse --show-toplevel)}"
UPSTREAM_URL="${SUPERPOWERS_UPSTREAM_URL:-https://github.com/obra/superpowers.git}"
MIRROR_REL="${SUPERPOWERS_MIRROR_REL:-vendor/obra-superpowers}"
MIRROR_DIR="$REPO_ROOT/$MIRROR_REL"
LOCK_FILE="$REPO_ROOT/plugins/superpowers-controller/upstream.lock.json"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

git clone --depth 1 "$UPSTREAM_URL" "$TMP_DIR/upstream" >/dev/null 2>&1
UPSTREAM_SHA="$(git -C "$TMP_DIR/upstream" rev-parse HEAD)"
UPSTREAM_VERSION="$(node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync(process.argv[1],"utf8")); process.stdout.write(String(p.version||"unknown"));' "$TMP_DIR/upstream/package.json")"

rm -rf "$MIRROR_DIR"
mkdir -p "$MIRROR_DIR"
rsync -a --exclude='.git/' "$TMP_DIR/upstream/" "$MIRROR_DIR/"

cat > "$MIRROR_DIR/.whitechronos-mirror.json" <<JSON
{
  "source": "https://github.com/obra/superpowers",
  "ref": "main",
  "commit": "$UPSTREAM_SHA",
  "version": "$UPSTREAM_VERSION",
  "policy": "read-only mirror; runtime uses the official Superpowers plugin"
}
JSON

if [[ -f "$LOCK_FILE" ]]; then
  python - "$LOCK_FILE" "$UPSTREAM_SHA" "$UPSTREAM_VERSION" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])
data=json.loads(p.read_text())
data["upstream"]["observed_sha"]=sys.argv[2]
data["upstream"]["observed_version"]=sys.argv[3]
p.write_text(json.dumps(data, indent=2)+"\n")
PY
fi

printf 'SUPERPOWERS_UPSTREAM_SHA=%s\n' "$UPSTREAM_SHA"
printf 'SUPERPOWERS_UPSTREAM_VERSION=%s\n' "$UPSTREAM_VERSION"
