#!/usr/bin/env python3
"""SessionStart hook (read-only): surface workspace repos with unpushed commits so
the agent can offer to sync them.

This is the "trigger" half of the on-demand sync design: detection is automatic and
safe here (no network, no writes — it only compares each repo's HEAD to its
already-known upstream tracking ref), so it cannot hang or be killed the way the old
SessionEnd push hook could. The actual push is done explicitly by the /sync-repos
skill when the user agrees. Stdout is injected into the session context.

Fail-silent, fast. Prints nothing when everything is already pushed.
"""
import os
import subprocess
import sys
from pathlib import Path

REPOS_ROOT = Path.home() / "workdir" / "repos"
PRUNE = {"node_modules", ".git", "archive", "dist", ".next", ".astro", "build", ".venv"}
MAX_DEPTH = 3


def find_repos(root):
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


def ahead_count(root):
    """Unpushed commits vs the known upstream. No fetch — purely local, so fast and
    it can never block. Returns 0 for no-upstream / detached / errors."""
    r = subprocess.run(
        ["git", "-C", str(root), "rev-list", "--count", "@{u}..HEAD"],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=5,
    )
    if r.returncode != 0:
        return 0
    try:
        return int(r.stdout.strip())
    except ValueError:
        return 0


def main():
    if not REPOS_ROOT.is_dir():
        return
    ahead = []
    for repo in find_repos(REPOS_ROOT):
        try:
            n = ahead_count(repo)
        except subprocess.TimeoutExpired:
            continue
        if n > 0:
            name = os.path.relpath(repo, REPOS_ROOT)
            ahead.append(f"{'repos' if name == '.' else name} ({n})")
    if ahead:
        print(
            f"[repos-sync] Workspace repos with unpushed commits ahead of upstream: "
            f"{', '.join(ahead)}. Offer to run the /sync-repos skill to push them."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # a status notice must never break session start
    sys.exit(0)
