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

## Index

- **`decisions/`** — design decisions & specs, one file per topic, each a **verbatim ask +
  Discussion** (copy `decisions/TEMPLATE.md` to start one). The append-only record of *why*
  things are the way they are.
  - [`decisions/chore-commit-carve-out.md`](decisions/chore-commit-carve-out.md) — the narrow
    exception letting an agent commit and push without asking.
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

<!-- Add state singletons here as the repo grows — one file each, rewritten in place:
- **`roadmap.md`** — phases / what's planned
- **`scope.md`** — what's in and out
- **`data-model.md`** — schema reference
-->
