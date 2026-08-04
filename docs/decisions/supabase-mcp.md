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

**Known wart, not a hole:** all 20 tools are still *advertised* in `tools/list`, including the
mutating ones. They appear available and then refuse. Don't read their presence as the flag
having failed.

**The cost of this choice, stated plainly:** applying a migration to hosted through the MCP is
**not possible** while the flag is set. That is the intended trade — hosted DDL stays a
deliberate act (SQL editor, or a temporary run without the flag), not something a session can do
in passing.

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

The wrong diagnosis still sits in `duri-v3/build/progress.md` and `docs/07` — both say the SQL
editor is the only path to hosted DDL, for a reason that turned out to be false. Correcting it is
`duri-v3`'s to make, not this repo's.
