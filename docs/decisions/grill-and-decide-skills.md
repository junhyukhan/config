---
type: Decision
title: "`grill` and `decide` — two skills absorbed from mattpocock/skills"
description: >-
  Three ideas were absorbed from mattpocock/skills and rewritten as the local `grill` and
  `decide`; the library was deliberately NOT cloned into the workspace and NOT installed as a
  plugin.
status: stable
tags: [config, skills, grill, decide, claude-code, external]
generated: { by: claude/opus-5, at: 2026-07-30T00:00:00Z }
---

# `grill` and `decide` — two skills absorbed from `mattpocock/skills`

**Status:** DECIDED (2026-07-30)

What was taken from an external skills library, what was left, and why it became two skills rather
than one. Governs [`../../claude/.claude/skills/`](../../claude/.claude/skills/).

## Why — the ask (verbatim)

> **Verbatim (2026-07-30):** "i don't want to use these skills blindly, use the ones that make sense
> for me, and build on top of them. i can clone this repo (mattpocock/skills) in my worskpace if
> that is better (there are a lot of skills in this repo)"

Settling the clone question:

> **Verbatim (2026-07-30):** "yes, i want 2-3 ideas absorbed into my own skills, i do not want to
> clone or use mattpocck-skills (i just mentioned cloning cause i assumed that would be easier for
> you to analyze)."

## Discussion

### The library, read directly

MIT, 41 skills, ~6,000 lines of markdown: `engineering/` (17), `productivity/` (5), `in-progress/`
(9), `misc/` (4), `personal/` (2), `deprecated/` (4). Cloned to a scratch directory and read as
files — a summarised read had mis-shaped one of the two skills Han named, describing
`grill-with-docs` as a substantial skill when it is seven lines whose entire body is
`Run a /grilling session, using the /domain-modeling skill.`

**Not cloned into the workspace, and not installed as a plugin.** `repos/` is defined as Han's own
projects, each an independent repo with its own remote; a read-only upstream mirror breaks that
invariant and would surface on the board, in the journal sweep, and in `sync-repos` as a repo
perpetually neither ahead nor his.

### What was taken

Judged against what the session itself demonstrated, not against the catalogue.

1. **The grilling loop** — one question at a time, dependency-ordered, a recommended answer with
   each, *facts looked up rather than asked*, nothing acted on until confirmed. Its value was
   concrete and immediate: it is what surfaced an unfair example for Han to catch, instead of that
   error propagating into a decision record.
2. **Composition — the record gets written as part of the session.** `grill-with-docs`' actual
   insight, and the answer to the trigger question in
   [`repos/docs/decisions/decision-capture.md`](../../../docs/decisions/decision-capture.md).
3. **Cross-reference against the artifact** — folded in as point-of-use checks rather than a third
   skill; see [`artifact-checking.md`](artifact-checking.md).

### What was left, and why

- `triage`, `to-tickets`, `wayfinder`, `improve-codebase-architecture` — all assume GitHub Issues as
  the tracker (`setup-matt-pocock-skills` exists to wire one up). This workspace tracks work in
  markdown inside repos.
- `tdd`, `implement`, `code-review` — overlap the per-repo `check` skills and the `pr-review-toolkit`
  plugin already in use.
- `domain-modeling`'s ADR shape — its `CONTEXT.md` + `docs/adr/` structure would fork the existing
  `docs/decisions/` convention, which is *stricter and better suited* here because it preserves Han's
  own words. Its three-part admission test was considered separately and rejected; see
  `decision-capture.md`.
- `misc/`, `personal/`, `deprecated/` — not applicable.

The glossary half of `domain-modeling` is a genuine gap — there is no `CONTEXT.md`, `glossary*`, or
equivalent anywhere in the workspace — but it is a new practice to start rather than a hole to patch,
and was left out of this change deliberately.

### Two skills, not one

The deciding argument is Han's own standing rule, which observes that the perishable material is
usually *"a one-line course-correction I drop during implementation"* — not a grilling session.

**If record-writing exists only inside `grill`, every mid-build steer leaks** — which is exactly the
hole the trigger decision was closing. So `decide` must be invocable on its own.

It is also what makes the deterministic backstop coherent: the checker asks *"a governed artifact
changed — did a record get written?"*, and that question needs an answer that does not presuppose a
full session took place.

- **Rejected — one `/grill` skill** doing loop, record-writing, and artifact-checking together.
  Record-writing would be unreachable except through a full session.
- **Rejected — three skills**, with artifact-checking standalone. See
  [`artifact-checking.md`](artifact-checking.md): it has no invocation point.

**Cost of two over one, accepted:** two skills to keep aligned, and a composition seam where `grill`
hands off to `decide`.

**Home:** `config/claude/.claude/skills/`, alongside `sync-repos` — versioned, Stow-linked, portable
across machines. Not per-repo, because these apply everywhere.

## Related records

- [`artifact-checking.md`](artifact-checking.md) — why the third idea became checks rather than a skill
- [`repos/docs/decisions/decision-capture.md`](../../../docs/decisions/decision-capture.md) — the
  routing rule `decide` implements
