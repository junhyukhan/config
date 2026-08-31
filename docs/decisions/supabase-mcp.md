---
type: Decision
title: Supabase MCP server
description: >-
  The Supabase MCP runs `--read-only` with a pinned `--project-ref` — removed 2026-08-05,
  restored 2026-08-06 with the CLI as the write path; all three settings sit in GUARDED_CONFIG.
status: stable
tags: [config, mcp, supabase, duri-v3, secrets, guarded-config]
generated: { by: human:junhyukhan, at: 2026-08-04T00:00:00Z }
---

# Supabase MCP server

**Status:** done (2026-08-04)

## Why — the ask (verbatim)

> **Verbatim (2026-08-04):** "As for postgres perhaps there is an mcp or something that makes
> things much easier?"

Asked after a session spent failing to reach hosted Supabase from an agent shell — the direct
Postgres host resolves **IPv6-only** and this machine has no IPv6 egress, which is the real
reason two earlier attempts hung (`duri-v3/build/progress.md` had recorded it as a pooler
transaction-mode problem, and told future sessions not to re-litigate it; that diagnosis was
wrong, and the session-mode pooler had never been tried).

Then, on the two questions put to him — read-only vs unrestricted, and whether to pin the
project ref:

> **Verbatim (2026-08-04):** "Your picks for the two questions are correct
> And yes let's add them to our config"

The picks he confirmed: **`--read-only`**, and **pin `--project-ref`**.

## Discussion

### Why an MCP at all

`docs/07` in `duri-v3` already specified this — *"A single install bundles the Supabase MCP
server so the agent can query the DB, manage migrations, deploy Edge Functions"* — it was simply
never wired into the Claude Code config. It talks to the **Management API over HTTPS**, so the
whole IPv6 / pooler-mode / DB-password obstacle course is irrelevant to it.

### D1 — `--read-only`

`duri-v3/docs/07` also says *"Never let a cloud agent autonomously mutate prod data for a money
app — schema via reviewed branch-merge only."* An unrestricted MCP hands every future session
`execute_sql` write access to live household finances, ambiently, forever. Read-only would have
answered every question that actually came up in the session that prompted this (table grants,
default ACLs, which migrations are tracked).

**Verified what the flag actually enforces, rather than trusting the name** — it is two
independent layers:

1. **Postgres-level, for `execute_sql`.** Probed live: `show transaction_read_only` → `on`. Writes
   are refused by the database, not by a prompt.
2. **Tool-level, for everything going through the Management API.** Every mutating tool carries an
   explicit `if (readOnly) throw` guard: `apply_migration`, `deploy_edge_function`,
   `create_branch` / `delete_branch` / `merge_branch` / `reset_branch` / `rebase_branch`,
   `create_project`, `pause_project`, `restore_project`, `update_storage_config`.

~~**Known wart, not a hole:** all 20 tools are still *advertised* in `tools/list`, including the
mutating ones. They appear available and then refuse. Don't read their presence as the flag
having failed.~~

**⚠️ CORRECTED 2026-08-05 — that was true of the version probed on 2026-08-04 and is not a stable
property.** In the version cached now (`0.9.0`), read-only mode takes a `readOnlyBehavior` option
that defaults to **`'exclude'` — mutating tools are removed from the tool list entirely**, not
advertised-then-refused. So the observable signature of the flag is version-dependent: sometimes
the tools are absent, sometimes present and throwing. **`.mcp.json` pins `@latest`**, so this can
change again under any session without a config edit. Don't treat either signature as the test of
whether the flag is on — read the `args` in `.mcp.json`, which is the only thing that actually
decides it.

**The cost of this choice, stated plainly:** applying a migration to hosted through the MCP is
**not possible** while the flag is set. That is the intended trade — hosted DDL stays a
deliberate act (SQL editor, or a run without the flag), not something a session can do
in passing.

