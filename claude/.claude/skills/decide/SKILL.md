---
name: decide
description: Write a decision record in the right repo — Han's verbatim ask plus the discussion, routed to the repo owning the artifact the decision governs. Use when a design fork closes, or when he drops a mid-build steer or 취향 call that carries intent, whether or not a /grill session is running.
---

# Decide

Write the record while the words still exist. **Han's exact wording is the perishable part** — once
the session ends, the best anyone reconstructs is a paraphrase, which is the thing this record
exists to prevent.

Invoke this whenever a decision lands. Most decisions here are *not* the close of a grilling
session; per Han's global rule they are *"a one-line course-correction I drop during
implementation."* Those count. Rule and reasoning:
`~/workdir/repos/docs/decisions/decision-capture.md`.

## 1. Route it — which repo?

**The record lives in the repo that owns the artifact the decision governs.** Not the repo whose
files happened to change, not the repo where the conversation happened.

Ask: *what does this decision bind?* Then find that repo's `decisions:` path from the `workspace:`
frontmatter in its `AGENTS.md`.

- A rule in `config/claude/.claude/AGENTS.md` → `config`, even if the work that motivated it was
  elsewhere.
- Workspace-wide conventions, the map, the ops layer, the journal → `repos`.
- A repo's own architecture, build, or deploy shape → that repo.

**Two repos genuinely governed → two records that cite each other.** Do not pick a "primary" and
have the other point at it; picking the primary is the judgment call that fails.

**A cross-repo design doc cites records — it never contains them.** If the reasoning belongs to
another repo's artifact, write it there and link.

The test that decides ties: **a repo is the unit that travels.** Clone it alone, or open it on
GitHub — the reasoning for why it is the way it is should be inside.

## 2. Write it

One file per **topic**, appended to as the topic evolves — not one file per session. If a record for
this topic exists, add to it; **the newest decision goes first.**

**Newest-first is not decoration — it is what keeps a growing record cheap to read.** A new amendment
goes directly under `## Discussion`, above the older ones. Never append to the bottom. This rule has
existed since the skill was written and was not followed once: `cross-repo-retrieval.md` grew to 877
lines with its newest entry — a deferral that *re-opened a decision closed two days earlier* — at
roughly line 870. A reader must reach the current state without reading the history.

Measured 2026-08-29 before keeping the one-file-per-topic rule: of 28 records, 16 are under 150 lines
and 25 are under 400. Files are not growing without bound; three long-running topics are large. So
the rule stands, and the fix for read cost is ordering plus `description`, not fragmenting the
argument. When a topic genuinely **forks**, give the fork its own file (as `source-of-truth.md` was
split out of `cross-repo-retrieval.md`) — split on evidence, not on a size rule.

### Frontmatter — OKF v0.2, used as-is

Every record carries YAML frontmatter in [OKF
v0.2](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) form. **No
local extensions** — the spec is used unmodified. Decision: `repos/docs/decisions/cross-repo-retrieval.md`.

```yaml
---
type: Decision
title: <Topic>
description: <one sentence — see below>
status: draft | stable | deprecated
tags: [...]
generated: { by: human:junhyukhan, at: <ISO 8601> }
---
```

- **`description` is the record's machine API.** The generated decisions index shows this line and
  nothing else, so it must be enough for an agent to recognise the record *applies*. A title cannot
  do that: `"Agent ops"` would not have stopped an agent re-proposing `ops/state.db` 23 days after
  it was retired, but *"SQLite persistence retired 2026-07-30; `seen.json` replaced it"* would have,
  instantly.
- **`status`** is OKF's three-value enum (§5.4), not a four-value one. **Superseded is written as
  `deprecated` plus a sentence naming the successor**, because OKF links are untyped by deliberate
  design (§6.1: *"the specific kind is conveyed by the surrounding prose, not by the link itself"*).
  Do not invent a `superseded_by` key.
- **`generated.by`** uses the actor convention (§7): `human:<id>` for hand-authored, `<producer>/<version>`
  for an agent. The `human:` prefix is what marks content as human-authored, so use it accurately —
  do not mark an agent-drafted record as `human:`.
- Keep the prose `**Status:**` line too; it carries detail the enum cannot.

Copy the shape from that repo's `docs/decisions/TEMPLATE.md`:

- **`## Why — the ask (verbatim)`** — Han's exact words in a blockquote, dated. Informal wording,
  typos, Korean and all. **Never tidy it up** — the raw phrasing is the intent. Stack multiple
  quotes as the topic evolves; mid-build steers belong here just as much as the opening ask.
- **`## Discussion`** — the analysis, the options *considered and rejected with why*, the decision,
  the honest cost of it, and anything still open.

What makes these worth keeping is the part git cannot hold: **a commit records what happened; it
never records what was considered and discarded.** Write the rejected branches down.

Also:

- **Record withdrawn findings.** If something was claimed and then disproved, say so in the record.
  A correction that only lives in chat will be re-derived wrong later.
- **Mark your own judgment calls as yours**, not as Han's, so they can be overruled rather than
  inherited as settled.
- **Note when something is provisional** and what signal should trigger a revisit.

## 3. Wire it up

- Add a line to that repo's `docs/README.md` index.
- Update the **constraint** wherever it binds — the read-first file or `AGENTS.md` of each affected
  repo — and have it **cite this record**. The constraint is short and normative; the record is long
  and historical. A standing rule with no citation is a defect.

## Checks — before you write

Rationale: `~/workdir/repos/config/docs/decisions/artifact-checking.md`.

- **Before recording that something was missed, forgotten, or skipped — date it against `git log`.**
  Check when the artifact landed *and* when the convention it supposedly violated landed. Most
  "misses" in this workspace predate their rule.
- **Never `\s`, `\b`, or `\d` in a pattern handed to `git grep`** — POSIX ERE, BSD engine; it
  matches nothing rather than erroring. Treat any empty result as suspect until cross-checked.
- **Quote from the artifact, not from memory of it.** Open the file and copy the line.
- **Verify a claimed count before putting a number in a record.** Numbers in records get cited.

## Do not

- Paraphrase Han into your own prose. That deletes the thing being captured.
- Batch several decisions to the end of a session.
- Write the record into the meta-repo because it is convenient — see routing above.
- Commit it unasked. Records are docs, but this skill fires inside larger changes; the `chore`
  carve-out requires an otherwise-clean tree.
