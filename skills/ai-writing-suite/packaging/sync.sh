#!/usr/bin/env bash
# sync.sh — Single-source → target assembler for AI Writing Suite packaging.
#
# SOURCE OF TRUTH: skills/ai-writing-suite/ (the directory above packaging/)
# GENERATED:      packaging/claude/   packaging/codex/
#
# Rule: NEVER hand-edit files inside packaging/claude/ or packaging/codex/.
#       Edit the source under skills/ai-writing-suite/ and re-run this script.
#       See packaging/README.md for the full rationale (design R4).
#
# Usage:
#   bash packaging/sync.sh            # from repo root OR from packaging/
#   bash packaging/sync.sh --dry-run  # print what would happen, copy nothing
#
# Idempotent: safe to run multiple times; always produces the same result.
# No external deps: pure bash + cp + mkdir.

set -euo pipefail

# ── Resolve paths ─────────────────────────────────────────────────────────────
# Works whether invoked from repo root, from packaging/, or via symlink.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGING="$SCRIPT_DIR"                        # packaging/
SOURCE="$SCRIPT_DIR/.."                        # skills/ai-writing-suite/

CLAUDE_TARGET="$PACKAGING/claude"
CODEX_TARGET="$PACKAGING/codex"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[sync] DRY RUN — no files will be written"
fi

# ── Helpers ───────────────────────────────────────────────────────────────────
do_copy() {
  local src="$1" dest="$2"
  if $DRY_RUN; then
    echo "  copy  $src  →  $dest"
  else
    mkdir -p "$(dirname "$dest")"
    cp -r "$src" "$dest"
  fi
}

do_copy_file() {
  local src="$1" dest="$2"
  if $DRY_RUN; then
    echo "  file  $src  →  $dest"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
  fi
}

log() { echo "[sync] $*"; }

# ── Read version from router SKILL.md frontmatter ─────────────────────────────
# Frontmatter format: --- \n name: ... \n version: X.Y.Z \n ---
# (version field is optional in v1; we default to 1.0.0 if absent)
SKILL_VERSION="$(
  sed -n '/^---[[:space:]]*$/,/^---[[:space:]]*$/ s/^version:[[:space:]]*//p' \
    "$SOURCE/SKILL.md" | head -n1 | tr -d '\r'
)"
if [ -z "$SKILL_VERSION" ]; then
  SKILL_VERSION="1.0.0"
  log "no version: field in SKILL.md frontmatter — defaulting to $SKILL_VERSION"
fi
log "source version: $SKILL_VERSION"

# ── What we copy ──────────────────────────────────────────────────────────────
# Both targets receive the same logical content; only the plugin manifest
# directory name differs (.claude-plugin vs .codex-plugin).
#
# Source layout (relative to $SOURCE):
#   SKILL.md                    router
#   skills/comms-polish/        sub-skill
#   skills/comms-draft/         sub-skill (stub)
#   skills/comms-qa/            sub-skill (stub)
#   skills/voice-onboard/       sub-skill
#   _shared/                    patterns, knowledge, voice-profile, etc.
#   NOTICE.md  LICENSE  README.md  CHANGELOG.md

SKILL_FILES=(SKILL.md NOTICE.md LICENSE README.md CHANGELOG.md)
SKILL_DIRS=(skills _shared)

sync_target() {
  local target="$1"
  local label="$2"
  log "syncing → $label ($target)"

  # Remove previously-generated content so deletions in source propagate.
  # We only wipe the content dirs, never the manifest dir (.claude-plugin /
  # .codex-plugin) because those contain hand-maintained manifests.
  for d in "${SKILL_DIRS[@]}"; do
    if [ -d "$target/$d" ]; then
      if $DRY_RUN; then
        echo "  rm -rf $target/$d"
      else
        rm -rf "${target:?}/$d"
      fi
    fi
  done

  # Top-level files
  for f in "${SKILL_FILES[@]}"; do
    [ -f "$SOURCE/$f" ] && do_copy_file "$SOURCE/$f" "$target/$f"
  done

  # Directories (recursive)
  for d in "${SKILL_DIRS[@]}"; do
    [ -d "$SOURCE/$d" ] && do_copy "$SOURCE/$d" "$target/$d"
  done

  log "  done → $label"
}

# ── Sync both targets ─────────────────────────────────────────────────────────
sync_target "$CLAUDE_TARGET" "claude"
sync_target "$CODEX_TARGET"  "codex"

# ── Version lockstep check ────────────────────────────────────────────────────
# Warn (not fail) if plugin manifests carry a different version than the source.
# Update the manifests manually to match after bumping the source version.
check_manifest_version() {
  local manifest="$1" label="$2"
  if [ ! -f "$manifest" ]; then
    log "  WARN: manifest not found: $manifest"
    return
  fi
  # Extract "version" field with python3 (available on macOS + Linux)
  local mver
  mver="$(python3 -c "
import json, sys
data = json.load(open(sys.argv[1]))
print(data.get('version', ''))
" "$manifest" 2>/dev/null || true)"
  if [ -z "$mver" ]; then
    log "  WARN ($label): could not read version from $manifest"
  elif [ "$mver" != "$SKILL_VERSION" ]; then
    log "  WARN ($label): manifest version ($mver) ≠ source version ($SKILL_VERSION)"
    log "         Update \"version\" in $manifest to match."
  else
    log "  OK ($label): manifest version matches source ($SKILL_VERSION)"
  fi
}

if ! $DRY_RUN; then
  check_manifest_version "$CLAUDE_TARGET/.claude-plugin/plugin.json" "claude"
  check_manifest_version "$CODEX_TARGET/.codex-plugin/plugin.json"   "codex"
fi

log "sync complete."
