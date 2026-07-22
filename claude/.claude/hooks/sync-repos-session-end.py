#!/usr/bin/env python3
"""SessionEnd hook: commit accumulated journal lines, then push every
workspace repo that is ahead of its upstream.

The workspace (~/workdir/repos) is a meta-repo of independent git repos. Rather
than trying to detect which repo each commit touched (commits happen via inline
`cd`, so the tool cwd lies), this runs once at session end and reconciles state:

  1. If journal/ has uncommitted changes in the meta-repo, commit them
     (pathspec-scoped, so it can ONLY ever touch journal/ — never sweeps up
     unrelated in-progress work). Guarded by a lock so concurrent session-ends
     don't race the meta-repo index.
  2. Push every repo that is strictly ahead of its upstream and NOT diverged.
     Never force. Diverged / no-upstream / offline repos are skipped silently.

Composes with manual pushes: a repo you already pushed is no longer ahead, so
it's a no-op here. Fail-silent by design — a sync miss must never break a
session, and next session's sweep catches whatever was missed.
"""
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPOS_ROOT = Path.home() / "workdir" / "repos"
LOCK_PATH = Path.home() / ".claude" / ".journal-sync.lock"
PRUNE = {"node_modules", ".git", "archive", "dist", ".next", ".astro", "build", ".venv"}
MAX_DEPTH = 3
PUSH_TIMEOUT = 30


def git(root, *args, timeout=10):
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, timeout=timeout,
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

    Locked so two session-ends can't race the shared meta-repo index. Whoever
    loses the lock simply skips — their lines get committed by the winner or by
    the next session. Returns without raising on any failure.
    """
    status = git(REPOS_ROOT, "status", "--porcelain", "--", "journal")
    if status.returncode != 0 or not status.stdout.strip():
        return  # nothing pending under journal/
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock = open(LOCK_PATH, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return  # another session owns the journal commit right now
    try:
        # re-check under lock; a racing session may have just committed
        if not git(REPOS_ROOT, "status", "--porcelain", "--", "journal").stdout.strip():
            return
        week = datetime.now().strftime("%G-W%V")
        git(REPOS_ROOT, "add", "--", "journal")
        git(REPOS_ROOT, "commit", "-q", "-m", f"journal: session stubs ({week})", "--", "journal")
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()


def push_ahead(root):
    """Push `root` iff it has an upstream, is ahead, and is not diverged."""
    counts = git(root, "rev-list", "--left-right", "--count", "@{u}...HEAD")
    if counts.returncode != 0:
        return  # no upstream / detached / not a work tree
    try:
        behind, ahead = (int(x) for x in counts.stdout.split())
    except ValueError:
        return
    if ahead == 0 or behind > 0:
        return  # nothing to push, or diverged (never force) — skip silently
    try:
        git(root, "push", timeout=PUSH_TIMEOUT)
    except subprocess.TimeoutExpired:
        pass  # offline / slow remote — next sweep retries


def main():
    try:
        json.load(sys.stdin)  # drain payload; sweep needs no field from it
    except (json.JSONDecodeError, ValueError):
        pass
    if not REPOS_ROOT.is_dir():
        return
    commit_journal()
    for repo in find_repos(REPOS_ROOT):
        try:
            push_ahead(repo)
        except subprocess.TimeoutExpired:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never break a session over a sync
    sys.exit(0)
