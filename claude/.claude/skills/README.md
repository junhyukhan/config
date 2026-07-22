# Global Claude skills (tracked)

Personal, machine-global Claude Code skills live here and are Stow-linked into
`~/.claude/skills/` (the `claude` package uses `stow -R --no-folding`, so each entry
is symlinked individually). Tracking them here means they're versioned and portable
across machines, same as `settings.json`, `commands/`, and `hooks/`.

**To add a skill:** create `~/workdir/repos/config/claude/.claude/skills/<name>/SKILL.md`,
then `cd ~/workdir/repos/config && stow -R --no-folding -t "$HOME" claude`.

Claude Code discovers skills by `*/SKILL.md`, so this top-level `README.md` is ignored
by skill discovery — it only documents the location.
