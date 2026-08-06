# .zshenv — sourced for EVERY zsh invocation: interactive, non-interactive, and
# scripts. Keep this file tiny and side-effect-free; anything interactive
# (prompt, plugins, aliases, completions) belongs in .zshrc instead.
#
# Why anything is here at all: .zshrc is sourced for INTERACTIVE shells only.
# Claude Code spawns MCP servers as non-interactive child processes, so an
# export living in .zshrc never reached them — the Supabase MCP started with no
# PAT and exited, surfacing as "✘ Connection closed" while the credentials were
# perfectly fine. Measured:
#
#   zsh -c   (non-interactive)  → NOT SET  → mcp: ✘ Connection closed
#   zsh -ic  (interactive)      → set      → mcp: ✔ Connected
#
# Full record: config/docs/decisions/supabase-mcp.md (D4, 2026-08-06).

# Supabase MCP server (repos/.mcp.json) authenticates with a personal access
# token. It reads SUPABASE_ACCESS_TOKEN from the environment and does NOT read
# the Supabase CLI's own token file, so bridge the two here rather than putting
# the value in .mcp.json — that file is committed, and a PAT is a secret.
# No secret enters the repo: this reads a local file that git never sees.
#
# Accepted cost of living in .zshenv rather than .zshrc: the PAT is now exported
# into every zsh process, not just interactive ones. On a single-user personal
# machine that is the same exposure by a wider door, and it is the price of the
# MCP working regardless of how a session was launched.
[ -r "$HOME/.supabase/access-token" ] && \
    export SUPABASE_ACCESS_TOKEN="$(cat "$HOME/.supabase/access-token")"
