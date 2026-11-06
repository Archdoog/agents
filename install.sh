#!/usr/bin/env bash
# Link every skill in skills/ into ~/.claude/skills/.
#
# Usage:
#   ./install.sh               link every skill
#   ./install.sh --dry-run     print the actions, change nothing
#   ./install.sh --force       replace a link or a file that has the same name
#   ./install.sh --claude-md   also add the writing-for-code block to ~/.claude/CLAUDE.md
#
# If ~/.claude/skills/ already has a link or a file with the same name, the
# script skips that skill. Use --force to replace it. The script never
# replaces a real directory.

set -euo pipefail

DRY_RUN=0
FORCE=0
CLAUDE_MD=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --force) FORCE=1 ;;
    --claude-md) CLAUDE_MD=1 ;;
    -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "install.sh: unknown argument: $arg" >&2; exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/skills"

run() {
  if [ "$DRY_RUN" -eq 1 ]; then echo "would: $*"; else "$@"; fi
}

run mkdir -p "$DEST"

status=0
for src in "$REPO_ROOT"/skills/*/; do
  name="$(basename "$src")"
  src="${src%/}"
  dst="$DEST/$name"
  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    echo "ok      $name"
    continue
  fi
  if [ -d "$dst" ] && [ ! -L "$dst" ]; then
    echo "skip    $name: $dst is a directory. Move it, then run again." >&2
    status=1
    continue
  fi
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    if [ "$FORCE" -eq 0 ]; then
      echo "skip    $name: $dst exists. Use --force to replace it." >&2
      status=1
      continue
    fi
    run rm "$dst"
  fi
  run ln -s "$src" "$dst"
  [ "$DRY_RUN" -eq 1 ] || echo "linked  $name"
done

if [ "$CLAUDE_MD" -eq 1 ]; then
  file="$HOME/.claude/CLAUDE.md"
  begin="<!-- writing-for-code:begin -->"
  end="<!-- writing-for-code:end -->"
  block="$begin
## Writing for code

Before you write or edit a code comment, docstring, README, doc page, error
message, commit message, PR body, issue, or review comment, read
\`$DEST/writing-for-code/SKILL.md\` and the file for that surface.
Before you commit or open a PR, run
\`$DEST/writing-for-code/scripts/writing-for-code check\`.
$end"
  if [ -f "$file" ] && grep -qF "$begin" "$file"; then
    echo "ok      $file already has the writing-for-code block"
  elif [ "$DRY_RUN" -eq 1 ]; then
    echo "would: add the writing-for-code block to $file"
  else
    mkdir -p "$(dirname "$file")"
    printf '\n%s\n' "$block" >> "$file"
    echo "added   the writing-for-code block to $file"
  fi
fi

exit "$status"
