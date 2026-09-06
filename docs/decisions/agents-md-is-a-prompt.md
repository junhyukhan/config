---
type: Decision
title: AGENTS.md is a prompt, not a contract — keep it minimal
description: >-
  The global AGENTS.md is unenforced text loaded every session, so length costs attention and buys
  nothing; rules go in one line and the reasoning goes in a record. Handwritten and short.
status: stable
tags: [agents-md, context, instructions, brevity]
generated: { by: claude/opus-5, at: 2026-09-06T00:00:00Z }
---

# AGENTS.md is a prompt, not a contract — keep it minimal

**Status:** DECIDED (2026-09-06).

## Why — the ask (verbatim)

> **Verbatim (2026-09-06, on cutting a 21-line section to 11):** "Yes i dont want the agent md to
> hold unnecessary info. The file is already not an enforced rule for the agent. Having it very long
> with verbose writing will not help. (In fact the anthropic guides say we should handwrite claude md
> amd keep it minimal)"

> **Verbatim (2026-09-06, two PR comments that made the same point first):** "Do we need this comment
> here?" / "Is this necessary?"

## Discussion

**Nothing enforces this file.** It is text prepended to a prompt. A rule in it is followed because
the model reads and weights it, not because anything checks. So every extra line competes for
attention with the lines that matter — length is a *cost* against the file's own purpose, not a
thoroughness signal.

**The rule:** a constraint gets one line. Its reasoning goes in a decision record and is reachable
by link. Do not write the argument into the instruction file — a rule nobody is arguing with does
not need a defence, and one that does need a defence is not settled enough to be a rule.

**Outside support, since Han cited it.** Anthropic's context-engineering guidance is to keep these
files short, handwritten, and just-in-time rather than exhaustive. Independently: a survey of 466
`AGENTS.md` files puts the mean at 142 lines against 287 for `CLAUDE.md`, and reports that files
treated as living documents — edited ten or more times — correlate with the highest satisfaction,
while half are never touched after creation. The measured failure mode is adding "just in case"
instructions to stabilise behaviour, which degrades it.

**What this replaced.** The section this rule was applied to carried a verbatim quote of Han and a
paragraph justifying its accepted cost — 21 lines for an instruction that fits in 11. Both were
already in the record one link away.

**Scope.** Written about the global `config/claude/.claude/AGENTS.md`, which every session and every
harness loads. It applies to any `AGENTS.md`; `repos/AGENTS.md` went 248 → 46 lines the same day
(`repos/docs/decisions/workspace-lab-split.md`).

**Not gated.** No check counts lines, deliberately — a length limit would be the same mistake in the
other direction. This is a disposition, like the rest of that file.
