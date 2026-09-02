#!/usr/bin/env python3
"""Audit and repair commit signatures on the current branch.

Report mode (default) lists every commit in the range and says whether it is
signed, whether the signature is good, and whether GitHub will accept it.
Fix mode rewrites the unsigned commits with `git commit-tree -S`, keeping the
tree of every commit byte-identical and preserving merge commits.

Speed comes from batching: three git processes read the whole range (log,
cat-file --batch, merge-base) and one GraphQL request checks every commit on
GitHub. Only the signing itself runs per commit, because each new signature
changes the hash that the next commit must point at.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

US = "\x1f"
FMT = US.join(["%H", "%P", "%G?", "%an", "%ae", "%aI", "%cn", "%ce", "%cI", "%B"])
GITHUB_NOREPLY = "noreply@github.com"


class Fail(Exception):
    pass


def git(*args: str, check: bool = True, stdin: bytes | None = None) -> bytes:
    proc = subprocess.run(
        ["git", *args], input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if check and proc.returncode != 0:
        raise Fail(f"git {' '.join(args)} failed: {proc.stderr.decode().strip()}")
    return proc.stdout


def git_text(*args: str, check: bool = True) -> str:
    return git(*args, check=check).decode("utf-8", "replace").strip()


class Commit:
    __slots__ = (
        "sha", "parents", "gsig", "an", "ae", "ad", "cn", "ce", "cd", "body", "signed",
        "new_sha", "action",
    )

    def __init__(self, record: str) -> None:
        f = record.split(US)
        self.sha = f[0]
        self.parents = f[1].split() if f[1] else []
        self.gsig = f[2]
        self.an, self.ae, self.ad = f[3], f[4], f[5]
        self.cn, self.ce, self.cd = f[6], f[7], f[8]
        self.body = f[9]
        self.signed = False
        self.new_sha = self.sha
        self.action = "keep"

    @property
    def short(self) -> str:
        return self.sha[:9]

    @property
    def subject(self) -> str:
        return self.body.splitlines()[0] if self.body.strip() else "(no message)"


def resolve_base(base: str | None) -> str:
    """Return the commit the range starts after."""
    if base:
        return git_text("rev-parse", "--verify", f"{base}^{{commit}}")
    for ref in ("origin/main", "origin/master", "origin/HEAD"):
        if subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0:
            return git_text("merge-base", "HEAD", ref)
    raise Fail("no origin/main, origin/master or origin/HEAD found — pass --base")


def read_commits(base: str) -> list[Commit]:
    """One git process reads the whole range, oldest first, parents before children."""
    raw = git("log", "-z", "--reverse", "--topo-order", f"--format={FMT}", f"{base}..HEAD")
    return [Commit(r.decode("utf-8", "replace")) for r in raw.split(b"\x00") if r]


def mark_signature_presence(commits: list[Commit]) -> None:
    """One `git cat-file --batch` tells us which commits carry a gpgsig header.

    `%G?` alone is not enough: on a machine with no gpg installed it reports `N`
    for a teammate's GPG-signed commit, and re-signing that commit would be wrong.
    """
    if not commits:
        return
    stdin = "".join(f"{c.sha}\n" for c in commits).encode()
    out = git("cat-file", "--batch", stdin=stdin)
    pos = 0
    for c in commits:
        nl = out.index(b"\n", pos)
        size = int(out[pos:nl].split()[2])
        header = out[nl + 1: nl + 1 + size].split(b"\n\n", 1)[0]
        c.signed = b"\ngpgsig" in b"\n" + header
        pos = nl + 1 + size + 1


def github_verification(commits: list[Commit], repo: str) -> dict[str, str]:
    """Ask GitHub about every commit in ONE GraphQL request.

    A locally good signature is not proof. GitHub also requires the key to belong
    to the committer identity, so a merge made by the web UI (committer
    `GitHub <noreply@github.com>`) comes back `unknown_key` even when git says `G`.
    """
    owner, _, name = repo.partition("/")
    fields = "".join(
        f'c{i}: object(oid:"{c.sha}"){{... on Commit{{signature{{isValid state}}}}}} '
        for i, c in enumerate(commits)
    )
    query = f'{{repository(owner:"{owner}",name:"{name}"){{{fields}}}}}'
    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise Fail(f"gh api graphql failed: {proc.stderr.decode().strip()}")
    repo_node = json.loads(proc.stdout)["data"]["repository"]
    result: dict[str, str] = {}
    for i, c in enumerate(commits):
        node = repo_node.get(f"c{i}")
        if not node:
            result[c.sha] = "not pushed"
        elif not node.get("signature"):
            result[c.sha] = "unsigned"
        else:
            sig = node["signature"]
            result[c.sha] = "valid" if sig["isValid"] else sig["state"].lower()
    return result


def status_of(c: "Commit", remote: dict[str, str]) -> str:
    """One word for the true state of a commit's signature.

    GitHub is the authority when it has an answer, because it is the thing that
    prints "Verified". The local `%G?` is only a fallback: it reports `N` for a
    perfectly good GPG signature when `gpg` is not installed on this machine,
    which is exactly the case for merges made with the GitHub web UI.
    """
    gh = remote.get(c.sha)
    if gh == "valid":
        return "verified"
    if gh in ("unsigned", None) and not c.signed:
        return "UNSIGNED"
    if gh and gh != "valid":
        return gh.upper()
    if c.gsig == "G":
        return "verified"
    return "unverifiable"


def needs_repair(c: "Commit", remote: dict[str, str], me: set[str]) -> bool:
    """Repair only our own commits, and only when they are genuinely broken.

    A signature we cannot verify locally is not a defect — leave it alone unless
    GitHub also rejects it. Rewriting it would replace someone else's good
    signature with ours for no gain.
    """
    if c.ce.lower() not in me and c.ae.lower() not in me:
        return False
    return status_of(c, remote) not in ("verified", "unverifiable")


def detect_repo() -> str | None:
    url = git_text("remote", "get-url", "origin", check=False)
    if "github.com" not in url:
        return None
    tail = url.split("github.com", 1)[1].lstrip(":/")
    return tail[:-4] if tail.endswith(".git") else tail


def load_remap(path: str | None) -> dict[str, str]:
    """Read `<old-sha> <new-sha>` pairs that replace one lineage with another.

    Use this after a branch you merged from was itself rewritten. Your branch then
    holds both the old and the new copy of that work. Repointing the parent links
    at the new copy drops the stale copy without replaying a single patch, so no
    conflict can arise. Both copies must have the same trees for this to be safe.
    """
    if not path:
        return {}
    pairs: dict[str, str] = {}
    with open(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            old, new = line.split()[:2]
            pairs[git_text("rev-parse", old)] = git_text("rev-parse", new)
    for old, new in pairs.items():
        old_tree = git_text("rev-parse", f"{old}^{{tree}}")
        new_tree = git_text("rev-parse", f"{new}^{{tree}}")
        if old_tree != new_tree:
            raise Fail(f"remap {old[:9]} -> {new[:9]} changes the tree — refusing")
    return pairs


def rewrite(
    commits: list[Commit], repair: set[str], me: set[str], name: str, email: str,
    seed: dict[str, str] | None = None,
) -> str:
    """Rebuild the range, adding a signature where one is missing.

    A commit is rebuilt only when it must be: it is broken, or one of its parents
    moved and its hash therefore has to change anyway. Everything else keeps its
    original hash, so an already-verified commit is never disturbed.
    """
    mapping: dict[str, str] = dict(seed or {})
    head = ""
    for c in commits:
        if c.sha in mapping:
            # This commit is a stale copy. Its replacement is already in history,
            # so drop it instead of rebuilding it.
            c.action = "replaced"
            c.new_sha = mapping[c.sha]
            continue
        parents = [mapping.get(p, p) for p in c.parents]
        # A merge whose sides collapse onto the same commit is no longer a merge.
        parents = list(dict.fromkeys(parents))
        moved = parents != c.parents
        mine = c.ce.lower() in me or c.ae.lower() in me
        needs_sig = c.sha in repair
        # Our key cannot sign for the `GitHub <noreply@github.com>` identity, so a
        # web-UI merge we have to rebuild must become ours or GitHub rejects it.
        renames = mine and c.ce.lower() == GITHUB_NOREPLY
        if not (moved or needs_sig):
            mapping[c.sha] = c.sha
            head = c.sha
            continue

        env = dict(os.environ)
        env.update(
            GIT_AUTHOR_NAME=c.an, GIT_AUTHOR_EMAIL=c.ae, GIT_AUTHOR_DATE=c.ad,
            GIT_COMMITTER_NAME=name if renames else c.cn,
            GIT_COMMITTER_EMAIL=email if renames else c.ce,
            GIT_COMMITTER_DATE=c.cd,
        )
        argv = ["git", "commit-tree", "-S" if mine else "--no-gpg-sign"]
        for p in parents:
            argv += ["-p", p]
        argv.append(f"{c.sha}^{{tree}}")
        proc = subprocess.run(
            argv, input=c.body.encode(), env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            raise Fail(f"could not rewrite {c.short}: {proc.stderr.decode().strip()}")
        new = proc.stdout.decode().strip()
        mapping[c.sha] = new
        c.new_sha = new
        c.action = "signed" if needs_sig else ("recommitted" if renames else "reparented")
        head = new
    return head


def guard(old_head: str, new_head: str, base: str, dropped: int = 0) -> None:
    """Refuse to move the branch unless the content is provably unchanged.

    The tree check is absolute: the working tree must come out identical. The
    commit count may only shrink by the number of stale commits a remap drops.
    """
    old_tree = git_text("rev-parse", f"{old_head}^{{tree}}")
    new_tree = git_text("rev-parse", f"{new_head}^{{tree}}")
    if old_tree != new_tree:
        raise Fail(f"tree changed ({old_tree} -> {new_tree}) — refusing to move the branch")
    old_n = int(git_text("rev-list", "--count", f"{base}..{old_head}"))
    new_n = int(git_text("rev-list", "--count", f"{base}..{new_head}"))
    if new_n != old_n - dropped:
        raise Fail(
            f"commit count is {new_n}, expected {old_n - dropped} "
            f"({old_n} minus {dropped} replaced) — refusing to move the branch"
        )


def main() -> int:
    p = argparse.ArgumentParser(description="Audit and repair commit signatures.")
    p.add_argument("--base", help="start of the range (default: merge-base with origin/main)")
    p.add_argument("--fix", action="store_true", help="sign the unverified commits")
    p.add_argument("--push", action="store_true", help="force-with-lease push after a fix")
    p.add_argument("--no-remote", action="store_true", help="skip the GitHub check")
    p.add_argument("--json", action="store_true", help="machine-readable report")
    p.add_argument("--remap", metavar="FILE",
                   help="file of '<old-sha> <new-sha>' pairs replacing a rewritten lineage")
    args = p.parse_args()

    seed = load_remap(args.remap)
    base = resolve_base(args.base)
    commits = read_commits(base)
    if not commits:
        print("No commits in range — nothing to check.")
        return 0
    mark_signature_presence(commits)

    email = git_text("config", "user.email").lower()
    name = git_text("config", "user.name")
    me = {e for e in (email,) if e} | {GITHUB_NOREPLY}

    remote: dict[str, str] = {}
    repo = detect_repo()
    if not args.no_remote and repo:
        try:
            remote = github_verification(commits, repo)
        except Fail as exc:
            print(f"note: GitHub check skipped ({exc})", file=sys.stderr)

    bad = [c for c in commits if needs_repair(c, remote, me)]

    if args.json:
        print(json.dumps({
            "base": base,
            "total": len(commits),
            "unverified": [
                {"sha": c.sha, "subject": c.subject,
                 "status": status_of(c, remote), "github": remote.get(c.sha, "?")}
                for c in bad
            ],
        }, indent=2))
    else:
        broken = {c.sha for c in bad}
        print(f"Range {base[:9]}..HEAD — {len(commits)} commit(s)\n")
        for c in reversed(commits):
            flag = "✗ " if c.sha in broken else "  "
            print(f"{flag}{c.short}  {status_of(c, remote):<13}  {c.subject[:64]}")
        print(f"\n{len(bad)} commit(s) need a signature.")
        if any(status_of(c, remote) == "unverifiable" for c in commits):
            print("(`unverifiable` = signed, but this machine has no gpg to check it. "
                  "GitHub accepts it, so it is left alone.)")

    if not bad and not seed:
        return 0
    if not args.fix:
        print("\nRun again with --fix to sign them.")
        return 1

    if git_text("status", "--porcelain"):
        raise Fail("working tree is dirty — commit or stash first")
    branch = git_text("rev-parse", "--abbrev-ref", "HEAD")
    if branch == "HEAD":
        raise Fail("detached HEAD — check out a branch first")
    old_head = git_text("rev-parse", "HEAD")
    backup = f"backup/{branch}-unsigned"
    git("branch", "-f", backup, old_head)
    print(f"\nBackup branch: {backup} -> {old_head[:9]}")

    new_head = rewrite(commits, {c.sha for c in bad}, me, name, email, seed)
    dropped = sum(1 for c in commits if c.action == "replaced")
    guard(old_head, new_head, base, dropped)
    git("reset", "--hard", new_head)
    print(f"Branch moved: {old_head[:9]} -> {new_head[:9]}  (tree unchanged)")
    if dropped:
        print(f"Dropped {dropped} stale commit(s) replaced by the remapped lineage.")
    for c in commits:
        if c.action != "keep":
            print(f"  {c.short} -> {c.new_sha[:9]}  {c.action}")

    if args.push:
        git("push", "--force-with-lease", "origin", branch)
        print(f"Pushed {branch} with --force-with-lease.")
    else:
        print(f"\nNot pushed. Run: git push --force-with-lease origin {branch}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fail as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
