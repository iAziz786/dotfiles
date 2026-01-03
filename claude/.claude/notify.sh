#!/bin/bash

action="$1"
message="$2"

case "$OSTYPE" in
  darwin*)
    if [[ "$action" == "sound" ]]; then
      afplay /System/Library/Sounds/Funk.aiff
    elif [[ "$action" == "notify" ]]; then
      osascript -e "display notification \"${message:-Done!}\" with title \"Claude Code\""
    fi
    ;;
  linux*)
    if [[ "$action" == "sound" ]]; then
      if command -v paplay &>/dev/null; then
        paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null ||
        paplay /usr/share/sounds/sound-icons/piano-3.wav 2>/dev/null
      elif command -v aplay &>/dev/null; then
        aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null
      fi
    elif [[ "$action" == "notify" ]]; then
      if command -v notify-send &>/dev/null; then
        notify-send "Claude Code" "${message:-Done!}"
      fi
    fi
    ;;
esac
