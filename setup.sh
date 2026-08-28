#!/bin/bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --------------------------------------------------------------------
# 1. Install platform packages
# --------------------------------------------------------------------
if [[ "$OSTYPE" == darwin* ]]; then
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found. Install it first:"
        echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    echo "Installing Homebrew packages..."
    brew bundle --file="$REPO_DIR/mac/Brewfile"

elif [[ -f /etc/fedora-release ]]; then
    echo "Installing dnf packages..."
    grep -v '^#' "$REPO_DIR/fedora/packages.txt" | grep -v '^$' | xargs sudo dnf install -y

    # Powerlevel10k (not available via dnf)
    if [[ ! -d "$HOME/powerlevel10k" ]]; then
        echo "Cloning powerlevel10k..."
        git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$HOME/powerlevel10k"
    fi

    # Install Ghostty terminfo system-wide so sudo commands work
    if infocmp xterm-ghostty &>/dev/null && ! sudo infocmp xterm-ghostty &>/dev/null 2>&1; then
        echo "Installing Ghostty terminfo system-wide..."
        infocmp -x xterm-ghostty | sudo tic -x -
    fi
fi

# --------------------------------------------------------------------
# 2. Set default shell to zsh
# --------------------------------------------------------------------
if [[ "$SHELL" != */zsh ]]; then
    echo "Changing default shell to zsh..."
    chsh -s "$(which zsh)"
fi

# --------------------------------------------------------------------
# 3. Link configs with GNU Stow
# --------------------------------------------------------------------
echo "Linking configs..."
cd "$REPO_DIR"

# --restow (-R) is idempotent: safe to re-run, and fixes broken links after
# the repo is moved (stow's relative symlinks break when the repo path changes).
stow -R -t "$HOME" shell nvim ghostty vim git tmux

# claude uses --no-folding so ~/.claude stays a REAL directory with per-file
# symlinks. Without it, stow folds the whole ~/.claude into one symlink and
# Claude Code's runtime state (sessions, jobs, logs...) gets written into the
# repo. See "`claude` package uses --no-folding" in AGENTS.md.
stow -R --no-folding -t "$HOME" claude

# codex: --no-folding for the same reason as claude (~/.codex holds sessions,
# SQLite DBs, logs, caches). The package tracks ONE file -- AGENTS.md, itself a
# symlink to claude/.claude/AGENTS.md -- so Codex loads the same global
# instructions Claude Code does. Before 2026-08-29 ~/.codex/AGENTS.md was an
# untracked real file containing a self-referential "@AGENTS.md", so Codex was
# very likely running with no global instructions at all.
stow -R --no-folding -t "$HOME" codex

# cloudflared is only used on Fedora
if [[ -f /etc/fedora-release ]]; then
    stow -R -t "$HOME" cloudflared
fi

# vscode is darwin-only: its config path is macOS-specific
# (Library/Application Support/Code/User); Fedora uses ~/.config/Code/User.
# --no-folding for the same reason as claude -- that User/ directory also holds
# VS Code's own state (globalStorage, History, profiles, workspaceStorage), and
# folding it would move all of that into this repo.
if [[ "$OSTYPE" == darwin* ]]; then
    stow -R --no-folding -t "$HOME" vscode
fi

# --------------------------------------------------------------------
# 4. Tools no package manager carries
# --------------------------------------------------------------------
# Same pattern as powerlevel10k above: guarded, idempotent, skipped if present.
# A tool installed this way is DECLARED here rather than tracked as files --
# the binaries and anything they generate (hooks, caches) are theirs to write.

# herdr - agent-aware terminal multiplexer (herdr.dev). The installer reads
# herdr.dev/latest.json and drops the binary in ~/.local/bin, which .zshrc
# already puts on PATH.
if ! command -v herdr &>/dev/null; then
    echo "Installing herdr..."
    curl -fsSL https://herdr.dev/install.sh | sh
fi
# Its Claude Code integration writes ~/.claude/hooks/herdr-agent-state.sh, which
# the tracked settings.json references. Installing it here is what makes that
# reference valid on a fresh machine -- the hook itself is herdr's to own, so it
# is deliberately not tracked.
if command -v herdr &>/dev/null && [[ ! -f "$HOME/.claude/hooks/herdr-agent-state.sh" ]]; then
    echo "Installing herdr's Claude Code integration..."
    herdr integration install claude || true
fi

# --------------------------------------------------------------------
# 5. Bootstrap check -- things you must have installed to get this far
# --------------------------------------------------------------------
# Claude Code self-installs and self-updates (`claude update`), so declaring an
# install here would be theatre: you cannot run an agent session without it.
# Report it instead, so a fresh machine surfaces the gap rather than hiding it.
if ! command -v claude &>/dev/null; then
    echo "NOTE: Claude Code is not installed. See https://claude.com/product/claude-code"
fi

echo "Done! Restart your shell to apply changes."
