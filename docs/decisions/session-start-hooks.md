---
type: Decision
title: SessionStart hooks — what they may do, and what watches them
description: >-
  SessionStart hooks stay read-only, fail-silent and quiet-when-nothing-to-say; the checker now
  guards their registration in `settings.json`, which nothing watched before.
status: stable
tags: [config, claude, hooks, session-start, agent-ops]
generated: { by: claude/opus-5, at: 2026-09-01T00:00:00Z }
---

# SessionStart hooks — what they may do, and what watches them

**Status:** DECIDED (2026-09-01). Written because the records-owed check began flagging changes to
these files and was right to.

## Why — the ask (verbatim)

No single ask created this. It is the standing shape of two features Han approved separately —
the unpushed-repos notice (`docs/decisions/…` in `repos`, `journal-and-sync.md`) and the
checker-liveness line (`repos/docs/decisions/cross-repo-retrieval.md`, Step 2) — plus this, on
widening what the checker watches:

> **Verbatim (Han, 2026-09-01):** "fix 3 and 5."

## Discussion

### The contract these hooks hold themselves to

A `SessionStart` hook runs before the user has typed anything, on every session, with its stdout
injected into context. That makes three properties non-negotiable:

- **Read-only.** No writes, no network, no `git fetch`. `repos-ahead-notice.py` compares each repo's
  HEAD to its *already-known* upstream ref, which is why it cannot hang the way the retired
  SessionEnd push hook could.
- **Fail-silent.** A hook that throws must not break session start. There is a blanket handler for
  that — but see below, it is not a licence to be careless.
- **Quiet when there is nothing to say.** A hook that prints on every session is a hook that gets
  ignored on every session.

### Fail-silent is a floor, not a design

The blanket `except Exception: pass` made a real bug invisible on 2026-08-31: `checker_age_days()`
put its subtraction outside the `try`, so a naive timestamp raised `TypeError` past a hand-guessed
except tuple, aborted `main()` **before the repo scan**, and was swallowed. The unpushed-repos
notice — the hook's original and unrelated job — went silent permanently, and nothing indicated it.

**So: a new code path added to one of these hooks must be independently safe, not merely wrapped.**
The outer handler exists for the unforeseeable, and treating it as coverage for the foreseeable is
how one feature silently deletes another.

### What now watches these files

Nothing did, which is why this record exists. Two additions in `repos/ops/index.py`:

- **`GOVERNED_PATHS`** — records-owed matched `GOVERNED` *basenames* only, so a live hook or
  `settings.json` could change with no record and no flag. It now also matches a short list of
  explicit paths. Deliberately a list, not a wider rule: adding `settings.json` or `*.py` to
  `GOVERNED` would flag every routine edit and recreate the flat cross-repo board that was measured,
  found misleading, and retired.
- **`GUARDED_CONFIG` rows** — a hook is registered inside `settings.json` **by name**. Delete the
  registration and the hook file sits on disk looking healthy while never running again. That is the
  purest form of the silent absence that table exists for, so `guard-secret-env.py` and
  `repos-ahead-notice.py` are now guarded by registration *and* by file existence.

The secret-env guard is the one that matters most: unregistered, the only mechanical backstop on
reading `.env` files is gone, and nothing else in the workspace would say so.

### Not covered

`aa6b24e` (enabling voice) is also flagged by records-owed and does **not** get a record — it is a
user preference toggle with no standing consequence. The check is explicitly *"a review queue, not
a defect list"*, and the correct outcome for some entries is to skim and dismiss them.

## Related records

- [`supabase-mcp.md`](supabase-mcp.md) — the incident that created `GUARDED_CONFIG`
- [`grill-and-decide-skills.md`](grill-and-decide-skills.md) — the other agent-config surface here
