#!/bin/bash

# Football Auto-Mute System Setup Script
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🏈 Setting up Football Auto-Mute System..."
echo "Project directory: $PROJECT_DIR"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p temp
mkdir -p backups

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Test Python dependencies
echo "🔍 Testing Python dependencies..."
python3 -c "import anthropic, yaml, requests, PIL; print('✅ All Python dependencies available')"

# Test CEC connection
echo "📺 Testing CEC connection..."
if command -v cec-client &> /dev/null; then
    echo "✅ CEC client found"
    
    # Test CEC device detection
    echo "🔍 Scanning for CEC devices..."
    timeout 10s cec-client -l 2>/dev/null | head -10 || echo "⚠️  Could not detect CEC devices (this is normal if TV is off)"
else
    echo "❌ CEC client not found. Please run install.sh first."
    exit 1
fi

# Check Claude API key
echo "🔑 Checking Claude API key..."
if grep -q "YOUR_CLAUDE_API_KEY_HERE" config/config.yaml; then
    echo "⚠️  Please update your Claude API key in config/config.yaml"
    echo "   Get your API key from: https://console.anthropic.com/"
    
    # Prompt for API key
    read -p "Enter your Claude API key (or press Enter to skip): " API_KEY
    if [ ! -z "$API_KEY" ]; then
        sed -i.bak "s/YOUR_CLAUDE_API_KEY_HERE/$API_KEY/" config/config.yaml
        echo "✅ API key updated"
    fi
else
    echo "✅ Claude API key appears to be configured"
fi

# Test API connection
echo "🧠 Testing Claude API connection..."
if ! grep -q "YOUR_CLAUDE_API_KEY_HERE" config/config.yaml; then
    python3 -c "
import sys
sys.path.append('src')
from football_detector import FootballDetector
import tempfile
from PIL import Image

try:
    detector = FootballDetector('config/config.yaml')
    print('✅ Claude API connection successful')
except Exception as e:
    print(f'❌ Claude API connection failed: {e}')
    sys.exit(1)
" || echo "⚠️  API test failed - check your API key"
fi

# Set up log rotation
echo "📝 Setting up log rotation..."
cat > logs/.logrotate << 'EOF'
/Users/austinglass/football-auto-mute/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 austinglass staff
}
EOF

# Create startup script
echo "🚀 Creating startup script..."
cat > scripts/start_system.sh << 'EOF'
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
EOF

chmod +x scripts/start_system.sh

# Create stop script
echo "🛑 Creating stop script..."
cat > scripts/stop_system.sh << 'EOF'
#!/bin/bash

echo "🏈 Stopping Football Auto-Mute System..."

# Disable the system
defaults write com.football-auto-mute enabled false

# Unmute TV if it's muted
if command -v cec-client &> /dev/null; then
    echo "📺 Ensuring TV is unmuted..."
    echo -e "on 0\nvolup 0\nvolup 0\nvolup 0\nvolup 0\nvolup 0\nq" | cec-client -s -d 1 2>/dev/null || true
fi

echo "✅ Football Auto-Mute System stopped!"
EOF

chmod +x scripts/stop_system.sh

# Create test script
echo "🧪 Creating test script..."
cat > scripts/test_system.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "🧪 Testing Football Auto-Mute System..."

source venv/bin/activate

# Create test screenshot
echo "📷 Creating test screenshot..."
mkdir -p temp
python3 -c "
from PIL import Image, ImageDraw, ImageFont
import os

# Create a test image that looks like a football broadcast
img = Image.new('RGB', (1920, 1080), color='green')
draw = ImageDraw.Draw(img)

# Draw field lines
for i in range(0, 1920, 120):
    draw.line([(i, 0), (i, 1080)], fill='white', width=3)

# Add fake score
draw.rectangle([(50, 50), (400, 150)], fill='blue', outline='white')
draw.text((60, 80), 'HOME 21 - AWAY 14', fill='white')

# Add fake down and distance
draw.rectangle([(1500, 50), (1850, 120)], fill='yellow', outline='black')
draw.text((1510, 70), '2nd & 7 at SF 35', fill='black')

img.save('temp/test_game_screenshot.png')
print('Created test game screenshot')

# Create test commercial screenshot
img2 = Image.new('RGB', (1920, 1080), color='red')
draw2 = ImageDraw.Draw(img2)
draw2.text((600, 400), 'BUY OUR PRODUCT!', fill='white')
draw2.text((700, 500), 'Call 1-800-TEST', fill='white')
img2.save('temp/test_commercial_screenshot.png')
print('Created test commercial screenshot')
"

# Test with game screenshot
echo "🏈 Testing game detection..."
python3 src/km_helper.py temp/test_game_screenshot.png '{"channel": "TEST", "title": "Test Game"}'

echo ""

# Test with commercial screenshot  
echo "📺 Testing commercial detection..."
python3 src/km_helper.py temp/test_commercial_screenshot.png '{"channel": "TEST", "title": "Test Game"}'

echo ""
echo "✅ System test complete!"
echo "Check logs/football_detector.log for detailed results"
EOF

chmod +x scripts/test_system.sh

# Set permissions
echo "🔒 Setting permissions..."
find scripts -name "*.sh" -exec chmod +x {} \;
chmod +x src/*.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Test the system: ./scripts/test_system.sh"
echo "2. Configure Keyboard Maestro (see config/keyboard_maestro_setup.md)"
echo "3. Start the system: ./scripts/start_system.sh"
echo ""
echo "Keyboard shortcuts (after KM setup):"
echo "  ⌘⌥F     - Start/resume detection"
echo "  ⌘⌥⇧F   - Toggle system on/off"
echo ""
echo "Log files:"
echo "  logs/football_detector.log - Main system log"
echo "  logs/km_activity.log - Keyboard Maestro activity"