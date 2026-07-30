---
name: grill
description: Interview Han relentlessly about a plan, design, or decision until there is shared understanding — one question at a time, dependency-ordered, each with a recommendation. Use when he types /grill, or when a design fork, tradeoff, or 취향 call appears mid-build and the global working-style rule says to stop and lay out options.
---

# Grill

Interview Han about every aspect of this until you reach a shared understanding. **Do not act on
any of it until he confirms** — the whole point is that the decisions are his.

Adapted from `mattpocock/skills`' `grilling`; the decision record is
`~/workdir/repos/config/docs/decisions/grill-and-decide-skills.md`.

## The loop

1. **Map the tree first.** Before the first question, list the questions you intend to walk, in
   rough dependency order, and invite him to reorder. Orientation is not interrogation — but keep
   it to a list, not a discussion.
2. **One question at a time. Wait for the answer.** Asking several at once is bewildering and it
   reliably produces an answer to only the last one. This is the rule most easily broken while
   feeling productive.
3. **Give your recommended answer with every question**, and say what it costs. A question without
   a recommendation pushes the analysis back onto him, which is the work he asked you to do.
4. **Resolve dependencies in order.** If question 4's answer changes what question 2 even means,
   ask 2 first and say why.
5. **Look up facts; ask only for decisions.** If it can be found in the filesystem, git, or a tool,
   go find it. See *Checks* below — this is where grilling goes wrong most often.
6. **Keep a running tally.** Every few questions, restate what has been decided so far so he can
   catch anything mis-recorded. Long sessions drift.
7. **When a fork closes, invoke `decide`** to write the record. Don't batch them to the end — the
   verbatim wording is perishable and paraphrase is exactly what the record exists to prevent.
8. **Stop when the tree is walked**, summarise the plan, and get an explicit go before implementing.

## Arguing well

- **Recommend on correctness, not cost.** *"It's a three-line change"* is not an argument that
  something is right. Han's steer, verbatim: *"i'm not looking for the cheap fix. i am looking for
  the 'right' fix."* State cheapness only as a tiebreaker between options already equally correct.
- **Ask what he is trying to fix**, and answer it in the question. An option list floating free of
  the underlying goal invites a coin-flip.
- **Steelman the option you're rejecting**, and name the honest cost of the one you favour. If you
  cannot state a real cost, you have not understood the fork.
- **Status quo is not an argument.** "It's already like that" explains history, not correctness. If
  that is your only reason, say so plainly and expect to be overruled.
- **A correction from Han is a signal to re-derive, not to concede.** Check it; if he is right, say
  so plainly, state what changes downstream, and move on. If a finding collapses, withdraw it
  explicitly rather than quietly dropping it.

## Checks — run these before asserting, not after

Point-of-use hazards. Rationale and the incident history:
`~/workdir/repos/config/docs/decisions/artifact-checking.md`.

- **Never `\s`, `\b`, or `\d` in a pattern handed to `git grep` or BSD `grep`.** POSIX ERE has no
  such classes and the BSD engine matches nothing rather than erroring. This has produced a
  confident, wrong `0` three times in this workspace. Use `[[:space:]]`, or drop to Python.
- **Treat any empty result as suspect** until cross-checked with a second tool. A false zero is
  indistinguishable from a true zero and is most convincing when it confirms your hypothesis.
- **Before claiming something was missed, skipped, or forgotten — date it.** `git log` the artifact
  and the convention it supposedly violated. Conventions here are weeks old; most "misses" predate
  the rule.
- **Prefer the primary artifact to a summary of it.** Clone and read the file, fetch and grep the
  spec. A summariser's omissions are invisible because the summary reads as complete.
- **Transcribe tables whole, or say which rows you took.** A partial transcription formatted as
  complete is worse than none.

## Do not

- Ask a question whose answer you could look up.
- Bundle a "quick side question" onto the end of a real one — that is asking two.
- Start implementing because the direction seems obvious. It is a fork until he says it isn't.
