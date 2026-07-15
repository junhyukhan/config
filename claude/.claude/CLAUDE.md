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
