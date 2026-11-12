#!/usr/bin/env bash

# shellcheck disable=SC2016
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

[[ $# -eq 1 && "$1" =~ ^PRRT_[A-Za-z0-9_-]+$ ]] || fail 'Usage: resolve.sh PRRT_THREAD_ID'
thread="$1"
load_repository
result="$(gh api --hostname "$hostname" graphql -f threadId="$thread" -f query='
mutation($threadId:ID!){
  resolveReviewThread(input:{threadId:$threadId}){ thread{ isResolved } }
}')"
jq -e '.data.resolveReviewThread.thread.isResolved == true' <<<"$result"
