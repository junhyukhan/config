---
workspace:
  readfirst: docs/README.md
  decisions: docs/decisions/
  backlog: []
  verify: stow -n -R -t "$HOME" shell nvim ghostty vim git tmux && stow -n -R --no-folding -t "$HOME" claude
  autonomy: chore
---

# AGENTS.md — config

Guidance for any coding agent working in this repository.

## Overview

Personal dotfiles for macOS and Fedora Linux, managed with GNU Stow. Configs are symlinked from the repo into `$HOME`, so edits to either location are the same file.

## Docs

Project state and decisions live in `docs/` — start at **`docs/README.md`** (status + index).
Design decisions are captured **verbatim** in `docs/decisions/` (one file per topic; copy
`docs/decisions/TEMPLATE.md`). This is the workspace-wide shape — see
`../docs/repo-docs-standardization.md`.

## Key Commands

```bash
# Initial setup on a new machine (installs packages + creates symlinks)
./setup.sh

# Re-link everything (idempotent; also fixes links after moving the repo)
./setup.sh

# Link a single package manually (-R = restow, safe to re-run)
stow -R -t ~ <package>

# Unlink a package
stow -t ~ -D <package>

# Export package lists (run manually after installing new packages)
# macOS:
brew bundle dump --file=mac/Brewfile --force
# Fedora:
dnf repoquery --userinstalled --qf '%{name}' | sort > fedora/packages.txt
```

## Architecture

**Symlink-based with GNU Stow**: Each top-level directory (shell, nvim, ghostty, vim, git, tmux, claude, vscode, cloudflared) is a stow package. The directory structure inside each package mirrors the path relative to `$HOME`. Running `stow -t ~ <package>` creates symlinks accordingly.

**Restowing / moving the repo**: Stow creates *relative* symlinks, so moving the repo directory breaks every link. To recover, re-run `./setup.sh` from the new location (it uses `stow -R`, which is idempotent and rebuilds the links).

**`claude` package uses `--no-folding`**: Claude Code writes runtime state (`sessions/`, `jobs/`, `plugins/`, `history.jsonl`, logs, etc.) into `~/.claude`. If stow folds the whole directory into a single `~/.claude` symlink, all that runtime state lands inside this repo. `--no-folding` keeps `~/.claude` a real directory and symlinks only the tracked files (`settings.json`, `commands/*`). Runtime state is also ignored via `.gitignore` (`claude/.claude/*` with whitelisted configs).

**`vscode` package is darwin-only and also uses `--no-folding`**, for both of the reasons above at
once. Its path (`Library/Application Support/Code/User`) is macOS-specific — Fedora uses
`~/.config/Code/User` — so `setup.sh` guards it on `$OSTYPE`. And that `User/` directory holds VS
Code's own state (`globalStorage`, `History`, `profiles`, `workspaceStorage`), so folding it would
drag all of that into the repo. Only `settings.json` and `keybindings.json` are tracked.

**Cross-platform zshrc**: OS detection at the top of `.zshrc` sets plugin/theme paths per platform. macOS uses Homebrew paths, Fedora uses `/usr/share/` and `~/powerlevel10k/`.

**`.zshenv` vs `.zshrc` — the split matters and has bitten once.** `.zshrc` is sourced for
**interactive** shells only; `.zshenv` for **every** zsh, including the non-interactive children
that Claude Code spawns MCP servers as. Anything an agent-launched process must see (env exports
like `SUPABASE_ACCESS_TOKEN`) belongs in `.zshenv`; everything interactive — prompt, plugins,
aliases, completions — stays in `.zshrc`. Putting the Supabase PAT in `.zshrc` made the MCP fail
with `✘ Connection closed` while the credentials were fine (`docs/decisions/supabase-mcp.md`, D4).

**What belongs where — the rule for a reproducible machine.** The repo's job is that a fresh
machine ends up like this one, so every thing on it falls into exactly one of three buckets:

