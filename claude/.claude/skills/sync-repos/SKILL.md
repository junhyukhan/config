---
name: sync-repos
description: Push every workspace repo under ~/workdir/repos that is ahead of its upstream (committing pending journal/ lines first). Use when asked to sync/push the repos, get the workspace "up to date" / "in sync", or when the SessionStart notice reports repos with unpushed commits.
---

# Sync workspace repos

`~/workdir/repos` is a meta-repo of independent git repos. This sweep commits any
pending `journal/` lines, then pushes **every** repo that is strictly ahead of its
upstream and not diverged. It is safe: never force-pushes, skips
diverged / no-upstream / offline repos (reports them instead), and never touches
uncommitted work.

This replaces the old SessionEnd push hook — running it in-session means you see
the result and nothing can silently die mid-run.

## Run it
```bash
python3 ~/.claude/skills/sync-repos/repos-sync.py
```

## Then report to the user
Relay the printed summary — which repos were pushed, and any `! <repo>: …` lines
(a failed push, or a **diverged** repo that needs a manual look; never force-push
to resolve it). The same summary is appended to `~/.claude/repo-sync.log`
(`tail ~/.claude/repo-sync.log` for history). Exit code is 1 if anything needs
attention, 0 otherwise.
