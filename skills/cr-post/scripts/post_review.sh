#!/usr/bin/env bash
# Post one review with inline comments on a GitHub PR.
#
# Usage (run inside the git repo of the PR):
#   post_review.sh --comments comments.json                 # PR of the current branch
#   post_review.sh --comments comments.json --pr 123
#   post_review.sh --comments comments.json --dry-run        # print the payload, post nothing
#   post_review.sh --comments comments.json --body "text"    # optional review summary
#
# comments.json is a JSON array of GitHub review-comment objects:
#   [{"path": "src/a.ts", "line": 135, "body": "..."},
#    {"path": "src/b.ts", "start_line": 10, "line": 12, "body": "..."}]
# "side" defaults to RIGHT (the new side of the diff), which is what an added or
# changed line needs. Use "side": "LEFT" only for a deleted line.
#
# What it does:
#   1. resolves the repo and the PR,
#   2. fails when local HEAD is not the PR head commit (line numbers would drift),
#   3. drops any comment whose path:line is not commentable in the PR diff,
#   4. posts everything left as ONE review with event=COMMENT,
#   5. prints the review URL on stdout.
# Dropped comments go to stderr as JSONL, each with a "_skip" reason.
set -euo pipefail

COMMENTS=""
PR=""
REPO=""
BODY=""
DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --comments) COMMENTS="$2"; shift 2 ;;
    --pr)       PR="$2"; shift 2 ;;
    --repo)     REPO="$2"; shift 2 ;;
    --body)     BODY="$2"; shift 2 ;;
    --dry-run)  DRY=1; shift ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -n "$COMMENTS" ]] || { echo "--comments <file.json> is required" >&2; exit 1; }
[[ -f "$COMMENTS" ]] || { echo "no such file: $COMMENTS" >&2; exit 1; }
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

if [[ -z "$REPO" ]]; then
  REPO=$(gh repo view --json owner,name -q '.owner.login + "/" + .name' 2>/dev/null || true)
  [[ -n "$REPO" ]] || { echo "no repo: run inside a GitHub repo or pass --repo owner/name" >&2; exit 1; }
fi

# Resolve the PR and its head commit.
if [[ -n "$PR" ]]; then
  meta=$(gh pr view "$PR" --repo "$REPO" --json number,headRefOid,state,url 2>/dev/null || true)
else
  meta=$(gh pr view --repo "$REPO" --json number,headRefOid,state,url 2>/dev/null || true)
fi
[[ -n "$meta" ]] || { echo "no PR found (pass --pr N)" >&2; exit 1; }

PR=$(jq -r .number <<<"$meta")
HEAD_SHA=$(jq -r .headRefOid <<<"$meta")
PR_URL=$(jq -r .url <<<"$meta")

# Line numbers in the comments come from the local tree. If local HEAD is not the
# PR head, they can point at the wrong code — refuse rather than mis-anchor.
LOCAL_SHA=$(git rev-parse HEAD 2>/dev/null || echo "")
if [[ -n "$LOCAL_SHA" && "$LOCAL_SHA" != "$HEAD_SHA" ]]; then
  echo "local HEAD ($LOCAL_SHA) is not the PR head ($HEAD_SHA) — push first, then rerun" >&2
  exit 2
fi

# Every new-side line the PR diff makes commentable: added lines and context lines.
PAIRS=$(gh pr diff "$PR" --repo "$REPO" | awk '
  /^\+\+\+ / { p=$2; sub(/^b\//,"",p); if (p=="/dev/null") p=""; inhunk=0; next }
  /^@@/      { match($0, /\+[0-9]+/); n=substr($0, RSTART+1, RLENGTH-1)+0; inhunk=1; next }
  inhunk && p!="" {
    if ($0 == "")                { print p "\t" n; n++; next }
    c = substr($0,1,1)
    if (c == "+" || c == " ")    { print p "\t" n; n++; next }
    if (c == "-" || c == "\\")   { next }
    inhunk=0
  }
' | jq -R -s '
  split("\n") | map(select(length > 0) | split("\t"))
  | map({key: (.[0] + ":" + .[1]), value: true}) | from_entries')

CHECKED=$(jq --argjson ok "$PAIRS" '
  def key(pth; ln): pth + ":" + (ln | tostring);
  map(
    . + {side: (.side // "RIGHT")}
    # A start_line outside the diff degrades to a single-line comment; the whole
    # comment is only dropped when its anchor line itself is not commentable.
    | if (.start_line != null) and (.side == "RIGHT")
         and (($ok[key(.path; .start_line)] // false) | not)
      then del(.start_line, .start_side) else . end
    | if (.side == "RIGHT") and (($ok[key(.path; .line)] // false) | not)
      then . + {_skip: "line is not part of the PR diff"} else . end
  )' "$COMMENTS")

jq -c '.[] | select(._skip != null)' <<<"$CHECKED" >&2
VALID=$(jq '[.[] | select(._skip == null) | del(._skip)]' <<<"$CHECKED")
COUNT=$(jq 'length' <<<"$VALID")

if [[ "$COUNT" -eq 0 ]]; then
  echo "nothing to post: every comment was dropped" >&2
  exit 3
fi

PAYLOAD=$(jq -n --arg commit "$HEAD_SHA" --arg body "$BODY" --argjson comments "$VALID" \
  '{commit_id: $commit, event: "COMMENT", comments: $comments}
   + (if ($body | length) > 0 then {body: $body} else {} end)')

if [[ "$DRY" -eq 1 ]]; then
  echo "dry run: would post $COUNT comment(s) on $PR_URL" >&2
  jq . <<<"$PAYLOAD"
  exit 0
fi

# One review, one notification — the same thing a person leaves.
RESPONSE=$(gh api "repos/$REPO/pulls/$PR/reviews" --input - <<<"$PAYLOAD")
jq -r '"posted \(.html_url)"' <<<"$RESPONSE"
echo "$COUNT comment(s) on $PR_URL" >&2
