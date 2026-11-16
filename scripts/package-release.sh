#!/usr/bin/env bash
# Build the four release tarballs and SHA256SUMS from themes/.
# Usage: scripts/package-release.sh            (output goes to dist/)
# Needs: bash, GNU tar, gzip, sha256sum, node (optional, syntax check only).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEMES=(dracula-inter dracula-macos nightcity tokyonight)
DIST="$ROOT/dist"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
# Fixed timestamp so the same input gives the same tarball.
MTIME="${SOURCE_DATE_EPOCH:-$(git -C "$ROOT" log -1 --format=%ct 2>/dev/null || echo 0)}"

rm -rf "$DIST"; mkdir -p "$DIST"

for t in "${THEMES[@]}"; do
  src="$ROOT/themes/$t"; dst="$STAGE/$t"
  [ -d "$src" ] || { echo "missing $src" >&2; exit 1; }
  cp -a "$src" "$dst"

  # Notices: shared file plus the licence texts every theme refers to.
  cp "$ROOT/THIRD_PARTY_NOTICES.md" "$dst/"
  mkdir -p "$dst/licenses"
  cp "$ROOT"/licenses/MIT-*.txt "$ROOT"/licenses/BSD-*.txt "$ROOT/licenses/Apache-2.0.txt" "$ROOT/licenses/NVD3-NOTICE.txt" "$dst/licenses/"
  # Every licence file named in THIRD_PARTY_NOTICES.md under licenses/ must be in the archive.
  grep -o 'licenses/[A-Za-z0-9._-]*\.txt' "$ROOT/THIRD_PARTY_NOTICES.md" | sort -u | while read -r l; do
    [ -f "$dst/$l" ] || { echo "$t: notices name $l but it is not in the archive" >&2; exit 1; }
  done

  # Checks
  [ ! -e "$dst/assets/stylesheets" ] || { echo "$t: stock SCSS present" >&2; exit 1; }
  for f in LICENSE.OPNsense LICENSE.ariamis LICENSE.bootstrap-select build/css/main.css build/js/theme.js; do
    [ -f "$dst/$f" ] || { echo "$t: missing $f" >&2; exit 1; }
  done
  if grep -rIl "vicuna" "$dst" >/dev/null 2>&1; then echo "$t: leftover 'vicuna' path" >&2; exit 1; fi
  # Every url(...) in main.css must point to a file in this theme.
  grep -o 'url("\?[^)"]*' "$dst/build/css/main.css" | sed 's/url("\?//; s/[?#].*//' | sort -u |
  while read -r u; do
    case "$u" in data:*|"") continue;; esac
    case "$u" in
      /ui/themes/"$t"/*) f="$dst/${u#/ui/themes/$t/}" ;;
      /ui/themes/*) echo "$t: main.css points to another theme: $u" >&2; exit 1 ;;
      *) f="$dst/build/css/$u" ;;
    esac
    [ -f "$f" ] || { echo "$t: main.css references missing file $u" >&2; exit 1; }
  done
  if command -v node >/dev/null 2>&1; then node --check "$dst/build/js/theme.js"; else echo "note: node not installed, skipping the JavaScript syntax check" >&2; fi

  tar --sort=name --mtime="@$MTIME" --owner=0 --group=0 --numeric-owner \
      -C "$STAGE" -cf - "$t" | gzip -9n > "$DIST/opnsense-theme-$t.tar.gz"
done

( cd "$DIST" && sha256sum opnsense-theme-*.tar.gz > SHA256SUMS && sha256sum -c SHA256SUMS )
echo "Done: $DIST"
