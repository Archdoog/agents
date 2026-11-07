#!/usr/bin/env bash
set -euo pipefail

usage() {
    printf '%s\n' \
        'Usage: bash install.sh [--dry-run] [--force] [--claude-md]' \
        '' \
        'Link skills with SKILL.md into ~/.claude/skills.' \
        '  --dry-run    Show planned changes without writing files.' \
        '  --force      Replace files and symlinks, but never real directories.' \
        '  --claude-md  Add or replace the managed block in ~/.claude/CLAUDE.md.' \
        '  -h, --help   Show this help.'
}

fail() {
    printf 'install.sh: %s\n' "$*" >&2
    exit 1
}

dry_run=false
force=false
claude_md_enabled=false
for arg in "$@"; do
    case "$arg" in
        --dry-run) dry_run=true ;;
        --force) force=true ;;
        --claude-md) claude_md_enabled=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'install.sh: Unknown argument: %s\n' "$arg" >&2; usage >&2; exit 2 ;;
    esac
done

[[ -n "${HOME:-}" ]] || fail 'HOME is empty. Set HOME before installation.'
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
claude_dir="$HOME/.claude"
target_dir="$claude_dir/skills"
claude_md="$claude_dir/CLAUDE.md"
begin='<!-- writing-for-code:begin -->'
end='<!-- writing-for-code:end -->'

write_block() {
    printf '%s\n' "$begin" \
        'Use the writing-for-code skill for technical prose and code comments.' \
        'Read ~/.claude/skills/writing-for-code/SKILL.md before writing.' \
        "$end"
}

update_instructions() {
    local line line_end last_end=$'\n' state=0 seen=0
    while true; do
        line_end=$'\n'
        IFS= read -r line || line_end=''
        [[ -n "$line$line_end" ]] || break
        last_end=$line_end
        if [[ "$line" == *writing-for-code:* || "$line" =~ \<\!--[[:space:]]*writing-for-code ]]; then
            if [[ "$line" == "$begin" && "$state" == 0 && "$seen" == 0 ]]; then
                state=1
                seen=1
                write_block
            elif [[ "$line" == "$end" && "$state" == 1 ]]; then
                state=0
            else
                fail 'Invalid managed markers in CLAUDE.md. Repair the block before installation.'
            fi
        elif [[ "$state" == 0 ]]; then
            printf '%s%s' "$line" "$line_end"
        fi
    done
    [[ "$state" == 0 ]] || fail 'Incomplete managed block in CLAUDE.md. Repair the block before installation.'
    if [[ "$seen" == 0 ]]; then
        [[ -n "$last_end" ]] || printf '\n'
        [[ ! -s "$claude_md" ]] || printf '\n'
        write_block
    fi
}

sources=()
for source in "$root"/skills/*; do
    [[ -f "$source/SKILL.md" ]] || continue
    sources+=("$source")
    target="$target_dir/${source##*/}"
    if [[ -L "$target" && "$(readlink -- "$target")" == "$source" ]]; then
        continue
    fi
    [[ ! -d "$target" || -L "$target" ]] || fail "Cannot replace a real directory: $target"
    if [[ -e "$target" || -L "$target" ]]; then
        "$force" || fail "Destination exists: $target. Use --force to replace a file or symlink."
    fi
done
[[ ${#sources[@]} -gt 0 ]] || fail 'No skills contain SKILL.md. Check the source directory.'

if "$claude_md_enabled"; then
    [[ -f "$root/skills/writing-for-code/SKILL.md" ]] || fail 'The writing-for-code skill is missing. Restore it before registration.'
    [[ ! -L "$claude_md" ]] || fail 'CLAUDE.md is a symlink. Use a regular file before registration.'
    [[ ! -e "$claude_md" || -f "$claude_md" ]] || fail 'CLAUDE.md is not a regular file.'
    input=/dev/null
    [[ ! -e "$claude_md" ]] || input=$claude_md
    update_instructions < "$input" > /dev/null
fi

for source in "${sources[@]}"; do
    target="$target_dir/${source##*/}"
    if [[ -L "$target" && "$(readlink -- "$target")" == "$source" ]]; then
        printf 'Already linked: %s\n' "$target"
        continue
    fi
    printf 'Link: %s -> %s\n' "$target" "$source"
    "$dry_run" && continue
    mkdir -p -- "$target_dir"
    [[ ! -d "$target" || -L "$target" ]] || fail "Cannot replace a real directory: $target"
    if [[ -e "$target" || -L "$target" ]]; then
        "$force" || fail "Destination exists: $target"
        rm -f -- "$target"
    fi
    ln -s -- "$source" "$target"
done

if "$claude_md_enabled"; then
    printf 'Update managed block: %s\n' "$claude_md"
    "$dry_run" && exit 0
    temp=$(mktemp "$claude_dir/.CLAUDE.md.XXXXXX")
    trap 'rm -f -- "$temp"' EXIT
    if [[ -f "$claude_md" ]]; then
        cp -p -- "$claude_md" "$temp"
    fi
    update_instructions < "$input" > "$temp"
    mv -- "$temp" "$claude_md"
fi
