#!/usr/bin/env bash
# Fetch PR review feedback from a GitHub repo via GraphQL (batched).
#
# Usage (run inside a git repo, or pass --repo):
#   fetch_pr_comments.sh --limit 300              # last N PRs of the current repo
#   fetch_pr_comments.sh --repo owner/name        # explicit repo
#   fetch_pr_comments.sh --since 2026-06-10       # PRs created after date
#   fetch_pr_comments.sh --since-pr 3160          # PRs numbered above N
#
# Output: JSONL on stdout — one object per comment:
#   {pr, prAuthor, kind: review|thread|issue, author, path, body}
# Excludes bots. Filtering out a PR author's own comments is the consumer's job.
set -euo pipefail

OWNER=""
REPO=""
LIMIT=300
SINCE=""
SINCE_PR=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      case "$2" in
        */*) OWNER="${2%%/*}"; REPO="${2##*/}" ;;
        *)   REPO="$2" ;;
      esac
      shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --since) SINCE="$2"; shift 2 ;;
    --since-pr) SINCE_PR="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Default to the repo we're standing in.
if [[ -z "$OWNER" || -z "$REPO" ]]; then
  current=$(gh repo view --json owner,name -q '.owner.login + "/" + .name' 2>/dev/null || true)
  if [[ -z "$current" ]]; then
    echo "no repo: run inside a GitHub repo or pass --repo owner/name" >&2
    exit 1
  fi
  OWNER=${OWNER:-${current%%/*}}
  REPO=${REPO:-${current##*/}}
fi

QUERY='
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: 25, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number
        createdAt
        author { login }
        reviews(first: 50) { nodes { author { login } state body } }
        reviewThreads(first: 50) {
          nodes { comments(first: 30) { nodes { author { login } path body } } }
        }
        comments(first: 30) { nodes { author { login } body } }
      }
    }
  }
}'

cursor=""
fetched=0
done=0
while [[ $done -eq 0 ]]; do
  if [[ -z "$cursor" ]]; then
    page=$(gh api graphql -f query="$QUERY" -F owner="$OWNER" -F repo="$REPO")
  else
    page=$(gh api graphql -f query="$QUERY" -F owner="$OWNER" -F repo="$REPO" -F cursor="$cursor")
  fi

  echo "$page" | jq -c --arg since "$SINCE" --argjson sincePr "$SINCE_PR" '
    .data.repository.pullRequests.nodes[]
    | select(($since == "" or .createdAt > $since) and .number > $sincePr)
    | . as $pr
    | (
        (.reviews.nodes[] | select((.body // "") != "")
          | {pr: $pr.number, prAuthor: ($pr.author.login // "ghost"), kind: "review",
             author: (.author.login // "ghost"), path: "", body}),
        (.reviewThreads.nodes[].comments.nodes[]
          | {pr: $pr.number, prAuthor: ($pr.author.login // "ghost"), kind: "thread",
             author: (.author.login // "ghost"), path: (.path // ""), body}),
        (.comments.nodes[] | select((.body // "") != "")
          | {pr: $pr.number, prAuthor: ($pr.author.login // "ghost"), kind: "issue",
             author: (.author.login // "ghost"), path: "", body})
      )
    | select(.author | test("\\[bot\\]$|^github-actions|^cursor|^claude|copilot|codex|coderabbit|sourcery|greptile"; "i") | not)
  '

  count=$(echo "$page" | jq '.data.repository.pullRequests.nodes | length')
  fetched=$((fetched + count))

  # stop when: page exhausted, limit hit, or oldest PR on page is older than cutoffs
  hasNext=$(echo "$page" | jq -r '.data.repository.pullRequests.pageInfo.hasNextPage')
  cursor=$(echo "$page" | jq -r '.data.repository.pullRequests.pageInfo.endCursor')
  oldestOk=$(echo "$page" | jq -r --arg since "$SINCE" --argjson sincePr "$SINCE_PR" '
    [.data.repository.pullRequests.nodes[]
     | (($since == "" or .createdAt > $since) and .number > $sincePr)] | all')

  if [[ "$hasNext" != "true" || $fetched -ge $LIMIT || "$oldestOk" != "true" || $count -eq 0 ]]; then
    done=1
  fi
done

echo "fetched $fetched PRs from $OWNER/$REPO" >&2