| Kind | Where it goes | Test |
|---|---|---|
| Config **you wrote** | tracked in a stow package | would you be annoyed to rewrite it? |
| **Tools** | declared in `setup.sh` — the Brewfile if brew carries it, a guarded install block if not (see herdr, powerlevel10k) | does a fresh machine need it present? |
| Files a **tool generates** | neither — they come back when the tool is installed | does the tool recreate it? |

The third bucket is why `~/.claude/hooks/herdr-agent-state.sh` is *not* tracked even though the
`hooks/` allowlist would take it: herdr writes it, herdr updates it, and `herdr integration
uninstall claude` removes it. Tracking it would mean owning a vendor file that gets overwritten.
`setup.sh` installs herdr and its integration instead, which is what makes the tracked
`settings.json` reference to that hook valid on a new machine.

**`brew bundle dump` rewrites `vscode` entries from live state, so it can delete them.** It emits
exactly what `code --list-extensions` reports. VS Code currently has **none** — the extensions in
daily use are in **Cursor**, and Homebrew Bundle has no directive for Cursor, so `brew bundle`
cannot capture or restore them. A dump therefore wipes the `vscode` block. Always verify a re-dump
with a set comparison rather than eyeballing the diff:

```bash
comm -23 <(git show HEAD:mac/Brewfile | grep -E '^(tap|brew|cask|vscode|go|npm) ' | sort) \
         <(grep -E '^(tap|brew|cask|vscode|go|npm) ' mac/Brewfile | sort)
```

Anything it prints was dropped.

**Package management**:
- macOS: `mac/Brewfile` with `brew bundle`
- Fedora: `fedora/packages.txt` with `dnf install`

## Stow Packages

| Package | Symlink Created |
|---------|----------------|
| shell | `~/.zshrc`, `~/.zshenv`, `~/.p10k.zsh` |
| nvim | `~/.config/nvim/init.lua`, `~/.config/nvim/lazy-lock.json` |
| ghostty | `~/.config/ghostty/config` |
| vim | `~/.vimrc` |
| claude | `~/.claude/` — `settings.json`, `AGENTS.md` + `CLAUDE.md` (global agent instructions), `commands/*` (slash commands), `hooks/*` (e.g. `guard-secret-env.py`), `skills/*` (global skills) — all via `--no-folding` |
| cloudflared | `~/.cloudflared/config.yml` (Fedora only, auto-stowed on Fedora) |

> The `claude` package is this repo's **agent-config home**: everything under
> `~/.claude` that should be versioned + portable (settings, the global `AGENTS.md`,
> slash commands, hooks, skills) lives in `claude/.claude/` and is Stow-linked. Add a
> new hook/command/skill by dropping the file there and re-running `./setup.sh` (or
> `stow -R --no-folding -t ~ claude`) — never hand-create the symlink.

## Agent tooling (workspace scaffolding)

Beyond dotfiles, this repo carries tooling for the `~/workdir/repos` agent workflow:

- **`templates/`** — canonical `AGENTS.md.tmpl` + `CLAUDE.md.tmpl` for a new project repo,
  plus `docs-README.md.tmpl` + `decision.md.tmpl` for the standard `docs/` shape.
- **`scripts/new-repo.sh <dir>`** — scaffolds those templates into a new repo (filled with
  its name): `AGENTS.md`, `CLAUDE.md`, `docs/README.md`, `docs/decisions/TEMPLATE.md`. It
  skips files that already exist, then prints the steps to wire the repo into the workspace
  meta-repo (`repos/.gitignore` line + `repos/AGENTS.md` table row). Keeps every new project
  on the standard agent-context shape.
- **`claude/.claude/skills/`** — the versioned home for personal global Claude skills
  (see its `README.md`).

### Legacy

Retired configs live in `legacy/`. They are not stow-linked or installed by `setup.sh`.

| Package | Notes |
|---------|-------|
| legacy/karabiner | Was `~/.config/karabiner/karabiner.json` (macOS). No longer used. |
