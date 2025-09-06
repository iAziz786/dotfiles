# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH
eval "$(starship init zsh)"

export ZSH="$HOME/.oh-my-zsh"

export XDG_CONFIG_HOME="$HOME/.config"

export EDITOR="nvim"
export SUDO_EDITOR="$EDITOR"

# OS Detection
case "$OSTYPE" in
  darwin*)  OS="macos" ;;
  linux*)   OS="linux" ;;
  *)        OS="unknown" ;;
esac
ARCH=$(uname -m)

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(git kubectl docker terraform aws)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='mvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

# iTerm2 integration (macOS only)
[[ "$OS" == "macos" ]] && test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"

# Add GOPATH/bin if go is installed
command -v go &>/dev/null && export PATH="$PATH:$(go env GOPATH)/bin"

# My Personal aliases
alias "$"=""
export EZA_CONFIG_DIR=$HOME/.config/eza
alias ls="eza --all --long --icons --git"
alias lt="eza --all --tree ---level=2 --icons --git"


alias n="nvim"

# Opening zellij
alias zj="zellij"

# Creating local tunnel, create URL at: https://iaziz786.loca.lt/
alias "clt"="lt --port 8080 --subdomain iaziz786 &"

# Add zig if exist
[[ -d "$HOME/.zig" ]] && export PATH="$PATH:$HOME/.zig"


[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# Add work related changes
[ -f ~/.work.sh ] && source ~/.work.sh

[[ $commands[kubectl] ]] && source <(kubectl completion zsh)

[ -f ~/.env ] && source ~/.env

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# NeoVim paths
if [[ "$OS" == "macos" ]]; then
  [[ -d "$HOME/nvim-macos-arm64/bin" ]] && export PATH="$PATH:$HOME/nvim-macos-arm64/bin"
  [[ -d "$HOME/nvim-macos/bin" ]] && export PATH="$PATH:$HOME/nvim-macos/bin"
elif [[ "$OS" == "linux" ]]; then
  [[ -d "$HOME/.local/nvim/bin" ]] && export PATH="$PATH:$HOME/.local/nvim/bin"
  [[ -d "/opt/nvim/bin" ]] && export PATH="$PATH:/opt/nvim/bin"
fi

export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$HOME/.local/bin:$PATH"

eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"

# Docker using layer caching
DOCKER_BUILDKIT=1

# Homebrew paths
if [[ "$OS" == "macos" ]]; then
  if [[ "$ARCH" == "arm64" ]] && [[ -d "/opt/homebrew" ]]; then
    export PATH="/opt/homebrew/bin:$PATH"
    export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
  elif [[ -d "/usr/local/bin" ]]; then
    export PATH="/usr/local/bin:$PATH"
    export PATH="/usr/local/opt/ruby/bin:$PATH"
  fi
elif [[ "$OS" == "linux" ]]; then
  [[ -x "/home/linuxbrew/.linuxbrew/bin/brew" ]] && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
fi

# Mise configuration
if [[ -x "$HOME/.local/bin/mise" ]]; then
  eval "$(~/.local/bin/mise activate)"
  eval "$(~/.local/bin/mise activate zsh)"
elif command -v mise &>/dev/null; then
  eval "$(mise activate)"
  eval "$(mise activate zsh)"
fi

eval "$(zoxide init zsh)"

# bun completions
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Render better text with bat for better looking help page
alias bathelp='bat --plain --language=help'
help() {
  "$@" --help 2>&1 | bathelp
}


. "$HOME/.atuin/bin/env"

eval "$(atuin init zsh)"