**A launch flag is not an approval gate — the distinction that D3 turned on.** `--read-only` is
fixed for the life of the server process. A Claude Code permission prompt decides whether a call
is *made*; it cannot change what an already-running server *accepts*. There is no "approve this
one write" path while the flag is set: either the tool is absent, or it throws, or Postgres
refuses under `transaction_read_only=on`. Changing it means editing `args` and restarting.

### D2 — pin `--project-ref`

The org holds two projects whose names differ only by capitalisation: `yxxpseirxloqbhxpvmpp`
("duri", ACTIVE_HEALTHY, live) and `zenlatqblbxesyyetmgb` ("Duri", INACTIVE). Unpinned, an agent
choosing "Duri" from a list reaches the wrong database. Pinning removes the choice.

### Where it lives, and why not in one place

Three files across two repos, because Claude Code splits these concerns:

| File | Repo | Why there |
|---|---|---|
| `repos/.mcp.json` | meta-repo | The server **definition**. `settings.json` has **no `mcpServers` key** — servers are defined in `.mcp.json` only. It sits at the meta-repo root, not in `duri-v3/`, because `repos/AGENTS.md` says sessions launch at `~/workdir/repos`; a `.mcp.json` inside `duri-v3/` would never load in the normal flow. |
| `config/claude/.claude/settings.json` | config | `enabledMcpjsonServers: ["supabase"]` — pre-approves the server so it is not re-prompted per session. This is the only MCP key settings.json has. |
| `config/shell/.zshrc` | config | Exports `SUPABASE_ACCESS_TOKEN` from `~/.supabase/access-token`. |

### The token, and why it is not in `.mcp.json`

The MCP server reads `SUPABASE_ACCESS_TOKEN` from the environment (or `--access-token`); it does
**not** read the Supabase CLI's own token file, even though the CLI already stores a working PAT
there. Putting the value in `.mcp.json` would commit a secret, and passing it as `--access-token`
would put it on a command line. So `.zshrc` bridges the two by reading the local file — **no
secret enters git**, only a command that reads a path git never sees.

Accepted downside: the PAT is exported into every interactive shell, so any process running as
this user can read it. Judged acceptable for a personal machine and the standard way MCP servers
are authenticated; revisit if the token ever gains broader scope than one org.

### Verified before landing

`initialize` handshake against the real server (`supabase 0.9.0`), 20 tools listed,
`transaction_read_only=on` confirmed by live query, JSON valid, `zsh -n` clean, and the repo's own
`stow -n -R` dry-run clean for all five packages.

### Open

~~The wrong diagnosis still sits in `duri-v3/build/progress.md` and `docs/07` — both say the SQL
editor is the only path to hosted DDL, for a reason that turned out to be false. Correcting it is
`duri-v3`'s to make, not this repo's.~~ **Closed 2026-08-05** — corrected in `duri-v3` (commit on
`feat/voice-parse-seam`), in the repo that owns those files.

## Amendment 2026-08-05 — D3: `--read-only` removed

**This supersedes D1's flag choice. D1's *reasoning* is left intact above** — it is why the flag
was there, and it is the argument to re-read before deciding whether it goes back.

### The ask (verbatim)

The amendment started from a correction Han made to a claim of mine — that the MCP could only
inspect hosted, never migrate it:

> **Verbatim (2026-08-05):** "Yes the mcp is read only by default. But it can write on my approval."

**That premise is wrong as configured, and the wrongness is the point.** There was no approval path:
`--read-only` is a launch argument, so no permission prompt could have unlocked a write (see the
paragraph added under D1). The belief is an easy one to hold — Claude Code *does* prompt before MCP
calls, so "it'll ask me first" generalises naturally — and it is exactly the kind of belief that
looks harmless until the write silently doesn't happen, or until someone counts on the prompt as
the safety mechanism when it isn't one. Shown the mechanism, Han chose to change the config rather
than the expectation:

> **Verbatim (2026-08-05):** "Yes and yes to removing the readonly"
>
> **Verbatim (2026-08-05):** "Fix all of them, push and clean up so that we can start a new session
> right away"

