---
workspace:
  readfirst: docs/README.md
  verify: python3 -B -m unittest discover -s scripts -p 'test_install_claude_settings.py' && python3 -B claude/.claude/hooks/guard-secret-env.test.py && stow -n -R -t "$HOME" shell nvim ghostty vim git tmux && stow -n -R --no-folding -t "$HOME" claude zed herdr-core && scripts/check-guards.sh
  autonomy: chore
---

# AGENTS.md — config

Guidance for any coding agent working in this repository.

`autonomy: chore` (frontmatter) means an agent may commit a docs-only chore here without asking;
anything else waits for Han.

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

**No global agent instructions are tracked here.** The `claude` package carries a public
`settings.json` bootstrap template and the hooks it runs. Runtime settings are a private
regular file, not a Stow link; see **`docs/claude-settings.md`** before updating the
template. The global `AGENTS.md`, `CLAUDE.md`, skills and slash commands were removed,
and there is no `codex` package. A machine that still has them holds
them as local files this repo does not manage.

**Restowing / moving the repo**: Stow creates *relative* symlinks, so moving the repo directory breaks every link. To recover, re-run `./setup.sh` from the new location (it uses `stow -R`, which is idempotent and rebuilds the links).

**`claude` package uses `--no-folding`**: runtime state must stay outside this repo.
Only `hooks/*` are linked. The package-local Stow ignore excludes `settings.json`;
`python3 scripts/install-claude-settings.py` creates private local settings or detaches
an old settings symlink without changing its bytes. Existing regular settings are never
overwritten. Do not put actual hostnames, addresses or private repo inventories in the
public template. Hook source edits are still live through Stow.

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
with `✘ Connection closed` while the credentials were fine. The public summary is
`docs/decisions/supabase-mcp.md`; the personalized history is retained privately.

**What belongs where — the rule for a reproducible machine.** The repo's job is that a fresh
machine ends up like this one, so every thing on it falls into exactly one of three buckets:

| Kind | Where it goes | Test |
|---|---|---|
| Config **you wrote** | tracked in a stow package | would you be annoyed to rewrite it? |
| **Tools** | declared in `setup.sh` — the Brewfile if brew carries it, a guarded install block if not (see Herdr, powerlevel10k) | does a fresh machine need it present? |
| Files a **tool generates** | neither — they come back when the tool is installed | does the tool recreate it? |

Herdr is the third bucket: its app rewrites `~/.config/herdr-app/AGENTS.md`, the type files and
its shipped layouts and mods on every start, so `setup.sh` installs Herdr rather than tracking them.
Your own Herdr settings (`settings.json`, `keys.json`) are not tracked yet.

**`brew bundle dump` can delete `vscode` entries.** Verify every re-dump with the set comparison in
[`docs/README.md`](docs/README.md) §Reference.

**Package management:** macOS `mac/Brewfile` (the core every new Mac gets; see `docs/new-mac.md`), Fedora
`fedora/packages.txt`.

## Stow Packages

| Package | Symlink Created |
|---------|----------------|
| shell | `~/.zshrc`, `~/.zshenv`, `~/.p10k.zsh` |
| nvim | `~/.config/nvim/init.lua`, `~/.config/nvim/lazy-lock.json` |
| ghostty | `~/.config/ghostty/config` |
| vim | `~/.vimrc` |
| claude | `~/.claude/hooks/*` via `--no-folding`; settings are bootstrapped as a private regular file, not linked |
| cloudflared | `~/.cloudflared/config.yml` (Fedora only, auto-stowed on Fedora) |
| zed | `~/.config/zed/settings.json` — settings only, via `--no-folding` |
| herdr-core | `~/.config/herdr-core/templates/*.md` — the `hc run <template>` roles (`implementer`, `reviewer`, `reviewer-pi`), via `--no-folding` |

> Add a hook under `claude/.claude/hooks/` and restow with `--no-folding`.
> Registration changes in the public settings template must also be deliberately
> reviewed and applied to each machine's private settings; a pull does not apply them.
> Use synthetic homes for installer tests; never run setup just to validate a change.

## Agent tooling (workspace scaffolding)

`templates/` and `scripts/new-repo.sh`: see
[`docs/README.md`](docs/README.md) §Reference.

### Legacy

Retired configs live in `legacy/`. They are not stow-linked or installed by `setup.sh`.

| Package | Notes |
|---------|-------|
| legacy/karabiner | Was `~/.config/karabiner/karabiner.json` (macOS). No longer used. |
