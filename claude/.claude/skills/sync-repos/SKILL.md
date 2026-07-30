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

## Cleanup — offer, don't delete
The run ends with a `cleanup — N branch(es) fully merged into main` section.
**Offer to delete them; never delete unasked** — branch deletion is on the
ask-first list in the global `AGENTS.md`. This step exists because merged
branches were previously only found by manual audit, months late, and the noise
they made is what hid a real unmerged branch. Han's framing: *"i usually end my
feature implementation sessions with a '… push and the cleanup …' I feel like
this should've been a part of that."*

A branch that is **not** merged is a different thing — it may be unreclaimed
work. Don't sweep it; surface it and let him decide, and if it's being dropped,
run `decide` so the reasoning exists somewhere other than a dangling branch.
Rationale: `~/workdir/repos/docs/decisions/git-workflow.md`.