("Yes and yes" = fix the stale `tools/list` paragraph, **and** remove the flag.)

### Discussion

**The forcing reason:** duri-v3 migration `0021` must reach hosted before PR #43 deploys, and both
deploy targets share one Supabase project. The two available paths were the Supabase SQL editor or
an MCP run without the flag. The MCP path is materially better for this specific job: `apply_migration`
both applies the DDL **and** records the row in `supabase_migrations.schema_migrations` — the two
steps that were hand-stitched for `0018` and drifted as a result.

**What is now true, stated plainly rather than buried:** every future session launched at
`~/workdir/repos` gets `execute_sql` **write** access to the live household-finance database,
ambiently. That is precisely the exposure D1 declined, and `duri-v3/docs/07`'s "never let a cloud
agent autonomously mutate prod data for a money app" now rests on session discipline rather than on
the flag. Han's call, made with the tradeoff in front of him.

**Scope of the removal was NOT settled and is the open question below.** The path originally put to
Han was "drop the flag, apply, put it back"; what he asked for and what is committed here is the
flag simply removed, because the follow-up asked for a pushed, clean state to start a new session
from — which means the config had to land in its write-capable form. Whether it goes back after
`0021` is his to decide, and is deliberately not decided here.

### Open

- **Does `--read-only` go back after `0021` is applied?** Restoring it is a one-line revert of this
  commit. Leaving it off is a standing grant, so the default answer should be "restore it" and the
  burden of argument is on keeping it off. **Not decided.**
- **Nothing enforces the restore.** No hook, reminder, or check will notice the flag is absent —
  this bullet is the only record. If the answer above is "restore it", that wants a mechanism, not
  a note.

## Amendment 2026-08-06 — D4: `--read-only` restored; the CLI becomes the write path

**This closes D3's open question** (*"does `--read-only` go back after `0021` is applied?"*) and
supersedes D3's flag choice. **D3's reasoning stays intact above** — it is why the flag came off,
and the forcing reason it names (get `0021` onto hosted) was real and is now discharged.

### The ask (verbatim)

The amendment opened as a push-back on a recommendation of mine to restore the flag:

> **Verbatim (2026-08-06):** "Hmm yeah the mcp was useless this round but i want to push back on
> your decision to remove the flag. And i want to ask whether using the cli or mcp is the better
> path forward when using a coding agent. My presumption is that a cli should be used if i want to
> manually control it myself. But since i want the agent to control it, i should either use an mcp
> or a skill that lists the commands. I feel like mcp is the better choice. As long as i get a
> confirmation for the writes, that should be fine no?"

Then, correcting his own wording and widening the question — this is the pivot of the whole
amendment:

> **Verbatim (2026-08-06):** "Ah yeah i made a typo. I meant i want to push back on restoring the
> readonly flag for the mcp
>
> But then i have a more fundamental question. Why even use an mcp if i can just use a skill + cli
> combo?
>
> And btw i just havent got the chance to add the credentials for the mcp yet. I will later once we
> decide our path."

Two questions that caught errors in my answers, in order:

> **Verbatim (2026-08-06):** "Wait i dont get it. The supabase cli doesnt do sql execute is what
> you're saying? Then how would a read only mcp help. What gap is this readonly mcp"

> **Verbatim (2026-08-06):** "Wait so how did you apply the migration sql this session?"

And the decision:

> **Verbatim (2026-08-06):** "Let's go with B, write the decision record"

### Discussion

**What was decided — option B of three offered.** The MCP is restored to `--read-only`; **the
Supabase CLI becomes the write path for hosted**, driven by the agent, wrapped in a skill so the
commands and traps are not rediscovered each session. The two tools are assigned by *direction*,
not by who is typing.

| | writes | reads (query, rows back) |
|---|---|---|
| CLI | ✅ — but only SQL that exists as a **tracked migration file** | ❌ none |
| MCP `--read-only` | ❌ (`transaction_read_only=on`) | ✅ arbitrary |
| MCP unrestricted | ✅ arbitrary | ✅ arbitrary |

