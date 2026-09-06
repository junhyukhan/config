---
type: Decision
title: A past decision is not an order — surface the conflict, never conform silently
description: >-
  When a record or doc contradicts what Han is asking now, the agent must name the conflict and ask;
  his current instruction outranks every artifact, and silent conformity is the defect.
status: draft
tags: [agent-behaviour, decisions, authority, agents-md]
generated: { by: claude/opus-5, at: 2026-09-06T00:00:00Z }
---

# A past decision is not an order — surface the conflict, never conform silently

**Status:** DECIDED (2026-09-06), pending the `AGENTS.md` edit that carries it. Part of the
restructuring in [`repos/docs/decisions/workspace-lab-split.md`](../../../docs/decisions/workspace-lab-split.md).

## Why — the ask (verbatim)

> **Verbatim (2026-09-06):** "everytime i tell the agent i want to change things, it sees that i made
> contradictory decisions in the past, recorded within my workspace, and conforms to those past
> decisions."

## Discussion

**The failure is agency, not retrieval.** The problem is not that the agent finds Han's past
decisions — that is valuable, and it is what stopped `ops/state.db` being re-proposed. The problem is
that it *obeys* them, resolving a conflict that was his to resolve.

### The rule

When an artifact — a decision record, a spec, a doc, a comment — contradicts what Han is asking for
now:

1. **Say so.** Name the artifact, the date, and the reason it gave.
2. **Ask.** *"You decided X on <date> because R. You're asking for not-X — are you overturning it?"*
3. **Do what he says.** His current instruction is rank 0; see
   [`repos/docs/decisions/source-of-truth.md`](../../../docs/decisions/source-of-truth.md),
   Amendment 2026-09-06.
4. **Never split the difference**, and never quietly deliver the old decision while describing it as
   the new one.

**Do not consult records before deciding.** They are history. Read them when Han asks what he
decided, or when you have already hit a conflict — not as a gate on new work.

### Why prose and not a gate

There is no mechanical check for this; it is a disposition, like *"verify against the artifact, not a
summary of it"* ([`artifact-checking.md`](artifact-checking.md)). Both are prose in `AGENTS.md` for
the same reason: the failure is a judgment, and a judgment cannot be grepped for.

### Evidence it works

This rule was applied ad hoc at the start of the 2026-09-06 session — the agent stated up front that
it would treat records as history rather than authority for that conversation. The result was a
rethink rather than a defense of the status quo. **That is the whole demonstration, and it is also the
argument against relying on it:** it worked because it was typed that session, and Han will not type it
every session forever.

### The cost, stated plainly

Rework protection weakens. Anything not captured as a short inline constraint in `AGENTS.md` can be
re-proposed by an agent that never saw the record. The `ops/state.db` re-proposal is the named
precedent. Accepted: a wasted conversation is cheaper than being unable to change your own mind.

### Marked as mine

"The failure is agency, not retrieval" and the four-step protocol are my formulation. Han named the
symptom and chose the behaviour; the wording can be overruled.

## Related

- [`repos/docs/decisions/source-of-truth.md`](../../../docs/decisions/source-of-truth.md) —
  the authority ladders this adds rank 0 to.
- [`artifact-checking.md`](artifact-checking.md) — the other ungated disposition in `AGENTS.md`.
- [`repos/docs/decisions/workspace-lab-split.md`](../../../docs/decisions/workspace-lab-split.md)
  — the restructuring this is one decision inside.
