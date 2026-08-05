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
