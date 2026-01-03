#!/bin/zsh

# Read JSON input from Claude Code
input=$(cat)
cwd=$(echo "$input" | jq -r '.workspace.current_dir')

# Catppuccin Mocha colors (ANSI 256-color codes for terminal compatibility)
c_surface0="\033[38;5;237m"
c_text="\033[38;5;189m"
c_peach="\033[38;5;216m"
c_green="\033[38;5;150m"
c_teal="\033[38;5;152m"
c_blue="\033[38;5;111m"
c_yellow="\033[38;5;229m"
c_purple="\033[38;5;183m"
c_mantle="\033[38;5;234m"
c_base="\033[38;5;235m"
c_red="\033[38;5;210m"
reset="\033[0m"

output=""

# ==================== OS Symbol ====================
os_symbol=""
case "$OSTYPE" in
  darwin*) os_symbol="" ;;
  linux*)
    if [[ -f /etc/os-release ]]; then
      . /etc/os-release
      case "$ID" in
        ubuntu) os_symbol="󰕈" ;;
        debian) os_symbol="󰣚" ;;
        arch) os_symbol="󰣇" ;;
        fedora) os_symbol="󰣛" ;;
        *) os_symbol="󰌽" ;;
      esac
    else
      os_symbol="󰌽"
    fi
    ;;
esac

# ==================== Username ====================
username=$(whoami)
output+="${c_surface0}${os_symbol} ${username}${reset}"

# ==================== Directory ====================
dir_path="$cwd"
# Apply directory substitutions
dir_path="${dir_path/#$HOME\/Documents/󰈙 }"
dir_path="${dir_path/#$HOME\/Downloads/ }"
dir_path="${dir_path/#$HOME\/Music/󰝚 }"
dir_path="${dir_path/#$HOME\/Pictures/ }"
dir_path="${dir_path/#$HOME\/Developer/󰲋 }"
dir_path="${dir_path/#$HOME/~}"

# Truncate to last 3 components if needed
IFS='/' read -rA path_parts <<< "$dir_path"
if [[ ${#path_parts[@]} -gt 3 ]]; then
  dir_display="…/${path_parts[-3]}/${path_parts[-2]}/${path_parts[-1]}"
else
  dir_display="$dir_path"
fi

output+=" ${c_peach}${dir_display}${reset}"

# ==================== Git Information ====================
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  # Git branch
  branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null)
  if [[ -z "$branch" ]]; then
    # Detached HEAD - show short commit hash
    branch=$(git -C "$cwd" --no-optional-locks rev-parse --short HEAD 2>/dev/null)
  fi

  if [[ -n "$branch" ]]; then
    output+=" ${c_green} ${branch}${reset}"

    # Git status
    git_status=""

    # Check for untracked files
    if [[ -n $(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null) ]]; then
      git_status+="?"
    fi

    # Check for modified files
    if ! git -C "$cwd" --no-optional-locks diff --quiet 2>/dev/null; then
      git_status+="!"
    fi

    # Check for staged files
    if ! git -C "$cwd" --no-optional-locks diff --cached --quiet 2>/dev/null; then
      git_status+="+"
    fi

    # Check for stashed changes
    if git -C "$cwd" --no-optional-locks rev-parse --verify refs/stash >/dev/null 2>&1; then
      git_status+="$"
    fi

    # Check ahead/behind
    upstream=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref @{upstream} 2>/dev/null)
    if [[ -n "$upstream" ]]; then
      ahead=$(git -C "$cwd" --no-optional-locks rev-list --count @{upstream}..HEAD 2>/dev/null)
      behind=$(git -C "$cwd" --no-optional-locks rev-list --count HEAD..@{upstream} 2>/dev/null)

      if [[ "$ahead" -gt 0 ]]; then
        git_status+="⇡${ahead}"
      fi
      if [[ "$behind" -gt 0 ]]; then
        git_status+="⇣${behind}"
      fi
    fi

    if [[ -n "$git_status" ]]; then
      output+=" ${c_green}${git_status}${reset}"
    fi
  fi
fi

# ==================== Language Versions ====================
lang_info=""

# Node.js
if [[ -f "$cwd/package.json" ]]; then
  if command -v node &>/dev/null; then
    node_version=$(node --version 2>/dev/null | sed 's/v//')
    if [[ -n "$node_version" ]]; then
      lang_info+="${c_teal} ${node_version}${reset} "
    fi
  fi
fi

# Python
if [[ -f "$cwd/pyproject.toml" ]] || [[ -f "$cwd/requirements.txt" ]] || [[ -f "$cwd/setup.py" ]] || [[ -f "$cwd/.python-version" ]]; then
  if command -v python3 &>/dev/null; then
    python_version=$(python3 --version 2>/dev/null | awk '{print $2}')
    if [[ -n "$python_version" ]]; then
      lang_info+="${c_teal} ${python_version}${reset} "
    fi
  fi
fi

# Rust
if [[ -f "$cwd/Cargo.toml" ]]; then
  if command -v rustc &>/dev/null; then
    rust_version=$(rustc --version 2>/dev/null | awk '{print $2}')
    if [[ -n "$rust_version" ]]; then
      lang_info+="${c_teal} ${rust_version}${reset} "
    fi
  fi
fi

# Go
if [[ -f "$cwd/go.mod" ]] || [[ -f "$cwd/go.sum" ]]; then
  if command -v go &>/dev/null; then
    go_version=$(go version 2>/dev/null | awk '{print $3}' | sed 's/go//')
    if [[ -n "$go_version" ]]; then
      lang_info+="${c_teal} ${go_version}${reset} "
    fi
  fi
fi

# Java
if [[ -f "$cwd/pom.xml" ]] || [[ -f "$cwd/build.gradle" ]] || [[ -f "$cwd/build.gradle.kts" ]]; then
  if command -v java &>/dev/null; then
    java_version=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}')
    if [[ -n "$java_version" ]]; then
      lang_info+="${c_teal} ${java_version}${reset} "
    fi
  fi
