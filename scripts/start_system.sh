#!/bin/bash

# Start Football Auto-Mute System
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🏈 Starting Football Auto-Mute System..."

# Activate virtual environment
source venv/bin/activate

# Enable the system
defaults write com.football-auto-mute enabled true

# Start Home Assistant integration if configured
python3 src/ha_integration.py

echo "✅ Football Auto-Mute System started!"
echo "Use ⌘⌥F in Keyboard Maestro to begin detection"
echo "Use ⌘⌥⇧F to toggle system on/off"