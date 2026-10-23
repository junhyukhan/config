#!/usr/bin/env bash
#
# check-guards.sh — config a decision put in place, checked for still being in place.
#
# Each guard here fails silently when removed: an unregistered hook stays on disk
# looking healthy while never running, and a token export moved back to .zshrc
# never reaches an MCP server. Nothing else says so. Run as part of this repo's
# `verify` (AGENTS.md frontmatter). Exit 0 only if every guard holds.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

FAILED=0
bad() { echo "✗ $1"; FAILED=$((FAILED + 1)); }

# The Supabase MCP reads its token from the environment, and .zshrc never reaches
# MCP servers: the export lives in .zshenv (decisions/supabase-mcp.md).
grep -q "export SUPABASE_ACCESS_TOKEN" shell/.zshenv \
  || bad "shell/.zshenv no longer exports SUPABASE_ACCESS_TOKEN: the Supabase MCP loses its token"
! grep -q "export SUPABASE_ACCESS_TOKEN" shell/.zshrc \
  || bad "shell/.zshrc exports SUPABASE_ACCESS_TOKEN again: it belongs in .zshenv"

# The secret-env PreToolUse hook is the only mechanical guard on reading .env files.
# settings.json registers it by name; a registration with no file, or a file with no
# registration, fails without a word.
grep -q "guard-secret-env.py" claude/.claude/settings.json \
  || bad "settings.json no longer registers guard-secret-env.py: the secret-file guard is off"
[[ -f claude/.claude/hooks/guard-secret-env.py ]] \
  || bad "claude/.claude/hooks/guard-secret-env.py is missing: settings.json points at nothing"

[[ $FAILED == 0 ]] && echo "guards ok ✓"
exit $(( FAILED > 0 ))
