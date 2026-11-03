#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

SKILL_NAME="generate-image"
CLAUDE_BASE="${HOME}/.claude"
COPILOT_BASE="${HOME}/.copilot"
CLAUDE_TARGET="${CLAUDE_BASE}/skills/${SKILL_NAME}"
COPILOT_TARGET="${COPILOT_BASE}/skills/${SKILL_NAME}"

CLAUDE_ONLY=false
COPILOT_ONLY=false
LINK_MODE=false
UNINSTALL=false
DRY_RUN=false

usage() {
  cat <<'EOF'
Usage: install.sh [options]

Install the generate-image skill for Claude Code CLI and/or GitHub Copilot CLI.

Options:
  --claude-only   Install only for Claude Code
  --copilot-only  Install only for GitHub Copilot CLI
  --link          Use symlinks instead of copying
  --uninstall     Remove installed skill
  --dry-run       Show what would be done without doing it
  --help          Show this help message
EOF
}

say() {
  printf '%s\n' "$*"
}

warn() {
  printf 'Warning: %s\n' "$*" >&2
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

run_cmd() {
  if [ "$DRY_RUN" = true ]; then
    printf '[dry-run]'
    for arg in "$@"; do
      printf ' %q' "$arg"
    done
    printf '\n'
  else
    "$@"
  fi
}

check_prerequisites() {
  local missing=0
  local tool

  for tool in curl python3 base64; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      warn "$tool is not installed or not on PATH. The skill may not work until it is installed."
      missing=1
    fi
  done

  if [ "$missing" -eq 0 ]; then
    say "Prerequisite check: curl, python3, and base64 found."
  fi
}

check_sources() {
  if [ ! -f "$SCRIPT_DIR/skills/generate-image/SKILL.md" ]; then
    printf 'Error: Missing required source file: %s/skills/generate-image/SKILL.md\n' "$SCRIPT_DIR" >&2
    exit 1
  fi
}

install_target() {
  local label="$1"
  local target="$2"
  local status_word="installed"

  if [ "$DRY_RUN" = true ]; then
    status_word="would install"
  fi

  if [ -e "$target" ]; then
    warn "$label skill already exists at $target. Overwriting it now. Use --uninstall to cleanly remove it first."
  fi

  run_cmd mkdir -p "$target"
  run_cmd rm -f "$target/SKILL.md"

  if [ "$LINK_MODE" = true ]; then
    run_cmd ln -s "$SCRIPT_DIR/skills/generate-image/SKILL.md" "$target/SKILL.md"
  else
    run_cmd cp "$SCRIPT_DIR/skills/generate-image/SKILL.md" "$target/SKILL.md"
  fi
  say "$label: $status_word at $target"
}

uninstall_target() {
  local label="$1"
  local target="$2"
  local status_word="removed"

  if [ "$DRY_RUN" = true ]; then
    status_word="would remove"
  fi

  if [ -e "$target" ]; then
    run_cmd rm -rf "$target"
    say "$label: $status_word $target"
  else
    say "$label: nothing to remove at $target"
  fi
}

selected_targets=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --claude-only)
      CLAUDE_ONLY=true
      ;;
    --copilot-only)
      COPILOT_ONLY=true
      ;;
    --link)
      LINK_MODE=true
      ;;
    --uninstall)
      UNINSTALL=true
      ;;
    --dry-run)
      DRY_RUN=true
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      die "Unknown option: $1"
      ;;
  esac
  shift
done

if [ "$CLAUDE_ONLY" = true ] && [ "$COPILOT_ONLY" = true ]; then
  die "Use only one of --claude-only or --copilot-only."
fi

if [ "$CLAUDE_ONLY" = true ]; then
  selected_targets+=("claude")
elif [ "$COPILOT_ONLY" = true ]; then
  selected_targets+=("copilot")
else
  if [ "$UNINSTALL" = true ]; then
    selected_targets+=("claude" "copilot")
  else
    [ -d "$CLAUDE_BASE" ] && selected_targets+=("claude")
    [ -d "$COPILOT_BASE" ] && selected_targets+=("copilot")

    if [ "${#selected_targets[@]}" -eq 0 ]; then
      cat <<EOF
No supported CLI config directories were found.

This installer supports:
  - Claude Code CLI ($CLAUDE_BASE)
  - GitHub Copilot CLI ($COPILOT_BASE)

Install one of those CLIs first, then run this script again.
You can also force a target with --claude-only or --copilot-only.
EOF
      exit 0
    fi
  fi
fi

if [ "$UNINSTALL" = true ]; then
  for target in "${selected_targets[@]}"; do
    case "$target" in
      claude)
        uninstall_target "Claude Code" "$CLAUDE_TARGET"
        ;;
      copilot)
        uninstall_target "GitHub Copilot CLI" "$COPILOT_TARGET"
        ;;
    esac
  done

  if [ "$DRY_RUN" = true ]; then
    say "Dry run complete."
  else
    say "Uninstall complete."
  fi
  exit 0
fi

check_prerequisites
check_sources

installed_paths=()
for target in "${selected_targets[@]}"; do
  case "$target" in
    claude)
      install_target "Claude Code" "$CLAUDE_TARGET"
      installed_paths+=("$CLAUDE_TARGET")
      ;;
    copilot)
      install_target "GitHub Copilot CLI" "$COPILOT_TARGET"
      installed_paths+=("$COPILOT_TARGET")
      ;;
  esac
done

say ""
if [ "$DRY_RUN" = true ]; then
  say "Dry run complete."
else
  say "Install complete."
fi
for path in "${installed_paths[@]}"; do
  say "  - $path"
done
say ""
say "The skill will guide you through API key setup the first time you generate an image."
say "Quick start: restart Claude Code CLI or Copilot CLI, then invoke the generate-image skill."
