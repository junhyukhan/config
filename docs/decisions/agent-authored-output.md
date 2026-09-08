---
type: Decision
title: What an agent publishes — identity, attribution, and how it reads
description: >-
  Agents post under Han's own GitHub identity (subscription, not API billing) and must attribute
  what he did not write; artifacts link rather than restate, lead with the conclusion, use plainer
  sentences.
status: stable
tags: [config, agents-md, attribution, identity, writing, github, orchestrator]
generated: { by: claude/opus-5, at: 2026-09-05T07:30:00Z }
---

# What an agent publishes — identity, attribution, and how it reads

**Status:** DECIDED (2026-09-05) · wired into
[`../../claude/.claude/AGENTS.md`](../../claude/.claude/AGENTS.md) 2026-09-06, uncommitted and
pending Han's review. `repos/ops/orchestrator.py`'s brief still does not carry it.

## Why — the ask (verbatim)

> **Verbatim (2026-09-05, on identity and attribution):** "hmm i use a claude subscription. so i
> should probably stick to letting the agent use my identity for commenting. if i don't want
> separate api charges.
> attribution should be done for every commit that I don't write myself. (we already have a co
> authored by message for the commits so that's fine.) the comments should have some kind of
> attribution as well."

> **Verbatim (2026-09-05, on style):** "btw the description/comments/commit messages are a bit too
> verbose and hard to understand for my liking. are there ways to improve this? (i want to search
> for options. do not change anything yet - this goes for most things i ask you. i dont want you to
> change anything prematurely on my behalf)"

> **Verbatim (2026-09-05, choosing among the four options offered):** "let's go with 1, 2, 4."

> **Verbatim (2026-09-05, the question that started it):** "btw, who posted the comment?"

## Discussion

### Amendment 2026-09-08 — the comment footer, settled

**The open item below is closed.** A dispatched review session reviewing PR #51 hit exactly the
gap this record named: it had findings ready, refused to invent a footer because this record told
it not to, and stopped to ask. That is the rule working, and it is also the second time the
question has blocked real work — so it is answered rather than deferred again.

> **Verbatim (Han, 2026-09-08):** "Review - what are the options for comment attribution?" …
> "Yup your recs are good for both"

Four options were put to him: a footer mirroring the commit convention; a short inline prefix; a
one-line footer with no link; or not posting to GitHub at all and keeping findings in a repo record
he cites himself. He took the first, with the addition below.

**The format:**

```
🤖 Review by Claude Opus 5 — dispatched review session, independent of the session that wrote this PR — via [Claude Code](https://claude.com/claude-code)
https://claude.ai/code/session_<id>
```

**Why a footer and not a prefix.** Commits already end with `Co-Authored-By` plus `Claude-Session`.
One attribution idiom across commits, PR bodies and comments means a reader learns it once, and a
script looking for agent-authored output has one shape to match rather than three.

**The load-bearing addition is "independent of the session that wrote this PR", and it is not a
disclaimer.** It is the most useful fact in the footer: it distinguishes a review from an author
marking their own homework. On PR #51 that distinction was the entire point of dispatching a
separate session, and without it the comment reads as the author agreeing with themselves. Where a
comment is *not* from an independent session, that clause must be dropped rather than reused — it
is a claim, and a false one would be worse than no footer.

**Each session uses its own session URL, or omits the line.** Reusing another session's link is a
wrong provenance pointer, which is worse than an absent one — the whole reason the link is there is
that a reader can reach the transcript that produced the text.

**Not settled here:** whether a comment an agent posts on Han's behalf that is *not* review output —
a reply in a thread, a status note — takes the same footer. Nothing has needed one yet; when one
does, it amends this section rather than inventing a second format.

### What triggered it

A dispatched `repos/review` session posted an 8.7k-character review to PR #3 with `gh`. GitHub
recorded the author as **`junhyukhan`** — the session inherits Han's authenticated CLI. Reading the
PR, it looks like Han wrote an adversarial review of his own pull request.

The session had attributed itself in prose (its opening line names the dispatch; its closing line
gives the reviewed commits), so a human reading it learns what wrote it. Nothing machine-visible
said so: no footer, no session link, nothing a script or search could find.

That was not the session's fault. The workspace had attribution conventions for **commits**
(`Co-Authored-By` plus `Claude-Session`) and for **PR descriptions**, and nothing at all for
anything else an agent publishes. The session did the reasonable thing in the absence of a rule.

