#!/usr/bin/env bash

# shellcheck disable=SC2034
set -euo pipefail

fail() {
  printf '%s\n' "$*" >&2
  exit 1
}

positive_number() {
  [[ "$1" =~ ^[1-9][0-9]*$ ]] || fail 'Expected a positive integer.'
}

load_repository() {
  local metadata
  metadata="$(gh repo view --json nameWithOwner,url)"
  repository="$(jq -er '.nameWithOwner' <<<"$metadata")"
  hostname="$(jq -er '.url | split("/")[2]' <<<"$metadata")"
}

read_body() {
  if [[ "${1:-}" == --body-file ]]; then
    [[ $# -eq 2 && -f "$2" ]] || fail 'Expected --body-file and a readable file.'
    body="$(cat -- "$2")"
  else
    [[ $# -eq 1 ]] || fail 'Expected one body argument or --body-file PATH.'
    body="$1"
  fi
  [[ "$body" =~ [^[:space:]] ]] || fail 'The reply body must not be empty.'
}
