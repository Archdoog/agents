#!/usr/bin/env bash

# shellcheck disable=SC2016
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

[[ $# -le 1 ]] || fail 'Usage: pr-threads.sh [PR_NUMBER]'
pr="${1:-}"
if [[ -n "$pr" ]]; then positive_number "$pr"; fi
load_repository
[[ -n "$pr" ]] || pr="$(gh pr view --json number -q .number)"
positive_number "$pr"
owner="${repository%%/*}"
repo="${repository#*/}"
metadata="$(gh api --hostname "$hostname" graphql -f owner="$owner" -f repo="$repo" -F pr="$pr" -f query='
query($owner:String!,$repo:String!,$pr:Int!){
  viewer{login}
  repository(owner:$owner,name:$repo){pullRequest(number:$pr){
    url author{login} baseRefName headRefName headRefOid
    baseRepository{nameWithOwner} headRepository{nameWithOwner}
  }}
}')"
jq -e '.data.repository.pullRequest.url and .data.viewer.login' <<<"$metadata" >/dev/null

connection() {
  local field="$1" selection="$2" pages
  pages="$(gh api --hostname "$hostname" graphql --paginate --slurp \
    -f owner="$owner" -f repo="$repo" -F pr="$pr" -f query="
query(\$owner:String!,\$repo:String!,\$pr:Int!,\$endCursor:String){
  repository(owner:\$owner,name:\$repo){pullRequest(number:\$pr){
    $field(first:100,after:\$endCursor){
      nodes{$selection} pageInfo{hasNextPage endCursor}
    }
  }}
}")"
  jq -e --arg field "$field" 'map(.data.repository.pullRequest[$field].nodes | arrays) | add // []' <<<"$pages"
}

threads="$(connection reviewThreads 'id isResolved isOutdated path line')"
top_comments="$(connection comments 'author{login} body url')"
reviews="$(connection reviews 'author{login} body url state commit{oid}')"
unresolved='[]'
while IFS= read -r thread; do
  thread_id="$(jq -r '.id' <<<"$thread")"
  pages="$(gh api --hostname "$hostname" graphql --paginate --slurp -f id="$thread_id" -f query='
query($id:ID!,$endCursor:String){
  node(id:$id){... on PullRequestReviewThread{
    comments(first:100,after:$endCursor){
      nodes{databaseId author{login} body url} pageInfo{hasNextPage endCursor}
    }
  }}
}')"
  comments="$(jq -e 'map(.data.node.comments.nodes | arrays) | add // []' <<<"$pages")"
  item="$(jq -n --argjson thread "$thread" --argjson comments "$comments" '
    $thread | {thread_id:.id,path,line,outdated:.isOutdated,
      reply_to:$comments[0].databaseId,
      comments:[$comments[] | {author:.author.login,body,url}]}')"
  unresolved="$(jq --argjson item "$item" '. + [$item]' <<<"$unresolved")"
done < <(jq -c '.[] | select(.isResolved == false)' <<<"$threads")

jq -n --argjson metadata "$metadata" --argjson pr "$pr" \
  --argjson threads "$unresolved" --argjson comments "$top_comments" --argjson reviews "$reviews" '
  $metadata.data.repository.pullRequest as $p | {
    pr:$pr,url:$p.url,author:$p.author.login,viewer:$metadata.data.viewer.login,
    base_ref:$p.baseRefName,head_ref:$p.headRefName,head_oid:$p.headRefOid,
    base_repository:$p.baseRepository.nameWithOwner,head_repository:$p.headRepository.nameWithOwner,
    unresolved_threads:$threads,
    top_level_comments:[$comments[] | {author:.author.login,body,url}],
    reviews:[$reviews[] | {author:.author.login,body,url,state,commit:.commit.oid}]
  }'
