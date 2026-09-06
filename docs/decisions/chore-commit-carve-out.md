---
type: Decision
title: The `chore` carve-out to the no-commit rule
description: >-
  The one exception letting an agent commit to main unasked; all four conditions must hold —
  docs-only, verifier green, working tree otherwise clean, and obviously a chore.
status: stable
tags: [config, agents-md, git, autonomy, chore, commits]
generated: { by: claude/opus-5, at: 2026-07-29T00:00:00Z }
---

# The `chore` carve-out to the no-commit rule

**Status:** DECIDED (2026-07-29) · record relocated here 2026-07-30

The narrow exception that lets an agent commit and push without asking. Governs the standing rule in
[`../../claude/.claude/AGENTS.md`](../../claude/.claude/AGENTS.md).

> **Why this record lives in `config`.** It was originally written into
> `repos/docs/decisions/agent-ops.md`, because agent-ops was the work that motivated it. That is the
> wrong home under the routing rule settled on 2026-07-30: **a record lives in the repo that owns the
> artifact it governs**, and the artifact here is `config`'s own `AGENTS.md`. Someone reading that
> file and wondering why an agent may self-commit should find the answer in this repo, not in a
> sibling that doesn't travel with a clone. Rule and reasoning:
> [`repos/docs/decisions/decision-capture.md`](../../../docs/decisions/decision-capture.md).

## Why — the ask (verbatim)

Answering how the standing no-commit rule squares with unattended agent work:

> **Verbatim (2026-07-29):** "The recommended path. Except, for trivial, docs only, chore commits, i
> usually tell the agent to commit directly to main and push. For other feature based changes, i
> usually create docs, make and capture decisions, have the agent implement, create a pr, review,
> and merge."

## Discussion

### Amendment 2026-09-05 — the gate covers every outward action, and every agent

> **Verbatim (2026-09-05):** "you're right. merge, mr creation/deletion, commits, push, comments,etc
> by the pr review bot or any agent should ask for my confirmation."

Two widenings, both from watching dispatched sessions act:

**The list of actions.** The rule read "never commit or push". It now covers **merge, PR creation
and deletion, commits, push, and comments** — every action that leaves the working tree. The `chore`
carve-out below is unchanged and still the only exception; it is about *commits*, and does not
license any of the newly-named actions.

**Who it binds.** Previously it read as a rule for the session Han is talking to. It binds **any
agent** — dispatched sessions, review bots, anything spawned. This is the load-bearing half:
a dispatched session inherits Han's authenticated `gh`, so it can merge, comment or open a PR *as
him* without ever passing through the session he is watching.

Two things in this session prompted it, both agents acting on inference rather than instruction:

- A `repos/review` dispatch posted an 8.7k comment to PR #3. Han had written *"the review agent
  should also comment on the pr for future reference no?"* — **a question**, which the orchestrating
  session treated as authorization. A question mark is not a go.
- A `repos/implement` dispatch opened PR #4. That one was instructed, and matches Han's documented
  flow (*"have the agent implement, create a pr, review, and merge"*) — but under this amendment it
  needs his confirmation too.

**The tension worth naming:** Han's own description of normal feature work has the agent creating
the PR. That still holds — this does not stop agents opening PRs, it stops them doing so *unasked*.
"It was on the permission allowlist" was already not "it should have been run"; this extends the
same reasoning from allowlists to inference.

**In `AGENTS.md` 2026-09-06, still unenforced.**
[`../../claude/.claude/AGENTS.md`](../../claude/.claude/AGENTS.md) now names all five actions and
binds any agent, extending the existing rule rather than adding a second one; the edit is
uncommitted. `repos/ops/orchestrator.py`'s brief still carries the old wording and is a `repos/`
job. There is still no hook and no gate, matching this workspace's rule that a gate is added when an
incident produces it. Identity and attribution:
[`agent-authored-output.md`](agent-authored-output.md).


The global rule reads *"Never commit or push on my behalf unless I ask."* The `chore` task class in
the agent-ops design contradicts it outright, and any session reading that rule would correctly
refuse to run one. Left implicit, the contradiction would be resolved by whichever text an agent
happened to read first.

**Decided — write it as an explicit amendment, not an undocumented exception**, and scope it
narrowly enough that it cannot be stretched. A change is a `chore` only when *all* hold:

- **Docs-only, no behavior change** — prose, comments, links, formatting, regenerated `journal/`
  files. Not source; not config that changes runtime behavior.
- **The repo's verifier is green** (or there is nothing to verify).
- **The working tree was otherwise clean** — nothing unrelated gets swept in.
- **It is something Han would call a chore out loud** — typo, stale ref, dead link, regenerated
  output.

Everything else keeps the original rule verbatim. Still ask first for: any source-file change,
anything under `quant/` (real-money API, no sandbox), anything creating standing config or
automation, force-push, and branch deletion. `feature`-shaped work stops at branch + PR and waits
for review; it never merges itself.

**"When in doubt it is not a chore."** The narrowness is the point — *"this is basically docs"* is a
signal to ask, not to proceed.

### Why an amendment rather than an exception

Two reasons, both about the failure mode rather than the ergonomics. An undocumented exception is
invisible to a fresh session, so the rule would be silently violated or silently over-obeyed
depending on reading order. And the amendment is where the *scope* lives — an exception without
written boundaries widens on every judgment call, which is precisely what a real-money repo and a
force-push flag cannot tolerate.

## Related records

- [`repos/docs/decisions/agent-ops.md`](../../../docs/decisions/agent-ops.md) — the design that
  motivated the carve-out (cites this record; no longer contains it)
- [`repos/docs/decisions/decision-capture.md`](../../../docs/decisions/decision-capture.md) — the
  routing rule that moved this file here
- [`repos/docs/decisions/git-workflow.md`](../../../docs/decisions/git-workflow.md) — squash-merge
  and the session-end cleanup step, which this rule's `feature` path feeds
