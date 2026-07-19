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
