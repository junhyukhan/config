# config

Personal dotfiles for macOS and Fedora Linux.

## Structure

```
config/
├── scripts/
│   ├── set_config.sh    # Deploy configs from repo to system
│   └── update_repo.sh   # Sync configs from system to repo
├── mac/
│   ├── Brewfile         # Homebrew packages
│   └── karabiner.json   # Keyboard remapping
├── fedora/
│   └── packages.txt     # dnf packages
├── nvim/
│   └── init.lua         # Neovim configuration
├── ghostty/
│   └── config           # Ghostty terminal config
└── zsh/
    └── zshrc            # Zsh configuration
```

## Quick Start

### macOS

1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Clone this repo and deploy configs:
   ```bash
   git clone https://github.com/junhyukhan/config.git ~/dev/github/config
   cd ~/dev/github/config
   ./scripts/set_config.sh
   ```

3. Set up Karabiner for right command key input switching:
   - Install Karabiner Elements (included in Brewfile)
   - Config is automatically deployed to `~/.config/karabiner/`
   - In **System Settings > Keyboard > Shortcuts > Input Sources**, set input switch to F18

### Fedora

1. Clone this repo and deploy configs:
   ```bash
   git clone https://github.com/junhyukhan/config.git ~/dev/github/config
   cd ~/dev/github/config
   ./scripts/set_config.sh
   ```

2. Some tools require manual installation:
   ```bash
   # Powerlevel10k
   git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.powerlevel10k

   # uv (Python package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # bun
   curl -fsSL https://bun.sh/install | bash
   ```

## Usage

### Deploying configs (repo to system)

Run this on a new machine or after pulling updates:

```bash
./scripts/set_config.sh
```

This will:
- Copy nvim, ghostty, zsh configs to their system locations
- **(Mac)** Install Homebrew packages and deploy Karabiner config
- **(Fedora)** Install dnf packages

### Saving configs (system to repo)

Run this after making changes to your local configs:

```bash
./scripts/update_repo.sh
```

This will:
- Copy nvim, ghostty, zsh configs from system to repo
- **(Mac)** Dump Brewfile and copy Karabiner config
- **(Fedora)** Export installed packages to packages.txt

Then commit and push your changes:
```bash
git add -A && git commit -m "update configs" && git push
```

## What's Included

| Config | Description |
|--------|-------------|
| **nvim** | Neovim config based on kickstart.nvim with LSP, Telescope, Treesitter |
| **zsh** | Zsh with powerlevel10k, fzf, zoxide, syntax highlighting, autosuggestions |
| **ghostty** | Ghostty terminal emulator config |
| **Brewfile** | Homebrew packages and casks (macOS) |
| **karabiner** | Right command key remapped to F18 for input switching (macOS) |
| **packages.txt** | dnf packages (Fedora) |
