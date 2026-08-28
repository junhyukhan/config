---
type: Decision
title: Codex was running with no global instructions — one canonical AGENTS.md, symlinked
description: ~/.codex/AGENTS.md was an untracked real file containing a self-referential "@AGENTS.md",
  so 41 Codex sessions very likely loaded none of the global rules; fixed 2026-08-29 with a `codex`
  stow package whose AGENTS.md is a symlink to claude/.claude/AGENTS.md. Verified resolving, NOT yet
  verified by an actual Codex run.
status: stable
tags: [config, stow, codex, claude-code, agent-ops, cross-harness]
generated: { by: claude/opus-5, at: 2026-08-29T04:24:00Z }
---

# Codex was running with no global instructions — one canonical AGENTS.md, symlinked

**Status:** fixed 2026-08-29. **One step outstanding:** confirm by launching Codex — see *Open*.

Governs `codex/.codex/AGENTS.md`, `.gitignore`, `setup.sh`, and the `verify:` line in
[`../../AGENTS.md`](../../AGENTS.md).

## Why — the ask (verbatim)

> **Verbatim (2026-08-24, on multi-harness — correcting the assistant's premise, carried from
> `../../../docs/decisions/cross-repo-retrieval.md`):** "As for the other harnesses, yes im only
> using claude code right now but i am planning to use other harnesses. So this current state is
> not an argument for skipping. In fact this is one of the big reasons im doing this
> refactor/restructure"

> **Verbatim (2026-08-24, on skills reaching other harnesses):** "Regarding skills, but codex is
> able to use skills. It just gotta be in a place where it could reach"

> **Verbatim (2026-08-29, approving the fix as part of the session plan):** "looks good"

## Discussion

### The defect

Found during the 2026-08-28 workspace reconnaissance. `~/.codex/AGENTS.md` was a **344-byte regular
file — not a symlink, not tracked by any stow package** — whose entire content was:

```
@AGENTS.md

<!--
Intentionally thin. AGENTS.md holds the canonical global instructions so every
coding agent can read the same file. Codex reads this AGENTS.md and resolves
the import; when a second agent is adopted, add a stow package symlinking its
global path (e.g. ~/.codex/AGENTS.md) to this same AGENTS.md. Codex-only notes below.
-->
```

**The file describes the fix that was never applied.** `find config -iname '*codex*'` returned
nothing: no stow package existed.

**Why it almost certainly loaded nothing.** The Claude side works because `~/.claude/CLAUDE.md` is a
*symlink* into `config/claude/.claude/`, so its `@AGENTS.md` resolves against the link target's
directory, where `AGENTS.md` exists. The Codex file was a **real file at `~/.codex/`**, so
`@AGENTS.md` resolves relative to `~/.codex/` — **to itself**. Even granting that Codex supports
`@`-imports at all (unverified), a self-import yields nothing.

**Scale of the exposure:** `~/.codex/sessions/` held **41 sessions**, `config.toml` was modified the
same day (2026-08-28 09:30), and `~/.codex/rules/default.rules` contains a prefix rule naming
`build/progress.md` — so Codex had been used, on duri-v3. Those sessions ran without the secrets
rule, the verbatim-capture rule, the chore carve-out, the never-commit-unasked rule, and the
`quant` real-money constraint.

`~/.codex/memories_1.sqlite` had **0 rows** in both `jobs` and `stage1_outputs`. No memory either.

### The fix — a symlink, not a copy, not an import

`config/codex/.codex/AGENTS.md` is a **relative symlink** to `../../claude/.claude/AGENTS.md`.
Stow links `~/.codex/AGENTS.md` → the package file → the canonical file. Verified resolving to
`/Users/junhyukhan/workdir/repos/config/claude/.claude/AGENTS.md`.

**Why a symlink rather than an `@`-import:** whether Codex supports `@`-imports is **UNKNOWN**, and
the existing broken file was built on assuming it does. A symlink is a plain file read — it works
under any harness that opens the path at all, so it removes the unknown rather than betting on it.

**Why not a copy:** two files, one canonical rule set, guaranteed drift. The whole defect being
fixed is that a harness read something other than the canonical file.

**`--no-folding`, for the `claude` reason but stronger.** `~/.codex` holds `sessions/`, three SQLite
databases with WAL sidecars, `logs`, caches, and plugins. Folding would drag all of it into this
repo. `.gitignore` mirrors the `claude` pattern: ignore `codex/.codex/*`, whitelist only `AGENTS.md`.

### Rejected

- **Leave it and add Codex-specific instructions.** Rejected: the goal is one rule set across
  harnesses (Han, 2026-08-24). Harness-specific notes go *below* the shared content in that
  harness's own file, not into a second canonical source.
- **Copy `AGENTS.md` into the codex package.** Rejected on drift, above.
- **`.agents/skills/` as the cross-harness convention** (`cross-repo-retrieval.md` correction 1,
  2026-08-25). Still unimplemented and **out of scope here** — this record fixes *instructions*, not
  *skills*. Codex still cannot reach `grill`, `decide`, or `sync-repos`.

### Gate

| Rule | Gate |
|---|---|
| The codex package stays stowed and resolvable | `verify:` in `../../AGENTS.md` now includes `codex` in the `stow -n -R --no-folding` dry run |
| `AGENTS.md` stays a symlink, never a copy | ⚠️ **prose — no gate.** A copy would still pass the stow dry run |
| Codex actually loads it | ⚠️ **unverified — see Open** |

## Open

- **Confirm by launching Codex.** The symlink resolves and the content is correct, but *nothing in
  this workspace can prove Codex reads `~/.codex/AGENTS.md`* — that needs one real session. **Do not
  treat cross-harness instruction parity as done until it has been run.** If Codex ignores the path,
  the fix is wrong and the real question — how Codex takes global instructions — is still open.
- **Skills remain Claude-only.** `~/.codex/skills/` holds six vendor skills and none of Han's.
- **Codex has no memory** (`memories_1.sqlite`, 0 rows) and no equivalent of Claude's auto-memory.
  Not addressed here.

## Related

- [`../../../docs/decisions/cross-repo-retrieval.md`](../../../docs/decisions/cross-repo-retrieval.md)
  — the multi-harness verbatim asks and the `.agents/skills/` correction.
- [`phone-agent-interaction.md`](phone-agent-interaction.md) — Remote Control is Claude-only, which
  is the standing case for a multiplexer.
