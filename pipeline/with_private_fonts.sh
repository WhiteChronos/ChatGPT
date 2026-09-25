#!/usr/bin/env bash
set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: $0 FONT_DIR command [args...]" >&2
  exit 64
fi

FONT_DIR=$1
shift

if [ ! -d "$FONT_DIR" ]; then
  echo "font directory does not exist: $FONT_DIR" >&2
  exit 66
fi

TMP_ROOT="${TMPDIR:-/tmp}/engineering-fonts-$$"
CFG="$TMP_ROOT/fonts.conf"
CACHE="$TMP_ROOT/cache"
mkdir -p "$CACHE"
cleanup() { rm -rf "$TMP_ROOT"; }
trap cleanup EXIT HUP INT TERM

cat > "$CFG" <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <dir>${FONT_DIR}</dir>
  <cachedir>${CACHE}</cachedir>
</fontconfig>
EOF

FONTCONFIG_FILE="$CFG" fc-cache -f >/dev/null 2>&1 || true
FONTCONFIG_FILE="$CFG" XDG_CACHE_HOME="$CACHE" "$@"