**Options rejected:**

- **A — skill + CLI, drop the MCP entirely**, filling read-back with a small committed
  `postgres.js` script (the `duri-v3/scripts/check-hosted-migrations.mjs` pattern). Genuinely
  defensible and nearly chosen; rejected as less ergonomic than a tool that already exists and
  works. **The cost of not choosing it:** a standing MCP server, pinned `@latest`, whose behaviour
  has already changed under this workspace once (see D1's 2026-08-05 correction).
- **C — keep the MCP unrestricted, rely on per-write confirmation.** This was Han's opening
  position and it is *mechanically coherent* — unlike the 2026-08-05 belief D3 corrected, where the
  flag was **on** and no prompt could unlock a write. With the flag off, the permission prompt is a
  real gate. It was rejected on what the prompt is worth in practice, not on principle: as
  configured, `config/claude/.claude/settings.json` sets `defaultMode: auto` with **no `allow`,
  `ask`, or `deny` entries at all**, so "I confirm the writes" rests on a classifier's judgment per
  invocation rather than a rule Han wrote. It also degrades silently in non-interactive contexts
  (cloud agents, `/loop`, background runs), which is the exposure `duri-v3/docs/07` names outright:
  *"Never let a cloud agent autonomously mutate prod data for a money app."*

**The argument that actually decided it, and it is not a safety argument.** The first case I made
for restoring the flag was about review surface — a migration file goes through a PR, an in-session
SQL string does not. True, and it still holds (constitution #2 and #3 in `duri-v3` are enforced by
*reviewed migration files*). But it framed the flag as a restriction Han had to accept. The better
argument, reached only after his second "wait", is that **the tools do not overlap**: the CLI
writes, the MCP reads, and neither can do the other's half. Restoring `--read-only` therefore costs
nothing — writes are not the MCP's job any more — rather than trading ergonomics for safety. The
flag stopped being contested once the question stopped being about permission.

**Two claims of mine were wrong and were corrected by Han's questions. Recorded because a
correction that lives only in chat gets re-derived wrong.**

1. **"The CLI has no SQL execution at all, in either direction" — false.** `npx supabase migration
   up --linked` executed the whole of `0021` against production this session. What the CLI lacks is
   *arbitrary* execution: there is no `supabase db execute "SELECT …"`. Verified against
   `npx supabase db --help`, whose subcommands are exactly `diff | dump | push | pull | reset |
   lint`. The gap is **read-back**, not execution — the agent can change hosted but cannot ask it a
   question.
2. **"CLI = manual control, MCP = agent control"** (Han's framing, and I initially answered inside
   it before challenging it) **is not the real axis.** The CLI was driven *by the agent* this
   session, gated by a Bash permission prompt exactly as an MCP call would be. Both paths are
   agent-drivable and both are confirmable; the difference is what the artifact is.

**The concrete gap, from this session rather than in the abstract.** Applying `0021` worked;
**verifying it did not**. After the migration landed, the `REVOKE UPDATE, DELETE, TRUNCATE` and the
creator-scoped RLS policy could not be checked directly on hosted — their effect was *inferred*
from `supabase db diff --linked` showing the table present. For a money app whose constitution #2
turns on "RLS is actually on, on *this* database", inference is the wrong strength of evidence, and
`0021`'s own header says why: default privileges are configured **per database**, so a privilege
diff against local proves nothing about hosted. That is the job the read-only MCP is being kept for.

**A premise to retire: the MCP's founding justification does not survive.** D1 adopted it partly
because hosted Postgres was unreachable from an agent shell — `db.<ref>.supabase.co` is IPv6-only,
this machine has no IPv6 egress. This record already carried the correction that the session-mode
pooler is reachable over IPv4 and *was never tried*; this session settled it, with the CLI reaching
hosted and applying `0021` with none of that trouble. The MCP was adopted to route around a wall
that had a door in it. It is being kept for a different and narrower reason than the one it arrived
with, and that should be visible rather than buried.

**Han's belief that credentials are still missing is false — do not act on it.** The closing
verbatim says *"i just havent got the chance to add the credentials for the mcp yet."* Nothing needs
adding: `~/.supabase/access-token` exists (44 bytes, dated 17 Jul 2026), `shell/.zshrc:33-34`
bridges it into the environment, and `claude mcp list` run from an **interactive** shell reports
`supabase … ✔ Connected`. Verified this session.

**Why it looked broken, and the one real defect this uncovered.** `.zshrc` is sourced for
**interactive** shells only, and there is no `~/.zshenv`. Claude Code spawns MCP servers as
non-interactive children, so the export never runs and the server starts with no PAT and exits —
surfacing as `✘ Connection closed`. Measured, not inferred:

```
zsh -c   (non-interactive)  → SUPABASE_ACCESS_TOKEN NOT SET   → mcp: ✘ Connection closed
zsh -ic  (interactive)      → set (44 chars)                  → mcp: ✔ Connected
```

**The fix is to move the export from `shell/.zshrc` to a new `~/.zshenv`** (a `shell` stow package
file), which zsh sources for every invocation regardless of interactivity. **Not yet done — it is
its own change and creates a new stowed file.** Until it is, the MCP works only when Claude Code
inherits an interactive environment, which is a coin-flip depending on how the session was launched.
This is the defect that made the MCP *"useless this round"*, and it is unrelated to the flag.

### As implemented — 2026-08-06, all three landed

- **`--read-only` restored** in `repos/.mcp.json`.
- **The token export moved** from `shell/.zshrc` to a new stowed `shell/.zshenv`, and stowed
  (`~/.zshenv` → `config/shell/.zshenv`). `.zshrc` keeps a pointer comment so the move is not
  re-litigated. **Accepted cost, stated in the file:** the PAT is now exported into every zsh
  process rather than only interactive ones — the same exposure through a wider door, and the price
  of the MCP working regardless of how a session was launched.
- **`duri-v3/.claude/skills/supabase-hosted/`** written, carrying the traps a tool schema cannot
  express. It is a **new** skill rather than an extension of `db-type-contract` because that one
  owns the schema↔types contract and the *local* apply, and this repo's `AGENTS.md` says skills are
  "one concern each". The two now cross-reference, and `db-type-contract` step 4 was corrected to
  `migration up --local` — it previously read bare `migration up`, which silently means local.

**Verified, not assumed** — the two failure modes this amendment exists to fix were both re-tested
after the change:

```
zsh -c 'claude mcp list'   → supabase … --read-only … ✔ Connected
zsh -c   (non-interactive) → SUPABASE_ACCESS_TOKEN set (44 chars)
```

The server now connects from a **non-interactive** shell, which is precisely what it could not do
before, and it does so with the flag on.

### Still open

- ~~**Nothing enforces any of this.**~~ **CLOSED 2026-08-06** — D3's long-standing open bullet
  (*"No hook, reminder, or check will notice the flag is absent"*) is answered. All three items are
  now in `GUARDED_CONFIG` in `repos/ops/index.py`, plus a fourth **regression** guard that fires if
  the PAT export is ever put back into `.zshrc`. Each was verified by breaking it and watching the
  check fire by name. Record: `repos/docs/decisions/agent-ops.md` § "the `guarded config` check".
  **Residual, and it is real:** nothing *runs* the checker automatically, so the guards help only on
  a run. That is now the highest-value item in the agent-ops sequencing list rather than a nice-to-
  have, because these checks are no longer purely informational.
- **`--read-only`'s observable signature is still version-dependent** and `.mcp.json` still pins
  `@latest` (see D1's 2026-08-05 correction). The `args` remain the only reliable test that the flag
  is on. Unresolved by this amendment, and an argument for pinning a version that was not made.
