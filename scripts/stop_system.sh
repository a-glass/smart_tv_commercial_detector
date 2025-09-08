#!/bin/bash

echo "🏈 Stopping Football Auto-Mute System..."

# Disable the system
defaults write com.football-auto-mute enabled false

# Unmute TV if it's muted (only if CEC is available)
if command -v cec-client &> /dev/null; then
    echo "📺 Ensuring TV is unmuted..."
    echo -e "on 0\nvolup 0\nvolup 0\nvolup 0\nvolup 0\nvolup 0\nq" | cec-client -s -d 1 2>/dev/null || true
fi

echo "✅ Football Auto-Mute System stopped!"