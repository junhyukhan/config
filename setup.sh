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
    # One failed package (a network blip, a cask checksum mismatch) must not stop the
    # config links below from being made. Warn, carry on, and remind at the end;
    # every step here is idempotent, so a re-run retries only what failed.
    if ! brew bundle --file="$REPO_DIR/mac/Brewfile"; then
        BUNDLE_FAILED=1
        echo "WARNING: some Brewfile packages failed to install. Continuing so the configs still get linked."
    fi

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

# Settings contain private machine context and application-written preferences.
# Bootstrap a regular local file (or detach the legacy settings symlink without
# changing its contents). Existing regular settings are never overwritten.
python3 "$REPO_DIR/scripts/install-claude-settings.py"

# Only hooks are stowed. The package-local ignore excludes settings.json;
# --no-folding keeps runtime state out of the repository.
stow -R --no-folding -t "$HOME" claude

# zed: --no-folding for the same reason -- only its settings file is tracked.
stow -R --no-folding -t "$HOME" zed

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

# Herdr - herdr-core (`hc`) keeps terminals and agents alive; the Herdr app
# (macOS) and the Herdr mobile app are its clients. Both installers read
# releases.herdr.dev/<core|app>/latest.json and check the SHA-256 before
# installing. The app installer puts Herdr.app in ~/Applications and installs
# herdr-core into ~/.local/bin only if none exists; after that, the app keeps
# itself and the core updated. Linux machines get only the core: the Mac and
# the phone reach them over SSH (`hc machine add`), and `hc machine update`
# updates it from the Mac.
if [[ "$OSTYPE" == darwin* ]]; then
    if [[ ! -d "$HOME/Applications/Herdr.app" && ! -d /Applications/Herdr.app ]]; then
        echo "Installing the Herdr app (and herdr-core)..."
        curl -fsSL https://releases.herdr.dev/app/install.sh | sh
    fi
elif ! command -v herdr-core &>/dev/null && [[ ! -x "$HOME/.local/bin/herdr-core" ]]; then
    echo "Installing herdr-core..."
    curl -fsSL https://releases.herdr.dev/core/install.sh | sh
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

if [[ -n "${BUNDLE_FAILED:-}" ]]; then
    echo "WARNING: some Homebrew packages failed earlier. Re-run ./setup.sh to retry them."
fi

echo "Done! Restart your shell to apply changes."
