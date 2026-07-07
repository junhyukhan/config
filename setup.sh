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
stow -R -t "$HOME" shell nvim ghostty vim

# claude uses --no-folding so ~/.claude stays a REAL directory with per-file
# symlinks. Without it, stow folds the whole ~/.claude into one symlink and
# Claude Code's runtime state (sessions, jobs, logs...) gets written into the
# repo. See "Restowing / moving the repo" in README.md.
stow -R --no-folding -t "$HOME" claude

# cloudflared is only used on Fedora
if [[ -f /etc/fedora-release ]]; then
    stow -R -t "$HOME" cloudflared
fi

echo "Done! Restart your shell to apply changes."
