# config

Personal dotfiles for macOS and Fedora Linux, managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Structure

```
config/
├── setup.sh                 # Bootstrap script (packages + symlinks)
├── shell/
│   ├── .zshrc               # -> ~/.zshrc
│   └── .p10k.zsh            # -> ~/.p10k.zsh
├── nvim/
│   └── .config/nvim/
│       ├── init.lua          # -> ~/.config/nvim/init.lua
│       └── lazy-lock.json    # -> ~/.config/nvim/lazy-lock.json
├── ghostty/
│   └── .config/ghostty/
│       └── config            # -> ~/.config/ghostty/config
├── vim/
│   └── .vimrc               # -> ~/.vimrc
├── claude/                   # Agent config (stowed with --no-folding)
│   └── .claude/
│       ├── settings.json     # -> ~/.claude/settings.json
│       ├── AGENTS.md         # -> ~/.claude/AGENTS.md  (global agent instructions)
│       ├── CLAUDE.md         # -> ~/.claude/CLAUDE.md  (thin @AGENTS.md import)
│       ├── commands/         # -> ~/.claude/commands/   (slash commands)
│       ├── hooks/            # -> ~/.claude/hooks/      (e.g. guard-secret-env.py)
│       └── skills/           # -> ~/.claude/skills/     (global skills)
├── cloudflared/
│   └── .cloudflared/
│       └── config.yml        # -> ~/.cloudflared/config.yml (dev gateway only)
├── templates/                # AGENTS/CLAUDE/docs templates for a new repo
├── scripts/
│   └── new-repo.sh           # Scaffold those templates into a new repo
├── docs/                     # This repo's own docs (status + decisions)
├── legacy/
│   └── karabiner/            # Retired configs (not linked)
│       └── .config/karabiner/
│           └── karabiner.json
├── mac/
│   └── Brewfile              # Homebrew packages
└── fedora/
    └── packages.txt          # dnf packages
```

Only `shell`, `nvim`, `ghostty`, `vim`, `claude`, and `cloudflared` are stow packages —
`templates/`, `scripts/`, `docs/`, `legacy/`, `mac/`, and `fedora/` are never linked.

## Quick Start

The canonical location is `~/workdir/repos/config` — one repo inside the `~/workdir/repos`
workspace. Stow links are relative, so any other path works too; just re-run `./setup.sh`
from wherever you cloned it (see [Moving the repo](#moving-the-repo)).

### macOS

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Clone and set up:
   ```bash
   git clone https://github.com/junhyukhan/config.git ~/workdir/repos/config
   cd ~/workdir/repos/config
   ./setup.sh
   ```

### Fedora

```bash
git clone https://github.com/junhyukhan/config.git ~/workdir/repos/config
cd ~/workdir/repos/config
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

### Moving the repo

Stow uses relative symlinks, so moving this repo breaks every link. Just re-run setup from the new location — it uses `stow -R` (restow), which is idempotent and rebuilds the links:
```bash
cd /new/path/to/config
./setup.sh
```

## How it works

GNU Stow creates symlinks from `$HOME` into this repo. When you edit `~/.config/nvim/init.lua`, you're editing the repo file directly -- no sync step needed.

```bash
# Link a specific package (-R = restow, idempotent)
stow -R -t ~ nvim

# The claude package MUST use --no-folding, or ~/.claude becomes a single
# symlink and Claude Code's runtime state gets written into this repo.
stow -R --no-folding -t ~ claude

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
| **zsh** | Zsh with powerlevel10k (`.p10k.zsh`), fzf, zoxide, syntax highlighting, autosuggestions |
| **ghostty** | Ghostty terminal emulator config |
| **vim** | Basic vim config |
| **Brewfile** | Homebrew packages and casks (macOS) |
| **packages.txt** | dnf packages (Fedora) |
| **claude** | Claude Code agent config: `settings.json`, global `AGENTS.md`, slash commands, hooks, skills |
| **cloudflared** | Dev gateway tunnel config (Fedora only, auto-stowed by setup.sh) |
| **templates + scripts** | `new-repo.sh` scaffolds the standard `AGENTS.md` / `CLAUDE.md` / `docs/` into a new workspace repo |
