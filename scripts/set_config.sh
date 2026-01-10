#!/bin/bash

# Define Repo Root (One level up from scripts/)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Deploying configs FROM Repository TO System..."

# Function to safely deploy
deploy_file() {
    local repo_path="$1"
    local sys_path="$2"

    if [ -f "$repo_path" ]; then
        mkdir -p "$(dirname "$sys_path")"
        cp "$repo_path" "$sys_path"
        echo "✅ Deployed: $repo_path -> $sys_path"
    else
        echo "⚠️  Skipped (Not found in repo): $repo_path"
    fi
}

# 1. Neovim
deploy_file "$REPO_ROOT/nvim/init.lua" "$HOME/.config/nvim/init.lua"

# 2. Ghostty
deploy_file "$REPO_ROOT/ghostty/config" "$HOME/.config/ghostty/config"

# 3. Zsh
deploy_file "$REPO_ROOT/zsh/zshrc" "$HOME/.zshrc"

# 4. Mac Specifics
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Karabiner
    deploy_file "$REPO_ROOT/mac/karabiner.json" "$HOME/.config/karabiner/karabiner.json"

    # Homebrew - install packages from Brewfile
    if [ -f "$REPO_ROOT/mac/Brewfile" ]; then
        echo "🍺 Installing Homebrew packages..."
        brew bundle --file="$REPO_ROOT/mac/Brewfile"
    fi
fi

# 5. Fedora/Linux Specifics
if [[ -f /etc/fedora-release ]]; then
    # Install dnf packages
    if [ -f "$REPO_ROOT/fedora/packages.txt" ]; then
        echo "📦 Installing dnf packages..."
        # Filter out comments and empty lines, then install
        grep -v '^#' "$REPO_ROOT/fedora/packages.txt" | grep -v '^$' | xargs sudo dnf install -y
    fi
fi

echo "🎉 Configs deployed! You may need to restart your shell or apps."
