#!/usr/bin/env python3
"""On-demand workspace repo-sync: commit pending journal/ lines, then push every
workspace repo that is ahead of its upstream.

Replaces the old SessionEnd push hook. This runs *in-session* — via the
`/sync-repos` skill, the SessionStart nudge that flags unpushed repos, or directly
(`python3 ~/.claude/skills/sync-repos/repos-sync.py`). Running in-session means the
output is visible, there's no reliance on a lifecycle hook the harness can kill
mid-run, and no dependence on SessionEnd firing at all (it doesn't, if you just
close the terminal).

Safety: only pushes committed, strictly-ahead, non-diverged repos; never force;
skips no-upstream / offline / diverged (reported, not pushed). The journal commit
is pathspec-scoped to `journal/`, so it can never sweep up in-progress work.

Observability:
  - Prints a summary to stdout (the caller / agent sees it inline).
  - Appends one line to ~/.claude/repo-sync.log — `tail ~/.claude/repo-sync.log`.
  - PROBLEM-ONLY Discord alert via ~/.claude/.discord-webhook, kept for future use:
    inert unless that file exists AND a push failed / a repo diverged.

Exit code: 0 if everything synced cleanly, 1 if any repo needs attention.
"""
import fcntl
import json
import os
import socket
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

REPOS_ROOT = Path.home() / "workdir" / "repos"
LOCK_PATH = Path.home() / ".claude" / ".journal-sync.lock"
LOG_PATH = Path.home() / ".claude" / "repo-sync.log"
WEBHOOK_PATH = Path.home() / ".claude" / ".discord-webhook"
LOG_MAX_LINES = 1000
PRUNE = {"node_modules", ".git", "archive", "dist", ".next", ".astro", "build", ".venv"}
MAX_DEPTH = 3
PUSH_TIMEOUT = 30

# Never let git block on a credential/terminal prompt — fail fast instead of hang.
GIT_ENV = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}


def git(root, *args, timeout=10):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, timeout=timeout,
        stdin=subprocess.DEVNULL, env=GIT_ENV,
    )


def find_repos(root):
    """Git repo roots under `root`, depth-limited, heavy/frozen dirs pruned."""
    roots = []
    root = Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_depth = len(Path(dirpath).relative_to(root).parts)
        if ".git" in dirnames or ".git" in filenames:
            roots.append(Path(dirpath))
        if rel_depth >= MAX_DEPTH:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in PRUNE and not d.startswith(".")]
    return roots


def commit_journal():
    """Commit uncommitted journal/ changes in the meta-repo, pathspec-scoped.

    Returns: "committed" | "clean" | "locked". Locked (non-blocking) so two callers
    can't race the shared meta-repo index; whoever loses simply skips.
    """
    status = git(REPOS_ROOT, "status", "--porcelain", "--", "journal")
    if status.returncode != 0 or not status.stdout.strip():
        return "clean"
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return "locked"
    try:
        if not git(REPOS_ROOT, "status", "--porcelain", "--", "journal").stdout.strip():
            return "clean"  # a racing caller just committed
        week = datetime.now().strftime("%G-W%V")
        git(REPOS_ROOT, "add", "--", "journal")
        r = git(REPOS_ROOT, "commit", "-q", "-m", f"journal: session stubs ({week})", "--", "journal")
        return "committed" if r.returncode == 0 else "clean"
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def push_ahead(root):
    """Reconcile one repo. Returns (name, outcome) or None if nothing to report.

    outcome ∈ {"pushed", "diverged", "failed: <reason>"}. Up-to-date and
    no-upstream repos return None.
    """
    name = os.path.relpath(root, REPOS_ROOT)
    if name == ".":
        name = "repos"
    counts = git(root, "rev-list", "--left-right", "--count", "@{u}...HEAD")
    if counts.returncode != 0:
        return None  # no upstream / detached / not a work tree
    try:
        behind, ahead = (int(x) for x in counts.stdout.split())
    except ValueError:
        return None
    if ahead == 0:
        return None  # up to date
    if behind > 0:
        return (name, "diverged")  # never force — report so it's visible
    try:
        r = git(root, "push", timeout=PUSH_TIMEOUT)
    except subprocess.TimeoutExpired:
        return (name, "failed: timeout (offline?)")
    if r.returncode == 0:
        return (name, "pushed")
    lines = [ln.strip() for ln in (r.stderr or r.stdout or "").splitlines() if ln.strip()]
    reason = next(
        (ln for ln in lines if any(k in ln.lower()
         for k in ("rejected", "fatal", "denied", "error", "failed"))),
        lines[0] if lines else "unknown",
    )
    return (name, f"failed: {reason[:120]}")


def log_run(session_id, journal_status, outcomes):
    """Append one summary line (+ detail lines for problems) and trim the log."""
    pushed = [n for n, o in outcomes if o == "pushed"]
    problems = [(n, o) for n, o in outcomes if o != "pushed"]
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = (
        f"{stamp} · session={session_id[:8] or '?'} · journal={journal_status} · "
        f"pushed: {', '.join(pushed) if pushed else 'none'}"
    )
    if problems:
        summary += f" · ATTENTION: {len(problems)}"
    lines = [summary + "\n"]
    for name, outcome in problems:
        lines.append(f"    ! {name}: {outcome}\n")
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.writelines(lines)
        existing = LOG_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
        if len(existing) > LOG_MAX_LINES:
            LOG_PATH.write_text("".join(existing[-LOG_MAX_LINES:]), encoding="utf-8")
    except OSError:
        pass


