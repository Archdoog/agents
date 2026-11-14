#!/usr/bin/env bash
set -euo pipefail

usage() {
    printf '%s\n' \
        'Usage: bash install.sh [--agent claude|codex|cursor|gemini] [options]' \
        '' \
        'Link skills with SKILL.md into the selected skills directory.' \
        '  --agent NAME          Select claude (default), codex, cursor, or gemini.' \
        '  --skills-dir PATH     Use a custom skills directory.' \
        '  --register            Update the selected agent instruction file.' \
        '  --instructions-file PATH  Update a custom instruction file.' \
        '  --dry-run             Show planned changes without writing files.' \
        '  --force               Replace files and symlinks, but never real directories.' \
        '  --claude-md           Register Claude instructions (legacy option).' \
        '  -h, --help            Show this help.' \
        '' \
        'Defaults: Claude uses ~/.claude/skills and ~/.claude/CLAUDE.md.' \
        'Codex uses ~/.agents/skills and ~/.codex/AGENTS.md (respects CODEX_HOME).' \
        'Cursor uses ~/.cursor/skills and ~/.cursor/rules/writing-for-code.mdc.' \
        'Gemini CLI uses ~/.gemini/skills and ~/.gemini/GEMINI.md.' \
        'Example: bash install.sh --agent codex --register' \
        'Custom: bash install.sh --skills-dir /path/to/skills' \
        'Add --instructions-file PATH to register a custom instruction file.'
}

fail() {
    printf 'install.sh: %s\n' "$*" >&2
    exit 1
}

dry_run=false
force=false
register=false
legacy_claude=false
agent=claude
target_dir=''
instructions_file=''
while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent|--skills-dir|--instructions-file)
            [[ $# -ge 2 && -n "$2" && "$2" != --* ]] || fail "Missing value for $1"
            case "$1" in
                --agent) agent=$2 ;;
                --skills-dir) target_dir=$2 ;;
                --instructions-file) instructions_file=$2; register=true ;;
            esac
            shift
            ;;
        --dry-run) dry_run=true ;;
        --force) force=true ;;
        --register) register=true ;;
        --claude-md) register=true; legacy_claude=true ;;
        -h|--help) usage; exit 0 ;;
        *) printf 'install.sh: Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

[[ -n "${HOME:-}" ]] || fail 'HOME is empty. Set HOME before installation.'
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
case "$agent" in
    claude)
        target_dir=${target_dir:-"$HOME/.claude/skills"}
        instructions_file=${instructions_file:-"$HOME/.claude/CLAUDE.md"}
        ;;
    codex)
        target_dir=${target_dir:-"$HOME/.agents/skills"}
        instructions_file=${instructions_file:-"${CODEX_HOME:-$HOME/.codex}/AGENTS.md"}
        ;;
    cursor)
        target_dir=${target_dir:-"$HOME/.cursor/skills"}
        instructions_file=${instructions_file:-"$HOME/.cursor/rules/writing-for-code.mdc"}
        ;;
    gemini)
        target_dir=${target_dir:-"$HOME/.gemini/skills"}
        instructions_file=${instructions_file:-"$HOME/.gemini/GEMINI.md"}
        ;;
    *) fail "Unknown agent: $agent. Use claude, codex, cursor, or gemini." ;;
esac
if "$legacy_claude" && [[ "$agent" != claude ]]; then
    fail "Use --register with --agent $agent."
fi
[[ "$target_dir" == /* ]] || target_dir="$PWD/$target_dir"
[[ "$instructions_file" == /* ]] || instructions_file="$PWD/$instructions_file"
begin='<!-- writing-for-code:begin -->'
end='<!-- writing-for-code:end -->'

write_block() {
    printf '%s\n' "$begin" \
        'Use the writing-for-code skill for technical prose and code comments.' \
        "Read $target_dir/writing-for-code/SKILL.md before writing." \
        "$end"
}

update_instructions() {
    local line line_end last_end=$'\n' state=0 seen=0
    if [[ "$agent" == cursor && "$instructions_file" == *.mdc && ! -s "$instructions_file" ]]; then
        printf '%s\n' '---' 'alwaysApply: true' '---' ''
    fi
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
                fail 'Invalid managed markers in the instruction file. Repair the block before installation.'
            fi
        elif [[ "$state" == 0 ]]; then
            printf '%s%s' "$line" "$line_end"
        fi
    done
    [[ "$state" == 0 ]] || fail 'Incomplete managed block in the instruction file. Repair the block before installation.'
    if [[ "$seen" == 0 ]]; then
        [[ -n "$last_end" ]] || printf '\n'
        [[ ! -s "$instructions_file" ]] || printf '\n'
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

if "$register"; then
    [[ -f "$root/skills/writing-for-code/SKILL.md" ]] || fail 'The writing-for-code skill is missing. Restore it before registration.'
    [[ ! -L "$instructions_file" ]] || fail 'The instruction file is a symlink. Use a regular file before registration.'
    [[ ! -e "$instructions_file" || -f "$instructions_file" ]] || fail 'The instruction file is not a regular file.'
    input=/dev/null
    [[ ! -e "$instructions_file" ]] || input=$instructions_file
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

if "$register"; then
    printf 'Update managed block: %s\n' "$instructions_file"
    "$dry_run" && exit 0
    instructions_dir=$(dirname -- "$instructions_file")
    mkdir -p -- "$instructions_dir"
    temp=$(mktemp "$instructions_dir/.instructions.XXXXXX")
    trap 'rm -f -- "$temp"' EXIT
    if [[ -f "$instructions_file" ]]; then
        cp -p -- "$instructions_file" "$temp"
    fi
    update_instructions < "$input" > "$temp"
    mv -- "$temp" "$instructions_file"
fi