fi

# PHP
if [[ -f "$cwd/composer.json" ]]; then
  if command -v php &>/dev/null; then
    php_version=$(php -v 2>/dev/null | head -n 1 | awk '{print $2}')
    if [[ -n "$php_version" ]]; then
      lang_info+="${c_teal} ${php_version}${reset} "
    fi
  fi
fi

if [[ -n "$lang_info" ]]; then
  output+=" ${lang_info}"
fi

# ==================== Docker Context ====================
# Only show when Docker-related files exist (matching Starship behavior)
if command -v docker &>/dev/null; then
  show_docker=false
  if [[ -f "$cwd/Dockerfile" ]] || \
     [[ -f "$cwd/docker-compose.yml" ]] || \
     [[ -f "$cwd/docker-compose.yaml" ]] || \
     [[ -f "$cwd/compose.yml" ]] || \
     [[ -f "$cwd/compose.yaml" ]] || \
     [[ -n "$DOCKER_HOST" ]] || \
     [[ -n "$DOCKER_MACHINE_NAME" ]] || \
     [[ -n "$COMPOSE_FILE" ]]; then
    show_docker=true
  fi

  if [[ "$show_docker" == "true" ]]; then
    docker_context=$(docker context show 2>/dev/null)
    if [[ -n "$docker_context" ]]; then
      output+=" ${c_blue} ${docker_context}${reset}"
    fi
  fi
fi

# ==================== Session Token Usage ====================
transcript_path=$(echo "$input" | jq -r '.transcript_path // ""')
context_limit=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

if [[ -n "$transcript_path" ]] && [[ -f "$transcript_path" ]]; then
  # Get the last assistant message's usage from transcript
  usage=$(tail -20 "$transcript_path" 2>/dev/null | jq -s 'map(select(.type == "assistant" and .message.usage)) | last | .message.usage // empty' 2>/dev/null)

  if [[ -n "$usage" ]]; then
    # Total context = input_tokens + cache_creation + cache_read
    context_tokens=$(echo "$usage" | jq '(.input_tokens // 0) + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)')

    if [[ "$context_tokens" -gt 0 ]] && [[ "$context_limit" -gt 0 ]]; then
      token_percent=$((context_tokens * 100 / context_limit))
      # Format token count (e.g., 44.7k)
      if [[ "$context_tokens" -ge 1000 ]]; then
        token_display=$(awk "BEGIN {printf \"%.1fk\", $context_tokens/1000}")
      else
        token_display="$context_tokens"
      fi
      # Color based on usage level
      if [[ "$token_percent" -ge 80 ]]; then
        token_color="$c_red"
      elif [[ "$token_percent" -ge 50 ]]; then
        token_color="$c_yellow"
      else
        token_color="$c_teal"
      fi
      limit_display=$((context_limit / 1000))
      output+=" ${token_color}󰊤 ${token_display}/${limit_display}k (${token_percent}%)${reset}"
    fi
  fi
fi

# ==================== Time ====================
current_time=$(date +%R)
output+=" ${c_purple} ${current_time}${reset}"

# Output the final status line
printf "%b" "$output"
