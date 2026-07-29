# Global user instructions

## Secrets: never read the contents of real secret files

Do **not** read the contents of real secret env files — `.env`, `.env.local`,
`.env.hosted`, `.env.production*`, or any `*.env` (e.g. `duri.env`). Their values
must never enter context or any console that can be logged.

- To learn what keys a secret file holds, read the matching **`*.example`** template
  — those are safe and intended, read them freely.
- When a real secret value genuinely has to move (e.g. onto a server), handle it
  **file-to-file** so the value is never printed: `cp`, `scp`, `grep <keys> src >
  dest` (redirect into a file), etc. Never `cat` / `echo` / `grep`-to-console a
  secret, and never pass it as an inline command argument.

A PreToolUse hook (`~/.claude/hooks/guard-secret-env.py`) hard-blocks the read/dump
vectors as a backstop, but the rule above is the intent — don't rely on the block.

## Capturing intent & taste: record my decisions in my own words

When you record a backlog item, design decision, or any choice I've made — in **any repo** —
preserve **my exact wording verbatim** in a `**Verbatim:**` blockquote, then a short
**Discussion** (analysis / options / decision / open questions). This includes **mid-build
steers and taste (취향) calls**, not just the opening ask: a one-line course-correction I drop
during implementation carries the intent, so quote it — don't fold it into your own prose as a
paraphrase.

Write it into the **repo's own design docs** (e.g. a `docs/` topic file or `SPEC.md`), indexed
from wherever that repo tracks work — not left in chat, and not only in your memory. Preserve my
exact phrasing, informal wording and all — that *is* verbatim. The raw wording captures intent and
taste better than a tidy restatement, and keeps a record of the product judgment and how each
decision evolved.

## Working style: discuss design forks; don't self-authorize commits/pushes

When building, if you find yourself **choosing between viable approaches** — a design fork, a
tradeoff, a taste (취향) call, anything with real pros/cons — **stop and lay out the options with
a recommendation, then let me decide.** Don't quietly resolve it and implement. A fork is a fork
even mid-build; "it felt like part of the implementation" is not a reason to skip the check. When
unsure, a two-line "options X / Y, I lean X — ok?" is the cheap hedge.

**Never commit or push on my behalf unless I ask.** Building a feature is not authorization to
land it in git. Make the edits; leave committing and pushing to me (or to the approved
session-end sync hook). "It was on the permission allowlist" is not "it should have been run" —
*allowed ≠ should*.

**Just do it** (no pre-check) for the reversible, single-obvious-answer things: typos, stale
refs, searches, reading, running tests, local edits I can undo. **Ask first** for: design forks,
outward-facing or hard-to-reverse actions (commit, push, send, publish, delete, deploy), and
anything that creates standing config or automation. When in doubt, ask — it's cheap; a wrong
autonomous commit/push is not.

## Verify against the artifact, not a summary of it

**A summarized read of a source is a lead, not a fact.** Before recording something as true — in a
doc, a knowledge card, code, or a claim to me — go to the actual artifact: fetch the spec and grep
it, open the file, run the query. Summaries of large documents drop things, and what they drop is
invisible precisely because the summary reads as complete.

This bites hardest on **absence**. "The docs don't mention X" from a summarizer usually means the
summarizer didn't mention X. (Real case: a summarized read of a vendor's `openapi.json` reported an
endpoint didn't exist; it was right there in `paths`, and a cost model was nearly built around the
false absence.)

Two corollaries:

- **Transcribe whole tables, or say which rows you took.** A partial transcription formatted as if
  complete is worse than none — nobody re-checks it.
- **"The vendor's docs are wrong" deserves more scepticism than believing them**, not less. It's
  the most flattering explanation for a discrepancy because it puts the error outside your own
  code. Before concluding it, ask what would have to be true about *our* code for the docs to be
  right — that story is usually the correct one.
