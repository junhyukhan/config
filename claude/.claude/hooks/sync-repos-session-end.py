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
     Never force. Diverged / no-upstream / offline repos are skipped.

Composes with manual pushes: a repo you already pushed is no longer ahead, so
it's a no-op here. Fail-silent for the *session* (a sync miss must never break a
session), but NOT silent for you: every run appends one summary line (plus detail
lines for failures) to ~/.claude/repo-sync.log so you can always see whether it
ran and whether each push succeeded — `tail ~/.claude/repo-sync.log`.
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
LOG_PATH = Path.home() / ".claude" / "repo-sync.log"
LOG_MAX_LINES = 1000
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

    Returns: "committed" | "clean" | "locked". Locked so two session-ends can't
    race the shared meta-repo index; whoever loses simply skips (the winner or
    the next session commits their lines).
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
            return "clean"  # a racing session just committed
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
    no-upstream repos return None (not worth a log line).
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


def main():
    session_id = ""
    try:
        session_id = (json.load(sys.stdin) or {}).get("session_id", "")
    except (json.JSONDecodeError, ValueError):
        pass
    if not REPOS_ROOT.is_dir():
        return
    journal_status = commit_journal()
    outcomes = []
    for repo in find_repos(REPOS_ROOT):
        try:
            result = push_ahead(repo)
        except subprocess.TimeoutExpired:
            result = (os.path.relpath(repo, REPOS_ROOT), "failed: timeout")
        if result:
            outcomes.append(result)
    log_run(session_id, journal_status, outcomes)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never break a session over a sync
    sys.exit(0)
