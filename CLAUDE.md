# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal dotfiles for macOS and Fedora Linux, managed with GNU Stow. Configs are symlinked from the repo into `$HOME`, so edits to either location are the same file.

## Key Commands

```bash
# Initial setup on a new machine (installs packages + creates symlinks)
./setup.sh

# Link a single package manually
stow -t ~ <package>

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

**Cross-platform zshrc**: OS detection at the top of `.zshrc` sets plugin/theme paths per platform. macOS uses Homebrew paths, Fedora uses `/usr/share/` and `~/powerlevel10k/`.

**Package management**:
- macOS: `mac/Brewfile` with `brew bundle`
- Fedora: `fedora/packages.txt` with `dnf install`

## Stow Packages

| Package | Symlink Created |
|---------|----------------|
| shell | `~/.zshrc` |
| nvim | `~/.config/nvim/init.lua` |
| ghostty | `~/.config/ghostty/config` |
| vim | `~/.vimrc` |
| claude | `~/.claude/settings.json`, `~/.claude/commands/*` |
| cloudflared | `~/.cloudflared/config.yml` |

### Legacy

Retired configs live in `legacy/`. They are not stow-linked or installed by `setup.sh`.

| Package | Notes |
|---------|-------|
| legacy/karabiner | Was `~/.config/karabiner/karabiner.json` (macOS). No longer used. |