def notify_discord(problems):
    """Problem-only Discord alert via an incoming webhook. No-op unless a URL is
    configured in ~/.claude/.discord-webhook. Best-effort — never blocks/raises.
    Kept wired for future use; the in-session summary is the primary channel now."""
    if not problems:
        return
    try:
        url = WEBHOOK_PATH.read_text(encoding="utf-8").strip()
    except OSError:
        return
    if not url.startswith("https://"):
        return
    host = socket.gethostname().split(".")[0]
    detail = "\n".join(f"• `{name}`: {outcome}" for name, outcome in problems)
    content = f"⚠️ **repo-sync** on `{host}` needs attention:\n{detail}"
    data = json.dumps({"content": content[:1900]}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        # Discord sits behind Cloudflare, which 403s the default python-urllib UA.
        "User-Agent": "duri-repo-sync/1.0 (+workspace hook)",
    })
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass  # alert is best-effort; the log + stdout still have the record


def squash_merged(root, branch, base="main"):
    """True if `branch`'s whole diff is already in `base` as a squashed commit.

    `git branch --merged` walks ancestry, and a squash-merge creates a NEW commit
    with a new hash — the branch's own commits never become ancestors of main. So
    under this workspace's squash-merge rule (repos/docs/decisions/git-workflow.md)
    ancestry-based detection reports *nothing*, forever, which is exactly the
    "merged branches found months late by manual audit" failure the cleanup step
    was added to prevent. Measured 2026-08-04: duri-v3's `feat/raw-ingestions-seam`
    was squash-merged and the sweep reported zero merged branches.

    The test that does work: rebuild the branch's entire diff against its merge-base
    as ONE synthetic commit, then ask `git cherry` whether that patch is already in
    base. A squash commit has precisely that patch, so its patch-id matches and
    cherry marks it `-` (already upstream). This is content equality, not ancestry,
    which is the right question for a squash.

    Side effect, deliberate and harmless: `commit-tree` writes one dangling object
    into the repo's object store. It is unreachable and `git gc` prunes it; nothing
    references it and no ref moves. That is the cost of asking this question
    locally, without a network round-trip to the forge.
    """
    mb = git(root, "merge-base", base, branch)
    tree = git(root, "rev-parse", f"{branch}^{{tree}}")
    if mb.returncode != 0 or tree.returncode != 0:
        return False
    mb, tree = mb.stdout.strip(), tree.stdout.strip()
    if not mb or not tree:
        return False
    synth = git(root, "commit-tree", tree, "-p", mb, "-m", "squash-probe")
    if synth.returncode != 0 or not synth.stdout.strip():
        return False
    r = git(root, "cherry", base, synth.stdout.strip())
    # `-` = patch already upstream; `+` = not present.
    return r.returncode == 0 and r.stdout.strip().startswith("-")


def merged_branches(root):
    """Local branches fully landed in main — reported, never deleted.

    Cleanup belongs to session end rather than to an occasional audit: a stale branch
    is either unreclaimed work or noise that hides unreclaimed work, and it was the
    seven merged ones that kept a five-month-old unmerged branch invisible. Reporting
    is read-only on purpose — branch deletion stays on the ask-first list in the
    global AGENTS.md. See repos/docs/decisions/git-workflow.md.

    Two ways a branch can have landed, and both must be checked: ancestry (a real
    merge or fast-forward) and content (a squash — see squash_merged).
    """
    listed = git(root, "branch", "--format=%(refname:short)")
    if listed.returncode != 0:
        return []
    branches = [b for b in listed.stdout.split() if b != "main"]
    if not branches:
        return []

    ancestry = git(root, "branch", "--merged", "main", "--format=%(refname:short)")
    merged = {b for b in ancestry.stdout.split() if b != "main"} if ancestry.returncode == 0 else set()

    out = []
    for b in branches:
        if b in merged:
            out.append((b, "merged"))
        elif squash_merged(root, b):
            out.append((b, "squashed"))
    return out


def main():
    if not REPOS_ROOT.is_dir():
        print(f"repos-sync: no workspace at {REPOS_ROOT}")
        return 0
    journal_status = commit_journal()
    outcomes = []
    for repo in find_repos(REPOS_ROOT):
        try:
            result = push_ahead(repo)
        except subprocess.TimeoutExpired:
            result = (os.path.relpath(repo, REPOS_ROOT), "failed: timeout")
        if result:
            outcomes.append(result)

    session_id = os.environ.get("CLAUDE_SESSION_ID", "manual")
    log_run(session_id, journal_status, outcomes)
    problems = [(n, o) for n, o in outcomes if o != "pushed"]
    notify_discord(problems)

    pushed = [n for n, o in outcomes if o == "pushed"]
    print(f"repos-sync · journal={journal_status} · "
          f"pushed: {', '.join(pushed) if pushed else 'none'}")
    for name, outcome in problems:
        print(f"  ! {name}: {outcome}  (needs a manual look)")
    if not pushed and not problems:
        print("  everything already in sync.")

    stale = []
    for repo in find_repos(REPOS_ROOT):
        for branch, how in merged_branches(repo):
            stale.append((os.path.relpath(repo, REPOS_ROOT), branch, how))
    if stale:
        print(f"\ncleanup — {len(stale)} branch(es) fully landed in main:")
        for name, branch, how in stale:
            # Name the mechanism: a squashed branch needs `git branch -D`, because
            # `-d` refuses it — git still considers it unmerged by ancestry.
            note = "  (squash-merged — `-d` will refuse it, needs `-D`)" if how == "squashed" else ""
            print(f"  {name}: {branch}{note}")
        print("  (reported only — deleting is Han's call)")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
