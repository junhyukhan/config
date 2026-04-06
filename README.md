# config

Personal dotfiles for macOS and Fedora Linux, managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Structure

```
config/
├── setup.sh                 # Bootstrap script (packages + symlinks)
├── shell/
│   └── .zshrc               # -> ~/.zshrc
├── nvim/
│   └── .config/nvim/
│       └── init.lua          # -> ~/.config/nvim/init.lua
├── ghostty/
│   └── .config/ghostty/
│       └── config            # -> ~/.config/ghostty/config
├── vim/
│   └── .vimrc               # -> ~/.vimrc
├── claude/
│   └── .claude/
│       ├── settings.json     # -> ~/.claude/settings.json
│       └── commands/
│           ├── pr.md               # -> ~/.claude/commands/pr.md
│           └── cloudflare-tunnel.md # -> ~/.claude/commands/cloudflare-tunnel.md
├── cloudflared/
│   └── .cloudflared/
│       └── config.yml        # -> ~/.cloudflared/config.yml (dev gateway only)
├── legacy/
│   └── karabiner/            # Retired configs (not linked)
│       └── .config/karabiner/
│           └── karabiner.json
├── mac/
│   └── Brewfile              # Homebrew packages
└── fedora/
    └── packages.txt          # dnf packages
```

## Quick Start

### macOS

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Clone and set up:
   ```bash
   git clone https://github.com/junhyukhan/config.git ~/dev/config
   cd ~/dev/config
   ./setup.sh
   ```

### Fedora

```bash
git clone https://github.com/junhyukhan/config.git ~/dev/config
cd ~/dev/config
./setup.sh
```

Some tools need manual installation on Fedora:
```bash
# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# bun
curl -fsSL https://bun.sh/install | bash
```

### Resolving conflicts

If Stow reports "existing target is not owned by stow", remove or back up the conflicting file first:
```bash
mv ~/.zshrc ~/.zshrc.bak
./setup.sh
```

## How it works

GNU Stow creates symlinks from `$HOME` into this repo. When you edit `~/.config/nvim/init.lua`, you're editing the repo file directly -- no sync step needed.

```bash
# Link a specific package
stow -t ~ nvim

# Unlink a package
stow -t ~ -D nvim
```

## Updating package lists

After installing new packages, export the updated list:

```bash
# macOS
brew bundle dump --file=mac/Brewfile --force

# Fedora
dnf repoquery --userinstalled --qf '%{name}' | sort > fedora/packages.txt
```

Then commit and push.

## What's Included

| Config | Description |
|--------|-------------|
| **nvim** | Neovim config based on kickstart.nvim with LSP, Telescope, Treesitter |
| **zsh** | Zsh with powerlevel10k, fzf, zoxide, syntax highlighting, autosuggestions |
| **ghostty** | Ghostty terminal emulator config |
| **vim** | Basic vim config |
| **Brewfile** | Homebrew packages and casks (macOS) |
| **packages.txt** | dnf packages (Fedora) |
| **claude** | Claude Code settings and custom slash commands |
| **cloudflared** | Dev gateway tunnel config (stow on active dev machine only) |
