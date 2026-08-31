---
type: Decision
title: Artifact-checking — a disposition in AGENTS.md, with checks at the point of use
description: >-
  "Verify against the artifact, not a summary of it" stays a short rule in AGENTS.md, while the
  concrete hazards live at their point of use inside the `grill` and `decide` skills.
status: stable
tags: [config, agents-md, skills, verification, artifact-checking, grill, decide]
generated: { by: claude/opus-5, at: 2026-07-30T00:00:00Z }
---

# Artifact-checking — a disposition in `AGENTS.md`, with checks at the point of use

**Status:** DECIDED (2026-07-30) · provisional by agreement

Whether "verify against the artifact, not a summary of it" stays a behavioural rule, becomes a
skill, or both. Governs the rule in [`../../claude/.claude/AGENTS.md`](../../claude/.claude/AGENTS.md).

## Why — the ask (verbatim)

> **Verbatim (2026-07-30):** "Regarding artifact-checking, is your lean on keeping it as a
> behavioral rule rather than a skill - only because it is already like that? We're here to pick the
> 'right' one, not the convenient one."
>
> "Also tell me more about what this artifact checking is. And the subtle differences between a
> skill and a behavioral rule defined in AGENTS.md"

Closing it:

> **Verbatim (2026-07-30):** "Lets try with your recommendation. We'll come back to it if it doesnt
> work out."

## Discussion

The challenge landed. The original lean was defended with two reasons — "it is already a rule" (pure
status quo) and "a third home creates duplication." The second is refuted by this workspace's own
practice: `quant/.claude/skills/toss-api-facts` **is** a third home for the same principle, and it is
correct — the principle specialised to one API's failure modes. The duplication objection argued
against a pattern already in use and working.

### Rule and skill are different mechanisms

| | `AGENTS.md` rule | Skill |
|---|---|---|
| **In context** | always (global loads every session) | name + description only; body loads on invocation |
| **How it fires** | never invoked — ambient | invoked, by the user (`/name`) or by description match |
| **Composable** | no; nothing can call a rule | yes — one skill can call another |
| **Holds procedure** | poorly; declarative by nature | yes — steps, loops, stop rules, supporting files |
| **Cost of growth** | dilutes every other rule in the file | ~zero until invoked |
| **Failure mode** | loaded but not noticed | never invoked |

Compressed: **a rule is a disposition that is always loaded but never invoked; a skill is a
procedure that is invoked but not always loaded.**

That yields the test — **does the thing have an invocation point?** `grill` does (a fork appears).
`decide` does (a fork closes). Both are bounded: they start, run steps, finish.

Artifact-checking does not. Its trigger is *"whenever you are about to assert anything"* — a
continuous condition, not a boundary. And it fails in a specific way as a skill: the moment you would
need to invoke it is the moment you don't realise you need it. A lazily-loaded skill is absent from
context at exactly the instants it is required.

**So the structural reason is the invocation point, not the status quo.**

### The counterevidence, stated because it cuts the other way

The rule was loaded in context for the entire session that produced this record, and was violated
three times:

1. The claim that the secret-env guard was an unrecorded decision — asserted without checking a
   single timestamp. It predated the convention by three days.
2. The claim that the decision habit "only formed in repos created after the standard" — one
   `--diff-filter=A` query showed all four folders were created the same week.
3. `\b` used inside a pattern handed to `git grep`, producing a confident `0` where the true answer
   was 131. This is the *third* occurrence of that exact bug in this workspace's history and the
   second in one session.

*"It is the right form"* and *"it is working"* are different claims, and only the first is
defensible. The disposition form is demonstrably not sufficient alone.

### Decided

**Neither pure form.** The disposition stays in `AGENTS.md`, short. The specific, accumulating
hazards move to their **points of use** — concrete steps inside `grill` and `decide`, where a
procedure is already running:

- before recording that something was missed, date it against `git log`;
- never `\s`, `\b`, or `\d` in a pattern handed to `git grep` (POSIX ERE, BSD engine — it matches
  nothing rather than erroring); treat any empty result as suspect until cross-checked with a second
  engine;
- prefer the primary artifact to a summary of it;
- transcribe tables whole, or say which rows were taken.

This is the pattern `toss-api-facts` already follows, and the one `domain-modeling` follows by
keeping `ADR-FORMAT.md` beside a short body. **The principle is the invariant; the checks are
point-of-use.**

**Honest cost, accepted rather than argued away:** the hazard list now lives in two skill bodies plus
a rule — three places, which can drift. The trade is checks positioned where failures actually occur,
against a principle stated where it has already been proven insufficient. Han accepted this
provisionally (*"We'll come back to it if it doesnt work out"*), so **treat a recurrence of any hazard
above as the signal to revisit this record**, not as a one-off.

### What artifact-checking *is*, concretely

Five distinguishable moves, each observed failing or succeeding in the session that produced this
record:

- **Prefer the primary artifact to a summary.** A summarised read of `mattpocock/skills` described
  `grill-with-docs` as a substantial skill; the file is seven lines of composition. The summary was
  not wrong, it was *shaped* wrong.
- **Distrust an empty result.** A false `0` is indistinguishable from a true `0`, and is most
  convincing when it confirms the hypothesis.
- **Date any claim about what was missed.**
- **Check the stated belief against the history**, and surface contradictions.
- **Transcribe completely, or say what was taken.** A partial transcription formatted as complete is
  worse than none, because nobody re-checks it.

## Related records

- [`grill-and-decide-skills.md`](grill-and-decide-skills.md) — the two skills carrying the
  point-of-use checks
- [`repos/docs/decisions/decision-capture.md`](../../../docs/decisions/decision-capture.md)
