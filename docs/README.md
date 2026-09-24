# config — docs

**Read this first.** The current state of config, plus an index of everything under `docs/`.

## Status — resume here

<!-- What's true right now, and what to pick up next. This is *state*: rewrite it in place,
     don't append history (history lives in decisions/). -->

**Phone → agent interaction** ([`decisions/phone-agent-interaction.md`](decisions/phone-agent-interaction.md))
— in progress. The hand-rolled session launcher is **superseded**: Herdr (`herdrdev/herdr`, Rust,
Apache-2.0, verified binary) covers session persistence, multi-harness, native attach, and the
working/blocked/idle signal tmux can't give. **Next: trial Herdr on the Mac.** The tmux prefix change
is parked until that lands; the secret web editor and iOS input ergonomics are independent and still
open.

The `claude/` stow package now carries two workflow skills — `grill` and `decide` — alongside
`sync-repos`. `sync-repos` also reports merged branches at the end of a run (reports only; deleting
stays Han's call).

**New 2026-08-29 — the `codex` stow package** ([`decisions/codex-global-instructions.md`](decisions/codex-global-instructions.md)).
`~/.codex/AGENTS.md` was an untracked real file whose `@AGENTS.md` pointed at itself, so 41 Codex
sessions very likely ran with **no global instructions at all**. It is now a symlink to
`claude/.claude/AGENTS.md` — one canonical file, both harnesses. **Outstanding: confirm by launching
Codex once.** Skills remain Claude-only.

**New 2026-09-06 — the publishing rules are in `claude/.claude/AGENTS.md`.** The confirmation gate
([`decisions/chore-commit-carve-out.md`](decisions/chore-commit-carve-out.md)) now names merge, PR
create/delete, commit, push and comment, and binds any agent; identity, attribution and writing style
([`decisions/agent-authored-output.md`](decisions/agent-authored-output.md)) are a new `## What you
publish` section. **Outstanding:** the edit is uncommitted and pending Han's review, what a comment's
attribution should say is still undecided, and `repos/ops/orchestrator.py`'s dispatch brief still
carries the old "never commit or push" wording.

## Index

- **[`new-mac.md`](new-mac.md)** — setting up a new Mac: what `setup.sh` does, what it can't, and the
  order to do the rest in. Why: [`decisions/new-mac-setup.md`](decisions/new-mac-setup.md).

- **`decisions/`** — design decisions & specs, one file per topic, each a **verbatim ask +
  Discussion** (copy `decisions/TEMPLATE.md` to start one). The append-only record of *why*
  things are the way they are.
  - [`decisions/chore-commit-carve-out.md`](decisions/chore-commit-carve-out.md) — the narrow
    exception letting an agent commit and push without asking; amended 2026-09-05 so the rule
    covers merge, PR create/delete and comments, and binds every agent rather than one session.
  - [`decisions/agent-authored-output.md`](decisions/agent-authored-output.md) — agents publish
    under Han's own GitHub identity, must attribute what he did not write, and write by linking
    rather than restating.
  - [`decisions/agents-md-is-a-prompt.md`](decisions/agents-md-is-a-prompt.md) — AGENTS.md is
    unenforced text loaded every session, so a rule gets one line and its reasoning goes in a record.
  - [`decisions/past-decisions-are-not-orders.md`](decisions/past-decisions-are-not-orders.md) — a
    record that contradicts what Han is asking now must be **named and asked about**, never silently
    obeyed. His current instruction is rank 0; records are history.
  - [`decisions/artifact-checking.md`](decisions/artifact-checking.md) — why "verify against the
    artifact" stays a disposition in `AGENTS.md`, with concrete checks at their points of use.
  - [`decisions/grill-and-decide-skills.md`](decisions/grill-and-decide-skills.md) — what was
    absorbed from `mattpocock/skills`, what was left, and why it became two skills.
  - [`decisions/phone-agent-interaction.md`](decisions/phone-agent-interaction.md) — using the
    iPhone as a real control surface: why SSH+tmux is the right door, the launcher design and why
    **Herdr supersedes it**, where chat belongs (low-bandwidth only), and the secret web editor.
  - [`decisions/supabase-mcp.md`](decisions/supabase-mcp.md) — project-pinned Supabase MCP: what
    `--read-only` enforced, why the token lives in `.zshrc` not `.mcp.json`, and **D4 (2026-08-06):
    the flag goes back on and the CLI becomes the write path** — the two tools split by direction
    (CLI writes, from reviewed migration files; MCP reads, arbitrary), superseding D3's removal.
  - [`decisions/codex-global-instructions.md`](decisions/codex-global-instructions.md) — Codex was
    reading a self-referential `@AGENTS.md` and loading no global rules across 41 sessions; the
    `codex` stow package symlinks it to the one canonical file. **Unverified until Codex is run.**
  - [`decisions/caveman-assessment.md`](decisions/caveman-assessment.md) — what was taken from
    `juliusbrussee/caveman` (its compression rules and, above all, the pattern of gating a prose
    rewrite with a deterministic validator) and what was left (the response-style skill: ~1–1.5k
    input tokens per turn, net-negative on terse coding Q&A). Its headline **"65% (measured)" is
    unsupported** — `benchmarks/results/` is empty and the repo's own `HONEST-NUMBERS.md` says so.

<!-- Add state singletons here as the repo grows — one file each, rewritten in place:
- **`roadmap.md`** — phases / what's planned
- **`scope.md`** — what's in and out
- **`data-model.md`** — schema reference
-->

## Reference

Moved here verbatim from `AGENTS.md` on 2026-09-23 to keep that file under its word budget
(`repos/docs/decisions/docs-budget-refactor.md`).

**`brew bundle dump` rewrites `vscode` entries from live state, so it can delete them.** It emits
exactly what `code --list-extensions` reports. VS Code currently has **none** — the extensions in
daily use are in **Cursor**, and Homebrew Bundle has no directive for Cursor, so `brew bundle`
cannot capture or restore them. A dump therefore wipes the `vscode` block. Always verify a re-dump
with a set comparison rather than eyeballing the diff:

```bash
comm -23 <(git show HEAD:mac/Brewfile | grep -E '^(tap|brew|cask|vscode|go|npm) ' | sort) \
         <(grep -E '^(tap|brew|cask|vscode|go|npm) ' mac/Brewfile | sort)
```

Anything it prints was dropped.

### Agent tooling (workspace scaffolding)

Beyond dotfiles, this repo carries tooling for the `~/workdir/repos` agent workflow:

- **`templates/`** — canonical `AGENTS.md.tmpl` + `CLAUDE.md.tmpl` for a new project repo,
  plus `docs-README.md.tmpl` + `decision.md.tmpl` for the standard `docs/` shape.
- **`scripts/new-repo.sh <dir>`** — scaffolds those templates into a new repo (filled with
  its name): `AGENTS.md`, `CLAUDE.md`, `docs/README.md`, `docs/decisions/TEMPLATE.md`. It
  skips files that already exist, then prints the steps to wire the repo into the workspace
  meta-repo (`repos/.gitignore` line + `repos/AGENTS.md` table row). Keeps every new project
  on the standard agent-context shape.
- **`claude/.claude/skills/`** — the versioned home for personal global Claude skills
  (see its `README.md`).
