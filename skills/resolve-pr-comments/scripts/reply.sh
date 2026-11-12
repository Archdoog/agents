#!/usr/bin/env bash

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

top=false
if [[ "${1:-}" == --top ]]; then
  top=true
  shift
fi
[[ $# -ge 2 ]] || fail 'Usage: reply.sh [--top] PR [COMMENT_ID] BODY | --body-file PATH'
pr="$1"
positive_number "$pr"
shift
if [[ "$top" == false ]]; then
  reply_to="$1"
  positive_number "$reply_to"
  shift
fi
read_body "$@"
load_repository

if [[ "$top" == true ]]; then
  gh api --hostname "$hostname" "repos/$repository/issues/$pr/comments" -f body="$body" -q .html_url
else
  gh api --hostname "$hostname" "repos/$repository/pulls/$pr/comments/$reply_to/replies" -f body="$body" -q .html_url
fi
