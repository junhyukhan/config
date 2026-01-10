#!/bin/bash

# Define Repo Root (One level up from scripts/)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🔄 Syncing SYSTEM configs TO Repository..."

# Function to safely copy
sync_file() {
    local sys_path="$1"
    local repo_path="$2"
    
    if [ -f "$sys_path" ]; then
        mkdir -p "$(dirname "$repo_path")"
        cp "$sys_path" "$repo_path"
        echo "✅ Copied: $sys_path -> $repo_path"
    else
        echo "⚠️  Skipped (Not found): $sys_path"
    fi
}

# 1. Neovim
sync_file "$HOME/.config/nvim/init.lua" "$REPO_ROOT/nvim/init.lua"
# sync_file "$HOME/.config/nvim/lua" "$REPO_ROOT/nvim/lua" # Uncomment if using external lua files

# 2. Ghostty
sync_file "$HOME/.config/ghostty/config" "$REPO_ROOT/ghostty/config"

# 3. Zsh
sync_file "$HOME/.zshrc" "$REPO_ROOT/zsh/zshrc"

# 4. Git (Copy base config ONLY if you maintain a separate file, 
#    otherwise we skip copying gitconfig to avoid leaking emails)
#    (We assume you edit the repo file directly for git aliases)

# 5. Mac Specifics
if [[ "$OSTYPE" == "darwin"* ]]; then
    # creating a directory in case it has not been created
    mkdir -p "$REPO_ROOT/mac"

    # Karabiner
    sync_file "$HOME/.config/karabiner/karabiner.json" "$REPO_ROOT/mac/karabiner.json"

    # Homebrew
    echo "🍺 Dumping Brewfile..."
    brew bundle dump --file="$REPO_ROOT/mac/Brewfile" --force
fi

# 6. Fedora/Linux Specifics
if [[ -f /etc/fedora-release ]]; then
    mkdir -p "$REPO_ROOT/fedora"

    echo "📦 Dumping dnf packages..."
    # Export user-installed packages (excluding dependencies)
    dnf repoquery --userinstalled --qf '%{name}' | sort > "$REPO_ROOT/fedora/packages.txt"
    echo "✅ Saved package list to fedora/packages.txt"
fi

echo "🎉 Repo updated! Don't forget to 'git commit' and 'push'."
