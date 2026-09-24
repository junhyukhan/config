# Setting up a new Mac

`setup.sh` does most of it. This is the rest, in order. Why it is shaped this way:
[`decisions/new-mac-setup.md`](decisions/new-mac-setup.md).

## Before you leave the old Mac

- **`agentlab` has no remote.** Its history exists only on the old Mac. Add a private remote and
  push before anything else. `archive/hskorea-util` has none either, if you want to keep it.
- **Local-only files to carry across**, file to file and never printed:
  - Claude's memory: `~/.claude/projects/-Users-junhyukhan-workdir-repos/memory/`. Keep the same
    `~/workdir/repos` path on the new Mac; the folder name is derived from it.
  - `~/.supabase/access-token`, which `.zshenv` reads for the Supabase MCP.
  - `quant/.env` and `jhkn-dev/.env`. duri's secrets are in Infisical.
- **`~/.ssh/config`**: two `Host` entries for the homelab box (`jun-hp-spectre`, `jun-hp-spectre-lan`).
  Not tracked, because this repo is public. Note them down.

## On the new Mac

1. **Base tools**: `xcode-select --install`, then install Homebrew with the one-liner from brew.sh.
2. **Clone and run setup**:
   ```bash
   git clone https://github.com/junhyukhan/workspace.git ~/workdir/repos
   git clone https://github.com/junhyukhan/config ~/workdir/repos/config
   cd ~/workdir/repos/config && ./setup.sh
   ```
   That installs the core Brewfile, sets zsh, stows every package and installs Herdr with its
   Claude Code integration.
3. **Install what the Brewfile does not carry**:
   - Tailscale, from its own package installer at pkgs.tailscale.com.
   - Amphetamine and Bitwarden, from the App Store.
   - DSMacLinker.
   - Claude Code, if `setup.sh` reported it missing.
4. **Sign in**: `gh auth login`, `claude`, `infisical login`, Tailscale, and the App Store.
5. **SSH**: make a new key for this Mac (`ssh-keygen -t ed25519`), add its public half to the box's
   `authorized_keys`, and recreate the two `Host` entries.
6. **Clone the child repos** into `~/workdir/repos`: `duri-v3`, `homelab`, `jhkn.dev` as `jhkn-dev`,
   `learning`, `quant`, and `agentlab` from its new remote. Then `pnpm install` in `duri-v3` and
   `uv sync` in `quant` and `learning`.
7. **Put the carried files in place**: the memory folder, the Supabase token and the two `.env` files.
8. **quant**: if it will run on this Mac, register the Mac's public IP in the Toss WTS panel first.
9. **Check**: from `~/workdir/repos`, run `python3 agentlab/ops/index.py`. Then start a Claude
   session and run `/context` and `/memory`.

## Rules

- **The Brewfile is the core only.** An app you want on one machine is simply installed there.
- **Never run `brew bundle cleanup`.** Against a core-only Brewfile it would uninstall everything
  else brew put on the machine.
- **An app installed outside brew can be adopted** with `brew install --cask --adopt <name>`, but
  only when its version matches the cask's. Apps that update themselves need no adopting: brew
  skips them on upgrade either way.
- **macOS settings are not tracked.** Set them by hand.
