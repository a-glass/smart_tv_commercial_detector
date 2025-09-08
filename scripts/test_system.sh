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