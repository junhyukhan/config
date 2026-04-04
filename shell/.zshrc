# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# ====================================================================
# My Zsh Configuration
# ====================================================================
# Structure:
# 0. Environment & Variables
# 1. History Settings
# 2. Completion System
# 3. Navigation & Utilities (Zoxide, FZF)
# 4. Aliases (Eza, Bat, Git)
# 5. Plugins & Prompts (Atuin, Starship)
# ====================================================================

# --------------------------------------------------------------------
# Section 0: Environment & Variables
# --------------------------------------------------------------------
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export EDITOR='nvim'
export PATH="$HOME/.local/bin:$PATH"

# Detect platform and set plugin/theme paths
if [[ "$OSTYPE" == darwin* ]]; then
    export BREW_PREFIX=$(brew --prefix)
    ZSH_HIGHLIGHT="$BREW_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
    ZSH_SUGGEST="$BREW_PREFIX/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
    P10K_THEME="$BREW_PREFIX/share/powerlevel10k/powerlevel10k.zsh-theme"
else
    ZSH_HIGHLIGHT="/usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
    ZSH_SUGGEST="/usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
    P10K_THEME="$HOME/powerlevel10k/powerlevel10k.zsh-theme"
fi

# Kubernetes Config
export KUBECONFIG=~/.kube/config:~/.kube/k3s-config

# Fix systemd pager warnings in non-standard terminals
export SYSTEMD_LESS=FRXMK

# --------------------------------------------------------------------
# Section 1: History Settings
# --------------------------------------------------------------------
# Note: Atuin handles most history, but these are good fallbacks.
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt SHARE_HISTORY
setopt EXTENDED_HISTORY

# --------------------------------------------------------------------
# Section 2: Completion System
# --------------------------------------------------------------------
autoload -U compinit && compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' auto-description 'specify: %d'
setopt COMPLETE_IN_WORD
setopt ALWAYS_TO_END

# --------------------------------------------------------------------
# Section 3: Navigation & Utilities
# --------------------------------------------------------------------
setopt AUTO_CD

# Initialize Zoxide (Smarter 'cd')
# usage: 'z directory_name'
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi

# Initialize FZF
# usage: Ctrl+T (files), Ctrl+R (history - unless Atuin takes over)
if command -v fzf >/dev/null 2>&1; then
  source <(fzf --zsh)
fi

# --------------------------------------------------------------------
# Section 4: Aliases
# --------------------------------------------------------------------
# Navigation
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Modern Replacements (Eza instead of ls)
if command -v eza >/dev/null 2>&1; then
  alias ls='eza --icons --group-directories-first'
  alias ll='eza --icons --group-directories-first -l'
  alias la='eza --icons --group-directories-first -la'
  alias tree='eza --icons --tree'
elif [[ "$OSTYPE" == darwin* ]]; then
  alias ls='ls -G'
  alias ll='ls -lFh'
  alias la='ls -lAFh'
else
  alias ls='ls --color=auto'
  alias ll='ls -lFh'
  alias la='ls -lAFh'
fi

# 'cat' with syntax highlighting (requires 'bat')
if command -v bat >/dev/null 2>&1; then
  alias cat='bat'
fi

# Tools

alias vi='nvim'
alias vim='nvim'

# --------------------------------------------------------------------
# Section 5: Load Plugins & Prompts (ALWAYS LAST)
# --------------------------------------------------------------------

# 1. Zsh Syntax Highlighting & Autosuggestions
[[ -f "$ZSH_HIGHLIGHT" ]] && source "$ZSH_HIGHLIGHT"
[[ -f "$ZSH_SUGGEST" ]] && source "$ZSH_SUGGEST"

# 2. Atuin (Magical Shell History)
# This replaces standard Ctrl+R and Up-Arrow history search
# if [ -f "$HOME/.atuin/bin/env" ]; then
    # . "$HOME/.atuin/bin/env"
    # eval "$(atuin init zsh)"
    # If you prefer standard Up-Arrow search, uncomment the bindkey lines below
    # and configure Atuin to not bind up-arrow in its config.toml
# else
    # Fallback if Atuin isn't present
    autoload -U up-line-or-beginning-search down-line-or-beginning-search
    zle -N up-line-or-beginning-search
    zle -N down-line-or-beginning-search
    bindkey "^[[A" up-line-or-beginning-search
    bindkey "^[[B" down-line-or-beginning-search
# fi

# 3. Powerlevel10k Prompt
# Must be last to capture previous command exit codes correctly
[[ -f "$P10K_THEME" ]] && source "$P10K_THEME"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Antigravity (macOS only)
if [[ "$OSTYPE" == darwin* ]] && [[ -d "$HOME/.antigravity/antigravity/bin" ]]; then
    export PATH="$HOME/.antigravity/antigravity/bin:$PATH"
fi
