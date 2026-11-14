# config — docs

This repository is public. Keep actual network identifiers, private repository
inventories and personalized operational records outside its tracked files.

## Status

**Phone → agent interaction** ([`decisions/phone-agent-interaction.md`](decisions/phone-agent-interaction.md))
— in use. herdr-core (`hc`) keeps terminals and agents alive on each machine. The Herdr app shows
them on the Mac, and the Herdr mobile app reaches each core over SSH. It replaced the Herdr TUI on
2026-11-13. Open: there is no notification CLI and no push to the phone; the secret web editor and
iOS input ergonomics are still open.

## Current configuration

- **[Claude settings](claude-settings.md):** public generic defaults, private
  regular runtime settings, and Stow-managed hooks. Existing local settings are
  preserved, not overwritten by setup. Other machines with an old settings
  symlink must detach it **before** pulling the sanitized template.
- **[New Mac](new-mac.md):** generic bootstrap guide. Actual machine roles,
  repository URLs, host mappings and migration details belong in private records.
- **[README](../README.md):** package layout and Stow usage.

The original personal records behind the public summaries below have been retained
verbatim in a private historical archive. Their old operational state is history,
not proof of the current setup or a new authorization grant.

## Public summaries

- [Agent-authored output](decisions/agent-authored-output.md)
- [Artifact-checking](decisions/artifact-checking.md)
- [Publishing permissions](decisions/chore-commit-carve-out.md)
- [Cross-harness instructions](decisions/codex-global-instructions.md)
- [New-Mac setup](decisions/new-mac-setup.md)
- [Supabase MCP](decisions/supabase-mcp.md)

## Other records

- [AGENTS.md is a prompt](decisions/agents-md-is-a-prompt.md)
- [Past decisions are not orders](decisions/past-decisions-are-not-orders.md)
- [Grill and decide skills](decisions/grill-and-decide-skills.md)
- [Phone → agent interaction](decisions/phone-agent-interaction.md)
- [Caveman assessment](decisions/caveman-assessment.md)
- [Session-start hooks](decisions/session-start-hooks.md)

These records are history. They do not mean the global instructions or skills they describe are
still managed by this repository.

## Reference

### Package-list caution

`brew bundle dump` reflects the extensions visible to the selected editor's CLI;
it can drop extension entries from the Brewfile. Review the diff before accepting
any regenerated package list. The Brewfile is the common core, not an exhaustive
inventory of every machine; do not run `brew bundle cleanup` against it.

### Agent tooling (workspace scaffolding)

- **`templates/`**: canonical `AGENTS.md.tmpl` + `CLAUDE.md.tmpl` for a new project repo, plus
  `docs-README.md.tmpl` + `decision.md.tmpl` for the standard `docs/` shape.
- **`scripts/new-repo.sh <dir>`**: scaffolds those templates into a new repo (filled with its
  name): `AGENTS.md`, `CLAUDE.md`, `docs/README.md`, `docs/decisions/TEMPLATE.md`. It skips files
  that already exist, then prints the steps to wire the repo into the workspace meta-repo.
