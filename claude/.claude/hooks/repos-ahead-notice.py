#!/usr/bin/env python3
"""SessionStart hook (read-only): surface workspace repos with unpushed commits, and
say how long it has been since the workspace checker last ran.

This is the "trigger" half of the on-demand sync design: detection is automatic and
safe here (no network, no writes — it only compares each repo's HEAD to its
already-known upstream tracking ref), so it cannot hang or be killed the way the old
SessionEnd push hook could. The actual push is done explicitly by the /sync-repos
skill when the user agrees. Stdout is injected into the session context.

The liveness half is Step 2 of `repos/docs/decisions/cross-repo-retrieval.md`. A
checker nobody runs is worse than no checker: every "no findings" it printed weeks ago
still reads as reassurance. `ops/index.py` now reports its own last-run age at the top
of its output, but that only helps someone already running it — so the age is surfaced
here too, where a session sees it without asking.

Fail-silent, fast. Prints nothing when everything is pushed and the checker is fresh.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPOS_ROOT = Path.home() / "workdir" / "repos"

# Read straight from the checker's own state file rather than a second timestamp of
# our own: one source, and it cannot disagree with what `ops/index.py` prints.
SEEN_PATH = REPOS_ROOT / "ops" / "seen.json"
STALE_DAYS = 7
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


def checker_age_days():
    """Whole days since `ops/index.py` last completed a written run, or None.

    Catches broadly and on purpose. The subtraction used to sit OUTSIDE the try, and
    the tuple was written by guessing at failure modes rather than tracing them, so a
    naive `updated` — or an int, a null, or a top-level list — raised TypeError past
    the handler. This function is called before the repo scan, so that did not
    degrade to "no age": it aborted main(), and the blanket handler at the bottom
    swallowed it. One missing `+00:00` and the unpushed-repos notice, which is the
    hook's original job, went silent forever.

    seen.json is gitignored, per-machine, deliberately human-readable, and documented
    as safe to delete by hand — so assume it will be hand-edited into odd shapes.
    """
    try:
        raw = json.loads(SEEN_PATH.read_text())
        when = datetime.fromisoformat(raw["updated"])
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - when).days
    except Exception:
        return None


def main():
    if not REPOS_ROOT.is_dir():
        return

    age = checker_age_days()
    if age is None:
        print("[repos-ops] Workspace checker has no recorded run. "
              "`python3 ops/index.py` reports drift, dead links, stale content and "
              "records owed.")
    elif age >= STALE_DAYS:
        print(f"[repos-ops] Workspace checker last ran {age} days ago — its last "
              f"clean bill of health is that old. Offer to run `python3 ops/index.py`.")

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
