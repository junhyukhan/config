# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal dotfiles repository for macOS and Fedora Linux. It manages configurations for nvim, zsh, ghostty terminal, and platform-specific settings.

## Key Scripts

```bash
# Deploy configs from repo to system (use on new machine or after pulling)
./scripts/set_config.sh

# Sync configs from system back to repo (use after local changes)
./scripts/update_repo.sh
```

## Architecture

**Cross-platform design**: Shared configs (nvim, ghostty, zsh) work on both platforms. Platform-specific configs are in `mac/` and `fedora/` directories, with OS detection in scripts using `$OSTYPE` for macOS and `/etc/fedora-release` for Fedora.

**Two-way sync model**:
- `set_config.sh`: Deploys from repo paths to system paths (e.g., `nvim/init.lua` → `~/.config/nvim/init.lua`)
- `update_repo.sh`: Copies from system paths back to repo

**Package management**:
- macOS: `mac/Brewfile` with `brew bundle`
- Fedora: `fedora/packages.txt` with `dnf install`

## Config Locations

| Repo Path | System Path |
|-----------|-------------|
| `nvim/init.lua` | `~/.config/nvim/init.lua` |
| `ghostty/config` | `~/.config/ghostty/config` |
| `zsh/zshrc` | `~/.zshrc` |
| `mac/karabiner.json` | `~/.config/karabiner/karabiner.json` |
