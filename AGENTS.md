# AGENTS.md — config

Guidance for any coding agent working in this repository.

## Overview

Personal dotfiles for macOS and Fedora Linux, managed with GNU Stow. Configs are symlinked from the repo into `$HOME`, so edits to either location are the same file.

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

**Symlink-based with GNU Stow**: Each top-level directory (shell, nvim, ghostty, vim, claude, cloudflared) is a stow package. The directory structure inside each package mirrors the path relative to `$HOME`. Running `stow -t ~ <package>` creates symlinks accordingly.

**Restowing / moving the repo**: Stow creates *relative* symlinks, so moving the repo directory breaks every link. To recover, re-run `./setup.sh` from the new location (it uses `stow -R`, which is idempotent and rebuilds the links).

**`claude` package uses `--no-folding`**: Claude Code writes runtime state (`sessions/`, `jobs/`, `plugins/`, `history.jsonl`, logs, etc.) into `~/.claude`. If stow folds the whole directory into a single `~/.claude` symlink, all that runtime state lands inside this repo. `--no-folding` keeps `~/.claude` a real directory and symlinks only the tracked files (`settings.json`, `commands/*`). Runtime state is also ignored via `.gitignore` (`claude/.claude/*` with whitelisted configs).

**Cross-platform zshrc**: OS detection at the top of `.zshrc` sets plugin/theme paths per platform. macOS uses Homebrew paths, Fedora uses `/usr/share/` and `~/powerlevel10k/`.

**Package management**:
- macOS: `mac/Brewfile` with `brew bundle`
- Fedora: `fedora/packages.txt` with `dnf install`

## Stow Packages

| Package | Symlink Created |
|---------|----------------|
| shell | `~/.zshrc`, `~/.p10k.zsh` |
| nvim | `~/.config/nvim/init.lua`, `~/.config/nvim/lazy-lock.json` |
| ghostty | `~/.config/ghostty/config` |
| vim | `~/.vimrc` |
| claude | `~/.claude/settings.json`, `~/.claude/commands/*` |
| cloudflared | `~/.cloudflared/config.yml` (Fedora only, auto-stowed on Fedora) |

### Legacy

Retired configs live in `legacy/`. They are not stow-linked or installed by `setup.sh`.

| Package | Notes |
|---------|-------|
| legacy/karabiner | Was `~/.config/karabiner/karabiner.json` (macOS). No longer used. |
