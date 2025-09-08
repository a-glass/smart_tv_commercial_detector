#!/bin/bash

# Football Auto-Mute System Installation Script
set -e

echo "🏈 Installing Football Auto-Mute System..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "✅ Homebrew already installed"
fi

# Install libcec for HDMI-CEC control
echo "📺 Installing libcec for TV control..."
brew install libcec

# Install Python if not present
if ! command -v python3 &> /dev/null; then
    echo "🐍 Installing Python..."
    brew install python@3.11
else
    echo "✅ Python already installed"
fi

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
chmod +x scripts/*.sh

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Configure your Claude API key in config/config.yaml"
echo "2. Set up Home Assistant integration if desired"
echo "3. Import the Keyboard Maestro macro from config/FootballAutoMute.kmmacros"
echo "4. Test CEC connection with your TV"