### The decisions

| | |
|---|---|
| **Identity** | Agents keep using Han's own GitHub identity. A separate bot account means API billing; he is on a Claude subscription, and avoiding that charge is the whole reason |
| **Attribution** | Required on anything an agent wrote that Han did not. Commits are already covered; **comments are the gap** |
| **Gate** | Merge, PR creation/deletion, commits, push and comments by any agent ask Han first — recorded in [`chore-commit-carve-out.md`](chore-commit-carve-out.md), which owns that rule |
| **Style** | Link rather than restate; conclusion first; plainer sentences |

Identity and attribution are two halves of one thing here. Because the identity is *shared*,
attribution is the only signal left — there is no author field to distinguish agent from human, so
the text has to carry it.

### The style rule, and why it is not a length limit

Four options were offered. Han took 1, 2 and 4 and **rejected 3 (hard caps)**.

1. **Each artifact says only what it owns, and links.** Adopted.
2. **Conclusion first.** Adopted.
3. **Hard caps** — commit body ≤ 10 lines, PR body ≤ 20, comment ≤ 40. *Rejected.*
4. **Plainer sentences** — fewer em-dashes and subordinate clauses. Adopted.

**The diagnosis was duplication, not length.** For PR #3 the same reasoning was written three times —
decision record, commit message, PR body — each a near-complete retelling. `repos`'s own
[`source-of-truth.md`](../../../docs/decisions/source-of-truth.md) already forbids exactly this: *a
lower-ranked artifact must never restate a value a higher-ranked one owns.* The rule was broken in
the artifacts describing the tool built to enforce it. So the fix is ownership, not a word budget —
which is also why the caps were the right option to drop: they treat the symptom.

Ownership, concretely: the **record** owns *why*; the **commit** owns *what changed*; the **PR** owns
*what a reviewer needs in order to decide*; the **backlog** owns *what is still open*. Anything a
higher-ranked artifact owns gets a link.

**This is a different axis from token compression.** [`caveman-assessment.md`](caveman-assessment.md)
measured prose compression as 49x net-negative here, because ~99.5% of tokens are input re-reads and
compression only touches output prose. Nothing above is a token argument — it is a comprehension
argument, and the two must not be conflated later. Writing *less* was rejected; writing *once, in the
right place* was adopted.

### Judgment calls, marked as mine so they can be overruled

- Bundling identity, attribution and style into one record. They arrived together and share a
  trigger; if style grows its own history it should fork into its own file, on evidence rather than
  on size.
- The ownership table above is my formulation, not Han's words. He named the symptom
  ("too verbose and hard to understand") and picked options; the four-artifact split is mine.

### Open

- **Wired 2026-09-06**, as a `## What you publish` section in
  [`../../claude/.claude/AGENTS.md`](../../claude/.claude/AGENTS.md) citing this record. The edit is
  uncommitted; Han decides whether it lands.
- ~~**What an attribution footer on a comment should say** is undecided~~ — **SETTLED 2026-09-08**,
  see the amendment at the top of this Discussion. The shape guessed here (agent name, dispatch,
  session link) was close; what it missed is that naming the session's *independence* is the useful
  part. The PR #3 comment still stands unattributed by Han's decision to keep it.
- **The dispatch brief still says the old rule.** `repos/ops/orchestrator.py` tells every session
  *"never commit or push on Han's behalf"* and is silent on publishing, which is how the PR comment
  happened. The `AGENTS.md` wiring above reaches a dispatched session only if it reads the global
  file; the brief is the channel that is certain to reach it, and changing it is a `repos/` job. See
  the amendment in
  [`../../../docs/decisions/orchestrator.md`](../../../docs/decisions/orchestrator.md).

## Related records

- [`chore-commit-carve-out.md`](chore-commit-carve-out.md) — owns the no-commit rule and the
  confirmation gate this record's third row points at.
- [`caveman-assessment.md`](caveman-assessment.md) — the token-compression measurement this
  deliberately is *not*.
- [`../../../docs/decisions/orchestrator.md`](../../../docs/decisions/orchestrator.md) — the brief
  that must carry these rules to dispatched sessions.
- [`../../../docs/decisions/source-of-truth.md`](../../../docs/decisions/source-of-truth.md) — the
  restatement rule the style decision applies.
